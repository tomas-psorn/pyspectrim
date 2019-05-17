from pyspectrim.ImagePanel import ImagePanelMain, ImagePanel, ImagePanelOrtho
from pyspectrim.SignalPanel import SignalPanel
from pyspectrim.enums import *
import tkinter as tk
from tkinter import ttk


class Cinema(tk.Frame):
    def __init__(self, app, **kwargs):

        self.app = app

        super().__init__(self.app.root)

        self.image_frame = tk.Frame(self)
        self.signal_frame = tk.Frame(self)
        self.orthoview_frame = tk.Frame(self)
        self.trans_frame = tk.Frame(self.orthoview_frame)
        self.sag_frame = tk.Frame(self.orthoview_frame)
        self.cor_frame = tk.Frame(self.orthoview_frame)

        self.image_panel_max_dim = 402

        self.image_panel_main = ImagePanelMain(cinema=self, max_dim=self.image_panel_max_dim, frame=self.image_frame)
        self.image_panel_trans = ImagePanelOrtho(cinema=self, max_dim=int(self.image_panel_max_dim/3), frame=self.trans_frame, fix_orient=VIEW_ORIENT.TRANS.value)
        self.image_panel_sag = ImagePanelOrtho(cinema=self, max_dim=int(self.image_panel_max_dim/3), frame=self.sag_frame, fix_orient=VIEW_ORIENT.SAG.value)
        self.image_panel_cor = ImagePanelOrtho(cinema=self, max_dim=int(self.image_panel_max_dim/3), frame=self.cor_frame, fix_orient=VIEW_ORIENT.CORR.value)

        self.trans_frame.grid(row=0)
        self.sag_frame.grid(row=1)
        self.cor_frame.grid(row=2)

        self.image_panel_main.canvas.grid(row=0, column=0)
        self.image_panel_trans.canvas.grid(row=0, column=0)
        self.image_panel_sag.canvas.grid(row=0, column=0)
        self.image_panel_cor.canvas.grid(row=0, column=0)

        self.signal_panel = SignalPanel(self)

        self.image_frame.grid(row=0, column=0)
        self.orthoview_frame.grid(row=0, column=1)
        self.signal_frame.grid(row=0, column=2)

    def draw(self, image=True, ortho=True, signal=True):
        if image:
            self.image_panel_main.draw()
        if ortho:
            self.image_panel_trans.draw()
            # self.image_panel_trans.draw_navig_cross()
            self.image_panel_sag.draw()
            # self.image_panel_sag.draw_navig_cross()
            self.image_panel_cor.draw()
            # self.image_panel_cor.draw_navig_cross()
        if signal:
            self.signal_panel.draw()

    def draw_empty(self, image=True, ortho=True, signal=True):
        if image:
            self.image_panel_main.draw_empty()
        if ortho:
            self.image_panel_trans.draw_empty()
            self.image_panel_sag.draw_empty()
            self.image_panel_cor.draw_empty()
        if signal:
            self.signal_panel.draw_empty()

    def update_geometry(self, image=True, ortho=True):
        if image:
            self.image_panel_main.update_geometry()
        if ortho:
            self.image_panel_trans.update_geometry()
            self.image_panel_sag.update_geometry()
            self.image_panel_cor.update_geometry()