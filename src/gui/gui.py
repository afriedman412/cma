# https://www.activestate.com/resources/quick-reads/how-to-display-data-in-a-table-using-tkinter/
# https://stackoverflow.com/questions/57772458/how-to-get-a-treeview-columns-to-fit-the-frame-it-is-within
# https://stackoverflow.com/questions/22262147/how-do-i-make-a-resizeable-window-with-a-sidepanel-and-content-area

import tkinter as tk
from tkinter import ttk, simpledialog
from tkinterdnd2 import DND_FILES, DND_TEXT, TkinterDnD
import os

from ..src.serato_advanced_classes import SeratoCrate
from ..src.helpers import load_all_crates, DB
from ..config.assets import db_table, db_columns


class MusicDBGUI:
    def __init__(self, db_table=db_table, db_columns=db_columns):
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

        # initate data
        self.update(f"SELECT {','.join(self.db_columns)} FROM {self.db_table}")

        self.root.mainloop()

    ### GRID FUNCTIONS
    def init_grid(self):
        self.root = TkinterDnD.Tk()

        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=3, minsize=350)
        self.root.rowconfigure(2, weight=0)
        self.root.rowconfigure(3, weight=3, minsize=350)
        self.root.rowconfigure(4, weight=3, minsize=25)

        self.root.columnconfigure(0, weight=2, minsize=300)
        self.root.columnconfigure(1, weight=5, minsize=900)
        return

    def init_sidebar(self):
        """
        Populates the sidebar with the playlist library.
        """
        self.sidebar_label = tk.Label(self.root, text="PLAYLIST LIBRARY", anchor="n")
        self.sidebar_label.grid(row=0, column=0, sticky="NS")
        
        self.playlist_library = load_all_crates()
        playlist_var = tk.Variable(value=self.playlist_library)
        self.sidebar_box = tk.Listbox(
            self.root,
            listvariable=playlist_var,
            selectmode=tk.SINGLE,
            )
        self.sidebar_box.bind("<<ListboxSelect>>", self.get_playlist)
        self.sidebar_box.grid(row=1, column=0, rowspan=3, sticky="NEWS")

        self.new_playlist_button = tk.Button(
            self.root, 
            text="New Playlist", 
            command=self.create_new_playlist)
        self.new_playlist_button.grid(row=4, column=0, sticky="EW")
        return  

    def init_library(self):
        self.tree = ttk.Treeview(
            self.root, show="headings", columns=tuple(db_columns))
        self.tree.bind('<Double-Button-1>', self.add_playlist_track_from_library)
        self.tree.grid(row=1, column=1, sticky="NEWS")
        return

    def track_info(self):
        i = self.tree.item(self.tree.focus())
        track_info_dict = dict(zip(self.db_columns, i['values']))
        return track_info_dict

    def init_searchbar(self):
        self.search_frame = tk.Frame(self.root)
        self.search_label = tk.Label(self.search_frame, text="SEARCH:")
        self.search_label.pack(side="left", fill="x")

        self.search_field = tk.Entry(self.search_frame)
        self.search_field.pack(side="left", fill="x")

        self.search_button = tk.Button(
            self.search_frame, 
            text="Search",
            command=self.search_db
            )
        self.search_button.pack(side="left", fill="x")

        self.search_frame.grid(row=0, column=1)

    def init_playlist(self, playlist: SeratoCrate=None):
        self.playlist_label = tk.Label(
            self.root,
            text=f"ACTIVE PLAYLIST: {playlist}", 
            anchor="nw")
        self.playlist_label.grid(row=2, column=1, sticky="EW")

        self.playlist_box = tk.Listbox(self.root)
        self.playlist_box.drop_target_register(DND_FILES, DND_TEXT)
        self.playlist_box.dnd_bind('<<Drop>>', self.add_playlist_track_from_library)
        self.playlist_box.grid(row=3, column=1, sticky="NEWS")

        self.export_playlist_button = tk.Button(
            self.root, 
            text="Export Playlist", 
            command=self.export_playlist)
        self.export_playlist_button.grid(row=4, column=1)

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
        print(path)
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
    def populate_playlist_box(self, crate: SeratoCrate):
        self.playlist_box.delete(0, tk.END)
        for t in crate.tracks:
            self.playlist_box.insert(tk.END, t)

    def rename_playlist(self):
        name = simpledialog.askstring("Rename playlist", "Enter new playlist name")
        self.playlist_library[self.active_playlist_index].crate_name = name
        self.init_playlist(self.playlist_library[self.active_playlist_index])

    def create_new_playlist(self):
        name = simpledialog.askstring("New playlist", "Enter new playlist name")
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
        print(f"{self.playlist.crate_name} exported!")

if __name__ == "__main__":
    MusicDBGUI()