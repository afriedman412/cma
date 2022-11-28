import tkinter as tk
from tkinter import Toplevel
from ..code.serato_advanced_classes import SeratoTrack
from ..assets.assets import serato_db_col_dict
import logging

class TrackInfo:
    """
    TODO: This can probably just be integrated into the Track class eventually.
    """
    def __init__(self, window: Toplevel, track: SeratoTrack):
        self.track = track
        self.window= window # make a new top level for the track info

        self.window.rowconfigure(0, weight=1, minsize=40) # label
        self.window.rowconfigure(1, weight=1, minsize=300) # info
        self.window.rowconfigure(2, weight=1, minsize=40) # button

        self.window.columnconfigure(0, weight=1, minsize=200)

        self.init_track_info()
        return

    def init_track_info(self):
        self.label_var = tk.StringVar(value=self.track)
        self.label = tk.Label(self.window, textvariable=self.label_var)
        self.label.grid(row=0, column=0)

        track_info = []
        for o in self.track.object_data: # have to do because of repr for Tracks :/
            o_type = o.__dict__['object_type']
            o_data = o.__dict__['object_data']
            o_label = serato_db_col_dict.get(o_type, o_type)
            track_info.append(f"{o_label}: {o_data} ({o_type})")

        track_info.append(f"grouping: {self.track.id3_info.get('grouping')}")
        self.var = tk.Variable(value=track_info)

        self.listbox = tk.Listbox(
            self.window,
            listvariable=self.var,
            name="track_info"
        )
        self.listbox.grid(row=1, column=0, sticky="nsew", padx=5)

        self.done_button = tk.Button(self.window, text="Done", command=self.window.destroy)
        self.done_button.grid(row=2)
        return




    

    