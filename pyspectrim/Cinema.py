from pyspectrim.ImagePanel import ImagePanel

import tkinter as tk
from tkinter import ttk


class Cinema(tk.Frame):
    def __init__(self, app, **kwargs):

        self.app = app

        super().__init__(self.app.root)

        self.imagePanel = ImagePanel(self)
