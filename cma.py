from CMA.gui import MusicDBGUI
from CMA.helpers import init_logger
import traceback
import sys
import logging

def log_exceptions(type, value, tb):
    for line in traceback.TracebackException(type, value, tb).format(chain=True):
        logging.exception(line)
    logging.exception(value)

    sys.__excepthook__(type, value, tb) # calls default excepthook

sys.excepthook = log_exceptions

if __name__=="__main__":
    init_logger()
    MusicDBGUI()
