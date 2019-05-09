import tkinter as tk
from tkinter import ttk

from enum import Enum


class SignalViewTab(tk.Frame):
    def __init__(self, contextTabs):
        self.app = contextTabs.app
        self.contextTabs = contextTabs

        super().__init__(self.contextTabs)
        self.contextTabs.add(self, text="Signal")

    def set_defaults(self):
        pass

    def set_context(self, image=None):
        pass
