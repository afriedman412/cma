"""
Adapted from https://github.com/MichaelKlemm/DJ-Database-Sync

TODO: add non-mp3 support!!!
"""

import mmap
import struct
from mutagen.id3 import ID3
from assets import label_table, serato_id3_import_table
from typing import List, Union, Optional

verbose = False
ignore_unknown = False

class SeratoObject:
    def __init__(self, object_type: str=None, object_data=None, object_len: int=0):
        self.object_type = object_type
        self.object_data = object_data if object_data else []
        self.dtype, self.label = label_table.get(self.object_type, (None, None))
        self.object_len = self.set_object_len()
        
    def __repr__(self):
        return f"(type: {self.object_type} // len: {self.object_len} // data: {self.object_data})"

    def set_object_len(self):
        if not self.dtype:
            return 0
        elif self.dtype == "s":
            return 2*(len(str(self.object_data))) # tweaked for ID3TimeStamp objects -- verify this!
        elif self.dtype[0] == "u":
            len_table = {"u8": 1, "u16": 2, "u32": 4}
            return len_table[self.dtype]
        else:
            return None

    def encode_compound_data(self) -> bytes:
        if len(self.object_data) < 1:
            encoded_data = b'\x00'
        else:
            for o_ in self.object_data:
                assert isinstance(o_, SeratoObject), f"bad object type: {type(o_)}"
                encoded_data += b"".join(list(o_.unparse()))
        
        return encoded_data

    def encode_data(self, data_len_only: bool=False):
        encoded_type = self.object_type.encode("utf-8")
        encoded_len = struct.pack(">I", self.object_len)

        encoded_data = b""
        if isinstance(self.object_data, List):
            encoded_data = self.encode_compound_data()
        
        elif self.dtype == "s":
            encoded_data = self.object_data.encode('utf-16be')

        elif self.dtype[0] == "u":
            encoding_table = {"u8": ">B", "u16": ">H", "u32": ">I"}
            try:
                encoded_data = struct.pack(encoding_table[self.dtype], int(self.object_data))
            except:
                raise ValueError(f"encoding table expected integer for {self.object_type} ({self.dtype})")
                
            assert len(encoded_data) == self.object_len, f"encoded length ({len(encoded_data)}) is not equal to object length ({self.object_len})"

        if data_len_only:
            return len(encoded_data)

        else:
            return encoded_type, encoded_len, encoded_data


class SeratoTrack(SeratoObject):
    def __init__(self, path: str, import_data: bool=True):
        super(SeratoTrack, self).__init__()
        self.object_type = "otrk"
        if import_data:
            self.songs_to_data(path)
            self.object_data.append(SeratoObject("pfil", path))
        else:
            self.object_data = [SeratoObject("ptrk", path)]
        return
    
    def songs_to_data(self, path: str):
        imported_data = self.extract_song_data(path)
        for k, v in imported_data.items():
            self.object_data.append(self.song_data_to_object(k, v))

        # TODO: add other possible tags

    
    def extract_song_data(self, path: str):
        """
        This assumes the file is an mp3!!
        """
        i = ID3(path)
        
        def import_tag(k):
            try: 
                return i.get(k).text[0]
            except AttributeError:
                return None

        imported_data = {
            serato_tag:import_tag(id3_tag) for id3_tag, serato_tag in serato_id3_import_table.items()
        }

        return imported_data
    
    def song_data_to_object(self, serato_tag, value):
        return SeratoObject(serato_tag, value)    


class SeratoStorage:
    """
    Works for DB or crate!

    unparse_and_write works too!
    """
    global verbose
    def __init__(self, path: Optional[str]):
        self.objects = []
        self.object = None
        if path:
            self.load_all_data(path)
        return

    def __len__(self):
        return len(self.objects)

    def __repr__(self):
        return self.objects if len(self.objects) < 10 else self.objects[:10]
    
    def load_all_data(self, path: str):
        with open(path, "r+b") as f:
            self.data = mmap.mmap(f.fileno(), 0)
        self.yield_all()
        
    def load_next_header(self):
        object_type = self.read_bytes(4).decode('utf-8')
        object_len = struct.unpack(">I", self.read_bytes(4))[0]
        if verbose:
            print(object_type, object_len, self.data.tell())
        return object_type, object_len
    
    def yield_object(self):
        object_type, object_len = self.load_next_header()
            
        if object_type in ['otrk', 'osrt', 'ovct', 'vrsn']:
            self.reset_object(object_type, object_len)
        
        else:      
            decoded_data = self.parse_object(object_type, object_len)
            o = SeratoObject(object_type, decoded_data, object_len)
            self.object.object_data.append(o)
        
    def yield_all(self):
        while self.data.tell() < self.data.size():
            self.yield_object()
            
        if self.object:
            self.objects.append(self.object)
        
    def read_bytes(self, num_bytes: int) -> bytes:
        return self.data.read(num_bytes)
    
    def parse_object(self, object_type, object_len):
        global ignore_unknown
        dtype, label = label_table.get(object_type, (None, None))
        
        if dtype == "s":
            decoded_data = self.read_bytes(object_len).decode('utf-16be')
            
        elif dtype == 'u32' and object_len == 4:
            decoded_data = struct.unpack(">I", self.read_bytes(4))[0]
            
        elif dtype == 'u16' and object_len == 2:
            decoded_data = struct.unpack(">H", self.read_bytes(2))[0]
            
        elif dtype == 'u8' and object_len == 1:
            decoded_data = struct.unpack(">B", self.read_bytes(1))[0]
            
        else:
            error_string = f"Unknown type '{object_type}' with size {object_len} at position {self.data.tell()}"
            if ignore_unknown:
                print(error_string)
                decoded_data = self.read_bytes(object_len).decode('utf-16be')
                
            else:
                raise IndexError(error_string)
            
        return decoded_data
    
    def reset_object(self, object_type: str, object_len: int, object_data=None):
        try:
            if self.object:
                self.objects.append(self.object)
        except AttributeError:
            pass
        if object_type == 'vrsn':
            decoded_data = self.parse_object(object_type, object_len)
            self.object = SeratoObject(object_type, decoded_data)
            self.yield_object()
        else:
            self.object = SeratoObject(object_type)
            
            
    def peek(self, num_bytes: int=4, start: int=0) -> bytes:
        pos = self.data.tell()
        if start:
            self.data.seek(start)
        data = self.read_bytes(num_bytes)
        self.data.seek(pos)
        return data
    
    def peek_next_object(self):
        return self.peek(4).decode('utf-8')

    def remove_tracks(self):
        self.objects = [o for o in self.objects if o.object_type!='otrk']

    def unparse_and_write(self, output_path: str):
        unparsed_objects = [b"".join(list(o.unparse())) for o in self.objects]

        with open(output_path, "wb+") as f:
            for o in unparsed_objects:
                f.write(o)


class SeratoCrate(SeratoStorage):
    """
    New crate. Load from path if provided, otherwise create an empty crate.

    TODO: see if metadata is required.
    """
    def __init__(self, path: Optional[str]=None):
        super(SeratoCrate, self).__init__(path)
        if not path:
            self.objects.append(SeratoObject('vrsn', "1.0/Serato ScratchLive Crate"))
        return

    def add_track(self, file_path: str):
        track_object = SeratoTrack(file_path, False)
        self.objects.append(track_object)

    