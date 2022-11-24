import tkinter as tk
from .gui_helpers import yield_button
from .serato_advanced_classes import SeratoTrack
import logging

class PlaylistMagic:
    def __init__(self, window):
        self.root=window
        self.init_window()
        return