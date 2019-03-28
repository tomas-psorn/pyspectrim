from pyspectrim.PositionTab import PositionTab
from pyspectrim.ImageViewTab import ImageViewTab

import tkinter as tk
from tkinter import ttk


class ContextTabs(ttk.Notebook):

    def __init__(self, app, **kwargs):
        self.app = app
        super().__init__(self.app.root)

        self.positionTab = PositionTab(self)
        self.imageViewTab = ImageViewTab(self)

    def setContext(self, image):
        self.cleanContext()
        self.positionTab.setPosSliders(image)
        self.imageViewTab.setAlpha(image)
        self.app.contentTabs.imagesTab.setIndexPhysSwitch()

    def cleanContext(self):
        self.positionTab.cleanPosSliders()
        self.imageViewTab.clean()
