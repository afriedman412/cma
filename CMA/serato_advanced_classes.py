from .serato_basic_classes import SeratoStorage, SeratoObject, SeratoBaseClass
import os
from .assets import serato_id3_import_table, audio_typing_table
from .config import serato_path
from typing import List, Union, Optional
import importlib
from mimetypes import guess_type
import mutagen
import logging
import subprocess



class SeratoTrack(SeratoObject):
    """
    For importing a track from a file using ID3 tags, not bytes!

    TODO: custom code for AAC/MP4 etc
    """
    #TODO: sort out crate track, importing with id3 and reading data!!!
    def __init__(self, path: str):
        super(SeratoTrack, self).__init__(object_type='otrk', object_data=[])
        self.song_artist = "" # instantiate both with empty string
        self.song_title = "" # instantiate both with empty string
        self.extract_song_data(path)
        self.set_song_info()
        logging.info(f"New SeratoTrack: {self.__repr__()}, {path}")

    def __repr__(self) -> str:
        return " - ".join([self.song_artist, self.song_title])

    def set_song_info(self):
        for k in ['tit2', 'tsng']:
            if k in self.data_keys:
                self.song_title = self.get_data_by_tag(k)
                logging.debug(f"setting song title: {k}, {self.song_title}")

        self.song_artist = self.get_data_by_tag('tart')
        logging.debug(f"setting song artist: {self.song_artist}")
        return

    def verify_song_path(self, path: str) -> Optional[str]:
        """
        Tries variations on path formats.
        """
        for path_ in [path, "/" + path, os.path.abspath(path)]:
            if os.path.exists(path_):
                logging.debug(f"Using {path_} as path for {path}")
                return path_
        else:
            logging.warning(f"No usable path found for {path}")
            return

    def parse_audio_type(self, path: str) -> mutagen.FileType:
        self.file_type, _ = guess_type(path)
        file_ext = audio_typing_table.get(self.file_type, None)
        logging.info(f"Guessed file type: {self.file_type}, using extension {file_ext}")

        mutagen_parser = importlib.import_module(f"mutagen.{file_ext.lower()}")
        parsed_file = getattr(mutagen_parser, file_ext)(path)
        return parsed_file

        
    def extract_song_data(self, path: str):
        """
        
        """
        verified_path = self.verify_song_path(path)
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

            for path_key in ['ptrk', 'pfil']:
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

    def add_track(self, input: Union[str, SeratoTrack]):
        if isinstance(input, str):
            file_path = os.path.abspath(input)
            track_object = SeratoTrack(file_path)
            logging.info(f"Adding {file_path} to {self.crate_name}")
        else:
            track_object = input
            logging.info(f"Adding {track_object.__repr__()} to {self.crate_name}")
        self.objects.append(track_object)

    def add_tracks(self, inputs: List[str]):
        for i in inputs:
            self.add_track(i)

    def get_track_data(self):
        """
        Load info for tracks in crate.
        """
        new_objects = []
        for o in self.objects:
            if o.object_type == "otrk":
                if not isinstance(o, SeratoTrack):
                    o = SeratoTrack(o.get_data_by_tag('ptrk'))
                o.extract_song_data(o.get_data_by_tag('pfil'))
            new_objects.append(o)
        self.objects = new_objects

    def export_crate(self, output_path: str=None):
        if not output_path:
            if self.crate_name[-6:] != ".crate":
                self.crate_name = self.crate_name + ".crate"
            output_path = os.path.join(serato_path, "Subcrates", self.crate_name)
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
