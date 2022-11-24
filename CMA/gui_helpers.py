import tkinter as tk
from typing import Callable
import os

def yield_button(root, text: str, command: Callable):
    """
    For adding buttons to the search bar. 
    """
    button = tk.Button(root, text=text, command=command)
    button.pack(side="left", fill="x")
    return

def cure_library_path(path):
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