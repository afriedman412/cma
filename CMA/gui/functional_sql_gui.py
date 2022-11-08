"""
Import via:
https://github.com/Saadmairaj/tkterminal

(drag and drop works though)

- create playlists
- read/write serato crates

reading works!

writing? creating? --> see seratopy code
smartcrates?

- import from seratodb maybe?
"""

# TODO: implement info labels on imported tracks after making SeratoTrack metadata more accessible

# https://www.activestate.com/resources/quick-reads/how-to-display-data-in-a-table-using-tkinter/
# https://stackoverflow.com/questions/57772458/how-to-get-a-treeview-columns-to-fit-the-frame-it-is-within
# https://stackoverflow.com/questions/22262147/how-do-i-make-a-resizeable-window-with-a-sidepanel-and-content-area

import tkinter as tk
from tkinter import Frame, Listbox, ttk, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from typing import Optional
import sqlite3
import os
import regex as re
from mutagen.id3 import ID3

from ..code.serato_query import SeratoCrate, SeratoTrack
from ..config.assets import serato_path



path = "/Users/af412/.config/beets/library.db"
table ='items'
columns = ['id', 'path', 'title', 'artist']

class MusicDBGUI():

    def __init__(self, path=path, table=table, columns=columns):
        self.playlist = SeratoCrate()

        self.path = path
        self.table = table

        if not columns:
            self.columns = self.get_columns()
        else:
            self.columns = columns

        # set up root
        self.root = TkinterDnD.Tk()
        self.root.geometry("1200x800")

        # sidebar
        self.sidebar = Frame(self.root, width=200)
        self.sidebar.pack(expand=True, fill='both', side='left')
        
        # library
        self.library = Frame(self.root, height=550)
        self.library.pack(expand=True, fill='both', side='top'),

        self.load_playlist()

        # build tree
        self.tree = ttk.Treeview(self.library, show="headings", columns=tuple(columns))
        self.tree.pack(expand=True, fill='both')

        # build sidebar (external function)
        self.load_sidebar()

        # initate data
        self.update(f"SELECT {','.join(self.columns)} FROM {self.table}")

        self.root.mainloop()

    def get_columns(self):
        with sqlite3.connect(self.path) as conn:
            cur = conn.cursor()
            columns = cur.execute(f"PRAGMA table_info([{self.table}]);")
        return [c[1] for c in columns]

    def get_data(self, q):
        with sqlite3.connect(path) as conn:
            cur = conn.cursor()
            cur.execute(q)
            rows = cur.fetchall()
            for r in rows:
                self.tree.insert("", tk.END, values=r)

    def load_sidebar(self):
        with sqlite3.connect(path) as conn:
            cur = conn.cursor()
            cur.execute(f"SELECT distinct(artist) FROM {self.table} ORDER BY artist desc")
            artists = [' '.join(a) for a in cur.fetchall()]
        
        artist_var = tk.Variable(value=artists)
        self.artist_box = tk.Listbox(
            self.sidebar, 
            listvariable=artist_var,
            selectmode=tk.SINGLE
            )
        self.artist_box.pack(side='left', expand=True, fill='both')
        self.artist_box.bind("<<ListboxSelect>>", self.get_artists)

    def load_playlist(self):
        self.playlist_box = tk.Listbox(self.root, height=200)
        self.playlist_box.drop_target_register(DND_FILES)
        self.playlist_box.dnd_bind('<<Drop>>', self.drag_import)
        self.playlist_box.pack(expand=True, fill='both', side='bottom')

        tk.Button(
            self.playlist_box, text="Export Playlist", command=self.export_playlist).pack(
                side='bottom', fill='x'
            )
    
    def populate_playlist_box(self):
        self.playlist_box.delete(0, tk.END)
        for t in self.playlist.tracks():
            self.playlist_box.insert(tk.END, t)

    def get_artists(self, event):
        artists_selected = [f'"{self.artist_box.get(i)}"' for i in self.artist_box.curselection()]
        self.update(f"""
            SELECT {','.join(self.columns)}
            FROM {self.table}
            WHERE artist IN ({",".join(artists_selected)});
            """)

    def update(self, q):
        if self.has_data:
            self.tree.delete(*self.tree.get_children())

        self.get_data(q)

        for c in columns:
            self.tree.heading(c, text=c)
            self.tree.column(c)
            
    def has_data(self):
        has_tree = self.tree.get_children()
        return True if has_tree else False

    def drag_import(self, event):
        path = re.sub(r"[\{\}]", "", str(event.data))
        self.playlist.add_track(path)
        self.populate_playlist_box()

    def export_playlist(self, crate_name: str="new crate"):
        if crate_name[-6:] != ".crate":
            crate_name = crate_name + ".crate"
        crate_path = os.path.join(serato_path, "Subcrates", crate_name)
        n = 0
        while os.path.isfile(crate_path):
            crate_name = ''.join([crate_name[:-6], "_", str(n), ".crate"])
            crate_path = os.path.join(serato_path, "Subcates", crate_name)
            n += 1

        print(crate_path)
        self.playlist.encode_and_write(crate_path)