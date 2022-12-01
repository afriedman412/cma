import os
import json
import getpass
import subprocess
from tkinter.filedialog import askdirectory, askopenfilename
from tkinter.messagebox import askokcancel
import logging
import traceback
import sys
from datetime import datetime as dt

def log_exceptions(type, value, tb):
    for line in traceback.TracebackException(type, value, tb).format(chain=True):
        logging.error(line)
    logging.error(value)

    sys.__excepthook__(type, value, tb) # calls default excepthook

def init_logger():
    timestamp = dt.strftime(dt.now(), "%Y%m%d")
    LOG_PATH = os.path.abspath(f"./cma_{timestamp}.log")
    os.environ["LOG_PATH"] = LOG_PATH
    return logging.basicConfig(
        filename=LOG_PATH,
        filemode="a+",
        format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',
        level=logging.INFO
        )

def load_log():
    LOG_PATH = os.environ.get("LOG_PATH", None)
    if LOG_PATH:
        subprocess.run(["open",  LOG_PATH])
    else:
        logging.info("No log path set!")
    return

class Config:
    """
    
    """
    def __init__(self):
        sys.excepthook = log_exceptions
        init_logger()
        load_log()
        vars = self.init_app()
        for k,v in zip(['SERATO_PATH', 'CRATES_PATH', 'DB_PATH', 'CRATE_AUTOLOAD', 'CONFIG_PATH'], vars):
            print(k,v)
            os.environ[k] = v
        return

    def init_app(self, config_path: str="/Users/af412/cma_config.json"):
        logging.info("initializing app...")
        default_username = getpass.getuser()
        default_serato_path = f"/Users/{default_username}/Music/_Serato_"
        default_db_path = f"/Users/{default_username}/.config/beets/library.db"

        if os.path.exists(config_path):
            logging.info("loading config from file")
            config = json.load(open(config_path))
        else:
            config = {}

        serato_path = config.get('serato_path', None)
        crates_path = config.get('crates_path', None)
        db_path = config.get('db_path', None)
        crate_autoload = config.get('crate_autoload', None)

        if not serato_path:
            logging.info("locating Serato Directory")
            _ = askokcancel("Serato Directory", "Press OK to locate your Serato directory")
            serato_path = askdirectory(initialdir=default_serato_path)
            logging.info(f"setting Serato Directory: {serato_path}")

        if not crates_path:
            logging.info("locating subcrates path")
            crates_bool = askokcancel("Subcrates Directory", "Press OK to use default crate path or cancel to choose one.")
            
            if crates_bool:
                crates_path = os.path.join(serato_path, "Subcrates")
                if not os.path.exists(crates_path):
                    os.mkdir(crates_path)

            else:
                crates_path = askdirectory(initialdir=serato_path)

            logging.info(f"setting Crates Directory: {crates_path}")

        if not db_path:
            logging.info("locating Beets DB")
            db_bool = askokcancel("Beets DB", "Press OK to locate your Beets database, or Cancel to select a folder of mp3s to initiate the database.")

            if db_bool:
                db_path = askopenfilename(initialdir=default_db_path)
                logging.info(f"setting Beets DB path: {db_path}")
            else:
                logging.info("installing beets from command line")
                subprocess.run(['pip3', 'install', 'beets'])
                music_path = askdirectory(initialdir=os.getcwd())
                logging.info(f"loading music files from {music_path}")
                print("Building Beets database from path.")
                subprocess.run(['beet', 'import', '-A', '-C', music_path])
                db_path = default_db_path
        logging.info(f"outputting config file to {config_path}")
        json.dump(
            {'serato_path': serato_path, 
            'crates_path': crates_path, 
            'db_path': db_path,
            'config_path': '~/cma_config.json',
            'crate_autoload': crate_autoload
            }, open(config_path, "w+"))
        return serato_path, crates_path, db_path, crate_autoload, config_path

