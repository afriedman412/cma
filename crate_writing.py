import struct
from serato_query import SeratoStorage, SeratoObject, verbose
from assets import label_table
from typing import List

def song_to_object(path):
    encoded_path = path.encode("utf-16be")
    l = len(encoded_path)
    return SeratoObject('otrk', l+8, [SeratoObject('ptrk', l, path)])

def make_playlist(track_paths: List, crate_name: str="1000"):
    crate_path = '/Users/af412/Music/_Serato_/Subcrates/crystal lake 111721.crate'
    r = SeratoStorage()
    r.load_all_data(crate_path)
    r.yield_all()

    r.objects = [o for o in r.objects if o.object_type!='otrk']
    new_track_objects = [song_to_object(path) for path in track_paths]

    print("adding paths...")
    for p in track_paths:
        print(p)

    r.objects += new_track_objects

    new_crate_path = f"/Users/af412/Music/_Serato_/Subcrates/crystal lake {crate_name}.crate"
    print(f"exporting crate {new_crate_path}")
    with open(new_crate_path, "wb+") as f:
        unparse_and_write(r.objects, f)

def unparse_object(o: SeratoObject):
        dtype, label = label_table.get(o.object_type, (None, None))
        
        encoded_type = o.object_type.encode("utf-8")
        encoded_len = struct.pack(">I", o.object_len)
        
        if verbose:
            print(o.object_type, o.object_len)
        
        if isinstance(o.object_data, List):
            encoded_data = None
            
        else:
            if dtype == "s":
                encoded_data = o.object_data.encode('utf-16be')

            elif dtype[0] == "u":
                encoding_table = {"u8": ">B", "u16": ">H", "u32": ">I"}
                encoded_data = struct.pack(encoding_table[dtype], o.object_data)
                
            assert len(encoded_data) == o.object_len

        return encoded_type, encoded_len, encoded_data

def unparse_and_write(objects: List[SeratoObject], writer):
    for o in objects:
        encoded_type, encoded_len, encoded_data = unparse_object(o)
        writer.write(encoded_type)
        writer.write(encoded_len)
        
        if encoded_data is None:
            if isinstance(o.object_data, list):
                if len(o.object_data) > 0:
                    unparse_and_write(o.object_data, writer)
                else:
                    writer.write(b'\x00') # required extra byte for empty lists
            
        else:
            writer.write(encoded_data)