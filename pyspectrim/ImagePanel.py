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

        self.frame_f = np.zeros((self.max_dim,self.max_dim,3),dtype=np.float32)
        self.frame_i = np.zeros((self.max_dim, self.max_dim,3), dtype=np.uint8)
        self.frame = None

        self.center_x = int(self.max_dim/2)
        self.center_y = int(self.max_dim/2)

        self.canvas = tk.Canvas(self.cinema, bg='black')
        self.canvas.config(width=self.max_dim, height=self.max_dim)

        self.canvas.bind("<Button-3>", self.on_right_click)

        self.canvas.pack()

    # event handlers
    def on_right_click(self,event):
        image = self.app.contentTabs.imagesTab.get_image_on_focus()

        if image is None:
            logging.info("No image selected, can't handle right click")
            return

        orient = self.app.contextTabs.imageViewTab.getImageOrent()
        x, y, z, value = image.get_pixel_info(event.x, event.y, orient)



    def draw(self):

        self.frame_f[:,:,:] = 0.0
        self.frame_i[:,:,:] = 0

        orient = self.app.contextTabs.imageViewTab.getImageOrent()
        cmap = self.app.contextTabs.imageViewTab.getColorMap()
        imagesList = self.app.contentTabs.imagesTab.get_visible()

        if not imagesList:
            self.draw_empty()
            return

        frames = []
        alphas = []

        for image in imagesList:
            alphas.append(image.visibility)

            if orient == 0:
                frames.append(image.getFrame(orient=0, max_dim = self.max_dim))
            elif orient == 1:
                frames.append(image.getFrame(orient=1, max_dim = self.max_dim))
            elif orient == 2:
                frames.append(image.getFrame(orient=2, max_dim = self.max_dim))

        # alphas = np.array(alphas)
        # alphas = alphas / np.sum(alphas)

        for frame_, alpha_ in zip(frames, alphas):
            # frame = frame + frame_ * alpha_
            self.frame_f = self.frame_f + frame_ * alpha_

        self.frame_i = cv2.cvtColor(self.frame_f.astype(np.uint8), cv2.COLOR_BGR2RGB)
        # frame = cv2.resize(frame, (self.width, self.height), interpolation=cv2.INTER_LINEAR)
        self.frame = Image.fromarray(self.frame_i)
        self.frame = ImageTk.PhotoImage(self.frame)

        self.canvas.create_image(self.center_x, self.center_y,image = self.frame)
        self.canvas.pack()

    def draw_empty(self):
        self.canvas.delete("all")
