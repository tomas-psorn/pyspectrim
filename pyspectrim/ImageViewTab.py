import tkinter as tk
from tkinter import ttk


class ImageViewTab(tk.Frame):
    def __init__(self, contextTabs):
        self.app = contextTabs.app
        self.contextTabs = contextTabs

        self.image = None

        super().__init__(self.contextTabs)
        self.contextTabs.add(self, text="Image view")

        self.alphaSlider = AlphaSlider(self)
        self.indPhysSwitch = IndPhysSwitch(self)
        self.imageOrientSwitch = ImageOrientSwitch(self)
        self.colorMapOptions = ColorMapOption(self)

        self.bind("<Visibility>", self.on_visibility)

    # event handlers
    def on_visibility(self, event):
        self.update()

    def update(self):
        self.image = self.app.contentTabs.imagesTab.get_image_on_focus()
        self.alphaSlider.set(self.image.visibility)



    # setters, getters
    def setIndPhys(self,value):
        self.indPhysSwitch.set(value)

    def getImageOrent(self):
        return self.imageOrientSwitch.value.get()

    def getColorMap(self):
        return self.colorMapOptions.value.get()

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

        super().__init__(self.layout,
                         variable=self.value,
                         orient=tk.HORIZONTAL,
                         length = 250,from_= 0.0,
                         to=1.0,
                         resolution=0.01)

        # bind
        self.bind("<B1-Motion>", self.drag)

        self.set(1.0)

        self.pack(anchor=tk.W)
        self.layout.pack(fill=tk.X)

    # event handlers
    def drag(self, event):
        self.tab.image.visibility = self.get()
        self.app.cinema.imagePanel.draw()


    def set(self,value):
        self.value.set(value)
        image = self.app.contentTabs.imagesTab.get_image_on_focus()
        if image:
            image.visibility = value


class IndPhysSwitch():
    def __init__(self, tab):

        self.tab = tab
        self.app = tab.app
        self.value = tk.IntVar()

        self.layout = tk.LabelFrame(self.tab, text="Viewing mode")


        # super().__init__(self.tab, text="Viewing mode")

        self.physSwitch = tk.Radiobutton(self.layout, text='physical', variable=self.value, value=0, command= lambda : self.set('phys'))
        self.indSwitch = tk.Radiobutton(self.layout, text='indexed', variable=self.value, value=1, command=lambda : self.set('ind'))

        self.value.set(1)

        self.indSwitch.grid(column=0, row =0)
        self.physSwitch.grid(column=1, row =0)

        self.layout.pack(fill=tk.X)

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


class ImageOrientSwitch():
    def __init__(self, tab):

        self.tab = tab
        self.app = tab.app
        self.value = tk.IntVar()

        self.layout = tk.LabelFrame(self.tab, text="ImageOrientation")

        self.axial = tk.Radiobutton(self.layout,
                                    text='axial',
                                    variable=self.value,
                                    value=0,
                                    command= lambda : self.set('axial'))

        self.transversal = tk.Radiobutton(self.layout,
                                          text='transversal',
                                          variable=self.value,
                                          value=1,
                                          command=lambda : self.set('transversal'))

        self.sagital = tk.Radiobutton(self.layout,
                                      text='sagital',
                                      variable=self.value,
                                      value=2,
                                      command=lambda : self.set('sagital'))

        # default orientation is axial
        self.value.set(0)

        self.axial.grid(column=0, row =0)
        self.transversal.grid(column=1, row =0)
        self.sagital.grid(column=2, row=0)

        self.layout.pack(fill=tk.X)

    def set(self, value):
        # todo
        #  if switched to indexed redraw
        if value == 'axial':
            self.value.set(0)
        elif value == 'transversal':
            self.value.set(1)
        elif value == 'sagital':
            self.value.set(2)

        self.app.cinema.imagePanel.draw()


class ColorMapOption(tk.OptionMenu):
    def __init__(self, tab):

        self.tab = tab
        self.app = tab.app

        self.optionsList = ('gray', 'winter','jet')

        self.value = tk.StringVar()
        self.value.set( self.optionsList[0])

        self.layout = tk.LabelFrame(self.tab, text='Color map')

        super().__init__(self.layout, self.value , *self.optionsList, command= self.set)

        self.pack(anchor=tk.W)
        self.layout.pack(fill=tk.X)

    def set(self, value):
        image = self.app.contentTabs.imagesTab.get_image_on_focus()
        image.colormap = value
        self.app.cinema.imagePanel.draw()
