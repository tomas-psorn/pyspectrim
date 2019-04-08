from pyspectrim.PositionTab import PositionTab
from pyspectrim.ImageViewTab import ImageViewTab
from pyspectrim.LoggerTab import LoggerTab

import tkinter as tk
from tkinter import ttk


class ContextTabs(ttk.Notebook):

    def __init__(self, app, **kwargs):
        self.app = app
        super().__init__(self.app.root)

        self.positionTab = PositionTab(self)
        self.imageViewTab = ImageViewTab(self)
        self.loggerTab = LoggerTab(self)

    def update_context(self):
        current_tab = self.tab(self.select(),'text')

        if current_tab == "Position":
            self.positionTab.on_visible()
        elif current_tab == "Image view":
            self.imageViewTab.on_visible()
        elif current_tab == "Logger":
            pass

