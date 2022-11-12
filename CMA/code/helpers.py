import os
from ..config.assets import serato_path, verbose, db_path
from .serato_advanced_classes import SeratoCrate
import sqlite3
import tkinter as tk

def load_all_crates():
    global verbose
    crates = []
    crate_dir = os.path.join(serato_path, "Subcrates")
    for c in os.listdir(crate_dir):
        try:
            if c[-6:] == ".crate":
                print(c)
                crate_path = os.path.join(crate_dir, c)
                if verbose:
                    print("****" + c.upper(), crate_path)
                crate = SeratoCrate(crate_path)
                crate.get_track_data()
                crates.append(crate)
        except IndexError:
            continue
    return crates

class DB:
    def __init__(self):
        self._conn = sqlite3.connect(db_path)
        self._cursor = self._conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def conn(self):
        return self._conn

    @property
    def cur(self):
        return self._cursor

    def commit(self):
        self.conn.commit()

    def close(self, commit=True):
        if commit:
            self.commit()
        self.conn.close()

    def fetchone(self):
        return self.cur.fetchone()

    def fetchall(self):
        return self.cur.fetchall()

    def query(self, q):
        self.cur.execute(q)
        return self.fetchall()

def print_event_info(event):
    print('\nAction:', event.action)
    print('Supported actions:', event.actions)
    print('Mouse button:', event.button)
    print('Type codes:', event.codes)
    print('Current type code:', event.code)
    print('Common source types:', event.commonsourcetypes)
    print('Common target types:', event.commontargettypes)
    print('Data:', event.data)
    print('Event name:', event.name)
    print('Supported types:', event.types)
    print('Modifier keys:', event.modifiers)
    print('Supported source types:', event.supportedsourcetypes)
    print('Operation type:', event.type)
    print('Source types:', event.sourcetypes)
    print('Supported target types:', event.supportedtargettypes)
    print('Widget:', event.widget, '(type: %s)' % type(event.widget))
    print('X:', event.x_root)
    print('Y:', event.y_root, '\n')
        