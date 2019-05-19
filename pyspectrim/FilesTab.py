from pyspectrim.File import FileHdf5, getH5Id, getH5Name, FileBruker, Scan, Reco

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
        image_code = self.filesTree.selection()[0]

        for file in self.filesList:
            if file.file_tree_id in image_code:
                self.app.contentTabs.imagesTab.insert_image(file=file, image_code=image_code)

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

        logging.info("Closing file: {}".format(file_code))

        for file in self.filesList:
            # first condition is for hdf5 second for bruker, the options are mutualy exclusive
            if file_code == file.filename or file_code == file.filename._str:

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

        logging.info("File closed")

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

        logging.info("Mounting: {}".format(path))

        self.filesList.append(FileBruker(app=self.app, path=path))
        self.add_tree_entry_bruker(file=self.filesList[-1])

        # try:
        #     self.filesList.append(FileBruker(app=self.app, path=path))
        #     logging.info("File mounted")
        # except:
        #     logging.info("File not mounted: {}".format(path))
        #     return
        #
        # try:
        #     self.add_tree_entry_bruker(file=self.filesList[-1])
        # except:
        #     logging.debug("File cannot be added into files list: {}".format(path))
        #     self.filesList = self.filesList[0:-1]
        #     return

    def add_tree_entry_bruker(self, file=None):

        file_tree_id = file.filename._str
        file_tree_name = file.filename.name

        self.filesTree.insert("", "end", file_tree_id, text=file_tree_name, image=self.app.bruker_icon)

        for scan_path in file.scan_paths:
            scan = Scan(path=scan_path, readFid=False)

            scan_tree_id = scan.path._str
            scan_tree_name = '\{}_{}'.format(scan.path.name,scan.acqp['PULPROG'].replace('.ppg',''))  # it is to be similar to HDF5 entry

            # add experiment level entry
            self.filesTree.insert(file_tree_id, "end", scan_tree_id, text=scan_tree_name)

            # add k-space to experiment
            self.filesTree.insert(scan_tree_id, "end", '{}.kspace'.format(scan_tree_id), text='kspace')

            reco_paths = listdir(scan_path / 'pdata')

            for reco_path in reco_paths:
                reco = Reco(path=scan_path / 'pdata' / reco_path, read2dseq=False)

                if not reco.isVisu:
                    return

                reco_tree_id = reco.path._str


                if reco.visu_pars['VisuSeriesTypeId'] == 'DERIVED_ISA':
                    for i in range(0,reco.visu_pars['VisuFGOrderDescDim']):
                        if reco.visu_pars['VisuFGOrderDesc'][i][1] == 'FG_ISA':
                            for proc_ind in range(reco.visu_pars['VisuFGOrderDesc'][i][0]):
                                reco_tree_id_ = '{}.reco_{}.proc_{}'.format(reco_tree_id, reco.path.name,proc_ind)
                                reco_tree_name = 'reco_{}_{}'.format(reco.path.name,reco.visu_pars['VisuFGElemComment'][proc_ind])
                                self.filesTree.insert(scan_tree_id, "end", reco_tree_id_, text=reco_tree_name)

                else:
                    reco_tree_id_ = '{}.reco_{}'.format(reco_tree_id, reco.path.name)
                    reco_tree_name = 'reco_{}'.format(reco.path.name)
                    self.filesTree.insert(scan_tree_id, "end", reco_tree_id_, text=reco_tree_name)










