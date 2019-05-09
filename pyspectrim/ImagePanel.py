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
    def __init__(self, cinema):

        self.cinema = cinema
        self.app = self.cinema.app

        # todo relate to window size
        self.max_dim = 400

        # used to fit the biggest dimension of any frame to max dim
        self.global_scale = 1.0

        self.init_geometry()

        self.frame = None

        # canvas is currently supposed to be square
        self.canvas = tk.Canvas(self.cinema, bg='black')
        self.canvas.config(width=self.max_dim, height=self.max_dim)

        self.popup_menu = tk.Menu(self.canvas, tearoff=0)
        self.popup_menu.add_command(label="Reset", command=self.reset_view)

        self.canvas.bind("<Button-3>", self.popup_context_menu)
        self.canvas.bind("<MouseWheel>", self.on_scroll)
        self.canvas.bind("<Button-1>", self.set_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag)

        # reference to text object indicating position and a value of pixel
        self.canvas.grid(column=0, row=0)

    def popup_context_menu(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.popup_menu.grab_release()

    def reset_view(self):
        self.update_geometry()
        self.draw()

    def on_scroll(self, event):
        zoom_ = 1.0 + 5/event.delta
        self.zoom(zoom=zoom_)

    def zoom(self, zoom=None):
        self.extent_from_phys *= zoom
        self.extent_to_phys *= zoom

        self.x_axis *= zoom
        self.y_axis *= zoom
        self.z_axis *= zoom

        self.draw()

    def set_drag_start(self,event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def on_drag(self, event):
        diff_x = (self.drag_start_y - event.y) / self.max_dim
        diff_y = (self.drag_start_x - event.x) / self.max_dim

        orient = self.app.contextTabs.imageViewTab.view_orient_switch.get()

        if orient == VIEW_ORIENT.TRANS.value:
            self.pane(x=diff_x, y=diff_y, z=0.0)
        elif orient == VIEW_ORIENT.SAG.value:
            self.pane(x=0.0, y=diff_x, z=diff_y)
        elif orient == VIEW_ORIENT.TRANS.value:
            self.pane(x=diff_x, y=0.0, z=diff_y)

    def pane(self,x=None, y=None, z=None):
        self.extent_from_phys[0] += x
        self.extent_from_phys[1] += y
        self.extent_from_phys[2] += z

        self.extent_to_phys[0] += x
        self.extent_to_phys[1] += y
        self.extent_to_phys[2] += z

        self.x_axis += x
        self.y_axis += y
        self.z_axis += z

        self.draw()


    def init_geometry(self):
        self.center_x = int(self.max_dim/2)
        self.center_y = int(self.max_dim/2)

        self.extent_from_phys = np.empty(3, dtype=np.float32)
        self.extent_to_phys = np.empty(3, dtype=np.float32)

        self.x_axis = None
        self.y_axis = None
        self.z_axis = None

        self.plane_xy = None
        self.plane_yz = None
        self.plane_xz = None

    def update_geometry(self):
        image = self.app.contentTabs.imagesTab.get_visible()[0]
        ind_phys_switch = self.app.contextTabs.imageViewTab.indPhysSwitch.get()

        if ind_phys_switch == IND_PHYS.IND.value:
            self.extent_from_phys[0] = -0.5
            self.extent_from_phys[1] = -0.5
            self.extent_from_phys[2] = -0.5

            self.extent_to_phys[0] = 0.5
            self.extent_to_phys[1] = 0.5
            self.extent_to_phys[2] = 0.5
        else :
            self.extent_from_phys[0] = image.dim_from_phys[0]
            self.extent_from_phys[1] = image.dim_from_phys[1]
            self.extent_from_phys[2] = image.dim_from_phys[2]

            self.extent_to_phys[0] = image.dim_to_phys[0]
            self.extent_to_phys[1] = image.dim_to_phys[1]
            self.extent_to_phys[2] = image.dim_to_phys[2]

        self.x_axis = np.linspace(self.extent_from_phys[0], self.extent_to_phys[0], self.max_dim)
        self.y_axis = np.linspace(self.extent_from_phys[1], self.extent_to_phys[1], self.max_dim)
        self.z_axis = np.linspace(self.extent_from_phys[2], self.extent_to_phys[2], self.max_dim)

        # self.plane_xy = Plane2D(x_axis=self.x_axis, y_axis=self.y_axis)
        # self.plane_yz = Plane2D(x_axis=self.y_axis, y_axis=self.z_axis)
        # self.plane_xz = Plane2D(x_axis=self.x_axis, y_axis=self.z_axis)

    # event handlers
    def update_info(self, x=None, y=None):
        orient = self.app.contextTabs.imageViewTab.get_view_orient()

        image = self.app.contentTabs.imagesTab.get_image_on_focus()
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

    def get_frame(self, image=None, orient=None):
        """
        If anny external entity, histogram for instance, wishes to access the same frame, as displayed.
        :param image:
        :return:
        """
        if orient is None:
            orient = self.app.contextTabs.imageViewTab.view_orient_switch.get()

        if orient == VIEW_ORIENT.TRANS.value:
            return image.get_frame(orient=VIEW_ORIENT.TRANS.value, x_axis=self.x_axis, y_axis=self.y_axis)
        elif orient == VIEW_ORIENT.SAG.value:
            return image.get_frame(orient=VIEW_ORIENT.SAG.value, x_axis=self.y_axis, y_axis=self.z_axis)
        elif orient == VIEW_ORIENT.CORR.value:
            return image.get_frame(orient=VIEW_ORIENT.CORR.value, x_axis=self.x_axis, y_axis=self.z_axis)


    def draw(self):
        self.frame = Image.new('RGB', (self.max_dim, self.max_dim))

        ind_phys_switch = IND_PHYS(self.app.contextTabs.imageViewTab.indPhysSwitch.get()).name
        orient = self.app.contextTabs.imageViewTab.get_view_orient()
        cmap = self.app.contextTabs.imageViewTab.getColorMap()
        imagesList = self.app.contentTabs.imagesTab.get_visible()

        # If images list is empty
        if not imagesList:
            self.draw_empty()
            return

        frames = []
        alphas = []
        frames_max_dim = 0
        self.global_scale = 1.0

        for image in imagesList:
            alphas.append(image.visibility)

            if orient == VIEW_ORIENT.TRANS.value:
                frames.append(image.get_frame(orient=VIEW_ORIENT.TRANS.value, x_axis = self.x_axis, y_axis=self.y_axis))
            elif orient == VIEW_ORIENT.SAG.value:
                frames.append(image.get_frame(orient=VIEW_ORIENT.SAG.value, x_axis = self.y_axis, y_axis=self.z_axis))
            elif orient == VIEW_ORIENT.CORR.value:
                frames.append(image.get_frame(orient=VIEW_ORIENT.CORR.value, x_axis = self.x_axis, y_axis=self.z_axis))


            if np.amax(frames[-1].shape) > frames_max_dim:
                frames_max_dim = np.amax(frames[-1].shape)

        self.global_scale = self.max_dim / frames_max_dim

        # alphas = np.array(alphas)
        # alphas = alphas / np.sum(alphas)

        for frame_, alpha_ in zip(frames, alphas):
            # frame = frame + frame_ * alpha_
            # all frames are stretched so they fit the final artwork
            # frame_ = frame_ * alpha_
            frame_ = cv2.resize(frame_,None, fx=self.global_scale, fy=self.global_scale, interpolation=cv2.INTER_LINEAR)
            pad_left = int(np.floor((self.max_dim - frame_.shape[1]) / 2))
            pad_right = self.max_dim - frame_.shape[1] - pad_left
            pad_top = int(np.floor((self.max_dim - frame_.shape[0]) / 2))
            pad_bottom = self.max_dim - frame_.shape[0] - pad_top
            frame_ = cv2.copyMakeBorder(frame_, top=pad_top, bottom=pad_bottom, left=pad_left, right=pad_right, borderType=cv2.BORDER_CONSTANT, value=0.0)
            frame_ = cv2.cvtColor(frame_.astype(np.uint8), cv2.COLOR_BGR2RGB)
            frame_ = Image.fromarray(frame_)

            self.frame = Image.blend(self.frame, frame_, alpha=alpha_)

        self.frame_tk = ImageTk.PhotoImage(self.frame)

        self.canvas.create_image(self.center_x, self.center_y,image = self.frame_tk)

        self.update_info()

        self.canvas.grid(column=0, row=0)


    def draw_empty(self):
        """
        Clear self.canvas
        :return:
        """
        self.canvas.delete("all")
