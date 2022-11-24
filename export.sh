#!/bin/sh

poetry run pyinstaller -w cma_launcher.py --additional-hooks-dir=. --hidden-import tkinter -Fy --clean

cp -r ./dist/ /Users/af412/Dropbox/CMA_DB