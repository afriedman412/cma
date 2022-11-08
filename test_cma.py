from CMA.code.serato_query import SeratoTrack, SeratoCrate, SeratoStorage
import os

serato_path = "/Users/af412/Music/_Serato_"
file_path = "./CMA/assets/Dangerous Liasons (DVA Remix).mp3"
db_path = os.path.join(serato_path, "database V2")
crate_path = os.path.join(serato_path, "Subcrates", "Unknown Album.crate")

# crate track
crate_track = SeratoTrack(file_path, False)

# full track
full_track = SeratoTrack(file_path)

# existing crate
crate = SeratoCrate(crate_path)

# add track
crate.add_track(file_path)

# new crate
new_crate = SeratoCrate()

# add tracks to new crate
new_crate.add_track("./CMA/assets/mc_breed_&_e-40_-_do_what_it_do.mp3")

# db
db = SeratoStorage(db_path)

def test_crate_track():
    assert crate_track.object_len == 100

def test_full_track():
    assert full_track.object_len == 366
    assert full_track.data_keys == [
        'tsng', 'tart', 'talb', 'tgen', 'tlen', 'utkn', 'tbpm', 'ttyr', 'tkey', 'tcmp', 'tsiz', 'pfil', 'ptrk'
        ]

def test_exiting_crate():
    crate_object_lens = [o.object_len for o in crate.objects]
    print(crate_object_lens)
    assert sorted(crate_object_lens) == sorted([56, 19, 26, 36, 30, 24, 28, 30, 32, 174, 276, 266, 146, 150, 180, 118, 122, 366])

def test_new_crate():
    assert new_crate.objects[0].object_len == 56
    assert new_crate.objects[1].object_len == 460

def test_db():
    assert len(db) == 794