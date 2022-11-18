from CMA.serato_advanced_classes import SeratoTrack, SeratoCrate
from CMA.config import init_logger
import logging
import os

init_logger()
logging.debug(f"initiating tests...")

serato_path = "/Users/af412/Music/_Serato_"
file_path = "./CMA/assets/Dangerous Liasons (DVA Remix).mp3"
db_path = os.path.join(serato_path, "database V2")
crate_path = os.path.join(serato_path, "Subcrates", "scaramanga.crate")



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
    assert sorted(crate_data_lens) == sorted([56, 500, 492, 498, 438, 456, 450, 504, 554, 504, 444, 420, 474, 492, 508, 576, 558, 500, 426])

def test_new_crate():
    assert new_crate.objects[0].data_len == 56
    assert new_crate.objects[1].data_len == 544