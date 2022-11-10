"""
Drag and drop files into a window, click button to export playlist.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import regex as re
from ..code.crate_writing import make_playlist
from ..code.serato_query_old import SeratoCrate
from ..config.assets import serato_path
import os
from typing import Optional

class PlaylistBuilder():

    def __init__(self):
        self.root = TkinterDnD.Tk()
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.drag_import)
        self.text = tk.Text(self.root)
        self.text.pack()

        tk.Button(self.root, text="Export Playlist", command=self.export_playlist).pack()
        self.root.mainloop()

    def drag_import(self, event):
        path = re.sub(r"[\{\}]", "", str(event.data))
        self.text.insert(tk.END, f"{path}\n")

    def export_playlist(self, crate_name: Optional[str]="new crate"):
        if crate_name[-6:] != ".crate":
            crate_name = crate_name + ".crate"
        new_crate = SeratoCrate()
        track_paths = self.text.get("1.0", "end-1c").split("\n")
        new_crate.add_tracks(track_paths)

        crate_path = os.path.join(serato_path, crate_name)
        n = 0
        while not os.path.isfile(crate_path):
            crate_name = ''.join([crate_name[-6], "_", str(n), ".crate"])
            crate_path = os.path.join(serato_path, crate_name)
            n += 1
        new_crate.encode_and_write(crate_path)