from pyspectrim.FileH5 import FileH5

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import h5py

class FilesTab:

    filesList = []

    def __init__(self,app):

        self.app = app
        self.frame = tk.Frame(self.app.contentTabs)
        self.app.contentTabs.add(self.frame, text="Files")

        self.filesTree = ttk.Treeview(self.frame)
        self.filesTree.config(columns=('size'))

        self.filesTree.column('#0', width=150)

        self.filesTree.heading('#0', text='Name')

        self.filesTree.bind("<Double-1>", self.OnDoubleClick)

        self.filesTree.pack()


    def mounth5dir(self,app):
        path = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("h5 files","*.h5"),))
        self.filesList.append(FileH5(app, path))


    def OnDoubleClick(self,event):
        code = self.filesTree.selection()[0]
        self.app.imagesTab.insertImage(self.GetDataset(code))

    def GetDataset(self, code):
        for _file in self.filesList:
            pathNoExtension = _file.path.rsplit('.',1)[0]
            pathIntra = code.replace(pathNoExtension,'')

            if pathNoExtension in code:
                return _file.file[pathIntra];
            else:
                return -1

