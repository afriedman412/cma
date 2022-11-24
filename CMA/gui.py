import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from tkinterdnd2 import DND_FILES, DND_TEXT, TkinterDnD
import logging
from .serato_advanced_classes import SeratoCrate
from .audio_player import AudioPlayer
from .helpers import load_all_crates, DB
from .assets import db_table, db_columns
from .config import load_log
from .gui_helpers import yield_button, cure_library_path

class MusicDBGUI:
    def __init__(self, db_table=db_table, db_columns=db_columns):

        self.root = TkinterDnD.Tk()

        self.db_table = db_table
        if db_columns:
            self.db_columns = db_columns
            
        else:
            columns = self.db_query(f"PRAGMA table_info([{self.db_table}]);")
            self.db_columns =[c[1] for c in columns]

        self.active_playlist_index = None
        self.init_grid()
        self.init_playlist_library()
        self.init_library()
        self.init_playlist()
        self.init_searchbar()
        self.init_playlist_buttons()

        # initate data
        self.update(f"SELECT {','.join(self.db_columns)} FROM {self.db_table}")
        self.root.mainloop()

    @property
    def active_playlist(self) -> SeratoCrate:
        return self.playlist_library[self.active_playlist_index]

    ### GRID FUNCTIONS
    def init_grid(self):

        self.root.rowconfigure(0, weight=4, minsize=40)
        self.root.rowconfigure(1, weight=2, minsize=350)
        self.root.rowconfigure(2, weight=2, minsize=50)
        self.root.rowconfigure(3, weight=2, minsize=350)
        self.root.rowconfigure(4, weight=5, minsize=50)

        self.root.columnconfigure(0, weight=2, minsize=300)
        self.root.columnconfigure(1, weight=5, minsize=900)
        return

    def init_library(self):
        logging.debug("loading library")
        self.tree = ttk.Treeview(
            self.root, show="headings", columns=tuple(db_columns), name="library")
        self.tree.bind('<Return>', self.add_playlist_track_from_library)
        self.tree.bind('<Double-Button-1>', self.play_song)
        self.tree.grid(row=1, column=1, padx=(5,10), sticky="NEWS")
        return

    def init_playlist_library(self):
        """
        Creates the playlist library sidebar and populates it with existing crates.
        """
        logging.debug("loading sidebar")
        self.sidebar_label = tk.Label(self.root, text="PLAYLIST LIBRARY", anchor="center")
        self.sidebar_label.grid(row=0, column=0, sticky="NS")
        
        self.playlist_library = load_all_crates()
        logging.debug(f"crates loaded: {len(self.playlist_library)}")
        self.playlist_library_var = tk.Variable(value=self.playlist_library)
        self.sidebar_box = tk.Listbox(
            self.root,
            listvariable=self.playlist_library_var,
            selectmode=tk.SINGLE,
            name="playlist_library"
            )
        self.sidebar_box.bind("<Double-Button-1>", self.load_playlist)
        self.sidebar_box.grid(row=1, column=0, rowspan=3, padx=(10,5), sticky="NEWS")
        return  

    def init_playlist(self):
        logging.debug("loading playlist window")
        self.playlist_label_frame = tk.Frame(self.root)
        self.playlist_title = tk.StringVar()
        self.playlist_title.set("NO PLAYLIST ACTIVE")
        self.playlist_label = tk.Label(
            self.playlist_label_frame,
            textvariable=self.playlist_title, 
            anchor="w")
        self.playlist_label.pack(side="left")
        yield_button(self.playlist_label_frame, "New Playlist", self.create_new_playlist)
        yield_button(self.playlist_label_frame, "Rename Playlist", self.rename_playlist)
        yield_button(self.playlist_label_frame, "Save Playlist", self.save_playlist)
        self.playlist_label_frame.grid(row=2, column=1, padx=(5,10), sticky="EW")

        self.playlist_box = tk.Listbox(self.root, name='playlist')
        self.playlist_box.grid(row=3, column=1, padx=(5,10), sticky="NEWS")
        self.playlist_box.drop_target_register(DND_FILES, DND_TEXT)
        self.playlist_box.dnd_bind('<<Drop>>', self.add_playlist_track_from_library)
        self.playlist_box.bind("<Double-Button-1>", self.play_song)
        self.playlist_box.bind("<BackSpace>", self.delete_track_from_playlist)

    def init_searchbar(self):
        logging.debug("loading searchbar")
        self.search_frame = tk.Frame(self.root)
        self.audio_player = AudioPlayer(self.search_frame)
        self.audio_player.frame.pack(side="left")
        self.search_label = tk.Label(self.search_frame, text="SEARCH:")
        self.search_label.pack(side="left", fill="x")

        self.search_field = tk.Entry(self.search_frame)
        self.search_field.pack(side="left", fill="x")

        yield_button(self.search_frame, "Search", self.search_db)
        yield_button(self.search_frame, "Load Log File", load_log)

        self.search_frame.grid(row=0, column=1)

    def init_playlist_buttons(self):
        self.playlist_button_frame = tk.Frame(self.root)
        yield_button(self.playlist_button_frame, "New Playlist", self.create_new_playlist)
        yield_button(self.playlist_button_frame, "Save Playlist", self.save_playlist)
        self.playlist_button_frame.grid(row=0, column=0)

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

    ### EVENT MANAGEMENT
    def add_playlist_track_from_library(self, event):
        song_path = self.get_library_song_path()
        if not self.active_playlist:
            self.create_new_playlist()
            self.active_playlist = self.playlist_library[-1]
        self.active_playlist.add_track(song_path)
        self.update_playlist()

    def delete_track_from_playlist(self, event):
        self.active_playlist.delete_track(self.playlist_box.curselection()[0])
        self.update_playlist()

    def load_playlist(self, event):
        self.active_playlist_index = self.sidebar_box.curselection()[0]
        self.update_playlist()

    def play_song(self, event):
        if event.widget._name == "library":
            song_path = self.get_library_song_path()
        elif event.widget._name == "playlist":
            selected_playlist_track = self.active_playlist.tracks[self.playlist_box.curselection()[0]]
            song_path = selected_playlist_track.path

        self.audio_player.load_song(song_path)

    ### PLAYLIST FUNCTIONS
    def update_playlist(self):
        """
        No variable passed because active playlist is entirely controlled by active_playlist_index property.
        """
        self.playlist_title.set(f"ACTIVE PLAYLIST: {self.active_playlist.crate_name}")
        self.playlist_box.delete(0, tk.END)
        for t in self.active_playlist.tracks:
            self.playlist_box.insert(tk.END, t)

    def rename_playlist(self):
        name = simpledialog.askstring("Rename playlist", "Enter new playlist name")
        self.playlist_library[self.active_playlist_index].crate_name = name
        self.update_playlist()

    def create_new_playlist(self):
        name = simpledialog.askstring("New playlist", "Enter new playlist name")
        if not name:
            return
        logging.info(f"creating new playlist: {name}")
        self.playlist_library.append(SeratoCrate(name=name))
        self.active_playlist_index=-1
        self.sidebar_box.insert(tk.END, name)
        

        # this is just navigating to the end of the playlist library
        self.sidebar_box.selection_clear(0, tk.END)
        self.sidebar_box.selection_set(tk.END)
        self.sidebar_box.activate(tk.END)

        self.update_playlist()
        return

    def save_playlist(self):
        self.active_playlist.export_crate()
        messagebox.showinfo(message=f"{self.active_playlist.crate_name} saved!")
        self.root.update()
        logging.info(f"{self.active_playlist.crate_name} exported!")

    def get_library_song_path(self):
        i = self.tree.item(self.tree.focus())
        track_info_dict = dict(zip(self.db_columns, i['values']))
        song_path = track_info_dict['path']
        song_path = cure_library_path(song_path)
        if isinstance(song_path, bytes):
            song_path = song_path.decode()
        return song_path