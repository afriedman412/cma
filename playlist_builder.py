"""
Drag and drop files into a window, click button to export playlist.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import regex as re
from crate_writing import make_playlist

class App():

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

    def export_playlist(self):
        track_paths = self.text.get("1.0", "end-1c").split("\n")
        make_playlist(track_paths)

App()