import tkinter as tk
from tkinter import ttk

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



        #
        self.frame = None

        self.center_x = int(self.max_dim/2)
        self.center_y = int(self.max_dim/2)

        self.canvas = tk.Canvas(self.cinema, bg='black')
        self.canvas.config(width=self.max_dim, height=self.max_dim)


        # reference to text object indicating position and a value of pixel

        self.canvas.grid(column=0, row=0)


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


    def draw(self):

        self.frame = Image.new('RGB', (self.max_dim, self.max_dim))

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

            if orient == 0:
                frames.append(image.getFrame(orient=0, max_dim = self.max_dim))
            elif orient == 1:
                frames.append(image.getFrame(orient=1, max_dim = self.max_dim))
            elif orient == 2:
                frames.append(image.getFrame(orient=2, max_dim = self.max_dim))

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
