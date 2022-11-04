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


# https://www.activestate.com/resources/quick-reads/how-to-display-data-in-a-table-using-tkinter/
# https://stackoverflow.com/questions/57772458/how-to-get-a-treeview-columns-to-fit-the-frame-it-is-within
# https://stackoverflow.com/questions/22262147/how-do-i-make-a-resizeable-window-with-a-sidepanel-and-content-area

import tkinter as tk
from tkinter import ttk, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkterminal import Terminal

import sqlite3
from functools import partial

path = "/Users/af412/.config/beets/library.db"
table ='items'
columns = ['id', 'path', 'title', 'artist']

class App():

    def __init__(self, path, table, columns):

        self.path = path
        self.table = table

        if not columns:
            self.columns = self.get_columns()
        else:
            self.columns = columns

        self.root = TkinterDnD.Tk()
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.drag_import)

        self.frame = tk.Frame(self.root, width=500)
        self.frame.pack(expand=True, fill='both', side='right')
        self.tree = ttk.Treeview(self.frame, show="headings", columns=tuple(columns))
        self.tree.pack(expand=True, fill=tk.BOTH)

        self.load_sidebar()
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
            self.root, 
            listvariable=artist_var,
            selectmode=tk.MULTIPLE
            )
        self.artist_box.pack(side=tk.LEFT, expand=True, fill='both')
        self.artist_box.bind("<<ListboxSelect>>", self.get_artists)

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
        # new_window = tk.Toplevel()
        # terminal = Terminal(new_window, pady=5, padx=5)
        # terminal.shell = True
        # terminal.pack(expand=True, fill='both')
        # p = str(event.data)[1:-1]
        # terminal.run_command(f"beet import \"{p}\"", give_input=None)

        messagebox.showinfo("Dragged", event.data)


App(path, table, columns)