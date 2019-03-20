import tkinter as tk
from tkinter import ttk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class ImagePanel():
    def __init__(self, app):
        self.app = app
        self.f = Figure(figsize=(5, 5), dpi=100)
        self.a = self.f.add_subplot(111)
        self.a.plot([1, 2, 3, 4, 5, 6, 7, 8], [5, 6, 1, 3, 8, 9, 3, 5])
        self.canvas = FigureCanvasTkAgg(self.f, app.root)
        self.canvas.get_tk_widget().grid(column=0, row=0)
        self.canvas._tkcanvas.grid(column=0, row=0)

    def draw(self):
        image = self.app.imagesTab.imagesList[0]
        self.a.imshow(image.getFrame())
        self.canvas.draw()