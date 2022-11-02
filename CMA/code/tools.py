from mutagen.id3 import ID3
import os

path = "/Users/af412/Downloads/musicdump/Graham Central Station/Record Plant (Sausalito, CA) 10_3_1974"

song = "04 I Believe In You.mp3"
p = os.path.join(path, song)

f = ID3(p)
print(f.pprint())