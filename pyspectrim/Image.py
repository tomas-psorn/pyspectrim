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

        self.min_data = np.amin(self.data)
        self.max_data = np.amax(self.data)

        self.min_preview = self.min_data
        self.max_preview = self.max_data

        self.reset_enhance()

        self.aspect = self.dim_phys_extent / np.amax(self.dim_phys_extent)

        self.init_geometry()

    def init_from_dataset(self, kwargs):

        dataset = kwargs['dataset']
        self.data = np.array(dataset)

        self.dim_size = np.array(dataset.attrs['dim_size'])
        self.ndim = dataset.attrs['ndim']

        self.dim_label = ['x', 'y', 'z']
        self.dim_from_phys = np.array(dataset.attrs['slice_pos'][0, :])

        for i in range(0, self.ndim - 3):
            self.dim_label.append(dataset.attrs['dim_desc'][i + 3].decode('UTF-8'))
            self.dim_from_phys = np.append(self.dim_from_phys, 0.0)

        self.dim_phys_extent = np.array(dataset.attrs['dim_extent'])
        self.dim_to_phys = self.dim_from_phys + self.dim_phys_extent

        self.dim_from = np.zeros(shape=(self.ndim,), dtype=np.int32)
        self.dim_to = self.dim_size

        # todo include slice spacing
        self.dim_spacing = self.dim_phys_extent / self.dim_size

        # there must be better way to do this
        self.dim_units = dataset.attrs['dim_units'].tolist()
        for i in range(0, len(self.dim_units)):
            self.dim_units[i] = self.dim_units[i].decode()

        for key in dataset.attrs:
            if "comment" in key:
                comment = dataset.attrs[key].tolist()
                for i in range(0, len(comment)):
                    comment[i] = comment[i].decode()

                setattr(self, key, comment)

        self.dim_spacing = self.dim_phys_extent / self.dim_size

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
        self.dim_units = []  # string of each dimension's unit
        self.dim_desc = []  # category of each dimension {spatial, spectroscopical, temporal, categorical}
        self.dim_label = []  # label of each dimension
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
            self.dim_units.append(pars["VisuCoreUnits"][i])
            self.dim_desc.append(pars["VisuCoreDimDesc"][i])

            # here i presume, that visu core can only have 3 dimensions and only be spatial or spectral
            if self.dim_desc[i] == 'spatial':
                if i == 0:
                    self.dim_label.append('x')
                    self.dim_from_phys = np.append(self.dim_from_phys, pars['VisuCorePosition'][0][0])
                    self.dim_to_phys = np.append(self.dim_to_phys, self.dim_from_phys[i] + self.dim_phys_extent[i])
                    self.x_axis = np.linspace(self.dim_from_phys[i], self.dim_to_phys[i], self.dim_size[i])

                elif i == 1:
                    self.dim_label.append('y')
                    self.dim_from_phys = np.append(self.dim_from_phys, pars['VisuCorePosition'][0][1])
                    self.dim_to_phys = np.append(self.dim_to_phys, self.dim_from_phys[i] + self.dim_phys_extent[i])
                    self.y_axis = np.linspace(self.dim_from_phys[i], self.dim_to_phys[i], self.dim_size[i])
                elif i == 2:
                    # this branch implies 3D scan, 3D dimension of pseudo 3D experiments is covered by
                    # FG_SLICE framegroup, see bellow
                    self.dim_label.append('z')
                    self.dim_from_phys = np.append(self.dim_from_phys, pars['VisuCorePosition'][0][2])
                    self.dim_to_phys = np.append(self.dim_to_phys, self.dim_from_phys[i] + self.dim_phys_extent[i])
                    self.z_axis = np.linspace(self.dim_from_phys[i], self.dim_to_phys[i], self.dim_size[i])

            elif self.dim_desc == 'spectroscopic':
                if i == 0:
                    self.dim_label.append('spectrum')
                elif i == 1:
                    self.dim_label.append('spectrum_2')
                elif i == 2:
                    self.dim_label.append('spectrum_2')
            else:
                raise KeyError('Bad thing happened')

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
                    self.z_axis = pars['VisuCorePosition'][:, 2]
                    self.dim_from_phys = np.append(self.dim_from_phys, self.z_axis[0])
                    self.dim_to_phys = np.append(self.dim_to_phys, self.z_axis[-1])
                    self.dim_phys_extent = np.append(self.dim_phys_extent, np.abs(np.subtract(self.z_axis[0], self.z_axis[-1])))

                elif pars["VisuFGOrderDesc"][i][1] == "FG_MOVIE":
                    self.dim_size = np.append(self.dim_size, int(pars["VisuFGOrderDesc"][i][0]))
                    self.dim_phys_extent = np.append(self.dim_phys_extent,
                                                    pars["VisuAcqRepetitionTime"] * pars["VisuFGOrderDesc"][i][0])
                    self.dim_from_phys = np.append(self.dim_from_phys, 0.0)
                    self.dim_to_phys = np.append(self.dim_to_phys, self.dim_phys_extent)
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
                    self.dim_desc.append('categorical')
                    self.dim_label.append('coils')
                elif pars['VisuFGOrderDesc'][i][1]== 'FG_ISA':
                    maps_dim_order = i + self.ndim
                    # these entries are later forgotten
                    self.dim_size = np.append(self.dim_size, int(pars["VisuFGOrderDesc"][i][0]))
                    self.dim_phys_extent = np.append(self.dim_phys_extent, float(pars["VisuFGOrderDesc"][i][0]))
                    self.dim_from_phys = np.append(self.dim_from_phys, 0.0)
                    self.dim_to_phys = np.append(self.dim_to_phys, self.dim_phys_extent)
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

            # modify parameters
            self.ndim -=1
            self.dim_size = np.delete(self.dim_size, maps_dim_order)
            self.dim_phys_extent = np.delete(self.dim_phys_extent, maps_dim_order)
            del self.dim_units[maps_dim_order]
            del self.dim_desc[maps_dim_order]
            del self.dim_label[maps_dim_order]

        self.dim_spacing = self.dim_phys_extent / self.dim_size

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

    def init_geometry(self):
        points = np.rollaxis(np.array(np.meshgrid(self.x_axis, self.y_axis)), 0, 3)
        self.transverse_plane = np.reshape(points, [points.shape[0] * points.shape[1], points.shape[2]])

        points = np.rollaxis(np.array(np.meshgrid(self.y_axis,self.z_axis)),0,3)
        self.sagittal_plane = np.reshape(points, [points.shape[0] * points.shape[1], points.shape[2]])

        points = np.rollaxis(np.array(np.meshgrid(self.x_axis, self.z_axis)), 0, 3)
        self.corronal_plane = np.reshape(points, [points.shape[0] * points.shape[1], points.shape[2]])


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
    def get_frame(self, enhance=True, **kwargs):

        ind_phys_switch = IND_PHYS(self.app.contextTabs.imageViewTab.indPhysSwitch.get()).value
        complex_part_switch = COMPLEX_PART(self.app.contextTabs.imageViewTab.complex_part_switch.get()).value

        location_high = tuple(self.dim_pos[3:])
        # coronal
        if kwargs['orient'] == VIEW_ORIENT.TRANS.value:
            location_low = ( slice( 0, self.dim_size[0] ), slice( 0, self.dim_size[1] ), self.dim_pos[2] )
            plane = self.transverse_plane.copy()
        # sagital
        elif kwargs['orient'] == VIEW_ORIENT.SAG.value:
            location_low = (self.dim_pos[0], slice(0, self.dim_size[1]), slice(0, self.dim_size[2]))
            plane = self.sagittal_plane.copy()
        # axial
        elif kwargs['orient'] == VIEW_ORIENT.CORR.value:
            location_low = (slice(0, self.dim_size[0]), self.dim_pos[1], slice(0, self.dim_size[2]))
            plane = self.corronal_plane.copy()

        # normalize plane
        if ind_phys_switch == IND_PHYS.IND.value:
            plane -=np.amin(plane)
            plane /= np.amax(plane)
            plane -= 0.5

        frame = self.data[location_low+ location_high]

        if complex_part_switch == COMPLEX_PART.ABS.value:
            frame = np.abs(frame)
        elif complex_part_switch == COMPLEX_PART.PHASE.value:
            frame = np.angle(frame)
        elif complex_part_switch == COMPLEX_PART.RE.value:
            frame = np.real(frame)
        else:
            frame = np.imag(frame)

        # interpolated frame to the geometry of caller

        # interpolate alpha mask
        if self.alpha_mask is not None:
            alpha = self.alpha_mask[location_low]

            # IMROT90
            if kwargs['orient'] == VIEW_ORIENT.TRANS.value:
                alpha = np.transpose(alpha, (1, 0))

            alpha = interpolate.griddata(plane, alpha.flatten(), (kwargs['querry_x'], kwargs['querry_y']), method='nearest',
                                 fill_value=0.0)

            alpha = 255.0*alpha

        # IMROT90
        if kwargs['orient'] == VIEW_ORIENT.TRANS.value:
            frame = np.transpose(frame,(1,0))

        frame = interpolate.griddata(plane, frame.flatten(), (kwargs['querry_x'], kwargs['querry_y']),  method='nearest', fill_value=0.0)
        # f = interpolate.interp2d(x_axis_im, y_axis_im, frame, kind='linear', fill_value=0.0)
        # frame = f(kwargs['x_axis'], kwargs['y_axis'])




        if enhance:
            frame = self.apply_enhance_(frame=frame)

        # todo change to apply_enhancement
        # frame = self.apply_preview(frame)
        frame = self.frame_to_0_255(frame)
        frame = frame * self.visibility
        frame = frame.astype(np.uint8)
        # todo this has to be done on cinema level
        # frame = self.resize(frame, export_size)
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

        x_label = 't'

        legend = '{} dim:{}'.format(self.tree_id.split('.h5')[1], dim_order)

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
    def apply_preview(self,frame):
        clip_stretch_switch = self.app.contextTabs.imageViewTab.contrastEnhance.clip_stretch_var.get()
        if clip_stretch_switch is True:
            return np.clip(frame,self.min_preview,self.max_preview)
        else:
            range_data = self.max_data - self.min_data
            range_preview = self.max_preview - self.min_preview
            return self.min_preview + (range_preview * (frame - self.min_data) / range_data)

    def frame_to_0_255(self, frame):
        255.0 * frame / self.max_preview
        return 255.0 * frame / self.max_preview

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

                self.min_data = np.amin(self.data)
                self.max_data = np.amax(self.data)
                self.min_preview = self.min_data
                self.max_preview = self.max_data

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
