import os
import json
import getpass


default_username = getpass.getuser()
config_path = "./cma_config.json"
config = json.load(open(config_path)) if os.path.exists(config_path) else None
for k, p in [
    ('serato_path', f"/Users/{default_username}/Music/_Serato_"), 
    ('db_path', f"/Users/{default_username}/.config/beets/library.db")]:
    if config and k in config.keys():
        os.environ[k] = config[k]
    elif os.path.exists(p):
        os.environ[k] = p
    else:
        if k[0] == 's':
            var = input(f'{k.replace("_", " ").title()} {p} doesn\'t exist, please enter the right one: ')
            
        else:
            var = input(f'{k.replace("_", " ").title()} {p} doesn\'t exist, please enter the right one or leave blank to initialize Beets: ')
            if var: 
                os.environ[k] = var
            else:
                while True:
                    beets_init_folder = input(
                        "Enter a path with some mp3s in it: "
                    )
                    if not os.path.exists(beets_init_folder):
                        print('invalid path!')
                    else:
                        break
                print("Buildng Beets database from path.")
                exec(f"beet import -A {beets_init_folder}")
            db_path = f"/Users/{default_username}/.config/beets/library.db"


serato_path = os.environ['serato_path']
db_path = os.environ['db_path']
json.dump({'serato_path': serato_path, 'db_path': db_path}, open(config_path, "w+"))

verbose = True