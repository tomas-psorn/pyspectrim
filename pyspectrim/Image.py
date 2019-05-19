from pyspectrim.File import Scan, Reco


from pyspectrim.enums import *

import logging

import tkinter as tk
from tkinter import ttk

import cv2
import numpy as np
from scipy import interpolate
import h5py

from enum import Enum

import matplotlib.pyplot as plt

class Image(object):
    def __init__(self, app=None, **kwargs):

        self.app = app
        self.tree_id = kwargs['tree_id']
        self.tree_name = self.app.contentTabs.filesTab.filesTree.item(self.tree_id)['text']

        if 'dataset' in kwargs:
            self.init_from_dataset(kwargs)
        elif 'reco' in kwargs:
            self.init_from_reco(kwargs)
        elif 'scan' in kwargs:
            self.init_from_scan(kwargs)

        # set initial browsing position, spatial dimenstions to the middle, all other to zero
        self.dim_pos = (self.dim_size / 2).astype(np.int32)
        self.dim_pos[3:] = 0

        # indexed boundaries
        self.dim_from_ind = np.zeros((self.ndim,))
        self.dim_to_ind = self.dim_from_ind + self.dim_size

        self._visibility = 1.0
        self.alpha_mask = None
        self._colormap = COLOR_MAP.GRAY.value

        self.reset_min_max_()

        self.reset_enhance()

        self.aspect = self.dim_phys_extent[0:3] / np.amax(self.dim_phys_extent[0:3])


    def init_from_dataset(self, kwargs):

        dataset = kwargs['dataset']
        self.data = np.array(dataset)

        self.dim_size = np.array(self.data.shape)
        self.ndim = len(self.dim_size)

        # dim_from
        try:
            dim_from = np.array(dataset.attrs['dim_from'])
        except:
            dim_from = np.zeros(shape=(self.ndim,))
        self.dim_from_phys = dim_from

        # dim_label
        try:
            dim_label = dataset.attrs['dim_label'].decode("utf-8").split(',')
        except:
            dim_label = ['x', 'y', 'z']
            for i in range(0, self.ndim - 3):
                dim_label.append('NA')
        self.dim_label = dim_label

        # dim_desc
        try:
            dim_desc = dataset.attrs['dim_desc'].decode("utf-8").split(',')
        except:
            dim_desc = ['spatial', 'spatial', 'spatial']
            for i in range(0, self.ndim - 3):
                dim_desc.append('NA')
        self.dim_desc = dim_desc

        # dim_extent
        try:
            dim_extent = np.array(dataset.attrs['dim_extent'])
        except:
            dim_extent = self.dim_size.astype(float)
        self.dim_phys_extent = dim_extent

        # dim_units
        try:
            dim_units =  dataset.attrs['dim_units'].decode("utf-8").split(',')
        except:
            dim_units = []
            for i in range(0, self.ndim):
                dim_units.append('NA')
        self.dim_units = dim_units

        # data_units
        try:
            data_units =  dataset.attrs['data_units'].decode("utf-8")
        except:
            data_units = None
        self.data_units = data_units

        self.dim_to_phys = self.dim_from_phys + self.dim_phys_extent
        self.dim_spacing = self.dim_phys_extent / self.dim_size
        self.slice_orient = None
        self.slice_pos = None

        self.axes = []

        for i in range(0,self.ndim):
            self.axes.append(self.calc_axis(from_=self.dim_from_phys[i], dim=self.dim_size[i], spacing=self.dim_spacing[i]))

    def init_from_reco(self, kwargs):

        reco = kwargs['reco'] # reco object just in local scope
        pars = reco.visu_pars.getDict()

        self.data = reco.data2dseq

        VisuFGOrderDescDim = None
        VisuFGOrderDesc = None

        try:
            VisuFGOrderDescDim = pars['VisuFGOrderDescDim']
            VisuFGOrderDesc = pars['VisuFGOrderDesc']
        except:
            pass

        # these are all possible parameters
        self.ndim = 0  # total number of dimensions
        self.data_units = None  # unit of data values in string
        self.dim_size = np.empty(shape=(0, 0), dtype=np.int32)  # size of each dimension
        self.dim_phys_extent = np.empty(shape=(0, 0), dtype=np.float32)  # physical extent of each dimension
        self.dim_from_phys = np.empty(shape=(0, 0), dtype=np.float32)
        self.dim_to_phys = np.empty(shape=(0, 0), dtype=np.float32)
        self.dim_spacing = np.empty(shape=(0, 0), dtype=np.float32)
        self.dim_units = []  # string of each dimension's unit
        self.dim_desc = []  # category of each dimension {spatial, spectroscopical, temporal, categorical}
        self.dim_label = []  # label of each dimension
        self.axes = []
        self.slice_orient = None
        self.slice_pos = None

        # spectroscopic datasets do not have spatial dimensions
        try:
            self.slice_orient = pars['VisuCoreOrientation']
            self.slice_pos = pars['VisuCorePosition']
        except:
            pass

        # only certain datasets have units
        try:
            # todo is it necessary to do the replace?
            self.data_units = pars['VisuCoreDataUnits'].replace('<', '').replace('>', '')
        except:
            self.data_units = 'a. u.'

        # number of dimensions
        self.ndim = int(pars["VisuCoreDim"])

        # iterate trough visu core
        for i in range(0, self.ndim):
            self.dim_size = np.append(self.dim_size, int(pars["VisuCoreSize"][i]))
            self.dim_phys_extent = np.append(self.dim_phys_extent, float(pars["VisuCoreExtent"][i]))
            self.dim_spacing = np.append(self.dim_spacing, self.dim_phys_extent[i] / self.dim_size[i])
            self.dim_units.append(pars["VisuCoreUnits"][i])
            self.dim_desc.append(pars["VisuCoreDimDesc"][i])

            # here i presume, that visu core can only have 3 dimensions and only be spatial or spectral
            if self.dim_desc[i] == 'spatial':
                if i == 0:
                    self.dim_label.append('x')
                    self.dim_from_phys = np.append(self.dim_from_phys, pars['VisuCorePosition'][0][0])

                elif i == 1:
                    self.dim_label.append('y')
                    self.dim_from_phys = np.append(self.dim_from_phys, pars['VisuCorePosition'][0][1])
                elif i == 2:
                    # this branch implies 3D scan, 3D dimension of pseudo 3D experiments is covered by
                    # FG_SLICE framegroup, see bellow
                    self.dim_label.append('z')
                    self.dim_from_phys = np.append(self.dim_from_phys, pars['VisuCorePosition'][0][2])

            elif self.dim_desc == 'spectroscopic':
                if i == 0:
                    self.dim_label.append('spectrum')
                elif i == 1:
                    self.dim_label.append('spectrum_2')
                elif i == 2:
                    self.dim_label.append('spectrum_2')
            else:
                raise KeyError('Bad thing happened')

            self.dim_to_phys = np.append(self.dim_to_phys, self.dim_from_phys[i] + self.dim_phys_extent[i])
            self.axes.append(self.calc_axis(from_=self.dim_from_phys[i], dim=self.dim_size[i], spacing=self.dim_spacing[i]))

        # todo solve this
        # tmp = self.dim_size[0]
        # self.dim_size[0] = self.dim_size[1]
        # self.dim_size[1] = tmp

        # iterate trough frame groups
        if VisuFGOrderDescDim:
            for i in range(0, pars["VisuFGOrderDescDim"]):

                if pars["VisuFGOrderDesc"][i][1] == "FG_SLICE":
                    self.dim_size = np.append(self.dim_size, int(pars["VisuFGOrderDesc"][i][0]))
                    self.dim_units.append('mm')
                    self.dim_desc.append('spatial')
                    self.dim_label.append('z')
                    self.axes.append(pars['VisuCorePosition'][:, 2])
                    self.dim_from_phys = np.append(self.dim_from_phys, self.axes[-1][0])
                    self.dim_to_phys = np.append(self.dim_to_phys, self.axes[-1][-1])
                    self.dim_phys_extent = np.append(self.dim_phys_extent, np.abs(np.subtract(self.axes[-1][0], self.axes[-1][-1])))
                    self.dim_spacing = np.append(self.dim_spacing, self.dim_phys_extent[-1] / self.dim_size[-1])
                elif pars["VisuFGOrderDesc"][i][1] == "FG_COMPLEX":
                    self.ndim -= 1 # it will be removed, but the counter will be implemented

                    position_real = ()
                    position_imag = ()

                    for j in range(0,len(self.data.shape)):
                        if j == i + pars['VisuCoreDim']:
                            position_real += (0,)
                            position_imag += (1,)
                        else:
                            position_real += (slice( 0, self.data.shape[j]),)
                            position_imag += (slice(0, self.data.shape[j]),)

                    self.data = np.squeeze(self.data[position_real]) + 1j * np.squeeze(self.data[position_imag])

                elif pars["VisuFGOrderDesc"][i][1] == "FG_MOVIE":
                    self.dim_size = np.append(self.dim_size, int(pars["VisuFGOrderDesc"][i][0]))
                    self.dim_phys_extent = np.append(self.dim_phys_extent,
                                                    pars["VisuAcqRepetitionTime"] * pars["VisuFGOrderDesc"][i][0])
                    self.dim_from_phys = np.append(self.dim_from_phys, 0.0)
                    self.dim_to_phys = np.append(self.dim_to_phys, self.dim_phys_extent)
                    self.dim_spacing = np.append(self.dim_spacing, self.dim_phys_extent[i] / self.dim_size[i])
                    self.axes.append(
                        self.calc_axis(from_=self.dim_from_phys[i], dim=self.dim_size[i], spacing=self.dim_spacing[i], shift=False))
                    self.dim_units.append('diff_comment')
                    self.diff_comment = np.string_(pars["VisuFGElemComment"])
                    self.dim_desc.append('categorical')
                    self.dim_label.append('diffusion')

                elif pars["VisuFGOrderDesc"][i][1] == "FG_CYCLE":
                    self.dim_size = np.append(self.dim_size, int(pars["VisuFGOrderDesc"][i][0]))
                    self.dim_phys_extent = np.append(self.dim_phys_extent,
                                                    pars["VisuAcqRepetitionTime"] * pars["VisuFGOrderDesc"][i][0])
                    self.dim_from_phys = np.append(self.dim_from_phys, 0.0)
                    self.dim_to_phys = np.append(self.dim_to_phys, self.dim_phys_extent)
                    self.dim_spacing = np.append(self.dim_spacing, self.dim_phys_extent[i] / self.dim_size[i])
                    self.axes.append(
                        self.calc_axis(from_=self.dim_from_phys[i], dim=self.dim_size[i], spacing=self.dim_spacing[i], shift=False))
                    self.dim_units.append('ms')
                    self.dim_desc.append('temporal')
                    self.dim_label.append('time series')

                elif pars["VisuFGOrderDesc"][i][1] == "FG_COIL":
                    self.dim_size = np.append(self.dim_size, int(pars["VisuFGOrderDesc"][i][0]))
                    self.dim_phys_extent = np.append(self.dim_phys_extent, float(pars["VisuFGOrderDesc"][i][0]))
                    self.dim_from_phys = np.append(self.dim_from_phys, 0.0)
                    self.dim_to_phys = np.append(self.dim_to_phys, self.dim_phys_extent)
                    self.dim_units.append('coil_comment')
                    self.coil_comment = np.empty(shape=(0, 0), dtype=np.string_)
                    for i in range(0, int(pars["VisuFGOrderDesc"][i][0])):
                        self.coil_comment = np.append(self.coil_comment, np.string_('coil {}'.format(i + 1)))
                    self.dim_spacing = np.append(self.dim_spacing, self.dim_phys_extent[i] / self.dim_size[i])
                    self.axes.append(
                        self.calc_axis(from_=self.dim_from_phys[i], dim=self.dim_size[i], spacing=self.dim_spacing[i], shift=False))
                    self.dim_desc.append('categorical')
                    self.dim_label.append('coils')
                elif pars['VisuFGOrderDesc'][i][1]== 'FG_ISA':
                    maps_dim_order = i + self.ndim
                    # these entries are later forgotten
                    self.dim_size = np.append(self.dim_size, int(pars["VisuFGOrderDesc"][i][0]))
                    self.dim_phys_extent = np.append(self.dim_phys_extent, float(pars["VisuFGOrderDesc"][i][0]))
                    self.dim_from_phys = np.append(self.dim_from_phys, 0.0)
                    self.dim_to_phys = np.append(self.dim_to_phys, self.dim_phys_extent)
                    self.dim_spacing = np.append(self.dim_spacing, self.dim_phys_extent[i] / self.dim_size[i])
                    self.axes.append(
                        self.calc_axis(from_=self.dim_from_phys[i], dim=self.dim_size[i], spacing=self.dim_spacing[i], shift=False))
                    self.dim_units.append('')
                    self.dim_desc.append('categorical')
                    self.dim_label.append('maps')
                else:
                    raise KeyError('Unknown FG identifier')

                self.ndim += 1

        else:
            pass

        # for parametric maps calculated in postprocessing
        if 'proc_code' in kwargs:
            if maps_dim_order is None:
                logging.debug('maps_dim_order not defined')
                raise ValueError
            proc_dim_order = int(kwargs['proc_code'].replace('proc_',''))

            index = ()

            for i in range(0, self.ndim):
                if i == maps_dim_order:
                    index = index + (proc_dim_order,)
                else:
                    index = index + (slice(0,self.dim_size[i]),)

            self.data = self.data[index] # exctract given map

            # delete reduntant dim parameters
            self.ndim -=1
            self.dim_size = np.delete(self.dim_size, maps_dim_order)
            self.dim_phys_extent = np.delete(self.dim_phys_extent, maps_dim_order)
            self.dim_from_phys = np.delete(self.dim_from_phys, maps_dim_order)
            self.dim_to_phys = np.delete(self.dim_to_phys, maps_dim_order)
            self.dim_spacing = np.delete(self.dim_spacing, maps_dim_order)

            del self.axes[maps_dim_order]
            del self.dim_units[maps_dim_order]
            del self.dim_desc[maps_dim_order]
            del self.dim_label[maps_dim_order]

    def init_from_scan(self, kwargs):
        scan = kwargs['scan']  # reco object just in local scope
        method = scan.method.getDict()
        acqp = scan.acqp.getDict()

        # basic reshape
        # format, bits, dimBlock, dimZ, dimR, dimAcq0, dimAcqHigh, dimCh, dimA = scan.fidBasicInfo()
        # self.data = np.reshape(scan.fid, [scan.fid.shape[0], scan.fid.shape[1], dimAcqHigh, dimZ, dimR],order='F')

        # put the coil dimension to last position
        # dims = np.array(range(len(self.data.shape)))
        # tmp = dims[0]
        # dims[0:-1] = dims[1:]
        # dims[-1] = tmp
        # self.data = np.transpose(self.data,tuple(dims))

        self.data = scan.fid

        self.ndim = 0
        self.data_units = 'a. u.'
        self.dim_size = np.empty(shape=(0,),dtype=np.int32)
        self.dim_phys_extent = np.empty(shape=(0,),dtype=np.float32)
        self.dim_from_phys = np.empty(shape=(0,),dtype=np.float32)
        self.dim_to_phys = np.empty(shape=(0,), dtype=np.float32)
        self.dim_spacing = np.empty(shape=(0,), dtype=np.float32)

        self.dim_units = []
        self.dim_desc = []
        self.dim_label = []

        self.slice_orient = None
        self.slice_pos = None


        for i in range(acqp['ACQ_dim']):
            self.ndim += 1
            self.dim_size = np.append(self.dim_size, int(method['PVM_EncMatrix'][i]))
            self.dim_spacing = np.append(self.dim_spacing, 1/acqp['ACQ_fov'][i])
            self.dim_phys_extent = np.append(self.dim_phys_extent, np.pi)
            self.dim_from_phys = np.append(self.dim_from_phys, -1.0 * self.dim_spacing[i] * self.dim_size[i] / 2)
            self.dim_to_phys = np.append(self.dim_to_phys, self.dim_spacing[i] * ((self.dim_size[i] / 2) - 1))
            self.dim_units.append('rad/m')
            self.dim_desc.append('kspace')

            if i == 0:
                self.dim_label.append('kx')
                self.x_axis = np.linspace(self.dim_from_phys[i], self.dim_to_phys[i], self.dim_size[i])
            elif i == 1:
                self.dim_label.append('ky')
                self.y_axis = np.linspace(self.dim_from_phys[i], self.dim_to_phys[i], self.dim_size[i])
            elif i == 2:
                self.dim_label.append('kz')
                self.y_axis = np.linspace(self.dim_from_phys[i], self.dim_to_phys[i], self.dim_size[i])


        for i in range(self.ndim, len(self.data.shape)):
            # slice, 3D acquisitions are covered in previous loop
            if i == 2:
                self.ndim += 1
                self.dim_size = np.append(self.dim_size, self.data.shape[i])
                self.slice_pos = acqp['ACQ_slice_offset']
                self.dim_phys_extent = np.append(self.dim_phys_extent, np.subtract(self.slice_pos[0],self.slice_pos[-1]))
                self.dim_from_phys = np.append(self.dim_from_phys, self.slice_pos[0])
                self.dim_to_phys = np.append(self.dim_to_phys, self.dim_from_phys[-1] + self.dim_phys_extent[-1])
                self.dim_spacing = np.append(self.dim_spacing, self.dim_phys_extent[-1]/self.dim_size[-1])
                self.dim_units.append('mm')
                self.dim_desc.append('spatial')
                self.dim_label.append('z')
            # echo
            elif i == 3 and self.data.shape[i] > 1:
                self.ndim += 1
                self.dim_size = np.append(self.dim_size, self.data.shape[i])
                self.dim_to_phys = np.append(self.dim_to_phys, method['EffectiveTE'][-1])
                self.dim_from_phys = np.append(self.dim_from_phys, method['EffectiveTE'][0])
                self.dim_phys_extent = np.append(self.dim_phys_extent,
                                                 self.dim_from_phys - self.dim_to_phys)
                self.dim_spacing = np.append(self.dim_spacing, self.dim_phys_extent[-1] / self.dim_size[-1])
                self.dim_units.append('ms')
                self.dim_desc.append('temporal')
                self.dim_label.append('TE')
            # repetition
            elif i == 4 and self.data.shape[i] > 1:
                self.ndim += 1
                self.dim_size = np.append(self.dim_size, self.data.shape[i])
                self.dim_phys_extent = np.append(self.dim_phys_extent, acqp['NR'] * acqp['ACQ_repetition_time'] / 1000.0)
                self.dim_to_phys = np.append(self.dim_to_phys, self.dim_from_phys[-1] + self.dim_phys_extent[-1])
                self.dim_spacing = np.append(self.dim_spacing, self.dim_phys_extent[-1] / self.dim_size[-1])
                self.dim_from_phys = np.append(self.dim_from_phys, 0.0)
                self.dim_units.append('s')
                self.dim_desc.append('temporal')
                self.dim_label.append('t')
            # coil
            elif i == 5 and self.data.shape[i] > 1:
                self.ndim += 1
                self.dim_size = np.append(self.dim_size, self.data.shape[i])
                self.dim_phys_extent = np.append(self.dim_phys_extent, float(method['PVM_EncAvailReceivers']))
                self.dim_from_phys = np.append(self.dim_from_phys, 0.0)
                self.dim_to_phys = np.append(self.dim_to_phys, self.dim_from_phys[-1] + self.dim_phys_extent[-1])
                self.dim_spacing = np.append(self.dim_spacing, self.dim_phys_extent[-1] / self.dim_size[-1])
                self.dim_units.append('coil_comment')
                self.coil_comment = []
                for i in range(method['PVM_EncAvailReceivers']):
                    self.coil_comment.append('coil {}'.format(i))
                self.dim_desc.append('categorical')
                self.dim_label.append('coil')

        # remove singleton dimensions
        self.data = np.squeeze(self.data)

    def reset_min_max_(self):
        self.min_data = np.zeros((4,))
        self.max_data = np.zeros((4,))

        if 'complex' in self.data.dtype.name:
            self.min_data[0] = np.amin(np.abs(self.data))
            self.min_data[1] = np.amin(np.angle(self.data))
            self.min_data[2] = np.amin(np.real(self.data))
            self.min_data[3] = np.amin(np.imag(self.data))

            self.max_data[0] = np.max(np.abs(self.data))
            self.max_data[1] = np.max(np.angle(self.data))
            self.max_data[2] = np.max(np.real(self.data))
            self.max_data[3] = np.max(np.imag(self.data))

        else:
            self.min_data[0] = np.amin(np.abs(self.data))
            self.min_data[1:3] = 0.0

            self.max_data[0] = np.max(np.abs(self.data))
            self.max_data[1:3] = 0.0

        self.min_preview = self.min_data
        self.max_preview = self.max_data



    def calc_axis(self, from_=None, dim=None, spacing=None, shift = True ):
        # shift is used to place the coordinate into the center of the pixel
        if shift:
            shift = spacing / 2.0
        else:
            shift = 0.0

        axis = np.zeros(dim)

        for i in range(0, dim):
            axis[i] = from_ + shift + i * spacing

        return axis


    def __getitem__(self, key):
        return getattr(self, key)

    # properties
    @property
    def colormap(self):
        return self._colormap

    @colormap.setter
    def colormap(self,value):
        self._colormap = value

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
    def get_axes(self, orient=None, ind_phys=None):
        if orient == VIEW_ORIENT.TRANS.value:
            if ind_phys == IND_PHYS.PHYS.value:
                return self.axes[0], self.axes[1]
            else:
                x_im = self.axes[0].copy()
                y_im = self.axes[1].copy()
                aspect_x = self.aspect[0]
                aspect_y = self.aspect[0]
        elif orient == VIEW_ORIENT.SAG.value:
            if ind_phys == IND_PHYS.PHYS.value:
                return self.axes[1], self.axes[2]
            else:
                x_im = self.axes[1].copy()
                y_im = self.axes[2].copy()
                aspect_x = self.aspect[1]
                aspect_y = self.aspect[2]
        elif orient == VIEW_ORIENT.CORR.value:
            if ind_phys == IND_PHYS.PHYS.value:
                return self.axes[0], self.axes[2]
            else:
                x_im = self.axes[0].copy()
                y_im = self.axes[2].copy()
                aspect_x = self.aspect[0]
                aspect_y = self.aspect[2]

        x_im -= np.amin(x_im)
        y_im -= np.amin(y_im)

        if np.amax(x_im) > 0:
            x_im /= np.amax(x_im)

        if np.amax(y_im) > 0:
            y_im /= np.amax(y_im)

        x_im *= aspect_x
        y_im *= aspect_y

        x_im -= np.amax(x_im) / 2.0
        y_im -= np.amax(y_im) / 2.0

        return x_im, y_im

    def get_location_low(self, orient=None):
        if orient == VIEW_ORIENT.TRANS.value:
            return ( slice( 0, self.dim_size[0] ), slice( 0, self.dim_size[1] ), self.dim_pos[2] )
        elif orient == VIEW_ORIENT.SAG.value:
            return (self.dim_pos[0], slice(0, self.dim_size[1]), slice(0, self.dim_size[2]))
        elif orient == VIEW_ORIENT.CORR.value:
            return (slice(0, self.dim_size[0]), self.dim_pos[1], slice(0, self.dim_size[2]))

    def get_frame(self, enhance=True, **kwargs):

        ind_phys_switch = IND_PHYS(self.app.contextTabs.imageViewTab.indPhysSwitch.get()).value
        complex_part_switch = COMPLEX_PART(self.app.contextTabs.imageViewTab.complex_part_switch.get()).value

        x_im, y_im = self.get_axes(orient=kwargs['orient'], ind_phys=ind_phys_switch)

        location_low = self.get_location_low(orient=kwargs['orient'])
        location_high = tuple(self.dim_pos[3:])

        frame = self.data[location_low+ location_high]

        if complex_part_switch == COMPLEX_PART.ABS.value:
            min_preview = self.min_preview[0]
            max_preview = self.max_preview[0]
            frame = np.abs(frame)
        elif complex_part_switch == COMPLEX_PART.PHASE.value:
            min_preview = self.min_preview[1]
            max_preview = self.max_preview[1]
            frame = np.angle(frame)
        elif complex_part_switch == COMPLEX_PART.RE.value:
            min_preview = self.min_preview[2]
            max_preview = self.max_preview[2]
            frame = np.real(frame)
        else:
            min_preview = self.min_preview[3]
            max_preview = self.max_preview[3]
            frame = np.imag(frame)

        q = np.array([kwargs['querry_x'], kwargs['querry_y']])
        q = np.transpose(q, (1, 2, 0))

        # interpolate alpha mask
        if self.alpha_mask is not None:
            alpha = self.alpha_mask[location_low]

            # IMROT90
            if kwargs['orient'] == VIEW_ORIENT.TRANS.value:
                alpha = np.transpose(alpha, (1, 0))

            alpha = interpolate.interpn((x_im, y_im), alpha, q, method='linear', bounds_error=False, fill_value=0.0)
            alpha = 255.0*alpha

        frame = interpolate.interpn((x_im,y_im), frame, q, method='linear', bounds_error=False, fill_value =min_preview  )

        # if enhance:
        #     frame = self.apply_enhance_(frame=frame)

        # todo change to apply_enhancement
        # frame = self.apply_preview(frame)
        frame = self.frame_to_0_255(frame=frame, min_= min_preview, max_=max_preview)
        frame = frame * self.visibility
        frame = frame.astype(np.uint8)
        # todo this has to be done on cinema level
        frame = self.applyColormap(frame)

        if self.alpha_mask is not None:
            b, g, r = cv2.split(frame)
            frame =  cv2.merge((b, r, g, alpha.astype(np.uint8)))

        return frame

    def get_signal(self, dim_order=None):
        if not dim_order:
            logging.debug("No dim_order")
            return

        index = tuple(self.dim_pos[0:dim_order]) + (slice(0,self.dim_size[dim_order]),) + tuple(self.dim_pos[dim_order+1:])

        y = self.data[index]

        x = np.linspace(self.dim_from_phys[dim_order], self.dim_to_phys[dim_order], self.dim_size[dim_order] )

        y_label = None

        x_label = 't [s]'

        legend = '{} dim:{}'.format(self.tree_name, dim_order)

        return x, y, x_label, y_label, legend

    def get_pixel_info(self, x=None, y=None, orient=None):
        # x,y, and orient are used when querying info about position on canvas

        label = self.dim_label
        pos_ind = self.dim_pos

        if x and y:
            if orient == VIEW_ORIENT.TRANS.value:
                # IMROT90
                pos_ind[0] = y
                pos_ind[1] = x
            elif orient == VIEW_ORIENT.SAG.value:
                pos_ind[1] = x
                pos_ind[2] = y
            elif orient == VIEW_ORIENT.CORR.value:
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
        if self.dim_pos[dim_order] < self.dim_to_ind[dim_order] - 1:
            self.dim_pos[dim_order] += 1

    def decrementPosition(self, dim_order):
        if self.dim_pos[dim_order] > self.dim_from_ind[dim_order]:
            self.dim_pos[dim_order] -= 1

    def posToMax(self, dim_order):
        self.dim_pos[dim_order] = self.dim_to_ind[dim_order] - 1

    def posToMin(self, dim_order):
        self.dim_pos[dim_order] = self.dim_from_ind[dim_order]

    # Visibility
    def isVisible(self):
        if self.visibility > 0.0:
            return "True"
        else:
            return "False"

    # Image manipulation
    def enhance_preview(self,frame):
        clip_stretch_switch = self.app.contextTabs.imageViewTab.contrastEnhance.clip_stretch_var.get()
        if clip_stretch_switch is True:
            return np.clip(frame,self.min_preview,self.max_preview)
        else:
            range_data = self.max_data - self.min_data
            range_preview = self.max_preview - self.min_preview
            return self.min_preview + (range_preview * (frame - self.min_data) / range_data)

    def enhance_data(self, log=False, pow=False, window=False, **kwargs):
        if log:
            self.data = np.log(self.data)
            self.reset_min_max_()
            self.app.cinema.draw()
        elif pow:
            self.data = np.power(self.data,kwargs['pow_coef'])
            self.reset_min_max_()
            self.app.cinema.draw()
        elif window:
            pass


    def frame_to_0_255(self, frame=None, min_ = None, max_=None):
        range = max_ - min_
        return 255.0 * (frame-min_) / range


    def applyColormap(self,frame):
        return cv2.applyColorMap(frame, self.colormap)

    def apply_visibility(self,frame=None, alpha=None):
        # b, g, r = cv2.split(frame)
        return cv2.merge((frame, frame, frame, alpha))

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
            self.reset_min_max_()

        else:
            range_data = self.max_data - self.min_data
            range_preview = self.max_preview - self.min_preview
            self.data = range_preview * (self.data - self.min_data) / range_data
            self.reset_min_max_()

    def apply_enhance_(self, frame=None):
        if self.point_trans == POINT_TRANS.POW.value:
            exponents = np.ones_like(frame) * self.point_trans_coef
            frame = np.float_power(frame, exponents)

        self.min_preview = np.amin(frame)
        self.max_preview = np.amax(frame)

        return frame

    def set_enhance(self, **kwargs):
        if 'pow' in kwargs:
            self.point_trans = POINT_TRANS.POW.value
            self.point_trans_coef = kwargs['pow']

    def reload_data(self):
        for file in self.app.contentTabs.filesTab.filesList:
            if str(file.filename) in self.tree_id:
                if file.__class__.__name__ == 'FileHdf5':
                    self.data = np.array(file.file[self.tree_id.split(".h5")[1]])
                    self.data = np.squeeze(self.data) #todo remove this after debugging jcamdx parser
                elif file.__class__.__name__ == 'FileBruker':
                    tmp = self.tree_id.split('.')
                    code = tmp[-1]
                    path = ''.join(tmp[0:-1])

                    # this is clumsy, but due to proc virtualization, it's necessary
                    if 'reco' in code:
                        image = Image(app=self.app, reco=Reco(path=path), tree_id=self.tree_id)

                    self.data = image.data

                self.reset_min_max_()

                self.alpha_mask = None


    def reset_enhance(self):
        self.point_trans = POINT_TRANS.LIN.value
        self.point_trans_coef = 1.0

        self.min_preview = self.min_data
        self.max_preview = self.max_data

    def encode_visibility(self, image_to_enc=None):
        alpha = image_to_enc.data
        range = np.amax(alpha) - np.amin(alpha)
        alpha = (alpha - np.amin(alpha)) / range
        self.alpha_mask = 1.0 - alpha
