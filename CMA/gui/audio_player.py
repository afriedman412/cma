import tkinter as tk
from tkinter.filedialog import askopenfilename
from pygame import mixer
from pygame import error as pygame_error
from .gui_helpers import yield_button
from ..code.serato_advanced_classes import SeratoTrack
import logging

class AudioPlayer:
    def __init__(self, window):
        mixer.init()
        self.root=window
        self.init_window()
        return

    def init_window(self):
        self.frame = tk.Frame(self.root)
        self.frame.pack()

        for k in ['stop', 'play']:
            var_name = f"{k}_var"
            button_name = f"{k}_button"
            self.__setattr__(var_name, tk.StringVar())
            self.__setattr__(
                button_name, 
                tk.Button(
                    self.frame, 
                    textvariable=self.__getattribute__(var_name),
                    command=self.__getattribute__(k))
                    )
            self.__getattribute__(button_name).pack(side="left", fill="x", padx=(5,5))
            self.__getattribute__(var_name).set(k.title())

        yield_button(self.frame, "Load", self.load_song)

        self.song_var = tk.StringVar()
        self.song_label = tk.Label(self.frame, textvariable=self.song_var, anchor="nw")
        self.song_label.pack(padx=(20,20), pady=(10,5))
        self.song_var.set("NOTHING PLAYING")
        return

    def play(self):
        if self.play_var.get() == "Pause":
            self.audio("pause")
            self.play_var.set("Unpause")
                 
        elif self.play_var.get() == "Unpause":
            self.audio("unpause")
            self.play_var.set("Pause")

        else:
            self.audio("play")
            self.play_var.set("Pause")
    
    def stop(self):
        if self.play_var.get() != "Play":
            self.play_var.set("Play")
        self.audio("stop")

    # def fwd(self):
    #     self.scrub(1)

    # def rwd(self):
    #     self.scrub(-1)

    # def scrub(self, dir=1, diff: int=5):
    #     pos = mixer.music.get_pos()/1000
    #     new_pos = pos + dir*diff
    #     print(pos, new_pos)
    #     self.audio("stop")
    #     mixer.music.set_pos(new_pos)
    #     self.audio("play")

    def audio(self, command: str):
        try:
            getattr(mixer.music, command)()
        except pygame_error:
            logging.error(f'audio error: {command}')
            pass

    def load_song(self, song_path: str=None):
        if not song_path:
            song_path = askopenfilename()
        new_track = SeratoTrack(path=song_path) # TODO: probably bad to do this
        mixer.music.load(song_path)
        self.song_var.set(new_track)
        self.stop()
        self.play()
        return