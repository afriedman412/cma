from .serato_basic_classes import SeratoStorage, SeratoObject, SeratoBaseClass
from .exceptions import *
import os
from mutagen.id3 import ID3
from ..config.assets import serato_id3_import_table, db_path, db_table, serato_path
from typing import List, Union
import sqlite3

def cure_missing_file(path: str):
    """
    Quick stupid method for searching Beets for song info if mp3 cannot be found.
    """
    with sqlite3.connect(db_path) as conn:
        q = f"""
            SELECT *
            FROM {db_table}
            WHERE path == "{path}";
            """
        cur = conn.cursor()
        cur.execute(q)
        rows = cur.fetchall()
    return rows

class SeratoTrack(SeratoObject):
    """
    For importing a track from a file using ID3 tags, not bytes!
    """
    #TODO: sort out crate track, importing with id3 and reading data!!!
    def __init__(self, path: str):
        super(SeratoTrack, self).__init__(object_type='otrk', object_data=[])
        self.extract_song_data(path)
        self.set_song_info()

    def __repr__(self) -> str:
        return " - ".join([self.song_artist, self.song_title])

    def set_song_info(self):
        for k in ['tit2', 'tsng']:
            if k in self.data_keys:
                self.song_title = self.get_data_by_tag(k)

        self.song_artist = self.get_data_by_tag('tart')
        return

    def verify_song_path(self, path: str):
        """
        Tries variations on path formats.
        """
        for path_ in [path, "/" + path, os.path.abspath(path)]:
            if os.path.exists(path_):
                return path_
        else:
            rows = cure_missing_file(path)
            print('NO SONG PATH FOUND!')
            # print(rows)
            # raise TrackPathException(f"File not found: {path}")
            return
        
    def extract_song_data(self, path: str):
        """
        This assumes the file is an mp3!!
        """
        verified_path = self.verify_song_path(path)
        if verified_path:
            i = ID3(verified_path)

            for id3_tag, serato_tag in serato_id3_import_table.items():
                value = i.get(id3_tag)
                if value:
                    try:
                        o = SeratoObject(serato_tag, value.text[0])
                        self.object_data.append(o)
                    except IndexError:
                        continue

            for path_key in ['ptrk', 'pfil']:
                if path_key not in self.data_keys:
                    self.object_data.append(SeratoObject(path_key, verified_path))


class SeratoCrate(SeratoStorage):
    def __init__(self, path: str=None, name: str="new_crate"):
        super(SeratoCrate, self).__init__(
            path=path,
            vrsn=SeratoObject("vrsn", "1.0/Serato ScratchLive Crate")
            )
        self.crate_name = os.path.basename(path).replace(".crate", "") if path else name
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
        else:
            track_object = input
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
