import tkinter as tk
from tkinter import ttk

class PositionTab():
    def __init__(self,app):
        self.app = app
        self.positionTab = tk.Frame(self.app.contextTabs)
        self.app.contextTabs.add(self.positionTab, text="Position")

        self.sliders = []

        self.xscale = Slider(self.positionTab, self.app)
        self.xscale.setLabel("x")
        self.xscale.pack()

        self.yscale = Slider(self.positionTab, self.app)
        self.yscale.setLabel("y")
        self.yscale.pack()

        self.zscale = Slider(self.positionTab, self.app)
        self.zscale.setLabel("z")
        self.zscale.bind("<Button-1>", self.zscale.callback)
        self.zscale.bind("<Button-3>", self.zscale.callback)
        self.zscale.pack()



class Slider(tk.Scale):
    def __init__(self, tab, app):
        super(Slider,self).__init__(tab, orient=tk.HORIZONTAL, length = 284, from_=0, to=250)
        self.app = app

    def setLabel(self,text):
        self.config(label=text)

    def setRange(self, from_, to):
        self.config(from_=from_)
        self.config(to=to)

    def setPosition(self, value):
        self.set(value)

    def callback(self,event):
        self.app.imagesTab.imagesList[0].pos_ind[2] = self.get()
        self.app.imagePanel.draw()
