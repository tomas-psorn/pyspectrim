from pyspectrim.File import File, getH5Id, getH5Name

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog


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
    def OnDoubleClick(self,event):
        code = self.filesTree.selection()[0]

        # insert image
        dataset = self.GetDataset(code)

        if dataset:
            self.app.contentTabs.imagesTab.insertImage(dataset)
        else:
            return

        # Switch tab to images in content section
        self.app.contentTabs.select(self.contentTabs.imagesTab)

    def popupContextMenu(self, event):
        try:
            self.filesTree.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.filesTree.popup_menu.grab_release()

    def closeFile(self):
        pass

    # uncategorized functionality
    def GetDataset(self, code):
        for _file in self.filesList:
            pathNoExtension = _file.filename.rsplit('.',1)[0]
            pathIntra = code.replace(pathNoExtension,'')

            if pathNoExtension in code:
                if  _file.file[pathIntra].__class__.__name__ == 'Dataset':
                    return _file.file[pathIntra]
                else:
                    return None
            else:
                return None

    def addEntry(self, object, parentId):
        if parentId == "":
            self.filesTree.insert("", "end", getH5Id(object), text=getH5Name(object))
        else:
            self.filesTree.insert(parentId, "end", getH5Id(object), text=getH5Name(object))

        if object.__class__.__name__ != 'Dataset':
            for key in object.keys():
                self.addEntry(object[key], getH5Id(object))

    def mounth5dir(self,app):
        path = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("h5 files","*.h5"),))
        self.filesList.append(File(app, path))
        self.addEntry(self.filesList[-1],"")
        self.app.contentTabs.select(self.contentTabs.filesTab)



