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

        self.imagesTree.bind("<Button-1>", self.OnClick)

        self.imagesTree.pack()

    def insertImage(self, dataset):
        self.imagesList.append(Image(dataset))
        self.imagesTree.insert('','end', getObjectId(dataset), text=dataset.name)
        self.setContext(self.imagesList[-1] )
        self.app.imagePanel.draw()

    def OnClick(self, event):
        code = self.imagesTree.selection()[0]

        for image in self.imagesList:
            if code == image.tree_id:
                self.setContext(image)


    def setContext(self, image):
        self.app.positionTab.xscale.setPosition( image.pos_ind[0] )
        self.app.positionTab.yscale.setPosition( image.pos_ind[1] )
        self.app.positionTab.zscale.setPosition( image.pos_ind[2] )

        self.app.positionTab.xscale.setRange( image.from_ind[0], image.to_ind[0] )
        self.app.positionTab.yscale.setRange( image.from_ind[1], image.to_ind[1] )
        self.app.positionTab.zscale.setRange( image.from_ind[2], image.to_ind[2] )

        # self.imagesTree.set('item1','size','128x128x25')