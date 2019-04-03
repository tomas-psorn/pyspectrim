import tkinter as tk
from tkinter import ttk

import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class ImagePanel():
    def __init__(self, cinema):

        self.cinema = cinema
        self.app = self.cinema.app
        self.f = Figure(figsize=(5, 5), dpi=100)
        self.a = self.f.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.f, self.cinema)
        self.canvas.get_tk_widget().grid(column=0, row=0)
        self.canvas._tkcanvas.grid(column=0, row=0)

    def draw(self):
        orient = self.app.contextTabs.imageViewTab.getImageOrent()
        cmap = self.app.contextTabs.imageViewTab.getColorMap()
        image = self.app.contentTabs.imagesTab.imagesList[0]


        frame = None

        if orient == 0:
            frame = image.getFrame_ax()

        elif orient == 1:
            frame = image.getFrame_cor()
        elif orient == 2:
            frame = image.getFrame_sag()

        frame = 255 * (frame - np.amin(frame)) / np.amax(frame)
        frame = frame.astype(int)

        self.a.imshow(frame, cmap=cmap)

        self.canvas.draw()