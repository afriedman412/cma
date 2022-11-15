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
        os.environ[k] = input(f'{k.replace("_", " ")} {p} doesn\'t exist, please enter the right one: ')

serato_path = os.environ['serato_path']
db_path = os.environ['db_path']
json.dump({'serato_path': serato_path, 'db_path': db_path}, open(config_path, "w+"))

verbose = True