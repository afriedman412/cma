import os
import json
import getpass
from tkinter.filedialog import askdirectory, askopenfilename
from tkinter.messagebox import askokcancel


default_username = getpass.getuser()
default_serato_path = f"/Users/{default_username}/Music/_Serato_"
default_db_path = f"/Users/{default_username}/.config/beets/library.db"

config_path = "./cma_config.json"
config = json.load(open(config_path)) if os.path.exists(config_path) else {}
serato_path = config.get('serato_path', None)
db_path = config.get('db_path', None)

if not serato_path:
    _ = askokcancel("Serato Directory", "Press OK to locate your Serato directory")
    serato_path = askdirectory(initialdir=default_serato_path)

if not db_path:
    db_bool = askokcancel("Beets DB", "Press OK to locate your Beets database, or Cancel to select a folder of mp3s to initiate the database.")

    if db_bool:
        db_path = askopenfilename(initialdir=default_db_path)
    else:
        music_path = askdirectory(initialdir=os.getcwd())
        print("Building Beets database from path.")
        os.system("beet import -A " + music_path)
        db_path = default_db_path

json.dump({'serato_path': serato_path, 'db_path': db_path}, open(config_path, "w+"))

verbose = True