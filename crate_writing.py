import struct
from serato_query import SeratoObject, label_table, verbose
from Typing import List

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