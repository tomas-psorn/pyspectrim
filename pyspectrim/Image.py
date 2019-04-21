from pyspectrim.File import getH5Id

from pyspectrim.ImageViewTab import IND_PHYS, VIEW_ORIENT

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

        self.dim_size = np.array(dataset.attrs['dim_size'])
        self.ndim = dataset.attrs['ndim']

        self.dim_label = ['x','y','z']
        self.dim_from_phys = np.array(dataset.attrs['slice_pos'][0, :])

        for i in range(0,self.ndim-3):
            self.dim_label.append(dataset.attrs['dim_desc'][i+3].decode('UTF-8'))
            self.dim_from_phys = np.append(self.dim_from_phys, 0.0)

        self.dim_phys_extent = np.array(dataset.attrs['dim_extent'])
        self.dim_to_phys = self.dim_from_phys + self.dim_phys_extent

        self.dim_from = np.zeros(shape=(self.ndim,),dtype=np.int32)
        self.dim_to = self.dim_size

        # todo include slice spacing
        self.dim_spacing = self.dim_phys_extent / self.dim_size

        # there must be better way to do this
        self.dim_units = dataset.attrs['dim_units'].tolist()
        for i in range(0,len(self.dim_units)):
            self.dim_units[i] = self.dim_units[i].decode()


        for key in dataset.attrs:
            if "comment" in key:
                comment = dataset.attrs[key].tolist()
                for i in range(0,len(comment)):
                    comment[i] = comment[i].decode()

                setattr(self, key, comment)

        # set initial browsing position, spatial dimenstions to the middle, all other to zero
        self.dim_pos = (self.dim_size / 2).astype(np.int32)
        self.dim_pos[3:] = 0

        self._visibility = 1.0
        self._colormap = cv2.COLORMAP_BONE

        self.min_data = np.amin(self.data)
        self.max_data = np.amax(self.data)

        self.min_preview = self.min_data
        self.max_preview = self.max_data

        self.aspect = self.dim_phys_extent / np.amax(self.dim_phys_extent)

    def __getitem__(self, key):
        return getattr(self, key)



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

        ind_phys_switch = IND_PHYS(self.app.contextTabs.imageViewTab.indPhysSwitch.get()).name

        if ind_phys_switch == 'IND':
            location_high = tuple(self.dim_pos[3:])
            # coronal
            if kwargs['orient'] == 0:
                location = ( slice( 0, self.dim_size[0] ), slice( 0, self.dim_size[1] ), self.dim_pos[2] ) + location_high
            # sagital
            elif kwargs['orient'] == 1:
                location = (self.dim_pos[0], slice(0, self.dim_size[1]), slice(0, self.dim_size[2])) + location_high
            # axial
            elif kwargs['orient'] == 2:
                location = (slice(0, self.dim_size[0]), self.dim_pos[1], slice(0, self.dim_size[2])) + location_high
            else:
                print("Unknown orientation")
                return None
            frame = self.data[location]

        # todo change to apply_enhancement
        frame = self.apply_preview(frame)
        frame = self.frame_to_0_255(frame)
        frame = frame * self.visibility
        frame = frame.astype(np.uint8)
        # todo this has to be done on cinema level
        # frame = self.resize(frame, export_size)
        frame = self.applyColormap(frame)

        return frame

    def get_pixel_info(self, x=None, y=None, orient=None):
        # x,y, and orient are used when querying info about position on canvas

        label = self.dim_label
        pos_ind = self.dim_pos

        if x and y:
            if orient == VIEW_ORIENT.AX.value:
                pos_ind[0] = x
                pos_ind[1] = y
            elif orient == VIEW_ORIENT.TRANS.value:
                pos_ind[1] = x
                pos_ind[2] = y
            elif orient == VIEW_ORIENT.SAG.value:
                pos_ind[0] = x
                pos_ind[2] = y

        pos_ind = pos_ind.tolist()
        pos_phys = []
        units = []
        # we might want to change one of the values to string

        for dim in range(0,self.ndim):
            if "comment" in self.dim_units[dim]:
                comment_list = self[ self.dim_units[dim]]
                pos_phys.append(comment_list[self.dim_pos[dim]])
                units.append('')
            else:
                pos_phys.append( self.dim_from_phys[dim] + pos_ind[dim] * self.dim_spacing[dim] )
                units.append(self.dim_units[dim])

        return label, pos_phys, units


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
