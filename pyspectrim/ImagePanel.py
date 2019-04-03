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

        self.width = 400
        self.height = 400

        self.center_x = int(self.width/2)
        self.center_y = int(self.height/2)

        self.canavas = tk.Canvas(self.cinema, bg='black')
        self.canavas.config(width=400, height=400)
        self.canavas.pack()





    def draw(self):

        orient = self.app.contextTabs.imageViewTab.getImageOrent()
        cmap = self.app.contextTabs.imageViewTab.getColorMap()
        imagesList = self.app.contentTabs.imagesTab.getVisible()

        if not imagesList:
            return

        frames = []
        alphas = []

        for image in imagesList:
            alphas.append(image.getVisibility())

            if orient == 0:
                frames.append(image.getFrame(orient=0))
            elif orient == 1:
                frames.append(image.getFrame(orient=1))
            elif orient == 2:
                frames.append(image.getFrame(orient=2))

        alphas = np.array(alphas)
        alphas = alphas / np.sum(alphas)

        frame = np.zeros(frames[0].shape, dtype=np.float32)

        for frame_, alpha_ in zip(frames, alphas):
            frame = frame + frame_ * alpha_

        frame = cv2.cvtColor(frame.astype(np.uint8), cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (self.width, self.height), interpolation=cv2.INTER_LINEAR)
        frame = Image.fromarray(frame)
        frame = ImageTk.PhotoImage(frame)

        self.frame = frame


        self.canavas.create_image(self.center_x, self.center_y,image = self.frame)
        self.canavas.pack()