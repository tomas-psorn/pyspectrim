import tkinter as tk
from tkinter import ttk

from os.path import basename

import h5py



class FileH5():

    children = []

    def __init__(self, app, path):
        self.path = path
        self.filename = basename(path)

        self.file = h5py.File(self.path,'r')

        self.root = GroupH5(self, app, self.file)


        # self.root = GroupH5(self, self.file)

        # for item in self.file:
        #     self.procItemH5(self.file[item])


class GroupH5():
    def __init__(self, fileH5, app, item):
        self.absPath = fileH5.path# get path without extension
        self.id = self.absPath.rsplit('.',1)[0]  + item.name
        self.parent = self.absPath.rsplit('.',1)[0] + item.parent.name

        if item.__class__.__name__ == "File":
            app.filesTab.filesTree.insert("","end",self.id,text=basename(fileH5.path), image=app.icons['folder'])
        else:
            app.filesTab.filesTree.insert(self.parent,"end",self.id,text=item.name[1:], image=app.icons['folder'])

        for key in item.keys():
            if item[key].__class__.__name__ == "Group":
                GroupH5(fileH5,app,item[key])
            elif item[key].__class__.__name__ == "Dataset":
                DatasetH5(fileH5,app, item[key])

class DatasetH5():
    def __init__(self, fileH5, app, item):
        self.absPath = fileH5.path # get path without extension
        self.id = self.absPath.rsplit('.',1)[0] + item.name
        self.parent = self.absPath.rsplit('.',1)[0] + item.parent.name
        app.filesTab.filesTree.insert(self.parent,"end",self.id,text=item.name.rsplit('/',1)[1], image=app.icons['folder'])



