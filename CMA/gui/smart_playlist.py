import tkinter as tk
from .gui_helpers import cure_library_path
from ..code.serato_advanced_classes import SeratoCrate
from ..code.helpers import DB
from ..assets.assets import db_table, select_genres
from typing import List
import logging


# TODO: consolidate classes for DB and GUI
class SmartPlaylistMenu:
    def __init__(self, window: tk.Toplevel, db_columns: List, genres):
        """
        Opens and assembles the smart playlist window.

        Currently a little janky -- strictly for Case to parse his "groupings" tags.

        Uses db_columns to streaming query. Genres are parsed on launch from db and passed here from the main GUI.
        """
        self.db_columns = db_columns
        self.window = window
        self.new_crate = None
        self.genres = genres
        self.init_grid()
        return

    def init_grid(self):
        """
        Creates the grid.
        """
        self.window.rowconfigure(0, minsize=50) # name playlist
        self.window.rowconfigure(1, minsize=150) # includes listboxes
        self.window.rowconfigure(2, minsize=150) # excludes
        self.window.rowconfigure(3, minsize=40) # buttons

        self.window.columnconfigure(0, minsize=250)
        self.window.columnconfigure(1, minsize=250)
        self.init_frames()

    def yield_listbox(self, k, root, values, selectmode="multiple"):
        """
        Creates a listbox. k used to name the tk variable and the listbox. Root is the window. Values go into the listbox. Selectmode is passed to listbox.

        Probably can throw **kwargs in here eventually.

        Also can probably move this to gui_helpers -- I think I rewrote this on the fly for more flexibility with names and didn't want to have to go back to adjust other code that used gui_helpers too.
        """
        var_name = f"{k}_var"
        listbox = f"{k}_listbox"
        self.__setattr__(var_name, tk.Variable(value=values))
        self.__setattr__(
            f"{k}_listbox", 
            tk.Listbox(
                root, 
                listvariable=self.__getattribute__(var_name),
                selectmode=selectmode,
                name=listbox,
                exportselection=0
                ))
        return

    def yield_frame(self, k: str): # k is include or exclude
        frame = f"{k}_frame"
        self.__setattr__(frame,  tk.Frame(self.window))
        tk.Label(
            self.__getattribute__(frame), 
            text=f"{k.upper()}...", 
            font=("Arial Bold", 14)).pack(anchor="nw", padx=15, pady=(15, 2))

        for label, var in zip(
                ["energy", "all_genre","sel_genre"],
                [[r for r in range(1,4)], self.genres, select_genres]
            ):
            self.yield_listbox("_".join([label, k]), self.__getattribute__(frame), var)
            self.__getattribute__(f"{label}_{k}_listbox").pack(side="left", fill="x", padx=15, pady=15)
        return 

    def get_selections(self, k: str):
        energies = [
            self.__getattribute__(f"energy_{k}_var").get()[n] \
                for n in self.__getattribute__(f"energy_{k}_listbox").curselection()
                ]

        all_genres = [
            self.__getattribute__(f"all_genre_{k}_var").get()[n] \
                for n in self.__getattribute__(f"all_genre_{k}_listbox").curselection()
            ]

        sel_genres = [
            self.__getattribute__(f"sel_genre_{k}_var").get()[n] \
                for n in self.__getattribute__(f"sel_genre_{k}_listbox").curselection()
            ]
        return energies, all_genres+sel_genres

    def init_frames(self):
        """
        Puts the frames in the grid.
        """

        # name frame
        self.name_frame = tk.Frame(self.window)
        self.name_label = tk.Label(self.name_frame, text="Playlist name:", font=("Arial Bold", 18))
        self.name_label.pack(side="left", fill="x", padx=(15,0))

        self.name_var = tk.StringVar(self.name_frame, "New Playlist")
        self.name_field = tk.Entry(self.name_frame, textvariable=self.name_var)
        self.name_field.pack(side="left", fill="x")
        self.name_frame.grid(row=0, column=0, columnspan=2)

        # includes
        self.yield_frame("include")
        self.yield_frame("exclude")

        self.include_frame.grid(row=1, column=0, columnspan=2)
        self.exclude_frame.grid(row=2, column=0, columnspan=2)

        # enter
        self.enter_button = tk.Button(self.window, text="Create Playlist", command=self.make_crate_from_menu)
        self.enter_button.grid(row=3, column=0, columnspan=2)
        return

    def get_playlist_tracks(self):
        """
        Assembles db queries based on includes and excludes from the listboxes, makes the queries and returns the tracks.

        If this gets built out, make this into multiple functions! 
        """
        q_commands = []
        
        include_energies, include_genres = self.get_selections("include")
        
        for e in include_energies:
            q_commands.append(f"grouping LIKE '{e} %'")

        for g in include_genres:
            g = g.replace("'", "\\'").replace('"', '\\"')
            q_commands.append(f"grouping LIKE '%{g}%'")

        exclude_energies, exclude_genres = self.get_selections("exclude")
        
        for e in exclude_energies:
            q_commands.append(f"grouping NOT LIKE '{e} %'")

        for g in exclude_genres:
            g = g.replace("'", "\\'").replace('"', '\\"')
            q_commands.append(f"grouping NOT LIKE '%{g}%'")

        subcommands = " AND ".join(q_commands)

        q = " ".join([self.q_header, "WHERE", subcommands])
        print(q)
        tracks = self.db_query(q)
        tracks = [dict(zip(self.db_columns, track)) for track in tracks]
        return tracks

    def make_crate_from_menu(self):
        tracks = self.get_playlist_tracks()
        if tracks:
            self.new_crate = SeratoCrate(name=self.name_field.get())
            for t in tracks:
                verified_path = cure_library_path(t['path'])
                if verified_path:
                    self.new_crate.add_track(verified_path)
        self.window.destroy()
        return

    @property
    def q_header(self):
        return f"SELECT {','.join(self.db_columns)} FROM {db_table}"

    def db_query(self, q):
        with DB() as db:
            return db.query(q)

    



    