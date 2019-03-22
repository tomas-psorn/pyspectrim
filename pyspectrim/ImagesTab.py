from pyspectrim.FilesTab import getObjectId
from pyspectrim.Image import Image
import tkinter as tk
from tkinter import ttk


class ImagesTab():

    imagesList = []
    imagesOnFocus = []

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


        self.imagesTree.popup_menu = tk.Menu(self.imagesTree, tearoff=0)
        self.imagesTree.popup_menu.add_command(label="Close", command=self.close)
        self.imagesTree.bind("<Button-3>", self.popup)


        self.imagesTree.pack()

    def insertImage(self, dataset):
        self.imagesList.append(Image(dataset))
        self.imagesTree.insert('','end', getObjectId(dataset), text=dataset.name)
        self.app.positionTab.drawPosSliders(self.imagesList[-1])
        self.app.imagePanel.draw()

    def OnClick(self, event):
        code = self.imagesTree.selection()[0]

        for image in self.imagesList:
            if code == image.tree_id:
                self.setContext(image)

    def close(self):
        code = self.imagesTree.selection()[0]
        self.app.positionTab.clean()
        self.imagesTree.delete(code)

    def popup(self, event):
        try:
            self.imagesTree.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.imagesTree.popup_menu.grab_release()
