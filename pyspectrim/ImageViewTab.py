import tkinter as tk
from tkinter import ttk


class ImageViewTab(tk.Frame):
    def __init__(self, contextTabs):
        self.app = contextTabs.app
        self.contextTabs = contextTabs

        super().__init__(self.contextTabs)
        self.contextTabs.add(self, text="Image view")

        self.alphaSlider = AlphaSlider(self)


class AlphaSlider(tk.Scale):
    def __init__(self, tab):

        self.tab = tab
        self.app = tab.app

        self.value = tk.DoubleVar
        self.layout = tk.LabelFrame(self.tab, text='Visibility')

        super().__init__(self.layout, variable=self.value ,orient=tk.HORIZONTAL, length = 250, from_= 0.0, to=1.0)
        self.set(1.0)

        self.pack()
        self.layout.pack()

