"""
Adapted from https://github.com/MichaelKlemm/DJ-Database-Sync

TODO: add non-mp3 support!!!
"""

import mmap
import struct
from mutagen.id3 import ID3
from ..config.assets import label_table, serato_id3_import_table
from typing import List, Tuple, Optional
import os

verbose = False
ignore_unknown = False

class SeratoObject:
    def __init__(self, object_type: str=None, object_data=None, object_len: int=None):
        self.object_type = object_type
        self.object_data = object_data if object_data else []
        self.dtype, self.label = label_table.get(self.object_type, (None, None))
        self.set_object_len()

        if object_len:
            assert object_len == self.object_len,f"Provided object length ({object_len}) != calculated object len ({self.object_len})"
        
    def __repr__(self):
        return f"(type: {self.object_type} // len: {self.object_len} // data: {self.object_data})"

    def set_object_len(self):
        """
        Might be some issues with some of the encoding lengths here.
        """
        encoded_data = self.encode_data()
        self.object_len = len(encoded_data)

        ### THIS IS THE OLD VERSION, YOU PROBABLY DON'T NEED IT
        # if isinstance(self.object_data, list):
        #     l = len(self.encode_compound_data())
        # elif self.dtype[0] == "u":
        #     len_table = {"u8": 1, "u16": 2, "u32": 4}
        #     l = len_table[self.dtype]
        # elif not self.dtype:
        #     l = 0
        # else: # if self.dtype == "s":
        #     l = 2*(len(str(self.object_data))) # tweaked for ID3TimeStamp objects -- verify this!

    def load_keys_set_len(self):
        """
        To run after loading data.
        """
        # print(f"loading keys, setting len, {self.object_type}")
        self.set_object_len()
        self.data_keys = [d.object_type for d in self.object_data]

    def encode_compound_data(self) -> bytes:
        """
        For objects whose data is a list of serato objects.
        """
        if len(self.object_data) < 1:
            encoded_data = b'\x00'
        else:
            encoded_data = b""
            for o_ in self.object_data:
                assert isinstance(o_, SeratoObject), f"bad object type: {type(o_)}"
                o_.set_object_len()
                encoded_data += b"".join(list(o_.encode_object()))
        
        return encoded_data

    def encode_data(self) -> bytes:
        """
        For all serato objects. 
        """
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

        return encoded_data

    def encode_object(self) -> Tuple[bytes]:
        """
        For the entire object.
        """
        self.set_object_len()
        encoded_type = self.object_type.encode("utf-8")
        encoded_data = self.encode_data()
        encoded_len = struct.pack(">I", self.object_len)
        
        return encoded_type, encoded_len, encoded_data


class SeratoTrack(SeratoObject):
    def __init__(self, path: str=None, import_data: bool=True):
        super(SeratoTrack, self).__init__()
        self.object_type = "otrk"
        if path:
            if import_data:
                self.songs_to_data(path)
                self.object_data.append(SeratoObject("pfil", path))
            else:
                self.object_data = [SeratoObject("ptrk", path)]
            self.load_keys_set_len()
        return

    def __repr__(self):
        if 'pfil' in self.data_keys:
            song_title = ""
            for k in ['tit2', 'tsng']:
                if k in self.data_keys:
                    song_title = self.get_data_by_tag(k)

            song_artist = self.get_data_by_tag('tart')
            
            return ": ".join([song_artist, song_title])
        else:
            return f"(type: {self.object_type} // len: {self.object_len} // data: {self.object_data})"

    def get_data_by_tag(self, tag):
        if tag in self.data_keys:
            return [d.object_data for d in self.object_data if d.object_type==tag][0]
        else:
            return "(NO DATA)"
    
    def songs_to_data(self, path: str):
        # TODO: add other possible tags
        imported_data = self.extract_song_data(path)
        for k, v in imported_data.items():
            self.object_data.append(self.song_data_to_object(k, v))
    
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
    For DB or crate, although crate has its own class.

    TODO: DB class?
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
        o = self.objects if len(self.objects) < 10 else self.objects[:10]
        return str(o)
    
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
            o = SeratoObject(object_type, decoded_data)
            self.object.object_data.append(o)
        
    def yield_all(self):
        while self.data.tell() < self.data.size():
            self.yield_object()
        
        # TODO: clean up the auto-key loading here, and in reset_object
        if self.object:
            if isinstance(self.object, SeratoTrack):
                self.object.load_keys_set_len()

            self.objects.append(self.object)

        self.reset_lens()

    def reset_lens(self):
        """
        Because object lengths are not being appropriately set, this will automatically do that.
        """
        for o in self.objects:
            assert isinstance(o, SeratoObject), f"bad object type: {type(o)}"
            o.set_object_len()

        
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
                if isinstance(self.object, SeratoTrack):
                    self.object.load_keys_set_len()
                self.objects.append(self.object)
        except AttributeError:
            pass
        if object_type == 'vrsn':
            decoded_data = self.parse_object(object_type, object_len)
            self.object = SeratoObject(object_type, decoded_data)
            self.yield_object()
        elif object_type == 'otrk':
            self.object = SeratoTrack()
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

    def reset_object_sizes(self):
        """
        Recalculate the object length for all objects.
        """
        for o in self.objects:
            o.load_keys_set_len()

    def encode_and_write(self, output_path: str):
        encoded_objects = [b"".join(list(o.encode_object())) for o in self.objects]

        with open(output_path, "wb+") as f:
            for o in encoded_objects:
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
        if "/" not in file_path:
            file_path = os.path.join(os.getcwd(), file_path)
        track_object = SeratoTrack(file_path, False)
        self.objects.append(track_object)

    