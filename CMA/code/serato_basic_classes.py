from ..assets.assets import label_table, char_table
from typing import Optional, Tuple, Union, List
import mmap
import struct
from .exceptions import LabelTypeError, EncodingError, LoadingError
import logging
from tqdm import tqdm

verbose=False

class SeratoBaseClass:
    """
    For loading objects from bytes.
    - read and decode its own data
    - loads data from a path if provided
    """
    def __init__(self, input: Union[str, bytes]):
        logging.debug("initiating SeratoBaseClass")
        if input:
            self.load_input(input)

    def __len__(self) -> int:
        return len(self.object_data)

    def load_input(self, input: Union[str, bytes]):
        """
        Load from a file or from raw bytes.

        Using mmap for ~reasons~, doing the write/read dance for bytes because it was less trouble than figuring out how to standardize the downstream code.
        TODO: fix this
        """
        if isinstance(input, str):
            logging.debug(f"loading SeratoBaseClass input: {input}")
            with open(input, "r+b") as f:
                self.object_data = mmap.mmap(f.fileno(), 0)
            
        elif isinstance(input, bytes):
            logging.debug(f"loading SeratoBaseClass input: {len(input)} bytes")
            with open("temp", "w+b") as f:
                f.write(input)
            with open("temp", "r+b") as f:
                self.object_data = mmap.mmap(f.fileno(), 0)
        return

    def read_bytes(self, num_bytes: int) -> bytes:
        return self.object_data.read(num_bytes)

    def peek(self, num_bytes: int=4, start: int=0) -> bytes:
        pos = self.object_data.tell()
        if start:
            self.object_data.seek(start)
        data = self.read_bytes(num_bytes)
        self.object_data.seek(pos)
        return data
    
    def peek_next_object(self) -> str:
        return self.peek(4).decode('utf-8')

    def read_char_table(self, k: str, v: Union[str, int], keys: Union[str, list]):
        if isinstance(keys, str):
            keys = [keys]
        try:
            char_data = next(c for c in char_table if c[k]==v)
            if len(keys) > 1:
                return tuple([char_data[k_] for k_ in keys])
            else:
                return char_data[keys[0]]
        except StopIteration:
            return

    def load_next_header(self) -> Tuple[str, int]:
        object_type = self.read_bytes(4).decode('utf-8')
        self.object_type = object_type
        given_len = struct.unpack(">I", self.read_bytes(4))[0]
        return object_type, given_len

    def get_type_info(self, object_type: str) -> Tuple[str, None]:
        return label_table.get(object_type, (None, None)) # TODO: redo label

    def yield_object(self):
        """
        Fully decodes bytes into a SeratoObject.
        """
        object_type, given_len = self.load_next_header()
        dtype, label = self.get_type_info(object_type)
        # logging.debug(f"yielding SeratoBaseClass object: {object_type}, {given_len}, {dtype}, {label}")
        if not dtype:
            raise LabelTypeError(f"No dtype found for object type {object_type} of length {given_len}")
        if verbose:
            print(object_type, given_len, self.object_data.tell(), dtype, label)
        decoded_data = self.decode_raw_data(given_len, dtype)
        return SeratoObject(object_type=object_type, object_data=decoded_data, given_len=given_len)

    def full_decode(self):
        """
        Returns a list of objects.

        Use pbar for SeratoStorage objects only!
        """
        objects = []
        while self.object_data.tell() < self.object_data.size():
            try:
                new_object = self.yield_object()
                objects.append(new_object)
                logging.debug("  //  ".join(
                    [
                        new_object.object_type, 
                        str(new_object.given_len)
                    ]))
            except LoadingError as e:
                logging.error("loading error")
                continue
        return objects

    def decode_raw_data(self, given_len: int, dtype: str) -> Union[str, int, bytes]:
        """
        Decode bytes when yielding an object.
        """
        if given_len == 1 and self.peek(1) == b"\x00":
            self.read_bytes(1)
            decoded_data = None

        elif dtype == "s":
            decoded_data = self.read_bytes(given_len).decode('utf-16be')

        elif dtype == "d":
            decoded_data = self.decode_compound_data(self.read_bytes(given_len))
                
        else:
            expected_len, struct_code  = self.read_char_table("dtype", dtype, ['expected_len', 'struct_code'])

            if given_len != expected_len:
                print(
                    f"given len ({given_len}) doesn't match expected len ({expected_len}) at position {self.object_data.tell()} for object type {self.object_type}"
                    )
                struct_code = self.read_char_table("expected_len", given_len, "struct_code")

            decoded_data = struct.unpack(struct_code, self.read_bytes(given_len))[0]
            
        return decoded_data

    def decode_compound_data(self, compound_data: bytes):
        """
        For decoding compound objects (ie objects where data is a list of objects)
        """
        sbc = SeratoBaseClass(compound_data)
        objects = sbc.full_decode()
        return objects


