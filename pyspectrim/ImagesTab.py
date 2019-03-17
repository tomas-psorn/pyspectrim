import tkinter as tk
from tkinter import ttk



class ImagesTab():

    imagesList = []

    def __init__(self, app):
        self.frame = tk.Frame(app.contentTabs)
        app.contentTabs.add(self.frame, text="Images")

        self.imagesTree = ttk.Treeview(self.frame)
        self.imagesTree.config(columns=('size'))

        self.imagesTree.column('#0', width=150)
        self.imagesTree.column('size', width=150)

        self.imagesTree.heading('#0', text='Name')
        self.imagesTree.heading('size', text='Size')

        self.imagesTree.pack()

    def insertImage(self, datasetH5):
        self.imagesTree.insert('','end',datasetH5.id, text=datasetH5.name)
        self.imagesList.append(datasetH5);
        print(dir(datasetH5))

        # self.imagesTree.set('item1','size','128x128x25')