from pyspectrim.File import FileHdf5, getH5Id, getH5Name, FileBruker, Scan

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import logging

from os import listdir

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
        self.filesTree.popup_on_file.add_command(label="Mount Bruker file", command=self.mount_bruker_dir)
        self.filesTree.popup_on_file.add_command(label="Close", command=self.close_file)

        self.filesTree.popup_on_blank = tk.Menu(self.filesTree, tearoff=0)
        self.filesTree.popup_on_blank.add_command(label="Mount H5 file", command=self.mount_h5_dir)
        self.filesTree.popup_on_blank.add_command(label="Mount Bruker file", command=self.mount_bruker_dir)

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
        dataset_code = self.filesTree.selection()[0]
        dataset = self.GetDataset(dataset_code.replace(".h5", ""))
        self.app.contentTabs.imagesTab.insertImage(dataset_code, dataset)

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

    def add_tree_entry_hdf5(self, object, parentId):
        if parentId == "":
            self.filesTree.insert("", "end", getH5Id(object), text=getH5Name(object), image=self.app.hdf_icon)
        else:
            self.filesTree.insert(parentId, "end", getH5Id(object), text=getH5Name(object))

        if object.__class__.__name__ != 'Dataset':
            for key in object.keys():
                self.add_tree_entry_hdf5(object[key], getH5Id(object))

    def mount_h5_dir(self):
        path = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("h5 files","*.h5"),))

        logging.info("Mounting: {}".format(path))

        try:
            self.filesList.append(FileHdf5(self.app, path))
        except:
            logging.info("File not mounted: {}".format(path))
            return

        try:
            self.add_tree_entry_hdf5(self.filesList[-1],"")
        except:
            logging.debug("File cannot be added into files list: {}".format(path))
            self.filesList = self.filesList[0:-1]
            return

        logging.info("Mounted: {}".format(path))

        self.app.contentTabs.select(self.contentTabs.filesTab)

    def mount_bruker_dir(self):
        path = filedialog.askdirectory(initialdir="/", title="Select directory")

        file = FileBruker(app=self.app, path=path)

        self.add_tree_entry_bruker(file=file)

    def add_tree_entry_bruker(self, file=None):
        self.filesTree.insert("", "end", file.path.name, text=file.path.name, image=self.app.bruker_icon)

        for folder in file.folders:
            scan = Scan(path=folder, readFid=False)

            # add experiment level entry
            self.filesTree.insert(file.path.name, "end", folder, text='\{}_{}'.format(folder.name,scan.acqp['PULPROG'].replace('.ppg','')))

            # add k-space to experiment
            self.filesTree.insert(folder, "end", '{}.kspace'.format(folder), text='kspace')

            recos = listdir(folder / 'pdata')







