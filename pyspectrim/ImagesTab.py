from pyspectrim.FilesTab import getObjectId

from pyspectrim.Image import Image

import tkinter as tk
from tkinter import ttk



class ImagesTab():

    imagesList = []

    def __init__(self, app):
        self.frame = tk.Frame(app.contentTabs)
        self.app = app;
        self.app.contentTabs.add(self.frame, text="Images")

        self.imagesTree = ttk.Treeview(self.frame)
        self.imagesTree.config(columns=('size'))

        self.imagesTree.column('#0', width=150)
        self.imagesTree.column('size', width=150)

        self.imagesTree.heading('#0', text='Name')
        self.imagesTree.heading('size', text='Size')

        self.imagesTree.pack()

    def insertImage(self, dataset):
        self.imagesList.append(Image(dataset))
        self.imagesTree.insert('','end', getObjectId(dataset), text=dataset.name)
        self.app.imagePanel.draw()


        # self.imagesTree.set('item1','size','128x128x25')