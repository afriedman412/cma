# CMA (Dev Info)

CMA is an app that helps DJ's do what we call "DJ homework", which is tagging and making playlists from our massive and often disorganized libraries for Serato, the de facto app for DJing off a computer.

It uses [Beets](https://beets.io/) to keep track of everything (although most of your metadata is stored in the audio files themselves!) and its GUI is built in [Tkinter](https://docs.python.org/3/library/tkinter.html).

### Basic Instructions
- Create a virtual env with `make install`
- Activate the env with `source venv/bin/activate`
- Run the app with `python cma_launcher.py`