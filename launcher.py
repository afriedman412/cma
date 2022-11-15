from CMA.gui.gui import MusicDBGUI
import os

if os.environ.get('DISPLAY','') == '':
    print('no display found. Using :0.0')
    os.environ.__setitem__('DISPLAY', '127.0.0.1:0.0')

if __name__=="__main__":
    MusicDBGUI()