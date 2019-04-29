import tkinter as tk
from tkinter import ttk

from enum import Enum

import matplotlib, sys
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from pyspectrim.enums import *

class ImageViewTab(tk.Frame):
    def __init__(self, contextTabs):
        self.app = contextTabs.app
        self.contextTabs = contextTabs

        super().__init__(self.contextTabs)
        self.contextTabs.add(self, text="Image")

        self.complex_part_switch = ComplexPartSwitch(self)
        self.alphaSlider = AlphaSlider(self)
        self.indPhysSwitch = IndPhysSwitch(self)
        self.view_orient_switch = ViewOrientSwitch(self)
        self.colorMapOptions = ColorMapOption(self)
        self.contrastEnhance = ContrastEnhance(self)


    # event handlers
    def on_visible(self, event=None):
        self.update()

    def update(self):
        image = self.app.contentTabs.imagesTab.get_image_on_focus()
        if image is None:
            self.set_defaults()
            return

        self.alphaSlider.set_image(image)
        self.colorMapOptions.set_image(image)
        self.contrastEnhance.set_image(image)

    def set_defaults(self):
        self.alphaSlider.set_image(None)
        self.colorMapOptions.set_image(None)
        self.contrastEnhance.set_image(None)

    # setters, getters
    def setIndPhys(self,value):
        self.indPhysSwitch.set(value)

    def get_view_orient(self):
        return self.view_orient_switch.value.get()

    def getColorMap(self):
        return self.colorMapOptions.value

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

        self.image = None

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
        value = self.get()

        if self.image.visibility == 0.0 and value > 0.0:
            self.app.contentTabs.imagesTab.imagesTree.set(self.image.tree_id, 'visibility', 'True')
            self.app.contentTabs.imagesTab.images_vis_list.append(self.image)
        elif self.image.visibility > 0.0 and value == 0.0:
            self.app.contentTabs.imagesTab.imagesTree.set(self.image.tree_id, 'visibility', 'False')
            self.app.contentTabs.imagesTab.images_vis_list.remove(self.image)

        self.image.visibility = value
        self.app.cinema.imagePanel.draw()

    def set_image(self,image):
        self.image = image
        self.set(image.visibility)


    def free_image(self):
        self.image = None

    def set(self,value):
        self.value.set(value)
        if self.image:
            self.image.visibility = value

class IndPhysSwitch():
    def __init__(self, tab):

        self.tab = tab
        self.app = tab.app
        self.value = tk.IntVar()

        self.layout = tk.LabelFrame(self.tab, text="Viewing mode")


        # super().__init__(self.tab, text="Viewing mode")

        self.physSwitch = tk.Radiobutton(self.layout, text='physical', variable=self.value, value=1, command= lambda : self.set(IND_PHYS.PHYS.value))
        self.indSwitch = tk.Radiobutton(self.layout, text='indexed', variable=self.value, value=0, command=lambda : self.set(IND_PHYS.IND.value))

        self.value.set(IND_PHYS.IND.value)

        self.indSwitch.grid(column=0, row =0)
        self.physSwitch.grid(column=1, row =0)

        self.layout.pack(fill=tk.X)

    def set(self, value):
        self.value.set(value)
        self.app.cinema.imagePanel.draw()


    def get(self):
        return self.value.get()

    def update(self):
        if self.app.contentTabs.imagesTab.dimConsistCheck():
            self.app.contextTabs.imageViewTab.setIndPhys(IND_PHYS.IND.value)
            self.app.contextTabs.imageViewTab.lockIndPhysSwitch(False)
        else:
            self.app.contextTabs.imageViewTab.lockIndPhysSwitch(True)
            self.app.contextTabs.imageViewTab.setIndPhys(IND_PHYS.PHYS.value)


    def lock(self,value):
        if value == True:
            self.value.set(1)
            self.indSwitch['state'] = 'disabled'
            self.physSwitch['state'] = 'disabled'
        else:
            self.indSwitch['state'] = 'normal'
            self.physSwitch['state'] = 'normal'

