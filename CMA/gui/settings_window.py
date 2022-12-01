import tkinter as tk
from tkinter import Toplevel
from tkinter.ttk import OptionMenu
from ..assets.assets import autoload_key
from typing import Literal
import os
import json
import logging

class SettingsWindow:
    def __init__(self, window: Toplevel):
        """
        Just displays config settings now, doesn't change them.
        """
        self.window = window # make a new top level for the track info
        self.window.geometry('380x500')

        self.init_window()
        return

    def init_window(self):
        tk.Label(
            self.window, text="SETTINGS", font=("Arial Bold", 18)
            ).pack(side="top", fill="both")

        tk.Label(
            self.window, text="Data Locations", font=("Arial Bold", 14)
            ).pack(anchor="w", padx=15, pady=(30, 5))

        for k in ['config', 'serato', 'crates', 'db']:
            self.make_row(k)

        tk.Label(
            self.window, text="Crate Autoload", font=("Arial Bold", 14)
        ).pack(anchor="w", padx=15, pady=(30, 5))

        self.autoload_var = tk.StringVar(self.window)
        autoload_menu = OptionMenu(
            self.window, 
            self.autoload_var,
            os.environ['CRATE_AUTOLOAD'],
            *autoload_key.keys(),
            command=lambda o: self.set_autoload(autoload=o)
        )
        autoload_menu.pack(anchor="w", padx=15, pady=(0,60))

        self.button_frame = tk.Frame(self.window)
        tk.Button(self.button_frame, text="CANCEL", command=self.window.destroy).pack(side="left", padx=7)
        tk.Button(self.button_frame, text="SAVE", command=self.save_and_quit).pack(side="right", padx=7)
        self.button_frame.pack(anchor="s")
        return

    def make_row(self, label: str):
        frame = tk.Frame(self.window)
        frame.geometry = "300x5"
        frame.columnconfigure(0, minsize=10, weight=0)
        frame.columnconfigure(1, minsize=270, weight=2)
        frame.columnconfigure(2, minsize=20, weight=1)

        label_ = tk.Label(
            frame, 
            text=label.title(), 
            font=("Arial Bold", 14), 
            width=10,
            justify="left")
        label_.grid(row=0, column=0, sticky="w")

        entry = tk.Label(
            frame, 
            text=os.environ[f"{label.upper()}_PATH"], 
            font=("Arial", 14), 
            justify="left")
        entry.grid(row=0, column=1, sticky="w")
        frame.pack(anchor="w", fill="both", padx=7)

    def set_autoload(self, autoload: str):
        if autoload in autoload_key.keys():
            os.environ['CRATE_AUTOLOAD'] = autoload
            self.autoload_var.set(autoload)
        else:
            raise ValueError("Invalid Crate Autoload setting")

    def save_and_quit(self):
        config = json.load(open(os.environ['CONFIG_PATH']))
        config['crate_autoload'] = self.autoload_var.get()
        json.dump(config, open(os.environ['CONFIG_PATH'], "w+"))
        self.window.destroy()
