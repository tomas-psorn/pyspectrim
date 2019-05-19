import tkinter as tk
from tkinter import ttk

from enum import Enum

import matplotlib, sys
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import numpy as np

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

    def set_defaults(self):
        self.alphaSlider.set_defaults()
        self.colorMapOptions.set_defaults()
        self.contrastEnhance.set_defaults()
        self.indPhysSwitch.set_defaults()
        self.view_orient_switch.set_defaults()
        self.complex_part_switch.set_defaults()

    def set_context(self, image=None):
        if image is None:
            self.set_defaults()
            return

        self.alphaSlider.set_context(image=image)
        self.indPhysSwitch.set_context(image=image)
        self.view_orient_switch.set_context(image=image)
        self.colorMapOptions.set_context(image=image)
        self.contrastEnhance.set_context(image=image)
        self.complex_part_switch.set_context(image=image)

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

    # set default and set context
    def set_defaults(self):
        self.value.set(1.0)

    def set_context(self, image=None):
        self.value.set(image.visibility)

    # event handlers
    def drag(self, event):
        value = self.get()

        image = self.tab.contextTabs.get_context_image()

        if image.visibility == 0.0 and value > 0.0:
            self.app.contentTabs.imagesTab.imagesTree.set(image.tree_id, 'visibility', 'True')
            self.app.contentTabs.imagesTab.images_vis_list.append(image)
        elif image.visibility > 0.0 and value == 0.0:
            self.app.contentTabs.imagesTab.imagesTree.set(image.tree_id, 'visibility', 'False')
            self.app.contentTabs.imagesTab.images_vis_list.remove(image)

        image.visibility = value
        self.app.cinema.draw(signal=False)

    def set(self,value):
        self.value.set(value)
        if self.image:
            self.image.visibility = value

    # no getter here, read visibility value from image on context

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

    def set_defaults(self):
        self.lock(False)
        self.value.set(IND_PHYS.IND.value)

    def set_context(self, image=None):
        # does not depend on image
        pass

    def set(self, value):
        self.value.set(value)
        self.app.cinema.update_geometry()
        self.app.cinema.draw(signal=False)

    def get(self):
        return self.value.get()

    def update(self):
        if self.app.contentTabs.imagesTab.dimConsistCheck():
            self.value.set(IND_PHYS.IND.value)
            self.lock(False)
        else:
            self.lock(True)
            self.value.set(IND_PHYS.PHYS.value)

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

    def set_defaults(self):
        self.value.set(VIEW_ORIENT.TRANS.value)

    def set_context(self, image=None):
        # does not depend on image
        pass

    def set(self, value):
        self.value.set(value)
        self.app.cinema.draw(ortho=False, signal=False)

    def get(self):
        return self.value.get()

class ColorMapOption(tk.OptionMenu):
    def __init__(self, tab):

        self.tab = tab
        self.app = tab.app
        self.image = None

        # this has to match with COLOR_MAP definition
        self.optionsList = ('GRAY', 'WINTER','JET')

        self.value = tk.StringVar()
        self.value.set( COLOR_MAP.GRAY.name)

        self.layout = tk.LabelFrame(self.tab, text='Color map')

        super().__init__(self.layout, self.value , *self.optionsList, command= self.set)

        self.pack(anchor=tk.W)
        self.layout.pack(fill=tk.X)

    def set_defaults(self):
        self.value.set(COLOR_MAP.GRAY.name)

    def set_context(self, image=None):
        self.value.set(COLOR_MAP(image.colormap).name)

    def set(self, value):
        image = self.tab.contextTabs.get_context_image()
        image.colormap = COLOR_MAP[self.value.get()].value
        self.app.cinema.draw()

    # no getter here, read color map value from image on context

class ContrastEnhance():
    def __init__(self, tab):

        self.tab = tab
        self.app = tab.app

        self.layout = tk.LabelFrame(self.tab, text='Contrast enhance')
        self.layout.pack(fill=tk.X)

        self.enhance_button = tk.Button(self.layout, text="Enhance", command=self.enhance_window_popup)
        self.enhance_button.pack()

    def set_defaults(self):
        pass

    def set_context(self, image=None):
        pass

    def enhance_window_popup(self):
        enhance_window = EnhanceWindow(app=self.app, image=self.tab.contextTabs.get_context_image())

    def hist_norm(self):
        if self.image:
            self.image.hist_norm()
            self.min_var.set(str(self.image.min_preview))
            self.max_var.set(str(self.image.max_preview))

            self.app.cinema.draw()
            self.app.contextTabs.update_context()