class ViewOrientSwitch():
    # scope - each image panel has its own
    def __init__(self, tab):

        self.tab = tab
        self.app = tab.app
        self.value = tk.IntVar()

        self.layout = tk.LabelFrame(self.tab, text="View Orientation")

        self.axial = tk.Radiobutton(self.layout,
                                    text='transversal',
                                    variable=self.value,
                                    value=0,
                                    command= lambda : self.set(VIEW_ORIENT.TRANS.value))

        self.transversal = tk.Radiobutton(self.layout,
                                          text='sagittal',
                                          variable=self.value,
                                          value=1,
                                          command=lambda : self.set(VIEW_ORIENT.SAG.value))

        self.sagital = tk.Radiobutton(self.layout,
                                      text='corronal',
                                      variable=self.value,
                                      value=2,
                                      command=lambda : self.set(VIEW_ORIENT.CORR.value))

        # default orientation is axial
        self.value.set(VIEW_ORIENT.TRANS.value)

        self.axial.grid(column=0, row =0)
        self.transversal.grid(column=1, row =0)
        self.sagital.grid(column=2, row=0)

        self.layout.pack(fill=tk.X)

    def set(self, value):
        self.value.set(value)
        self.app.cinema.imagePanel.draw()

    def get(self):
        return self.value.get()

class ColorMapOption(tk.OptionMenu):
    def __init__(self, tab):

        self.tab = tab
        self.app = tab.app
        self.image = None

        self.optionsList = ('gray', 'winter','jet')

        self.value = tk.StringVar()
        self.value.set( self.optionsList[0])

        self.layout = tk.LabelFrame(self.tab, text='Color map')

        super().__init__(self.layout, self.value , *self.optionsList, command= self.set)

        self.pack(anchor=tk.W)
        self.layout.pack(fill=tk.X)

    def set_image(self,image):
        self.image = image
        self.value = image.colormap

    def free_image(self):
        self.image = None

    def set(self, value):
        self.image.colormap = value
        self.app.cinema.imagePanel.draw()

class ContrastEnhance():
    def __init__(self, tab):

        self.tab = tab
        self.app = tab.app
        self.image = None

        self.layout = tk.LabelFrame(self.tab, text='Contrast enhance')
        self.layout.pack(fill=tk.X)

        self.min_var = tk.StringVar()
        self.max_var = tk.StringVar()
        self.clip_stretch_var = tk.BooleanVar()

        # The default enhancement mode is clip
        self.clip_stretch_var.set(True)
        #
        # self.min_var.trace('w',callback=self.set_min)
        # self.max_var.trace('w', callback=self.set_max)

        self.min_entry = tk.Entry(self.layout, textvariable=self.min_var)
        self.max_entry = tk.Entry(self.layout, textvariable=self.max_var)
        self.apply_button = tk.Button(self.layout, text="Apply to data", command=self.apply_enhance)
        self.hist_norm_button = tk.Button(self.layout, text="Normalize histogram", command=self.hist_norm)
        self.enhance_button = tk.Button(self.layout, text="Enhance", command=self.enhance_window_popup)

        self.stretch_button = tk.Radiobutton(self.layout,
                                    text='stretch',
                                    variable=self.clip_stretch_var,
                                    value=0,
                                    command=self.on_switch_click
                                    )

        self.clip_button = tk.Radiobutton(self.layout,
                                    text='clip',
                                    variable=self.clip_stretch_var,
                                    value=1,
                                    command=self.on_switch_click
                                    )

        self.min_entry.bind('<Return>', self.set_min)
        self.max_entry.bind('<Return>', self.set_max)

        self.min_label = tk.Label(self.layout, text="min:")
        self.max_label = tk.Label(self.layout, text="max:")

        self.min_label.grid(row=0,column=0)
        self.min_entry.grid(row=0,column=1)
        self.max_label.grid(row=0,column=2)
        self.max_entry.grid(row=0,column=3)
        self.clip_button.grid(row=1,column=0, columnspan=2)
        self.stretch_button.grid(row=1,column=2, columnspan=2)


        # self.min_label.pack(side=tk.LEFT)
        # self.min_entry.pack(side=tk.LEFT)
        # self.max_label.pack(side=tk.LEFT)
        # self.max_entry.pack(side=tk.LEFT)
        # self.stretch_button.pack(side=tk.BOTTOM)
        # self.clip_button.pack(side=tk.BOTTOM)


        self.apply_button.grid(row=2,column=0, columnspan=2)
        self.hist_norm_button.grid(row=2,column=2, columnspan=2)
        self.enhance_button.grid(row=3,column=0, columnspan=2)

    def enhance_window_popup(self):
        enhance_window = EnhanceWindow(app=self.app, image=self.image)

    def on_switch_click(self):
        self.app.cinema.imagePanel.draw()

    def set_image(self,image):
        self.image = image
        self.min_var.set(str(self.image.min_preview))
        self.max_var.set(str(self.image.max_preview))

    def free_image(self):
        self.image = None

    def set_min(self, event):
        if self.image:
            value = float(self.min_var.get())
            # If value entered is lower than data minimum
            if value < self.image.min_data or value > float(self.max_var.get()):
                # write the minimal value into the entry
                self.min_var.set(str(self.image.min_data))
                self.image.min_preview = self.image.min_data
            else:
                self.image.min_preview = value

            self.app.cinema.imagePanel.draw()

    def set_max(self, event):
        if self.image:
            value = float(self.max_var.get())
            # If value entered is lower than data minimum
            if value > self.image.max_data or value < float(self.min_var.get()):
                # write the minimal value into the entry
                self.max_var.set(str(self.image.max_data))
                self.image.max_preview = self.image.max_data
            else:
                self.image.max_preview = value

            self.app.cinema.imagePanel.draw()

    def hist_norm(self):
        if self.image:
            self.image.hist_norm()
            self.min_var.set(str(self.image.min_preview))
            self.max_var.set(str(self.image.max_preview))

            self.app.cinema.imagePanel.draw()
            self.app.contextTabs.update_context()

    def apply_enhance(self):
        if self.image:
            self.image.apply_enhance()

        self.app.contextTabs.update_context()
        self.app.cinema.imagePanel.draw()

