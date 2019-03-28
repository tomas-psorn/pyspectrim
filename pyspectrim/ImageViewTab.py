import tkinter as tk
from tkinter import ttk


class ImageViewTab(tk.Frame):
    def __init__(self, contextTabs):
        self.app = contextTabs.app
        self.contextTabs = contextTabs

        super().__init__(self.contextTabs)
        self.contextTabs.add(self, text="Image view")

        self.alphaSlider = AlphaSlider(self)
        self.indPhysSwitch = IndPhysSwitch(self)

    # setters, getters
    def setAlpha(self, image):
        self.alphaSlider.set(image.getVisibility())

    def setIndPhys(self,value):
        self.indPhysSwitch.set(value)

    def lockIndPhysSwitch(self,value):
        self.indPhysSwitch.lock(value)

    # maintenance

    def clean(self):
        self.alphaSlider.value.set(1.0)
        self.indPhysSwitch.lock(False)
        self.indPhysSwitch.set('ind')

    def destroy(self):
        self.alphaSlider.layout.destroy()
        self.indPhysSwitch.layout.destroy()

class AlphaSlider(tk.Scale):
    def __init__(self, tab):

        self.tab = tab
        self.app = tab.app

        self.value = tk.DoubleVar()
        self.layout = tk.LabelFrame(self.tab, text='Visibility')

        super().__init__(self.layout, variable=self.value ,orient=tk.HORIZONTAL, length = 250, from_= 0.0, to=1.0)
        self.set(1.0)

        self.pack()
        self.layout.pack()

    def set(self,value):
        self.value.set(value)


class IndPhysSwitch():
    def __init__(self, tab):

        self.tab = tab
        self.app = tab.app
        self.value = tk.IntVar()

        self.layout = tk.LabelFrame(self.tab, text="Viewing mode")

        # super().__init__(self.tab, text="Viewing mode")

        self.physSwitch = tk.Radiobutton(self.layout, text='physical', variable=self.value, value=0, command=self.set)
        self.indSwitch = tk.Radiobutton(self.layout, text='indexed', variable=self.value, value=1, command=self.set)

        self.value.set(1)

        self.indSwitch.grid(column=0, row =0)
        self.physSwitch.grid(column=1, row =0)

        self.layout.pack()

    def set(self, value):
        # todo
        #  if switched to indexed redraw
        if value == 'ind':
            self.value.set(1)
        elif value == 'phys':
            self.value.set(0)

    def lock(self,value):
        if value == True:
            self.value.set(1)
            self.indSwitch['state'] = 'disabled'
            self.physSwitch['state'] = 'disabled'
        else:
            self.indSwitch['state'] = 'normal'
            self.physSwitch['state'] = 'normal'