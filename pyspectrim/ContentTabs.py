from pyspectrim.FilesTab import FilesTab
from pyspectrim.ImagesTab import ImagesTab

import tkinter as tk
from tkinter import ttk


class ContentTabs(ttk.Notebook):
    def __init__(self, app, **kwargs):

        self.app = app
        super().__init__(self.app.root)

        self.filesTab = FilesTab(self)
        self.imagesTab = ImagesTab(self)