class EnhanceWindow():
    def __init__(self, app=None, image=None):
        self.app = app
        self.image = image
        self.enhance_window = tk.Tk()
        self.enhance_window.wm_title("Enhance")
        self.enhance_window.geometry('400x600')

        self.hist_frame = tk.Frame(self.enhance_window)
        self.options_frame = tk.Frame(self.enhance_window)

        self.hist_fig = Figure(figsize=(5, 4), dpi=100)

        ax = self.hist_fig.add_subplot(111)
        n, bins, patches = ax.hist(image.data.flatten(), 250, density=False, label='data')
        n, bins, patches = ax.hist(self.app.cinema.imagePanel.get_frame(image=image).flatten(), 50, density=False, label='frame')
        # ax.legend(loc='upper right')

        self.pow_frame = tk.LabelFrame(self.options_frame, text='Power')
        self.pow_coef_val = tk.StringVar()
        self.pow_coef_val.set('1.0')
        self.pow_coef_entry = tk.Entry(self.pow_frame, textvariable=self.pow_coef_val)
        self.apply_button = tk.Button(self.pow_frame, text="Apply to preview", command=self.set_enhance)
        self.pow_coef_entry.grid(row=0, column=0)
        self.apply_button.grid(row=0, column=1)
        self.pow_frame.pack()

        self.log_frame = tk.LabelFrame(self.options_frame, text='Logarithm')

        self.canvas = FigureCanvasTkAgg(self.hist_fig, master=self.hist_frame)
        self.canvas.get_tk_widget().pack()
        self.canvas.draw()

        self.hist_frame.pack()
        self.options_frame.pack()

        self.done_button = tk.Button(self.enhance_window, text="Okay", command=self.enhance_window.destroy)
        self.done_button.pack()

    def set_enhance(self):
        if float(self.pow_coef_entry.get()) != 1.0:
            self.image.set_enhance(pow=float(self.pow_coef_entry.get()))

        self.app.cinema.imagePanel.draw()
        self.app.cinema.imagePanel.update_info()


class ComplexPartSwitch():
    def __init__(self, tab):
        self.tab = tab
        self.app = tab.app
        self.value = tk.IntVar()

        self.layout = tk.LabelFrame(self.tab, text="Complex part")

        self.abs = tk.Radiobutton(self.layout,
                                    text='magnitude',
                                    variable=self.value,
                                    value=COMPLEX_PART.ABS.value,
                                    command=lambda: self.set(COMPLEX_PART.ABS.value))

        self.phase = tk.Radiobutton(self.layout,
                                          text='phase',
                                          variable=self.value,
                                          value=COMPLEX_PART.PHASE.value,
                                          command=lambda: self.set(COMPLEX_PART.PHASE.value))

        self.real = tk.Radiobutton(self.layout,
                                      text='real',
                                      variable=self.value,
                                      value=COMPLEX_PART.RE.value,
                                      command=lambda: self.set(COMPLEX_PART.RE.value))

        self.imag = tk.Radiobutton(self.layout,
                                      text='imag',
                                      variable=self.value,
                                      value=COMPLEX_PART.IM.value,
                                      command=lambda: self.set(COMPLEX_PART.IM.value))

        # default orientation is axial
        self.value.set(COMPLEX_PART.ABS.value)

        self.abs.grid(column=0, row=0)
        self.phase.grid(column=1, row=0)
        self.real.grid(column=2, row=0)
        self.imag.grid(column=3, row=0)

        self.layout.pack(fill=tk.X)

    def set(self, value):
        # todo
        #  if switched to indexed redraw
        self.value.set(value)

        self.app.cinema.imagePanel.draw()
        self.app.cinema.signalPanel.draw()

    def get(self):
        return self.value.get()


