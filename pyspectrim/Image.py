from pyspectrim.File import getH5Id

import logging

import tkinter as tk
from tkinter import ttk

import cv2
import numpy as np
import h5py

import matplotlib.pyplot as plt

class Image():
    def __init__(self, dataset):

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

        self.min = np.amin(self.data)
        self.max = np.amax(self.data)

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

        frame = self.frame_to_0_255(frame)
        frame = frame * self.visibility
        frame = self.resize(frame.astype(np.uint8), export_size)
        frame = self.applyColormap(frame)

        return frame

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
    def frame_to_0_255(self, frame):
        255.0 * frame / self.max
        return 255.0 * frame / self.max

    def applyColormap(self,frame):
        return cv2.applyColorMap(frame, self.colormap)

    def resize(self,frame, export_size):
        return cv2.resize(frame, export_size, interpolation=cv2.INTER_LINEAR)


