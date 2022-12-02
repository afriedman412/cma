
import logging
from tkinter.ttk import Treeview

class LibraryFrame:
    def __init__(self, root, db_columns):
        self.init_library(root, db_columns)
        return

    def init_library(self, root, db_columns):
        logging.debug("loading library")
        self.tree = Treeview(
            root, 
            show="headings", 
            columns=db_columns, 
            name="library")

        for col in db_columns:
            self.tree.heading(col, text=col, command=lambda col_=col: self.sort_by_column(col_, False))
        return

    def sort_by_column(self, col: str, reverse: bool=False):
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        l.sort(key=lambda t: t[0], reverse=reverse)

        for i, (_, k) in enumerate(l):
            self.tree.move(k, '', i)
        
        self.tree.heading(col, command=lambda: self.sort_by_column(col, not reverse))
        return