from pyspectrim.PositionTab import PositionTab

import tkinter as tk
from tkinter import ttk


class ContextTabs(ttk.Notebook):
    def __init__(self, app, **kwargs):
        self.app = app
        super().__init__(self.app.root)

        self.positionTab = PositionTab(self)

    def setContext(self, image):
        self.positionTab.setPosSliders(image)

    def cleanContext(self):
        self.positionTab.cleanPosSliders()