class EnhanceWindow():
    def __init__(self, app=None, image=None):
        self.app = app
        self.image = image
        self.enhance_window = tk.Tk()
        self.enhance_window.wm_title("Enhance")
        self.enhance_window.geometry('600x300')
        self.enhance_window.protocol("WM_DELETE_WINDOW", self.on_exit)



        self.hist_frame = tk.LabelFrame(self.enhance_window, text='Histogram')
        self.options_frame=tk.Frame(self.enhance_window)

        self.window_frame = tk.LabelFrame(self.options_frame, text='Windowing')
        self.pow_frame = tk.LabelFrame(self.options_frame, text='Power scaling')
        self.log_frame = tk.LabelFrame(self.options_frame, text='Logarithmic  scaling')
        self.hist_eq_frame = tk.LabelFrame(self.options_frame, text='Normalize histogram')

        self.init_hist()
        self.init_log()
        self.init_pow()
        self.init_hist_eq()

        self.hist_frame.grid(row=0, column=0)
        self.options_frame.grid(row=0, column=1)

        self.window_frame.pack(fill=tk.X)
        self.pow_frame.pack(fill=tk.X)
        self.log_frame.pack(fill=tk.X)
        self.hist_eq_frame.pack(fill=tk.X)

        # self.done_button = tk.Button(self.enhance_window, text="Okay", command=self.enhance_window.destroy)
        # self.done_button.pack()

    def on_exit(self):
        self.image = None
        self.enhance_window.destroy()

    def set_enhance(self):
        if float(self.pow_coef_entry.get()) != 1.0:
            self.image.set_enhance(pow=float(self.pow_coef_entry.get()))

        self.app.cinema.draw()
        self.app.cinema.image_panel_main.update_info()

    def init_hist(self):

        if 'complex' in self.image.data.dtype.name:
            data = np.abs(self.image.data)
        else:
            data = self.image.data

        self.hist_fig = Figure(figsize=(2, 2), dpi=100)

        ax = self.hist_fig.add_subplot(111)
        n, bins, patches = ax.hist(data.flatten(), 250, density=False, label='data')
        n, bins, patches = ax.hist(self.app.cinema.image_panel_main.get_frame(image=self.image).flatten(), 50, density=False, label='frame')
        # ax.legend(loc='upper right')

        self.canvas = FigureCanvasTkAgg(self.hist_fig, master=self.hist_frame)
        self.canvas.get_tk_widget().pack()
        self.canvas.draw()

    def init_pow(self):
        self.pow_coef_entry = tk.Entry(self.pow_frame)
        self.pow_coef_entry.insert(tk.END, '1.0')
        self.apply_prew_button = tk.Button(self.pow_frame, text="Apply to preview", command=self.set_pow_prew)
        self.apply_data_button = tk.Button(self.pow_frame, text="Apply to data", command=self.set_pow_data)
        self.pow_coef_entry.grid(row=0, column=0)
        self.apply_prew_button.grid(row=0, column=1)
        self.apply_data_button.grid(row=0, column=2)

    def init_log(self):
        self.apply_prew_button = tk.Button(self.log_frame, text="Apply to preview", command=self.set_log_prew)
        self.apply_data_button = tk.Button(self.log_frame, text="Apply to data", command=self.set_log_data)
        self.apply_prew_button.grid(row=0, column=0)
        self.apply_data_button.grid(row=0, column=1)

    def init_hist_eq(self):
        self.apply_hist_eq_button = tk.Button(self.hist_eq_frame, text="Equalize histogram", command=self.hist_eq)
        self.apply_hist_eq_button.grid(row=0, column=0)

    def set_pow_prew(self):
        pass

    def set_pow_data(self):
        self.image.enhance_data(pow=True, pow_coef=float(self.pow_coef_entry.get()))

    def set_log_prew(self):
        pass

    def set_log_data(self):
        self.image.enhance_data(log=True)



    def hist_eq(self):
        self.image.hist_eq()

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

    def set_defaults(self):
        self.value.set(COMPLEX_PART.ABS.value)

    def set_context(self, image=None):
        # not image dependent
        pass

    def set(self, value):
        self.value.set(value)
        self.app.cinema.draw()

    def get(self):
        return self.value.get()


