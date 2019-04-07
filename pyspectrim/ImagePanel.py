import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

import cv2

import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class ImagePanel():
    def __init__(self, cinema):

        self.cinema = cinema
        self.app = self.cinema.app

        # todo relate to window size
        self.max_dim = 400

        self.frame_f = np.zeros((self.max_dim,self.max_dim),dtype=np.float32)
        self.frame_i = np.zeros((self.max_dim, self.max_dim), dtype=np.uint8)

        self.center_x = int(self.max_dim/2)
        self.center_y = int(self.max_dim/2)

        self.canavas = tk.Canvas(self.cinema, bg='black')
        self.canavas.config(width=self.max_dim, height=self.max_dim)
        self.canavas.pack()


    def draw(self):

        self.frame_f[:,:] = 0.0
        self.frame_i[:,:] = 0

        orient = self.app.contextTabs.imageViewTab.getImageOrent()
        cmap = self.app.contextTabs.imageViewTab.getColorMap()
        imagesList = self.app.contentTabs.imagesTab.getVisible()

        if not imagesList:
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
        self.frame_i = Image.fromarray(self.frame_i)
        self.frame_i = ImageTk.PhotoImage(self.frame_i)



        self.canavas.create_image(self.center_x, self.center_y,image = self.frame_i)
        self.canavas.pack()