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

        self.pos_ind = [ int(self.dim_size[0]/2), int(self.dim_size[1]/2), int(self.dim_size[2]/2) ]
        self.from_ind = [0, 0, 0]
        self.to_ind = [self.dim_size[0], self.dim_size[1], self.dim_size[2]]

        self.visibility = 1.0

    def getFrame(self):

        frame = self.data[:,:,self.pos_ind[2]]
        frame = 255*(frame - np.amin(frame))/np.amax(frame)
        frame = frame.astype(int)

        return frame



