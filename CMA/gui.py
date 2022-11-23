import tkinter as tk
from tkinter import ttk, simpledialog
from tkinterdnd2 import DND_FILES, DND_TEXT, TkinterDnD
import os
import logging
from .serato_advanced_classes import SeratoCrate
from .audio_player import AudioPlayer
from .helpers import load_all_crates, DB
from .assets import db_table, db_columns
from typing import Callable
from .config import load_log

class MusicDBGUI:
    def __init__(self, db_table=db_table, db_columns=db_columns):

        self.root = TkinterDnD.Tk()

        self.db_table = db_table
        if db_columns:
            self.db_columns = db_columns
            
        else:
            columns = self.db_query(f"PRAGMA table_info([{self.db_table}]);")
            self.db_columns =[c[1] for c in columns]

        self.playlist = None
        self.active_playlist_index = None
        self.init_grid()
        self.init_sidebar()
        self.init_library()
        self.init_playlist()
        self.init_searchbar()
        self.init_playlist_buttons()

        # initate data
        self.update(f"SELECT {','.join(self.db_columns)} FROM {self.db_table}")
        self.root.mainloop()

    ### GRID FUNCTIONS
    def init_grid(self):

        self.root.rowconfigure(0, weight=4, minsize=50)
        self.root.rowconfigure(1, weight=2, minsize=350)
        self.root.rowconfigure(2, weight=0)
        self.root.rowconfigure(3, weight=2, minsize=350)
        self.root.rowconfigure(4, weight=5, minsize=50)

        self.root.columnconfigure(0, weight=2, minsize=300)
        self.root.columnconfigure(1, weight=5, minsize=900)
        return

    def init_sidebar(self):
        """
        Populates the sidebar with the playlist library.
        """
        logging.debug("loading sidebar")
        self.sidebar_label = tk.Label(self.root, text="PLAYLIST LIBRARY", anchor="center")
        self.sidebar_label.grid(row=0, column=0, sticky="NS")
        
        self.playlist_library = load_all_crates()
        logging.debug(f"crates loaded: {len(self.playlist_library)}")
        playlist_var = tk.Variable(value=self.playlist_library)
        self.sidebar_box = tk.Listbox(
            self.root,
            listvariable=playlist_var,
            selectmode=tk.SINGLE,
            )
        self.sidebar_box.bind("<<ListboxSelect>>", self.get_playlist)
        self.sidebar_box.grid(row=1, column=0, rowspan=3, padx=(10,5), sticky="NEWS")
        return  

    def init_library(self):
        logging.debug("loading library")
        self.tree = ttk.Treeview(
            self.root, show="headings", columns=tuple(db_columns))
        self.tree.bind('<Return>', self.add_playlist_track_from_library)
        self.tree.bind('<Double-Button-1>', self.play_from_library)
        self.tree.grid(row=1, column=1, padx=(5,10), sticky="NEWS")
        return

    def play_from_library(self, event):
        song_path = self.track_info()['path']
        song_path = self.cure_library_path(song_path)
        if isinstance(song_path, bytes):
            song_path = song_path.decode()
        self.audio_player.load_song(song_path)
        self.audio_player.root.focus()

    def play_from_playlist(self, event): # TODO: consolidate w play_from_library
        selected_playlist_track = self.playlist.tracks[self.playlist_box.curselection()[0]]
        for path_key in ['ptrk', 'pfil']:
            if path_key in selected_playlist_track.data_keys:
                song_path = selected_playlist_track.get_data_by_tag(path_key)
                break
        self.audio_player.load_song(song_path)
        self.audio_player.root.focus()

    def track_info(self):
        i = self.tree.item(self.tree.focus())
        track_info_dict = dict(zip(self.db_columns, i['values']))
        return track_info_dict

    def init_searchbar(self):
        logging.debug("loading searchbar")
        self.search_frame = tk.Frame(self.root)
        self.audio_player = AudioPlayer(self.search_frame)
        self.audio_player.frame.pack(side="left")
        self.search_label = tk.Label(self.search_frame, text="SEARCH:")
        self.search_label.pack(side="left", fill="x")

        self.search_field = tk.Entry(self.search_frame)
        self.search_field.pack(side="left", fill="x")

        self.yield_button(self.search_frame, "Search", self.search_db)
        self.yield_button(self.search_frame, "Load Log File", load_log)

        self.search_frame.grid(row=0, column=1)

    def init_playlist_buttons(self):
        self.playlist_button_frame = tk.Frame(self.root)

        self.yield_button(self.playlist_button_frame, "New Playlist", self.create_new_playlist)
        self.yield_button(self.playlist_button_frame, "Export Playlist", self.export_playlist)

        self.playlist_button_frame.grid(row=0, column=0)

    def yield_button(self, root, text: str, command: Callable):
        """
        For adding buttons to the search bar. 
        """
        button = tk.Button(root, text=text, command=command)
        button.pack(side="left", fill="x")

    def init_playlist(self, playlist: SeratoCrate=None):
        logging.debug("loading playlist window")
        self.playlist_title = tk.StringVar()
        self.playlist_title.set("NO ACTIVE PLAYLIST")
        self.playlist_label = tk.Label(
            self.root,
            textvariable=self.playlist_title, 
            anchor="w")
        self.playlist_label.grid(row=2, column=1, padx=(5,10), sticky="EW")

        self.playlist_box = tk.Listbox(self.root)
        self.playlist_box.grid(row=3, column=1, padx=(5,10), sticky="NEWS")
        self.playlist_box.drop_target_register(DND_FILES, DND_TEXT)
        self.playlist_box.dnd_bind('<<Drop>>', self.add_playlist_track_from_library)
        self.playlist_box.bind("<Double-Button-1>", self.play_from_playlist)
        # self.playlist_box.bind("<Delete>", self.remove_from_playlist)

        if playlist:
            self.populate_playlist_box(playlist)
    
    ### TREE/DB MANAGEMENT
    def db_query(self, q):
        with DB() as db:
            return db.query(q)

    def update(self, q: str):
        if self.has_data:
            self.tree.delete(*self.tree.get_children())
        
        rows = self.db_query(q)
        for r in rows:
            self.tree.insert("", tk.END, values=r)
        
        for n, c in enumerate(db_columns):
            self.tree.heading(c, text=c)
            if n == 0:
                self.tree.column(c, width=50, stretch="NO")
            else:
                self.tree.column(c)
            
    def has_data(self):
        has_tree = self.tree.get_children()
        return True if has_tree else False

    def search_db(self):
        search_query = self.search_field.get()
        q = f"""
            SELECT *
            FROM {db_table}
            WHERE path LIKE "%{search_query}%"
            OR artist LIKE "%{search_query}%"
            OR title LIKE "%{search_query}%"
            OR album LIKE "%{search_query}%"
            OR albumartist LIKE "%{search_query}%"
        """
        self.update(q)
        return

    def cure_library_path(self, path):
        """
        File paths saved as bytes then saved as strings need to be sorted out.
        """
        if os.path.exists(path):
            return path

        try:
            p = eval(path).decode()
            if os.path.exists(p):
                return p
        except AttributeError:
            pass

        try:
            p = path.decode()
            if os.path.exists(p):
                return p
        except AttributeError:
            pass
        
        raise "No viable file path!"

    ### EVENT MANAGEMENT
    def add_playlist_track_from_library(self, event):
        path = self.track_info()['path']
        path = self.cure_library_path(path)
        if isinstance(path, bytes):
            path = path.decode()
        if not self.playlist:
            self.create_new_playlist()
            self.playlist = self.playlist_library[-1]
        self.playlist.add_track(path)
        self.populate_playlist_box(self.playlist)

    def get_artists(self, event):
        artists_selected = [f'"{self.artist_box.get(i)}"' for i in self.artist_box.curselection()]
        self.update(f"""
            SELECT {','.join(self.db_columns)}
            FROM {self.db_table}
            WHERE artist IN ({",".join(artists_selected)});
            """)

    def get_playlist(self, event):
        self.active_playlist_index = self.sidebar_box.curselection()[0]
        self.playlist = self.playlist_library[self.active_playlist_index] # this is redundant
        self.init_playlist(self.playlist)

    ### PLAYLIST FUNCTIONS
    def populate_playlist_box(self, active_playlist: SeratoCrate):
        self.playlist_title.set(f"ACTIVE PLAYLIST: {active_playlist.crate_name}")
        self.playlist_box.delete(0, tk.END)
        for t in active_playlist.tracks:
            self.playlist_box.insert(tk.END, t)

    def rename_playlist(self):
        name = simpledialog.askstring("Rename playlist", "Enter new playlist name")
        self.playlist_library[self.active_playlist_index].crate_name = name
        self.init_playlist(self.playlist_library[self.active_playlist_index])

    def create_new_playlist(self):
        name = simpledialog.askstring("New playlist", "Enter new playlist name")
        logging.info(f"creating new playlist: {name}")
        new_playlist = SeratoCrate(name=name)
        self.sidebar_box.insert(tk.END, name)
        self.playlist_library.append(new_playlist)
        self.sidebar_box.selection_clear(0, tk.END)
        self.sidebar_box.selection_set(tk.END)
        self.sidebar_box.activate(tk.END)
        self.init_playlist(self.playlist_library[-1])
        return

    def export_playlist(self):
        self.playlist.export_crate()
        logging.info(f"{self.playlist.crate_name} exported!")