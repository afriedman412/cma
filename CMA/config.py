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
        logging.exception(line)
    logging.exception(value)

    sys.__excepthook__(type, value, tb) # calls default excepthook

def init_logger():
    timestamp = dt.strftime(dt.now(), "%Y%m%d")
    LOG_PATH = os.path.abspath(f"./cma_{timestamp}.log")
    os.environ["LOG_PATH"] = LOG_PATH
    print(timestamp)
    return logging.basicConfig(
        filename=LOG_PATH,
        filemode="a+",
        format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',
        level=logging.DEBUG
        )

def load_log():
    LOG_PATH = os.environ.get("LOG_PATH", None)
    if LOG_PATH:
        subprocess.run(["open",  LOG_PATH])
    else:
        logging.info("No log path set!")
    return

class Config:
    def __init__(self):
        sys.excepthook = log_exceptions
        init_logger()
        load_log()
        os.environ['SERATO_PATH'], os.environ['DB_PATH'] = self.init_app()
        logging.info(os.environ)
        return

    def init_app(self, config_path: str="./cma_config.json"):
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
        db_path = config.get('db_path', None)

        if not serato_path:
            logging.info("locating Serato Directory")
            _ = askokcancel("Serato Directory", "Press OK to locate your Serato directory")
            serato_path = askdirectory(initialdir=default_serato_path)
            logging.info(f"setting Serato Directory: {serato_path}")

        if not db_path:
            logging.info("locating Beets DB")
            db_bool = askokcancel("Beets DB", "Press OK to locate your Beets database, or Cancel to select a folder of mp3s to initiate the database.")

            if db_bool:
                db_path = askopenfilename(initialdir=default_db_path)
                logging.info(f"setting Beets DB path: {db_path}")
            else:
                logging.info("installing beets from command line")
                subprocess.run(['pip', 'install', 'beets'])
                music_path = askdirectory(initialdir=os.getcwd())
                logging.info(f"loading music files from {music_path}")
                print("Building Beets database from path.")
                subprocess.run(['beet', 'import', '-A', music_path])
                db_path = default_db_path
        logging.info(f"outputting config file to {config_path}")
        json.dump({'serato_path': serato_path, 'db_path': db_path}, open(config_path, "w+"))
        return serato_path, db_path

