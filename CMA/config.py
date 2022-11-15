import os
import json
import getpass
from tkinter.filedialog import askdirectory, askopenfilename


default_username = getpass.getuser()
config_path = "./cma_config.json"
config = json.load(open(config_path)) if os.path.exists(config_path) else None
for k, p in [
    ('serato_path', f"/Users/{default_username}/Musix/_Serato_"), 
    ('db_path', f"/Users/{default_username}/.config/beets/library.db")]:
    if config and k in config.keys():
        os.environ[k] = config[k]
    elif os.path.exists(p):
        os.environ[k] = p
    else:
        k_ = {k.replace("_", " ").title()}
        if k == 'serato_path':
            var = input(f'Serato directory {p} doesn\'t exist!! Press enter to select the correct Serato directory ...')
            new_serato_dir = askdirectory(title=f'Select Serato Directory ...')
            os.environ['serato_path'] = new_serato_dir
            
        else:
            var = input(f'No Beets Database found at {p}!! Press enter to find an existing Beets Database, or Space to initialize Beets ...')
            if var != ' ': 
                new_db = askopenfilename(title=f'Select Beets Database...')
                os.environ[k] = var
            else:
                while True:
                    _ = input(
                        "Select a directory with some mp3s in it ... "
                    )
                    new_music_dir = askdirectory(title=f'Select a Music Directory ...')
                    if not os.path.exists(new_music_dir):
                        print('invalid path!')
                    else:
                        break
                print("Building Beets database from path.")
                exec(f"beet import -A {new_music_dir}")
            db_path = f"/Users/{default_username}/.config/beets/library.db"


serato_path = os.environ['serato_path']
db_path = os.environ['db_path']
json.dump({'serato_path': serato_path, 'db_path': db_path}, open(config_path, "w+"))

verbose = True