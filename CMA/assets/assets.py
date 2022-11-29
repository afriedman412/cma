db_table ='items'
db_columns = ['id', 'title', 'artist', 'grouping', 'genre', 'path']

char_table = [
    {
        "dtype": "u8",
        "expected_len": 1,
        "struct_code": ">B"
    },
    {
        "dtype": "u16",
        "expected_len": 2,
        "struct_code": ">H"
    },
    {
        "dtype": "u32",
        "expected_len": 4,
        "struct_code": ">I"
    },

]

audio_typing_table = {
    "audio/x-wav": "WAVE",
    "audio/wav": "WAVE",
    "audio/aac": "AAC", 
    "audio/mpeg": "MP3",
    "audio/x-mpeg": "MP3",
    'audio/x-aiff': "AIFF",
    "audio/aiff": "AIFF",
    "audio/aifc": "AIFF",
    "audio/ogg": "OGG",
    "audio/mp4": "MP4",
    "audio/mp4a-latm": "MP4",
    "audio/flac": "FLAC"
}

decoding_table = {"u32": (4, ">I"), "u16": (2, ">H"), "u8": (1, ">B")}
encoding_table = {"u8": ">B", "u16": ">H", "u32": ">I"}

label_table = {
        "otrk": ("d", "track"),
        "orvc": ("d", "???"),
        "osrt": ("d", "sorted_column"),
        "ovct": ("d", "unsorted_column?"),
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

serato_db_col_dict = {
    'ttyp': "track_type", 
    'pfil': "file_path", 
    'tsng': "title", 
    'tart': "artist", 
    'talb': "album", 
    'tgen': "genre", 
    'tlen': "length", 
    'tsiz': "file_size", 
    'tbit': "bitrate",
    'tsmp': "sample_rate", 
    'tbpm': "bpm", 
    'tgrp': "grouping", 
    'tadd': "date_added", 
    'tcor': "corrupt_desc", 
    'tiid': "tiid", 
    'uadd': "time_added_32bit", 
    'ulbl': "label_color", 
    'utme': "unk_ctme",
    'ufsb': "file_size_bytes", 
    'sbav': "sbav", 
    'bhrt': "bhrt", 
    'bmis': "missing_bool", 
    'bply': "bply", 
    'blop': "blop", 
    'bitu': "bitu", 
    'bovc': 'bovc', 
    'bcrt': "corrupt_bool",
    'bwlb': 'bwlb', 
    'bwll': 'bwll', 
    'buns': 'buns', 
    'bbgl': 'bbgl', 
    'bkrk': "bkrk", 
    'tcom': "comment", 
    'utkn': "track_num", 
    'tkey': "key",
    'tlbl': "label", 
    'ttyr': "year", 
    'udsc': "disc_num", 
    'tcmp':"composer", 
    'utpc': 'utpc', 
    'trmx': "remixer",
    'ptrk': "playlist_track_file_path"
}

serato_id3_import_table = {
    'TIT2': 'tsng',
    'TPE1': 'tart',
    'TALB': 'talb',
    'TCON': 'tgen',
    'TLEN': 'tlen',
    'TRCK': 'utkn',
    'TBPM': 'tbpm',
    'TDRC': 'ttyr',
    'TDRL': 'ttyr',
    'TKEY': 'tkey',
    'TCOM': 'tcmp',
    'TSIZ': 'tsiz',
    'GRP1': 'tgrp'
 }

known_tags = list(serato_id3_import_table.keys()) + [
    'TENC', 'TPOS', 'TPE2', 'TPUB', 'TIT1', 'TPE4', 'TOPE', 'TCOP', 'TPE3', 'TSRC', 'TIT3', 'TCMP', 'MCDI',
    'TSOA', 'TSOT'
]