from .serato_basic_classes import SeratoStorage, SeratoObject, SeratoBaseClass
import os
from ..assets.assets import serato_id3_import_table, audio_typing_table
from ..gui.gui_helpers import cure_library_path
from typing import List, Union, Optional
import importlib
from mimetypes import guess_type
import mutagen
import logging
from mutagen.easyid3 import EasyID3

class SeratoTrack(SeratoObject):
    """
    For importing a track from a file using ID3 tags, not bytes!

    TODO: custom code for AAC/MP4 etc
    TODO: save changes
    """
    #TODO: sort out crate track, importing with id3 and reading data!!!
    def __init__(self, path: str):
        super(SeratoTrack, self).__init__(object_type='otrk', object_data=[])
        self.update_song_data(path)
        logging.debug(f"New SeratoTrack: {self.__repr__()}, {path}")

    def __repr__(self) -> str:
        return " - ".join([self.song_artist, self.song_title])

    @property
    def path(self) -> str:
        return self.multi_key(['ptrk', 'pfil'])

    @property
    def song_title(self) -> str:
        return self.multi_key(['tit2', 'tsng'])

    @property
    def song_artist(self) -> str:
        return self.multi_key(['tart'])

    @property
    def id3_info(self) -> dict:
        return EasyID3(self.path)

    def parse_audio_type(self, path: str) -> mutagen.FileType:
        self.file_type, _ = guess_type(path)
        file_ext = audio_typing_table.get(self.file_type, None)
        logging.debug(f"Guessed file type: {self.file_type}, using extension {file_ext}")

        mutagen_parser = importlib.import_module(f"mutagen.{file_ext.lower()}")
        parsed_file = getattr(mutagen_parser, file_ext)(path)
        return parsed_file

    def update_song_data(self, path: str):
        """
        Extracts song info from songs in playlist.
        
        (This needs to be done because Serato crates only store minimal info on their songs.)
        """
        verified_path = cure_library_path(path)
        if verified_path:
            i = self.parse_audio_type(verified_path)

            for id3_tag, serato_tag in serato_id3_import_table.items():
                value = i.get(id3_tag)
                if value:
                    try:
                        o = SeratoObject(serato_tag, value.text[0])
                        self.object_data.append(o)
                        logging.debug(f"Adding SeratoObject for {id3_tag}")
                    except IndexError:
                        logging.debug(f"No text found for tag {id3_tag}")
                        continue
            
            for path_key in ['ptrk', 'pfil']: # cure path keys
                if path_key not in self.data_keys:
                    self.object_data.append(SeratoObject(path_key, verified_path))
                    logging.debug(f"Setting {path_key} to {verified_path}")



class SeratoCrate(SeratoStorage):
    def __init__(self, path: str=None, name: str="new_crate"):
        super(SeratoCrate, self).__init__(
            path=path,
            vrsn=SeratoObject("vrsn", "1.0/Serato ScratchLive Crate")
            )
        self.crate_name = os.path.basename(path).replace(".crate", "") if path else name
        logging.info(f"Loading Crate {self.crate_name} from {path}")
        return

    def __repr__(self):
        return self.crate_name

    @property
    def tracks(self):
        return [o for o in self.objects if o.object_type=='otrk']

    def add_track(self, input: Union[str, bytes, SeratoTrack]):
        if not isinstance(input, SeratoCrate):
            track_object = SeratoTrack(input)
            logging.debug(f"Adding {track_object} to {self.crate_name}")
        else:
            track_object = input
            logging.debug(f"Adding {track_object.__repr__()} to {self.crate_name}")
        self.objects.append(track_object)

    def add_tracks(self, inputs: List[str]):
        for i in inputs:
            self.add_track(i)

    def delete_track(self, n: int):
        """
        Removes the nth track from the crate.

        Technically removes object # n + "number of non-track objects"

        (There should be only the "vrsn" object but this allows for variation.)
        """
        non_track_len = len([o for o in self.objects if o.object_type!='otrk'])
        removed_track = self.objects.pop(n+non_track_len)
        logging.info(f"Removed {removed_track} at {removed_track.path} from {self.crate_name}")
        self.objects
        return removed_track

    def get_track_data(self):
        """
        Load info for tracks in crate.
        """
        new_objects = []
        for o in self.objects:
            if o.object_type == "otrk":
                if not isinstance(o, SeratoTrack):
                    o = SeratoTrack(o['ptrk'])
                o.update_song_data(o['pfil'])
            new_objects.append(o)
        self.objects = new_objects

    def export_crate(self, output_path: str=None):
        if not output_path:
            if self.crate_name[-6:] != ".crate":
                self.crate_name = self.crate_name + ".crate"
            output_path = os.path.join(os.environ['CRATES_PATH'], self.crate_name)
        logging.info(f"Exporting crate {self.crate_name} to {output_path}")
        encoded_objects = [b"".join(list(o.encode_object())) for o in self.objects]

        with open(output_path, "wb+") as f:
            for o in encoded_objects:
                f.write(o)
        return

class SeratoDB(SeratoBaseClass):
    def __init__(self, path: str=None):
        super(SeratoDB, self).__init__(
            path=path,
            vrsn=SeratoObject("vrsn", "2.0/Serato Scratch LIVE Database")
            )
        return
