from pyspectrim.File import getH5Id
from pyspectrim.Image import Image
import tkinter as tk
from tkinter import ttk

import logging

import gc

def getImageSizeStr(image):

    sizeStr = ''

    for dim in image.dim_size:
        sizeStr += str(dim)
        sizeStr += 'x'

    return sizeStr[:-1]


class ImagesTab(tk.Frame):

    def __init__(self, contentTabs):

        self.images_list = []
        self.images_vis_list = []

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

        self.imagesTree.bind("<Button-1>", self.on_click)
        self.imagesTree.bind("<Key>", self.on_key_enter)

        self.imagesTree.popup_menu = tk.Menu(self.imagesTree, tearoff=0)
        self.imagesTree.popup_menu.add_command(label="Reload", command=self.reload_image_data)
        self.imagesTree.popup_menu.add_separator()
        self.imagesTree.popup_menu.add_command(label="Set visible", command= lambda: self.set_im_vis(1.0))
        self.imagesTree.popup_menu.add_command(label="Set invisible", command= lambda: self.set_im_vis(0.0))
        self.imagesTree.popup_menu.add_separator()
        self.imagesTree.popup_menu.add_command(label="Close", command=self.close_image)
        self.imagesTree.bind("<Button-3>", self.popupContextMenu)

        self.imagesTree.pack()

    # getters
    def get_visible(self):
        return self.images_vis_list

    def get_image_on_focus(self):
        for image in self.images_list:
            if image.tree_id == self.imagesTree.focus():
                return image
            elif image.tree_id == self.imagesTree.selection()[0] and len(self.imagesTree.selection()[0]) == 1:
                return image

    # setters
    def set_image_on_focus(self, image):
        self.imagesTree.focus(image.tree_id)
        self.app.contextTabs.update_context()

    def insertImage(self, image_code, dataset):

        if dataset.__class__.__name__ == 'Dataset':
            self.dataset = dataset
        else:
            return

        # Insert new image to images list
        self.images_list.append(Image(self.app,dataset))
        self.images_vis_list.append(self.images_list[-1])
        self.setIndexPhysSwitch()

        self.app.contentTabs.select(self)

        # Insert new image to images tree & configure
        objectId = getH5Id(dataset)
        self.imagesTree.insert('',tk.END, objectId, text=dataset.name)
        self.imagesTree.set(objectId, 'size',getImageSizeStr(self.images_list[-1]))
        self.imagesTree.set(objectId, 'dtype',self.dataset.dtype)
        self.imagesTree.set(objectId, 'visibility',self.images_list[-1].isVisible())
        self.imagesTree.selection_set(objectId)
        self.set_image_on_focus(self.images_list[-1])

        # Draw what's to be drawn
        self.app.cinema.imagePanel.draw()

    # Handlers
    def on_key_enter(self,event):
        if event.keysym == 'Delete':
            self.closeImage()

    def on_click(self, event):
        self.contentTabs.select(self)
        self.imagesTree.focus_set()
        self.imagesTree.focus(self.imagesTree.identify_row(event.y))
        # self.imagesTree.selection_add(self.imagesTree.identify_row(event.y))
        # self.set_image_on_focus(image)
        self.app.contextTabs.update_context()

    def close_image(self):

        code = self.imagesTree.selection()[0]


        for image in self.images_list:
            if image.tree_id == code:
                if image in self.images_list:
                    self.images_list.remove(image)
                if image in self.images_vis_list:
                    self.images_vis_list.remove(image)
                del image

                logging.info("Image {} deleted from the list".format(code))


        self.imagesTree.delete(code)
        self.app.contextTabs.update_context()
        self.app.cinema.imagePanel.draw()
        logging.info("Image {} deleted from the tree".format(code))


    def popupContextMenu(self, event):
        try:
            code = self.imagesTree.selection()[0]
        except IndexError:
            return

        try:
            self.imagesTree.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.imagesTree.popup_menu.grab_release()



    # Context menu handle functions

    def set_im_vis(self, value):
        code = self.imagesTree.selection()[0]
        for image in self.images_list:
            if image.tree_id == code:
                image.visibility = value

                if value == 0.0:
                    self.imagesTree.set(code, 'visibility','False')
                    if image in self.images_vis_list:
                        self.images_vis_list.remove(image)
                else:
                    self.imagesTree.set(code, 'visibility', 'True')
                    if image not in self.images_vis_list:
                        self.images_vis_list.append(image)

        self.app.contextTabs.update_context()
        self.app.cinema.imagePanel.draw()


    def setIndexPhysSwitch(self):
        if self.dimConsistCheck():
            self.app.contextTabs.imageViewTab.setIndPhys('ind')
        else:
            self.app.contextTabs.imageViewTab.lockIndPhysSwitch(True)
            self.app.contextTabs.imageViewTab.setIndPhys('phys')


    def dimConsistCheck(self):
        """
        :return: boolean value indicating whether the images in images_vis_list
        are geometrically consistent
        """
        for image1 in self.images_vis_list:
            for image2 in self.images_vis_list:
                if image1.dim_size != image2.dim_size:
                    return False
        return True


    def reload_image_data(self):
        image = self.get_image_on_focus()
        image.reload_data()
        self.app.contextTabs.update_context()
        self.app.cinema.imagePanel.draw()
