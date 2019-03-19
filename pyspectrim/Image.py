import tkinter as tk
from tkinter import ttk

import numpy as np
import h5py

class Image():
    def __init__(self, dataset):

        self.data = np.array(dataset)
        self.data = np.squeeze(self.data)
        print(self.data.shape)

        self.frame = self.data[:,:,12]



