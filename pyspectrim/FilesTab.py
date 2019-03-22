# from pyspectrim.FileH5 import FileH5
from pyspectrim.File import File

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import h5py

from os.path import basename

def getObjectId(object):
    if object.__class__.__name__ == 'File':
        return object.filename.rsplit('.',1)[0]
    elif object.__class__.__name__ == 'Group':
        return object.file.filename.rsplit('.',1)[0]  + object.name
    elif object.__class__.__name__ == 'Dataset':
        return object.file.filename.rsplit('.',1)[0]  + object.name


def getObjectName(object):
    if object.__class__.__name__ == 'File':
        return basename(object.filename)
    elif object.__class__.__name__ == 'Group':
        return object.name
    elif object.__class__.__name__ == 'Dataset':
        return object.name


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
        self.filesList.append(File(app, path))
        self.addEntry(self.filesList[-1],"")

    def OnDoubleClick(self,event):
        code = self.filesTree.selection()[0]
        self.app.imagesTab.insertImage(self.GetDataset(code))


    def GetDataset(self, code):
        for _file in self.filesList:
            pathNoExtension = _file.filename.rsplit('.',1)[0]
            pathIntra = code.replace(pathNoExtension,'')

            if pathNoExtension in code:
                return _file.file[pathIntra];
            else:
                return -1

    def addEntry(self, object, parentId):
        if parentId == "":
            self.filesTree.insert("", "end", getObjectId(object), text=getObjectName(object))
        else:
            self.filesTree.insert(parentId, "end", getObjectId(object), text=getObjectName(object))

        if object.__class__.__name__ != 'Dataset':
            for key in object.keys():
                self.addEntry(object[key], getObjectId(object))





