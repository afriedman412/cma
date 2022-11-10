from CMA.code.serato_advanced_classes import SeratoTrack, SeratoCrate
import os

serato_path = "/Users/af412/Music/_Serato_"
file_path = "./CMA/assets/Dangerous Liasons (DVA Remix).mp3"
db_path = os.path.join(serato_path, "database V2")
crate_path = os.path.join(serato_path, "Subcrates", "Scaramanga- Seven Horns, Seven Eyes.crate")

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

def test_full_track():
    assert full_track.data_len == 306
    assert set(full_track.data_keys) == {'tsng', 'tbpm', 'tart', 'ptrk', 'tkey', 'pfil'}

def test_existing_crate():
    crate_data_lens = [o.data_len for o in crate.objects]
    print(crate_data_lens)
    assert sorted(crate_data_lens) == sorted([56, 192, 194, 200, 248, 194, 214, 174, 198, 186, 182, 238, 180, 184, 200, 202, 204, 470])

def test_new_crate():
    assert new_crate.objects[0].data_len == 56
    assert new_crate.objects[1].data_len == 588