from pyspectrim.File import getH5Id, Reco, Scan
from pyspectrim.Image import Image

import tkinter as tk
from tkinter import ttk

import logging

import numpy as np

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

        self.imagesTree.popup_menu = tk.Menu(self.imagesTree, tearoff=0)
        self.imagesTree.popup_menu.add_command(label="Encode visibility", command=self.encode_alpha)
        self.imagesTree.popup_menu.add_command(label="Reload", command=self.reload_image_data)
        self.imagesTree.popup_menu.add_separator()
        self.imagesTree.popup_menu.add_command(label="Set visible", command= lambda: self.set_im_vis(1.0))
        self.imagesTree.popup_menu.add_command(label="Set invisible", command= lambda: self.set_im_vis(0.0))
        self.imagesTree.popup_menu.add_separator()
        self.imagesTree.popup_menu.add_command(label="Close", command=self.close_image)
        self.imagesTree.bind("<Button-3>", self.popupContextMenu)

        self.imagesTree.pack()

    def encode_alpha(self,event):
        self.contentTabs.select(self)
        self.imagesTree.focus_set()
        self.imagesTree.focus(self.imagesTree.identify_row(event.y))
        for image in self.images_list:
            if image.tree_id == self.imagesTree.focus():
                encode_window = EncodeWindow(app=self.app, image=image)

    # getters
    def get_visible(self):
        return self.images_vis_list

    def insert_image(self, file=None, image_code=None):

        if file.__class__.__name__ == 'FileBruker':
            reco_code = image_code.split('.')[-1]
            reco_path = image_code[0:-len(reco_code)-1] # this is a robust way to cut the suffix, only the last dot split can be relied on

            if 'reco' in reco_code:
                image = Image(app=self.app, reco=Reco(path=reco_path), tree_id=image_code)
            elif 'proc' in reco_code:
                proc_code = reco_code
                reco_code = reco_path.split('.')[-1]
                reco_path = reco_path[0:-len(reco_code)-1]
                image = Image(app=self.app, reco=Reco(path=reco_path), proc_code=proc_code, tree_id=image_code)
            elif 'kspace' in reco_code:
                image = Image(app=self.app, scan=Scan(path=reco_path), tree_id=image_code)
            else:
                logging.debug('Problem with Bruker and image_code')
                return

        elif file.__class__.__name__ == 'FileHdf5':
            image = Image(app=self.app, dataset=file.get_dataset(code=image_code), tree_id=image_code)
        else:
            logging.debug('Unknown file class')

        self.images_list.append(image)
        self.images_vis_list.append(image)

        self.app.contentTabs.select(self)

        # Insert new image to images tree & configure
        image_id = image.tree_id
        image_name = image.tree_name

        self.imagesTree.insert('',tk.END, image_id, text=image_name)
        self.imagesTree.set(image_id, 'size',getImageSizeStr(image))
        self.imagesTree.set(image_id, 'dtype',image.data.dtype)
        self.imagesTree.set(image_id, 'visibility',image.isVisible())

        # Needs to be done first
        self.app.cinema.imagePanel.update_geometry()

        # Update context
        self.app.contextTabs.set_context_image(image=image)

        # Draw what's to be drawn
        self.app.cinema.imagePanel.draw()
        self.app.cinema.signalPanel.draw()

        # TODO this might not be neccessary
        self.imagesTree.selection_set(image_id)

    def on_click(self, event):
        self.app.contextTabs.set_context_image(image=self.get_clicked_on_image(event))

    def close_image(self):
        image = self.clicked_on_image
        code = image.tree_id

        if image in self.images_list:
            self.images_list.remove(image)
        if image in self.images_vis_list:
            self.images_vis_list.remove(image)
        # if image to be deleted was the one on focus, switch to other
        if image.tree_id == self.app.contextTabs.get_context_image().tree_id:
            if self.images_list:
                self.app.contextTabs.set_context_image(self.images_list[0])
                self.imagesTree.focus_set()
                self.imagesTree.focus(self.images_list[0].tree_id)
            else:
                self.app.contextTabs.free_context_image()
        del image


        logging.info("Image {} deleted from the list".format(code))

        self.imagesTree.delete(code)

        self.app.cinema.imagePanel.update_geometry()
        self.app.cinema.imagePanel.draw_empty()
        self.app.cinema.imagePanel.draw()
        self.app.cinema.signalPanel.draw_empty()
        self.app.cinema.signalPanel.draw()

        logging.info("Image {} deleted from the tree".format(code))

    def popupContextMenu(self, event):
        # all functions invoked by the menu, will have access to the image
        self.clicked_on_image = self.get_clicked_on_image(event)
        try:
            self.imagesTree.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.imagesTree.popup_menu.grab_release()

    # Context menu handle functions
    def get_clicked_on_image(self,event):
        self.contentTabs.select(self)
        self.imagesTree.focus_set()
        self.imagesTree.focus(self.imagesTree.identify_row(event.y))

        for image in self.images_list:
            if image.tree_id == self.imagesTree.focus():
                return image

    def set_im_vis(self, value):
        image = self.clicked_on_image

        image.visibility = value

        if value == 0.0:
            self.imagesTree.set(image.tree_id, 'visibility','False')
            if image in self.images_vis_list:
                self.images_vis_list.remove(image)
        else:
            self.imagesTree.set(image.tree_id, 'visibility', 'True')
            if image not in self.images_vis_list:
                self.images_vis_list.append(image)

        self.clicked_on_image = None

        self.app.cinema.imagePanel.draw()

    def dimConsistCheck(self):
        """
        :return: boolean value indicating whether the images in images_vis_list
        are geometrically consistent
        """
        for image1 in self.images_vis_list:
            for image2 in self.images_vis_list:
                if not np.array_equal(image1.dim_size, image2.dim_size):
                    return False
        return True

    def reload_image_data(self):
        image = self.clicked_on_image
        image.reload_data()
        self.app.contextTabs.update_context(image=image)
        self.app.cinema.imagePanel.draw()

        self.clicked_on_image = None

class EncodeWindow():
    def __init__(self, app=None, image=None):
        self.app = app
        self.image = image

        self.encode_window = tk.Tk()
        self.encode_window.wm_title("Encode visibility")
        self.encode_window.geometry('400x400')

        self.treeview_frame = tk.Frame(self.encode_window)
        self.treeview = ttk.Treeview(self.treeview_frame)
        self.treeview.config(columns=('image'))

        self.treeview.column('#0')


        self.treeview.heading('#0', text='Image')
        self.populate()

        self.treeview.bind("<Double-1>", self.on_double_click)

        self.treeview.pack()
        self.treeview_frame.pack()

        self.done_button = tk.Button(self.encode_window, text="Okay", command=self.encode_window.destroy)
        self.done_button.pack()

    def on_double_click(self,event):
        image_to_enc = self.get_image_on_focus()
        self.image.encode_visibility(image_to_enc=image_to_enc)
        self.app.cinema.imagePanel.draw()
        self.encode_window.destroy()

    def get_image_on_focus(self):
        for image in self.app.contentTabs.imagesTab.images_list:
            if image.tree_id == self.treeview.focus():
                return image
            elif image.tree_id == self.treeview.selection()[0] and len(self.treeview.selection()[0]) == 1:
                return image

    def populate(self):
        for image in self.app.contentTabs.imagesTab.images_list:
            if image.tree_id != self.image.tree_id and (image.dim_size[0:2] == self.image.dim_size[0:2]).all():
                self.treeview.insert('','end',image.tree_id,text=image.tree_name)
