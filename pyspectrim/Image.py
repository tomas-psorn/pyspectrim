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

        self.dim_from = [0,0,0]
        self.dim_from_phys = [0.0, 0.0, 0.0]

        self.dim_to = [self.dim_size[0], self.dim_size[1], self.dim_size[2]]
        self.dim_to_phys = [25.6,25.6, 20.0]

        self.dim_spacing = [0.1, 0.1, 0.5]

        self.dim_pos = [ int(self.dim_size[0]/2), int(self.dim_size[1]/2), int(self.dim_size[2]/2) ]

        self.visibility = 1.0
        self.colormap = cv2.COLORMAP_BONE

        self.min = np.amin(self.data)
        self.max = np.amax(self.data)

    # properties
    @property
    def colormap(self):
        return self.__colormap

    @colormap.setter
    def colormap(self,var):
        if var == 'gray':
            self.__colormap = cv2.COLORMAP_BONE
        elif var == 'cold':
            self.__colormap = cv2.COLORMAP_COOL
        elif var == 'winter':
            self.__colormap = cv2.COLORMAP_WINTER
        else:
            self.__colormap = cv2.COLORMAP_BONE
            logging.debug("Colormap: {} unknown".format(var))


    # getters
    def getFrame(self, **kwargs):

        if kwargs['orient'] == 0:
            frame = self.data[:, :, self.dim_pos[2]]
        elif kwargs['orient'] == 1:
            frame = self.data[:, self.dim_pos[1], :]
        elif kwargs['orient'] == 2:
            frame = self.data[self.dim_pos[0], :, :]
        else:
            print("Unknown orientation")
            return None

        frame = self.frameToUint8(frame)

        frame = self.applyColormap(frame)

        return frame


    def getVisibility(self):
        return self.visibility

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

    def setVisibility(self, value):
            self.visibility = value

    # Image manipulation
    def frameToUint8(self, frame):
        frame = 255.0 * frame / self.max
        return frame.astype(np.uint8)

    def applyColormap(self,frame):
        return cv2.applyColorMap(frame, self.colormap)


