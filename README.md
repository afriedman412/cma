# CMA
Countin Money Always<br> 
Critical Minds Ascend<br>
Cant Make Another<br>
a positive Cause in ur Massively Annoying dj library 

### What It Does
CMA is an app for DJ homework that lets you prep for gigs without the overhead of other music apps. Create playlists, smart playlists, edit tags, pull metadata from a variety of sources, etc. (Not all of this works yet!!!)

It uses [Beets](https://beets.io/) to keep track of everything (although most of your metadata is stored in the audio files themselves!) and its GUI is built in [Tkinter](https://docs.python.org/3/library/tkinter.html).

### Requirements
Python ^3.8
Beets OR a folder of a few random mp3s<a name="f"></a>

### The Basics (might not work)
`poetry run cma_launcher.py`

Not sure if you need to install poetry manually or not!

### The Basics (if you need to install poetry)
1. Install [poetry](https://python-poetry.org/) if needed
`pip install poetry`

2. Install dependencies.
`poetry install`

3. Run CMA.
`poetry run cma_launcher.py`

### On Launching
- set your Serato folder (can be whatever, doesn't matter rn)
- set your crates folder (can also be whatever, its just the destination for any exported crates)
- locate your Beets DB if you have Beets installed ...
- ... or give it some songs to initialize the DB (use <a href="#f">your folder of random mp3s</a>)

It will open the log file automatically too.

### In the App
- double click any song to play
- "i" loads track info
- return adds selected track from library to playlist

Smart playlists are only set up for "grouping" tags, so not widely useful yet!


