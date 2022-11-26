import tkinter as tk
from typing import List
from .helpers import DB
from .gui_helpers import cure_library_path
from .serato_advanced_classes import SeratoCrate
from .assets import db_table
import regex as re
import logging


# TODO: consolidate classes for DB and GUI
class SmartPlaylistMenu:
    def __init__(self, window, db_columns):
        self.db_columns = db_columns

        self.window= window
        self.init_grid()
        return

    def init_grid(self):
        self.window.rowconfigure(0, minsize=50)
        self.window.rowconfigure(1, minsize=150)
        self.window.rowconfigure(2, minsize=50)

        self.window.columnconfigure(0, minsize=250)
        self.window.columnconfigure(1, minsize=250)

        # name frame
        self.name_frame = tk.Frame(self.window)
        self.name_label = tk.Label(self.name_frame, text="Playlist name:")
        self.name_label.pack(side="left", fill="x")
        self.name_field = tk.Entry(self.name_frame)
        self.name_field.pack(side="left", fill="x")

        self.name_frame.grid(row=0, column=0, columnspan=2)

        # energy
        self.energy_frame = tk.Frame(self.window)
        self.energy_var = tk.Variable(value=[i for i in range(5)])
        self.energy_listbox = tk.Listbox(
            self.energy_frame, 
            listvariable=self.energy_var, 
            selectmode="multiple",
            exportselection=0
            )
        self.energy_listbox.pack(side="left", fill="y")
        self.energy_frame.grid(row=1, column=0)

        # genre
        self.genre_frame = tk.Frame(self.window)
        self.genre_var = tk.Variable(value=self.genres)
        self.genre_listbox = tk.Listbox(
            self.genre_frame, 
            listvariable=self.genre_var, 
            selectmode="multiple",
            exportselection=0)
        self.genre_listbox.pack(side="left",fill="y")
        self.genre_frame.grid(row=1, column=1)

        self.enter_button = tk.Button(self.window, text="Create Playlist", command=self.make_crate_from_menu)
        self.enter_button.grid(row=2, column=0, columnspan=2)
        return

    def get_playlist_tracks(self):
        q_commands = []
        
        selected_energies = [self.energy_var.get()[n] for n in self.energy_listbox.curselection()]
        selected_genres = [self.genre_var.get()[n] for n in self.genre_listbox.curselection()]
        
        for e in selected_energies:
            q_commands.append(f"grouping LIKE '{e} %'")

        for g in selected_genres:
            g = g.replace("'", "\\'").replace('"', '\\"')
            q_commands.append(f"grouping LIKE '%{g}%'")

        subcommands = " OR ".join(q_commands)

        q = " ".join([self.q_header, "WHERE", subcommands])
        print(q)
        tracks = self.db_query(q)
        tracks = [dict(zip(self.db_columns, track)) for track in tracks]
        return tracks

    def make_crate_from_menu(self):
        self.new_crate = SeratoCrate(name=self.name_field.get())
        tracks = self.get_playlist_tracks()
        for t in tracks:
            verified_path = cure_library_path(t['path'])
            if verified_path:
                self.new_crate.add_track(verified_path)
        self.window.destroy()
        return

    @property
    def q_header(self):
        return f"SELECT {','.join(self.db_columns)} FROM {db_table}"

    @property
    def genres(self):
        rows = self.db_query(f"""SELECT grouping FROM {db_table} WHERE grouping IS NOT ''""")
        genres = []
        for r in rows:
            r = re.sub(r"^\d\s", "", r[0])
            genres += r.split("/")
        return list(set(genres))

    def db_query(self, q):
        with DB() as db:
            return db.query(q)

    



    