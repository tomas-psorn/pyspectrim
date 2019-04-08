import tkinter as tk
from tkinter import ttk


import time

class PositionTab(tk.Frame):
    def __init__(self,contextTabs):
        self.app = contextTabs.app
        self.contextTabs = contextTabs

        super().__init__(self.contextTabs)
        self.contextTabs.add(self, text="Position")

        self.sliders = []

        self.bind("<Visibility>", self.on_visible)


    def set_pos_sliders(self, image):
        for i in range(0, image.ndim):
          self.sliders.append(PositionSlider(self, image=image, dim_order = i))

    def clear_pos_sliders(self):
        for slider in self.sliders:
            slider.destroy_()
        self.sliders = []

    def on_visible(self,event=None):
        self.clear_pos_sliders()
        image = self.app.contentTabs.imagesTab.get_image_on_focus()

        if image:
            self.set_pos_sliders(self.app.contentTabs.imagesTab.get_image_on_focus())

class PositionSlider(tk.Scale):

    def_length = 250

    def __init__(self, tab, **kwargs):

        self.tab = tab
        self.app = tab.app

        self.image = kwargs['image']
        self.dim_order = kwargs['dim_order']  # a position of dimension in dim lists

        self.value = tk.IntVar()

        self.layout = tk.LabelFrame(self.tab, text=self.image.dim_label[self.dim_order])
        # super(Slider,self).__init__(self.layout, orient=tk.HORIZONTAL, length = 284, from_=0, to=250)
        super().__init__(self.layout, variable=self.value ,orient=tk.HORIZONTAL, length = 250, from_= self.image.dim_from[self.dim_order], to=self.image.dim_to[self.dim_order])

        # set initial position
        self.set(self.image.dim_pos[self.dim_order])



        # self.setLabel(kwargs['label'])
        self.bind("<Button-1>", self.callback)
        self.bind("<Button-3>", self.callback)
        self.grid(row=0, column = 2, pady=5)

        self.beginButton = tk.Button(self.layout,text='begin')
        self.beginButton.bind("<Button-1>", self.beginClick)
        self.beginButton.grid(row=0, column = 0)

        self.leftButton = tk.Button(self.layout,text='left')
        self.leftButton.bind("<Button-1>", self.leftClick)
        self.leftButton.grid(row=0, column = 1)

        self.rightButton = tk.Button(self.layout,text='right')
        self.rightButton.bind("<Button-1>", self.rightClick)
        self.rightButton.grid(row=0, column = 3)

        self.endButton = tk.Button(self.layout,text='end')
        self.endButton.bind("<Button-1>", self.endClick)
        self.endButton.grid(row=0, column = 4)

        self.playButton = tk.Button(self.layout,text='play')
        self.playButton.bind("<Button-1>", self.playClick)
        self.playButton.grid(row=0, column = 5)

        self.physIndSwtch = tk.IntVar()
        self.physSwtch = tk.Radiobutton(self.layout, text='physical', variable=self.physIndSwtch, value=1, command=self.setPhysical)
        self.physSwtch.grid(row=0, column = 6)
        self.indSwtch = tk.Radiobutton(self.layout, text='index', variable=self.physIndSwtch, value=0, command=self.setIndexed)
        self.indSwtch.grid(row=0, column = 7)

        self.layout.pack()



    def setLabel(self,text):
        self.config(label=text)

    def setRange(self, from_, to):
        self.config(from_=from_)
        self.config(to=to)

    def setPosition(self, value):
        self.set(value)

    def callback(self,event):
        # TODO
        self.image.dim_pos[self.dim_order] = self.value.get()
        self.app.cinema.imagePanel.draw()

    def leftClick(self, event):
        self.set(self.get()-1)
        self.image.decrementPosition(self.dim_order)
        self.app.cinema.imagePanel.draw()

    def rightClick(self, event):
        self.set(self.get()+1)
        self.image.incrementPosition(self.dim_order)
        self.app.cinema.imagePanel.draw()

    def beginClick(self, event):
        self.set(self.cget('from'))
        self.image.posToMin(self.dim_order)
        self.app.cinema.imagePanel.draw()

    def endClick(self, event):
        self.set(self.cget('to'))
        self.image.posToMax(self.dim_order)
        self.app.cinema.imagePanel.draw()

    def playClick(self,event):
        # TODO
        for i in range(int(self.get()), int(self.cget('to'))):
            self.set(self.get()+1)
            self.image.incrementPosition(self.dim_order)
            self.app.cinema.imagePanel.draw()
            time.sleep(0.5)

    def setPhysical(self):
        # TODO
        self.from_ = self.image.dim_from_phys[self.dim_order]
        self.to = self.image.dim_to_phys[self.dim_order]
        self.resolution = self.image.dim_spacing[self.dim_order]

    def setIndexed(self):
        pass

    def destroy_(self):
        self.layout.destroy()


