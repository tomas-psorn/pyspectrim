from pyspectrim.FilesTab import getObjectId
from pyspectrim.Image import Image
import tkinter as tk
from tkinter import ttk

def getImageSizeStr(image):

    sizeStr = ''

    for dim in image.dim_size:
        sizeStr += str(dim)
        sizeStr += 'x'

    return sizeStr[:-1]


class ImagesTab(tk.Frame):

    imagesList = []
    imagesOnFocus = []

    def __init__(self, contentTabs):

        self.contentTabs = contentTabs
        self.app = self.contentTabs.app

        super().__init__(self.contentTabs)
        self.contentTabs.add(self, text="Images")

        self.imagesTree = ttk.Treeview(self)
        self.imagesTree.config(columns=('size','dtype','visibility'))

        self.imagesTree.column('#0', width=150)
        self.imagesTree.column('size', width=150)
        self.imagesTree.column('dtype', width=70)
        self.imagesTree.column('visibility', width=50)

        self.imagesTree.heading('#0', text='Name')
        self.imagesTree.heading('size', text='Size')
        self.imagesTree.heading('dtype', text='Data type')
        self.imagesTree.heading('visibility', text='Visible')

        self.imagesTree.bind("<Button-1>", self.OnClick)


        self.imagesTree.popup_menu = tk.Menu(self.imagesTree, tearoff=0)
        self.imagesTree.popup_menu.add_command(label="Set visible", command=self.setImageVisible)
        self.imagesTree.popup_menu.add_command(label="Set invisible", command=self.setImageInvisible)
        self.imagesTree.popup_menu.add_separator()
        self.imagesTree.popup_menu.add_command(label="Close", command=self.closeImage)
        self.imagesTree.bind("<Button-3>", self.popupContextMenu)

        self.imagesTree.pack()

    def insertImage(self, dataset):

        self.dataset = dataset

        # Insert new image to images list
        self.imagesList.append(Image(dataset))

        # Insert new image to images tree & configure
        objectId = getObjectId(dataset)
        self.imagesTree.insert('',tk.END, objectId, text=dataset.name)
        self.imagesTree.set(objectId, 'size',getImageSizeStr(self.imagesList[-1]))
        self.imagesTree.set(objectId, 'dtype',self.dataset.dtype)
        self.imagesTree.set(objectId, 'visibility',self.imagesList[-1].isVisible())
        self.imagesTree.selection_set(objectId)

        # Set focus
        self.setFocus(self.imagesList[-1])

        # Draw what's to be drawn
        self.app.cinema.imagePanel.draw()

    def OnClick(self, event):
        code = self.imagesTree.selection()[0]

        for image in self.imagesList:
            if code == image.tree_id:
                self.setFocus(image)

    def closeImage(self):
        code = self.imagesTree.selection()[0]
        self.app.contextTabs.cleanContext()

        for image in self.imagesList:
            if image.tree_id == code:
                self.imagesList.remove(image)
                print("Image ", code, " deleted from the list")

        self.imagesTree.delete(code)
        self.app.contextTabs.cleanContext()
        print("Image ", code, " deleted from the tree")

    def popupContextMenu(self, event):

        print(dir(self.imagesTree.selection()[0]))

        try:
            code = self.imagesTree.selection()[0]

        except IndexError:
            return


        try:
            self.imagesTree.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.imagesTree.popup_menu.grab_release()

    def setFocus(self, image):

        objectId = getObjectId(image)

        self.imagesTree.focus(objectId)
        self.app.contextTabs.cleanContext()
        self.app.contextTabs.setContext(image)

    # Context menu handle functions

    def setImageVisible(self):
        code = self.imagesTree.selection()[0]

        for image in self.imagesList:
            if image.tree_id == code:
                image.setVisible()

        self.app.contextTabs.setContext(image)
        self.imagesTree.set(code, 'visibility','True')

    def setImageInvisible(self):
        code = self.imagesTree.selection()[0]

        for image in self.imagesList:
            if image.tree_id == code:
                image.setInvisible()

        self.app.contextTabs.setContext(image)
        self.imagesTree.set(code, 'visibility','False')