class SeratoObject(SeratoBaseClass):
    """
    - instantiate with object info (type, len and data if available).
    - decode and encode its own data.
    - recursively handle sub-objects in its own data

    TODO: adjust default data to dtype

    LENGTH TAXONOMY:
    *** given_len:
    - provided on instantiation to instruct on how many bytes of data to read
    - data_len = given_len if provided until calculated_len is available 

    *** calculated_len:
    - calculated length of the encoded object data in bytes
    - data_len = calculated_len after data is read

    *** object_len:
    - calculated length of the entire object in bytes
    - sum of object type length, data len length and calculated data length)
    - mostly making this explicit so the difference is clear

    *** data_len:
    - parses given_len v. calculated_len at any given time
    """

    def __init__(
        self, 
        object_type: str, 
        object_data, 
        given_len: Optional[int]=None, 
        path: Optional[str]=None
        ):
        super(SeratoObject, self).__init__(path)
        self.object_type = object_type
        self.dtype, self.label = self.get_type_info(object_type)
        self.object_data = object_data
        if isinstance(object_data, bytes):
            assert given_len == len(object_data), "given length != length of encoded data"
            self.object_data = self.decode_raw_data(object_data)
        self.given_len = given_len
        return

    def __len__(self):
        return self.object_len

    def __getitem__(self, key):
        try:
            return [d.object_data for d in self.object_data if d.object_type==key][0]
        except (IndexError, TypeError):
            return "(NO DATA)" 

    def __repr__(self):
        return f"(type: {self.object_type} // len: {self.data_len} // data: {self.object_data})"

    @property
    def data_keys(self):
        if isinstance(self.object_data, list):
            return list(set([d.object_type for d in self.object_data]))
        else:
            return

    @property
    def object_len(self):
        """
        calculated length of the entire object in bytes
        """
        return len(b"".join(list(self.encode_object())))

    @property
    def calculated_len(self):
        """
        calculated length of the encoded object data in bytes
        """
        l = len(self.encode_data())
        return l if isinstance(l, int) else 0

    @property
    def data_len(self) -> int:
        """
        TODO: Handle other data types.
        """
        if self.object_data:
            if isinstance(self.object_data, bytes):
                return len(self.object_data)
            else:
                return self.calculated_len

        elif self.object_data == 0:
            return 1
        else:
            return self.given_len

    def multi_key(self, keys: List[str], default="(NO DATA)"):
        """
        Queries all objects with provided keys and returns the value for the first one that hits.
        Not ideal but the best way to handle inconsistent tagging across files.

        For example:
        Since the file path for a song could be a 'ptrk' or a 'pfil' object, multi_key(['ptrk', 'pfil']) gives you a best guess at a path.
        """
        for k in keys:
            if k in self.data_keys:
                return self[k]
        return default

    ### ENCODE DATA
    def encode_object(self) -> Tuple[bytes]:
        """
        For the entire object.
        """
        encoded_type = self.object_type.encode("utf-8")
        encoded_data = self.encode_data()
        encoded_len = struct.pack(">I", self.data_len)
        
        return encoded_type, encoded_len, encoded_data

    def encode_data(self) -> bytes:
        """
        Only for object data. 
        """
        if self.object_type == "utkn":
            # some mp3 track number formats are like "03/12" ie 3 of 12
            try:
                self.object_data = int(self.object_data.split("/")[0])
            except (TypeError, AttributeError):
                pass

        encoded_data = b""
        if isinstance(self.object_data, list):
            encoded_data = self.encode_compound_data()
        
        elif self.dtype == "s":
            encoded_data = self.object_data.encode('utf-16be')

        elif self.dtype[0] == "u":
            try:
                struct_code  = self.read_char_table("dtype", self.dtype, 'struct_code')
                encoded_data = struct.pack(struct_code, 0 if not self.object_data else int(self.object_data))
            except:
                raise EncodingError(f"encoding table expected integer for {self.object_type} ({self.dtype}), value {self.object_data}")

        return encoded_data

    def encode_compound_data(self) -> bytes:
        """
        Encode data into bytes if data is a list of objects.
        """
        assert isinstance(self.object_data, list), "Trying to encode compound data but data is not a list!"

        if len(self.object_data) < 1:
            encoded_data = b'\x00'

        else:
            encoded_data = b""
            for o_ in self.object_data:
                assert isinstance(o_, SeratoObject), f"bad object type: {type(o_)}"
                encoded_data += b"".join(list(o_.encode_object()))
        
        return encoded_data

    
class SeratoStorage(SeratoBaseClass):
    """
    For DB and crates. Not a SeratoObject.
    """
    def __init__(self, path: Optional[str]=None, vrsn: SeratoObject=None):
        super(SeratoStorage, self).__init__(path)
        if path:
            self.yield_all()
        elif vrsn:
            self.objects = [vrsn]
        else:
            self.objects = []
        return

    def __len__(self) -> int:
        try:
            return len(self.objects)
        except AttributeError:
            return len(self.object_data)

    def yield_all(self):
        self.objects = self.full_decode()

    # def yield_all_pbar(self):
    #     """
    #     Returns a list of objects.

    #     This is just full_decode with a pbar added.
    #     """
    #     objects = []
    #     pbar = tqdm(total=len(self))
    #     while self.object_data.tell() < self.object_data.size():
    #         print(self.object_data.tell(), self.object_data.size())
    #         try:
    #             new_object = self.yield_object()
    #             objects.append(new_object)
    #             logging.debug("  //  ".join(
    #                 [
    #                     new_object.object_type, 
    #                     str(new_object.given_len)
    #                 ]))
    #         except LoadingError as e:
    #             logging.error("loading error")
    #             continue
    #         pbar.update(self.object_data.tell())
    #     pbar.close()
    #     self.objects = objects







    

    

