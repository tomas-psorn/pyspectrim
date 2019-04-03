from pyspectrim.File import File, getH5Id, getH5Name

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import logging

class FilesTab(tk.Frame):



    def __init__(self, contentTabs):

        self.filesList = []

        self.contentTabs = contentTabs
        self.app = contentTabs.app

        super().__init__(self.contentTabs)
        self.contentTabs.add(self, text="Files")

        # init tree
        self.filesTree = ttk.Treeview(self)
        self.filesTree.config(columns=('size'))

        self.filesTree.column('#0', width=150)

        self.filesTree.heading('#0', text='Name')

        self.filesTree.bind("<Double-1>", self.on_double_click)
        self.filesTree.bind("<Button-1>", self.on_left_click)
        self.filesTree.bind("<Button-3>", self.on_right_click)

        # init context menu
        self.filesTree.popup_on_file = tk.Menu(self.filesTree, tearoff=0)
        self.filesTree.popup_on_file.add_command(label="Mount H5 file", command=self.mount_h5_dir)
        self.filesTree.popup_on_file.add_command(label="Close", command=self.close_file)

        self.filesTree.popup_on_blank = tk.Menu(self.filesTree, tearoff=0)
        self.filesTree.popup_on_blank.add_command(label="Mount H5 file", command=self.mount_h5_dir)

        self.filesTree.pack()


    # event handlers
    def on_right_click(self, event):
        item = self.filesTree.identify_row(event.y)
        if item != '':
            self.filesTree.selection_set(item)
            self.filesTree.focus(item)
            self.popup_on_file(event)
        else:
            self.poup_on_blank(event)

    def on_left_click(self,event):
        if self.filesTree.identify_row(event.y) == '':
            self.filesTree.selection_remove(self.filesTree.selection())

    def on_double_click(self,event):
        code = self.filesTree.selection()[0]

        # insert image
        dataset = self.GetDataset(code.replace(".h5",""))

        if dataset:
            self.app.contentTabs.imagesTab.insertImage(dataset)
        else:
            return

        # Switch tab to images in content section
        self.app.contentTabs.select(self.contentTabs.imagesTab)

    # poups
    def popup_on_file(self, event):
        try:
            self.filesTree.popup_on_file.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.filesTree.popup_on_file.grab_release()

    def poup_on_blank(self,event):
        try:
            self.filesTree.popup_on_blank.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.filesTree.popup_on_blank.grab_release()

    #
    def close_file(self):
        file_code = self.filesTree.focus()

        for file in self.filesList:
            if file_code == file.filename:
                try:
                    self.filesList.remove(file)
                    logging.debug("Removed file from files list {}".format(file_code))
                except:
                    logging.warning("Failed to remove file from files list {}".format(file_code))
                    return

                try:
                    self.filesTree.delete(file_code)
                    logging.debug("Removed file from files tree {}".format(file_code))
                except:
                    logging.warning("Failed to remove file from files tree {}".format(file_code))
                    return



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

    def mount_h5_dir(self):
        path = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("h5 files","*.h5"),))


        logging.info("Mounting: {}".format(path))

        try:
            self.filesList.append(File(self.app, path))
        except:
            logging.info("File not mounted: {}".format(path))
            return

        try:
            self.addEntry(self.filesList[-1],"")
        except:
            logging.debug("File cannot be added into files list: {}".format(path))
            self.filesList = self.filesList[0:-1]
            return

        logging.info("Mounted: {}".format(path))

        self.app.contentTabs.select(self.contentTabs.filesTab)





