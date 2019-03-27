from pyspectrim.FilesTab import getObjectId

import tkinter as tk
from tkinter import ttk

import numpy as np
import h5py

class Image():
    def __init__(self, dataset):

        self.tree_id = getObjectId(dataset)
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

    def getFrame_ax(self):

        frame = self.data[:,:,self.dim_pos[2]]
        frame = 255*(frame - np.amin(frame))/np.amax(frame)
        frame = frame.astype(int)

        return frame

    def getFrame_cor(self):
        return -1

    def getFrame_trans(self):
        return -1

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

    def setVisible(self):
        self.visibility = 1.0

    def setInvisible(self):
        self.visibility = 0.0

