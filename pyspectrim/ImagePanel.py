import tkinter as tk
from tkinter import ttk

from pyspectrim.Geometry import Plane2D
from pyspectrim.enums import *

from PIL import Image, ImageTk

import cv2

import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import logging


class ImagePanel():
    def __init__(self, **kwargs):

        self.cinema = kwargs['cinema']
        self.app = self.cinema.app

        # todo relate to window size
        self.max_dim = kwargs['max_dim']

        if 'fix_orient' in kwargs:
            self.fix_orient = kwargs['fix_orient']
        else:
            self.fix_orient = None

        self.init_geometry()

        self.frame = None

        # canvas is currently supposed to be square
        self.canvas = tk.Canvas(kwargs['frame'], bg='black')
        self.canvas.config(width=self.max_dim, height=self.max_dim)

    def init_geometry(self):
        self.center_x = int(self.max_dim/2)
        self.center_y = int(self.max_dim/2)

        self.space_from = np.empty(2, dtype=np.float32)
        self.space_to = np.empty(2, dtype=np.float32)

        self.plane_x = None
        self.plane_y = None


    def update_geometry(self):

        visible_images = self.app.contentTabs.imagesTab.get_visible()

        if visible_images:
            image = visible_images[0]
            ind_phys_switch = self.app.contextTabs.imageViewTab.indPhysSwitch.get()

            if ind_phys_switch == IND_PHYS.IND.value:
                self.space_from[0] = -0.5
                self.space_from[1] = -0.5

                self.space_to[0] = 0.5
                self.space_to[1] = 0.5
            else :
                max_ext_ind = np.where(image.dim_phys_extent == np.amax(image.dim_phys_extent))

                self.space_from[0] = image.dim_from_phys[max_ext_ind]
                self.space_from[1] = image.dim_from_phys[max_ext_ind]

                self.space_to[0] = image.dim_to_phys[max_ext_ind]
                self.space_to[1] = image.dim_to_phys[max_ext_ind]

            x_axis = np.linspace(self.space_from[0], self.space_to[0], self.max_dim)
            y_axis = np.linspace(self.space_from[1], self.space_to[1], self.max_dim)

            self.plane_x, self.plane_y = np.meshgrid(x_axis,y_axis)

        else:
            self.init_geometry()

    def get_frame(self, image=None):
        """
        If anny external entity, histogram for instance, wishes to access the same frame, as displayed.
        :param image:
        :return:
        """
        if self.fix_orient is not None:
            orient = self.fix_orient
        else:
            orient = self.app.contextTabs.imageViewTab.view_orient_switch.get()

        if orient == VIEW_ORIENT.TRANS.value:
            return image.get_frame(orient=VIEW_ORIENT.TRANS.value, querry_x = self.plane_x, querry_y = self.plane_y)
        elif orient == VIEW_ORIENT.SAG.value:
            return image.get_frame(orient=VIEW_ORIENT.SAG.value, querry_x = self.plane_x, querry_y = self.plane_y)
        elif orient == VIEW_ORIENT.CORR.value:
            return image.get_frame(orient=VIEW_ORIENT.CORR.value, querry_x = self.plane_x, querry_y = self.plane_y)

    def draw(self):
        self.frame = Image.new('RGB', (self.max_dim, self.max_dim))

        imagesList = self.app.contentTabs.imagesTab.get_visible()

        # If images list is empty
        if not imagesList:
            self.draw_empty()
            return

        frames = []
        alphas = []


        for image in imagesList:
            alphas.append(image.visibility)
            frames.append(self.get_frame(image=image))

        for frame_, alpha_ in zip(frames, alphas):
            frame_ = cv2.cvtColor(frame_.astype(np.uint8), cv2.COLOR_BGR2RGB)
            frame_ = Image.fromarray(frame_)
            self.frame = Image.blend(self.frame, frame_, alpha=alpha_)

        self.frame_tk = ImageTk.PhotoImage(self.frame)
        self.canvas.create_image(self.center_x, self.center_y,image = self.frame_tk)

        self.canvas.grid(column=0, row=0)

    def draw_empty(self):
        """
        Clear self.canvas
        :return:
        """
        self.canvas.delete("all")


class ImagePanelMain(ImagePanel):
    def __init__(self, **kwargs):
        super(ImagePanelMain, self).__init__(**kwargs)

        self.popup_menu = tk.Menu(self.canvas, tearoff=0)
        self.popup_menu.add_command(label="Reset", command=self.reset_view)
        self.popup_menu.add_command(label="Save as", command=self.save_view)

        self.canvas.bind("<Button-3>", self.popup_context_menu)
        self.canvas.bind("<MouseWheel>", self.on_scroll)
        self.canvas.bind("<Button-1>", self.set_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag)

    def popup_context_menu(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.popup_menu.grab_release()

    def reset_view(self):
        self.update_geometry()
        self.draw()

    def save_view(self):

        filename = tk.filedialog.asksaveasfile(defaultextension=".png")
        self.frame.save(filename.name)


    def on_scroll(self, event):
        if event.delta > 0:
            self.zoom(zoom=1.1)
        elif event.delta < 0:
            self.zoom(zoom=0.9)

    def zoom(self, zoom=None):
        self.space_from *= zoom
        self.space_to *= zoom

        self.plane_x *= zoom
        self.plane_y *= zoom

        self.draw()

    def set_drag_start(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def on_drag(self, event):
        # diff_x = (self.drag_start_x - event.x)
        # diff_y = (self.drag_start_y - event.y)
        spacing = (self.plane_x[0,1] - self.plane_x[0,0])

        print(spacing)

        self.pane(x=event.x, y=event.y)


    def pane(self, x=None, y=None):
        self.space_from[0] += x
        self.space_from[1] += y

        self.space_to[0] += x
        self.space_to[1] += y

        for i in range(0,self.max_dim):
            self.plane_x[i,:] += x

        # self.plane_x += x
        # self.plane_y += y
        self.draw()

    def update_info(self, x=None, y=None):
        orient = self.app.contextTabs.imageViewTab.view_orient_switch.get()

        image = self.app.contextTabs.get_context_image()

        labels, pos_phys, units = image.get_pixel_info(x=x, y=y, orient=orient)

        text = ''

        for label, phys, unit in zip(labels, pos_phys, units):
            try:
                text += '{}: {:.2f} {} \n'.format(label, phys, unit)
            except:
                text += '{}: {} {} \n'.format(label, phys, unit)

        self.info_text_id = self.canvas.create_text(10, 10, fill="white", text='', anchor=tk.N + tk.W)
        self.canvas.itemconfig(self.info_text_id, text=text)
        self.canvas.tag_raise(self.info_text_id)

    def imspace_gridspace(self,x_im,y_im):
        x = 0
        y = 0
        for i in range(0, self.plane_x.shape[1]):
            if self.plane_x[0, i] > x_im:
                x=i

        for i in range(0, self.plane_y.shape[0]):
            if self.plane_y[i, 0] > y_im:
                y=i

        return x,y

class ImagePanelOrtho(ImagePanel):
    def __init__(self, **kwargs):
        super(ImagePanelOrtho, self).__init__(**kwargs)

    def draw_navig_cross(self):
        image = self.app.contextTabs.get_context_image()
        # x,y,z = image.get_location_low()
        # x,y = self.imspace_gridspace(x_im, y_im)
        # self.horizontal_line = self.canvas.create_line(0, y, self.max_dim, y, fill='blue', width=2)
        # self.vertical_line = self.canvas.create_line(x,0,x, self.max_dim, fill='blue', width=2)


    def draw_horizontal(self, image):
        pass

