from pyspectrim.FileH5 import FileH5

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import h5py

class FilesTab:

    mountedFiles = []

    def __init__(self,app):
        self.frame = tk.Frame(app.contentTabs)
        app.contentTabs.add(self.frame, text="Files")

        self.filesTree = ttk.Treeview(self.frame)
        self.filesTree.config(columns=('size'))

        self.filesTree.column('#0', width=150)

        self.filesTree.heading('#0', text='Name')

        self.filesTree.bind("<Double-1>", self.OnDoubleClick)

        self.filesTree.pack()


    def mounth5dir(self,app):

        path = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("h5 files","*.h5"),))
        file = FileH5(app, path)

    def OnDoubleClick(self,event):
        item = self.filesTree.selection()[0]
        print("Clicked: ", item)
