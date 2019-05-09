from pyspectrim.PositionTab import PositionTab
from pyspectrim.ImageViewTab import ImageViewTab
from pyspectrim.SignalViewTab import SignalViewTab
from pyspectrim.LoggerTab import LoggerTab


import tkinter as tk
from tkinter import ttk


class ContextTabs(ttk.Notebook):

    def __init__(self, app, **kwargs):
        self.app = app
        super().__init__(self.app.root)

        self.image = None

        # populate
        self.positionTab = PositionTab(self)
        self.imageViewTab = ImageViewTab(self)
        self.signalViewTab = SignalViewTab(self)
        self.loggerTab = LoggerTab(self)

        # set default values
        self.set_defaults()

    def set_defaults(self):
        self.positionTab.set_defaults()
        self.imageViewTab.set_defaults()
        self.signalViewTab.set_defaults()

    def set_context_image(self, image=None):
        # this function does not call any draw function along the way
        if image is not None:
            self.image = image

            self.positionTab.set_context(image=self.image)
            self.imageViewTab.set_context(image=self.image)
            self.signalViewTab.set_context(image=self.image)

    def free_context_image(self):
        self.image = None
        self.set_defaults()

    def get_context_image(self):
        return self.image


