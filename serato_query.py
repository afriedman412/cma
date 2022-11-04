"""
Adapted from https://github.com/MichaelKlemm/DJ-Database-Sync
"""

import mmap
import struct

verbose = False
ignore_unknown = False

class SeratoObject:
    def __init__(self, object_type: str, object_len: int, object_data=None):
        self.object_type = object_type
        self.object_len = object_len
        self.object_data = object_data if object_data else []
        
    def __repr__(self):
        return f"(type: {self.object_type} // len: {self.object_len} // data: {self.object_data})"


class SeratoStorage:
    """
    Works for DB or crate
    """
    global verbose
    def __init__(self, path: str=None):
        if path:
            self.load_all_data(path)
        self.objects = []
        return
    
    def load_all_data(self, path: str):
        f = open(path, "r+b")
        self.data = mmap.mmap(f.fileno(), 0)
        
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
            o = SeratoObject(object_type, object_len, decoded_data)
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
            self.objects.append(self.object)
        except AttributeError:
            pass
        if object_type == 'vrsn':
            decoded_data = self.parse_object(object_type, object_len)
            self.object = SeratoObject(object_type, object_len, decoded_data)
            self.yield_object()
        else:
            self.object = SeratoObject(object_type, object_len)
            
            
    def peek(self, num_bytes: int, start: int=0) -> bytes:
        pos = self.data.tell()
        if start:
            self.data.seek(start)
        data = self.read_bytes(num_bytes)
        self.data.seek(pos)
        return data
    
    def peek_next_object(self):
        return self.peek(4).decode('utf-8')


label_table = {
            "ptrk": ("s", "path"),  # Crate v1.0
            "pfil": ("s", "path"),  # DB v2.0
            "ttyp": ("s", "filetype"),
            "tsng": ("s", "title"),
            "tart": ("s", "artist"),
            "talb": ("s", "album"),
            "tgen": ("s", "genre"),
            "tlen": ("s", "duration"),
            "tlbl": ("s", "label"),
            "tbit": ("s", "resolution"),
            "tsmp": ("s", "sample_rate"),
            "tbpm": ("s", "beats_per_minute"),
            "ttyr": ("s", "year"),
            "tkey": ("s", "tone_key"),
            "tiid": ("s", "uuid"),
            "tadd": ("s", "track_added"),
            "tcmp": ("s", "composition"),
            "tcor": ("s", "cor"),
            "tcom": ("s", "composition2"),
            "trmx": ("s", "remix?"),
            "tsiz": ("s", "size"),
            "tgrp": ("s", "grouping"),
            "vrsn": ("s", "version"),
            "tvcn": ("s", "col_name"),
            "tvcw": ("s", "col_width"),
            "uadd": ("u32", "ts_added"),
            "utkn": ("u32", "track_number"),
            "ulbl": ("u32", "label"),
            "utme": ("u32", "modified"),
            "udsc": ("u32", "dsc"),
            "utpc": ("u32", "play_count"),
            "ufsb": ("u32", "fsb"),
            "sbav": ("u16", "bav"),
            "bhrt": ("u8", "hrt"),
            "bmis": ("u8", "mis"),
            "bply": ("u8", "ply"),
            "blop": ("u8", "lop"),
            "bitu": ("u8", "itu"),
            "bovc": ("u8", "ovc"),
            "bcrt": ("u8", "crt"),
            "biro": ("u8", "iro"),
            "bwlb": ("u8", "wlb"),
            "bwll": ("u8", "wll"),
            "buns": ("u8", "uns"),
            "bbgl": ("u8", "bgl"),
            "bkrk": ("u8", "krk"),
            "brev": ("u8", "brev")
            
        }