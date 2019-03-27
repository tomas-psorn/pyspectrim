from pyspectrim.File import File

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

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


class FilesTab(tk.Frame):

    filesList = []

    def __init__(self, contentTabs):

        self.contentTabs = contentTabs
        self.app = self.contentTabs.app

        super().__init__(self.contentTabs)
        self.contentTabs.add(self, text="Files")

        # init tree
        self.filesTree = ttk.Treeview(self)
        self.filesTree.config(columns=('size'))

        self.filesTree.column('#0', width=150)

        self.filesTree.heading('#0', text='Name')

        self.filesTree.bind("<Double-1>", self.OnDoubleClick)

        # init context menu
        self.filesTree.popup_menu = tk.Menu(self.filesTree, tearoff=0)

        self.filesTree.popup_menu.add_command(label="Mount H5 file", command= lambda: self.mounth5dir(self.app))
        self.filesTree.popup_menu.add_command(label="Close", command=self.closeFile)
        self.filesTree.bind("<Button-3>", self.popupContextMenu)


        self.filesTree.pack()


    # event handlers

    def mounth5dir(self,app):
        path = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("h5 files","*.h5"),))
        self.filesList.append(File(app, path))
        self.addEntry(self.filesList[-1],"")
        self.app.contentTabs.select(self.contentTabs.filesTab)

    def OnDoubleClick(self,event):
        code = self.filesTree.selection()[0]

        # insert image
        self.app.contentTabs.imagesTab.insertImage(self.GetDataset(code))

        # Switch tab to images in content section
        self.app.contentTabs.select(self.contentTabs.imagesTab)

    def popupContextMenu(self, event):

        try:
            self.filesTree.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.filesTree.popup_menu.grab_release()

    def closeFile(self):
        pass

    def GetDataset(self, code):
        for _file in self.filesList:
            pathNoExtension = _file.filename.rsplit('.',1)[0]
            pathIntra = code.replace(pathNoExtension,'')

            if pathNoExtension in code:
                return _file.file[pathIntra]
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





