from pyspectrim.File import getH5Id

import logging

import tkinter as tk
from tkinter import ttk

import cv2
import numpy as np
import h5py

import matplotlib.pyplot as plt

class Image(object):
    def __init__(self, app, dataset):

        self.app = app

        self.tree_id = getH5Id(dataset)
        self.data = np.array(dataset)
        self.data = np.squeeze(self.data)

        self.dim_size = self.data.shape
        self.ndim = len(self.dim_size)
        self.dim_label = ['x','y','z']

        self.dim_from = np.array([0,0,0])
        self.dim_from_phys = np.array([0.0, 0.0, 0.0])

        self.dim_to = np.array([self.dim_size[0], self.dim_size[1], self.dim_size[2]])
        self.dim_to_phys = np.array([25.6,25.6, 20.0])

        self.dim_spacing = np.array([0.1, 0.1, 0.5])

        self.dim_phys_extent = self.dim_size * self.dim_spacing

        self.dim_pos = [ int(self.dim_size[0]/2), int(self.dim_size[1]/2), int(self.dim_size[2]/2) ]

        self._visibility = 1.0
        self._colormap = cv2.COLORMAP_BONE

        self.min_data = np.amin(self.data)
        self.max_data = np.amax(self.data)

        self.min_preview = self.min_data
        self.max_preview = self.max_data

        self.aspect = self.dim_phys_extent / np.amax(self.dim_phys_extent)


    # properties
    @property
    def colormap(self):
        return self._colormap

    @colormap.setter
    def colormap(self,value):
        if value == 'gray':
            self._colormap = cv2.COLORMAP_BONE
        elif value == 'winter':
            self._colormap = cv2.COLORMAP_COOL
        elif value == 'jet':
            self._colormap = cv2.COLORMAP_JET
        else:
            self._colormap = cv2.COLORMAP_BONE
            logging.debug("Colormap: {} unknown".format(value))

    @property
    def visibility(self):
        return self._visibility

    @visibility.setter
    def visibility(self,value):
        if value > 1.0:
            self._visibility = 1.0
        elif value < 0.0:
            self._visibility = 0.0
        else:
            self._visibility = value

    # getters
    def getFrame(self, **kwargs):

        # coronal
        if kwargs['orient'] == 0:
            frame = self.data[:, :, self.dim_pos[2]]
            export_size = ( int(kwargs['max_dim'] * self.aspect[0]) , int(kwargs['max_dim'] * self.aspect[1]) )
        # sagital
        elif kwargs['orient'] == 1:
            frame = self.data[self.dim_pos[0],:, :]
            export_size = (int(kwargs['max_dim'] * self.aspect[1]), int(kwargs['max_dim'] * self.aspect[2]))
        # axial
        elif kwargs['orient'] == 2:
            frame = self.data[:,self.dim_pos[1], :]
            export_size = (int(kwargs['max_dim'] * self.aspect[0]), int(kwargs['max_dim'] * self.aspect[2]))
        else:
            print("Unknown orientation")
            return None

        frame = self.apply_preview(frame)
        frame = self.frame_to_0_255(frame)
        frame = frame * self.visibility
        frame = self.resize(frame.astype(np.uint8), export_size)
        frame = self.applyColormap(frame)

        return frame

    def get_pixel_info(self, x_canvas, y_canvas, orient):
        # todo implement
        return 0.5,1.5,5.5,10.22


    # Handling position

    def incrementPosition(self, dim_order):
        if self.dim_pos[dim_order] < self.dim_to[dim_order] - 1:
            self.dim_pos[dim_order] += 1

    def decrementPosition(self, dim_order):
        if self.dim_pos[dim_order] > self.dim_from[dim_order]:
            self.dim_pos[dim_order] -= 1

    def posToMax(self, dim_order):
        self.dim_pos[dim_order] = self.dim_to[dim_order] - 1

    def posToMin(self, dim_order):
        self.dim_pos[dim_order] = self.dim_from[dim_order]

    # Visibility
    def isVisible(self):
        if self.visibility > 0.0:
            return "True"
        else:
            return "False"

    # Image manipulation
    def apply_preview(self,frame):
        clip_stretch_switch = self.app.contextTabs.imageViewTab.contrastEnhance.clip_stretch_var.get()
        if clip_stretch_switch is True:
            return np.clip(frame,self.min_preview,self.max_preview)
        else:
            range_data = self.max_data - self.min_data
            range_preview = self.max_preview - self.min_preview
            return self.min_preview + (range_preview * (frame - self.min_data) / range_data)

    def frame_to_0_255(self, frame):
        255.0 * frame / self.max_data
        return 255.0 * frame / self.max_data

    def applyColormap(self,frame):
        return cv2.applyColorMap(frame, self.colormap)

    def resize(self,frame, export_size):
        return cv2.resize(frame, export_size, interpolation=cv2.INTER_LINEAR)

    def hist_norm(self):
        # num_bins = int(np.log(np.prod(self.dim_size)))
        num_bins = 256
        data = self.data
        imhist, bins= np.histogram(data.flatten(), num_bins, normed=True)
        cdf = imhist.cumsum()  # cumulative distribution function
        cdf = 255 * cdf / cdf[-1]  # normalize

        # use linear interpolation of cdf to find new pixel values
        data_= np.interp(data.flatten(), bins[:-1], cdf)

        self.data = data_.reshape(data.shape)

        self.min_data = np.amin(self.data)
        self.max_data = np.amax(self.data)

        self.min_preview = self.min_data
        self.max_preview = self.max_data

    def apply_enhance(self):
        clip_stretch_switch = self.app.contextTabs.imageViewTab.contrastEnhance.clip_stretch_var.get()
        if clip_stretch_switch is True:
            self.data = np.clip(self.data,self.min_preview,self.max_preview)
            self.min_data = np.amin(self.data)
            self.max_data = np.amax(self.data)
            self.min_preview = self.min_data
            self.max_preview = self.max_data

        else:
            range_data = self.max_data - self.min_data
            range_preview = self.max_preview - self.min_preview
            self.data = range_preview * (self.data - self.min_data) / range_data
            self.min_data = np.amin(self.data)
            self.max_data = np.amax(self.data)
            self.min_preview = self.min_data
            self.max_preview = self.max_data


    def reload_data(self):
        for file in self.app.contentTabs.filesTab.filesList:
            if file.filename in self.tree_id:
                self.data = np.array(file.file[self.tree_id.split(".h5")[1]])
                self.data = np.squeeze(self.data) #todo remove this after debugging jcamdx parser
                self.min_data = np.amin(self.data)
                self.max_data = np.amax(self.data)
                self.min_preview = self.min_data
                self.max_preview = self.max_data
