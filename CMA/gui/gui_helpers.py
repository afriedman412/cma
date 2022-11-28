import tkinter as tk
from typing import Callable, List, Union
import os
import logging

def yield_button(root, text: str, command: Callable):
    """
    For adding buttons to the search bar. 
    """
    button = tk.Button(root, text=text, command=command)
    button.pack(side="left", fill="x")
    return

def yield_drop_down(root, options: List, name :str="drop_down_menu"):
    drop_down_var = tk.StringVar(root)
    drop_down_var.set(options[0]) # default value

    drop_down_menu = tk.OptionMenu(root, drop_down_var, *options)
    drop_down_menu.pack(side="left", fill="x")
    return drop_down_var, drop_down_menu

def yield_listbox(root, options: List, selectmode="single", name: str="listbox"):
    listbox_var = tk.Variable(value=options)
    listbox = tk.Listbox(
            root, 
            listvariable=listbox_var, 
            selectmode=selectmode,
            name=name
            )
    listbox.pack(side="left", fill="x")
    return listbox_var, listbox

def cure_library_path(path: Union[str, bytes]) -> str:
    """
    File paths saved as bytes then saved as strings need to be sorted out.
    """
    if isinstance(path, bytes):
        return cure_library_path(path.decode())

    for p in [path, "/" + path, os.path.abspath(path)]:
        if os.path.exists(p):
            logging.debug(f"Using {p} as path for {path}")
            return p
    try:
        return cure_library_path(eval(path))
    except (AttributeError, SyntaxError):
        pass

    return