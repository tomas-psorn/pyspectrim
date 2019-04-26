import h5py

from os.path import basename, isfile
from os import listdir, walk

import builtins

import sys

from pathlib import Path

import numpy as np

'''
HDF5 part
'''

def getH5Id(object):
    if object.__class__.__name__ == 'FileHdf5':
        # return object.filename.rsplit('.',1)[0]
        return object.filename
    elif object.__class__.__name__ == 'Group':
        # return object.file.filename.rsplit('.',1)[0]  + object.name
        return object.file.filename  + object.name
    elif object.__class__.__name__ == 'Dataset':
        # return object.file.filename.rsplit('.',1)[0]  + object.name
        return object.file.filename  + object.name

def getH5Name(object):
    if object.__class__.__name__ == 'FileHdf5':
        return basename(object.filename)
    elif object.__class__.__name__ == 'Group':
        return object.name
    elif object.__class__.__name__ == 'Dataset':
        return object.name


class FileHdf5(h5py.File):
    def __init__(self, app, path):
        try:
            super(FileHdf5, self).__init__(path, 'r')
        except FileNotFoundError:
            pass


'''
Bruker part
'''
class FileBruker(h5py.File):
    def __init__(self, app=None, path=None):

        self.app = app
        self.path = Path(path)

        self.folders = [self.path / f for f in listdir(self.path) if not isfile(self.path / f) and f.isdigit()]

        for folder in self.folders:
            print(folder)

class Scan(object):

    def __init__(self, path, readFid=True, readReco=False, readTraj=True, readJobs = False, readSpnam = False, fs=None):

        if fs is None:
            self.fs = FS()
        else:
            self.fs = fs

        self.path = Path(path)
        self.isAcqp = None
        self.isMethod = None
        self.isFid = None
        self.isTraj = None
        self.isPdata = None
        self.fid = None
        self.isScan = None # indicates presence of acqp, method and fid file

        # jobs acquisitions
        self.jobsList = None
        self.jobs = None

        # RF pulse shapes

        # sets variables indicating presence of files
        self.browse_scan(self.fs)

        if self.isAcqp is False or self.isMethod is False or self.isFid is False:
            self.isScan = False
            return None
        else:
            self.isScan = True

        # Create instances of parameter and data classes

        if self.isAcqp:
            # self.acqp = ParamGroup(self.path / 'acqp', self.fs)
            self.acqp = ParamGroup(self.path / 'acqp')

        if self.isMethod:
            # self.method = ParamGroup(self.path / 'method', self.fs)
            self.method = ParamGroup(self.path / 'method')

        if self.isFid and readFid:
            self.fid = self.read_fid_file(path=self.path / 'fid', fs=self.fs)
            try:
                self.methodBasedReshape()
            except:
                print("There was a problem with method based data reshape. Data are avaliable in basic form")

        # Not necessary for PySpectrim at the moment
        # if self.isTraj and readTraj:
        #     self.traj = readers.readBrukerTrajFile (self, self.path + 'traj', self.fs)

        # read jobs data
        if self.jobsList and readJobs:
            for jobFile in self.jobsList:
                if not self.jobs:
                    self.jobs = [self.read_fid_file(self, path=self.path + '/' + jobFile, fs=self.fs, job=True)]
                else:
                    self.jobs.append(self.read_fid_file(self, path=self.path + '/' + jobFile, fs=self.fs ,job=True))

        return

    def browse_scan(self, fs):
        """
        Detect which files are present in the scan file
        :return:
        isAcqp
        isMethod
        isFid
        isTraj
        isPdata
        recolist - list of reconstruction files
        """
        content = fs.listdir(self.path)

        jobsList = []
        spnamList = []
        recoList = []

        for file in content:

            if 'pdata' in file:
                scanRecos = fs.listdir(self.path / 'pdata')

                for file in scanRecos: #todo not the best criteria
                    if file.isdigit():
                        recoList.append(file)

            if 'rawdata.job' in file:
                jobsList.append(file)

            if 'spnam' in file and '~' not in file:
                spnamList.append(file)


        if spnamList:
            self.spnamList = spnamList

        if jobsList:
            self.jobsList = jobsList

        if recoList:
            self.recoList = recoList

        if 'acqp' in content:
            self.isAcqp = True

        if 'method' in content:
            self.isMethod = True

        if 'fid' in content:
            self.isFid = True

        if 'traj' in content:
            self.isTraj = True

        if 'pdata' in content:
            self.isPdata = True

        return

    def read_fid_file(self, path=None, fs=None, job=False):
        """
        Pvtools original algorithm to read and reshape fid data is used. It lacks some of the advanced functionality
        of the original code.

        The reading process is encapsulated so that it can be used for online data analysis.

        Parameters
        ----------
        path - path  to fid file
        dataObject - bruker scan object

        Returns
        -------
        dataOut - fid data in folloving shape [dimCh, dimAcq0. dimHigh]
        """

        # test the presence of all required parameters, get read essential parameters
        format, bits, dimBlock, dimZ, dimR, dimAcq0, dimAcqHigh, dimCh, dimA = self.fidBasicInfo()

        # reading part
        with fs.open(path, "rb") as fidFile:
            fidData = self.fid_basic_read(fidFile, format)

        # if reading fid file, reshape it in pv-tools way
        if job:
            return self.job_basic_reshape(fidData)
        else:
            return self.fid_basic_reshape(fidData, dimBlock, dimZ, dimR, dimAcq0, dimAcqHigh, dimCh, dimA)

    def fid_basic_read(self, format, startRead=0, dimRead=-1):

        self.seek(startRead)  # find the start position in the file

        fidData = np.fromfile(self, dtype=format, count=dimRead)  # read

        if dimRead == -1:
            return fidData
        else:
            endRead = self.tell()
            return fidData, endRead

    def job_basic_reshape(dataIn):
        """
        TODO implement
        :param dataIn:
        :return:
        """
        return dataIn

    def fid_basic_reshape(self, fidData, dimBlock, dimZ, dimR, dimAcq0, dimAcqHigh, dimCh, dimA):

        if len(fidData) != dimBlock * dimAcqHigh * dimZ * dimR * dimA:
            print('Missmatch')

        fidData = np.reshape(fidData, (dimBlock, dimAcqHigh * dimZ * dimR));

        if dimBlock != dimAcq0 * dimCh:
            fidData = np.transpose(fidData, (1, 0))
            fidData = fidData[:, :(dimAcq0 * dimCh)]
            fidData = np.reshape(fidData, (dimAcqHigh * dimZ * dimR * dimA, dimAcq0, dimCh), order='F')
            fidData = np.transpose(fidData, (2, 1, 0))
        else:
            fidData = np.reshape(fidData, (dimAcq0, dimCh, dimAcqHigh * dimZ * dimR * dimA), order='F')
            fidData = np.transpose(fidData, (1, 0, 2))

        fidDataOut = fidData[:, 0::2, :] + 1j * fidData[:, 1::2, :]

        return fidDataOut

    def methodBasedReshape(self):
        """
        Description
        -----------
        Call a particular function, according to the pulse program, to reshape fid data.
        If no function for handling of the fid of a given pulse program (sequence)
        is not specified, nothing happens.

        To add a new function for a certain sequence, just add an another elif line.

        Parameters
        ----------
        rawdataobject

        Returns
        -------

        -
        """
        """
        if self.acqp.PULPROG in ['UTE.ppg','macicekGAUTE.ppg']:
            #readers.fidHandle_UTE(self)
            pass
        elif self.acqp.PULPROG in ['FAIR_RARE.ppg']:
            readers.fidHandle_FAIR_RARE(self)
        elif self.acqp.PULPROG in ['DtiEpi.ppg', 'EPI.ppg', 'navigatorEPI_OM.ppg']:
            readers.fidHandle_Epi(self)
        elif self.acqp.PULPROG in ['FLASH.ppg']:
            readers.fidHandle_Flash(self)
        elif self.acqp.PULPROG in ['PRESS.ppg']:
            readers.fidHandle_PRESS(self)
        elif self.acqp.PULPROG in ['SINGLEPULSE.ppg']:
            readers.fidHandle_SINGLEPULSE(self)
        elif self.acqp.PULPROG in ['RfProfile.ppg']:
            readers.fidHandle_RfProfile(self)
        else:
            print('Function to reshape fid data of ' + self.acqp.PULPROG + ' sequence is not developed yet')
        """

        return

    def getSelectedReceivers(self):
        """
        Pvtools original function to determine number of channels used for acquisition

        Parameters
        ----------
        rawdataobject

        Returns
        -------
        Number of channels
        """
        numSelectedReceivers = 1

        if self.acqp.ACQ_experiment_mode == 'ParallelExperiment':
            try:
                if self.acqp.GO_ReceiverSelect[0].isalpha():
                    numSelectedReceivers = 0
                    for channel in self.acqp.GO_ReceiverSelect:
                        if channel == 'Yes':
                            numSelectedReceivers += 1
            except:
                pass

            try:
                if self.acqp.ACQ_ReceiverSelect[0].isalpha():
                    numSelectedReceivers = 0
                    for channel in self.acqp.ACQ_ReceiverSelect:
                        if channel == 'Yes':
                            numSelectedReceivers += 1
            except:
                pass

        return numSelectedReceivers

    def fidBasicInfo(self):

        minCondition = ('GO_raw_data_format','BYTORDA','NI','NR','ACQ_size','GO_data_save','GO_block_size', 'AQ_mod');
        all_here = self.bruker_requires(minCondition, 'acqp')
        if not all_here:
            print("ERROR: visu_pars file does not provide enough info")
            sys.exit(1)

        dimZ = self.acqp.NI
        dimR = self.acqp.NR
        dimAcqHigh = int(np.prod(self.acqp.ACQ_size[1:]))
        dimAcq0 = int(self.acqp.ACQ_size[0])
        dimCh = self.getSelectedReceivers()
        acqp_BYTORDA = self.acqp.BYTORDA
        acqp_GO_raw_data_format = self.acqp.GO_raw_data_format
        acqp_GO_block_size = self.acqp.GO_block_size
        method_Method = self.method.Method
        # because of reading jobfiles
        if method_Method == 'Bruker:PRESS':
            dimA = self.method.PVM_NAverages
        else:
            dimA = 1

        #   get data type and number of bits
        if acqp_GO_raw_data_format == 'GO_32BIT_SGN_INT' and acqp_BYTORDA == 'little':
            format = np.dtype('i4').newbyteorder('<')
            bits = 32
        elif acqp_GO_raw_data_format == 'GO_16BIT_SGN_INT' and acqp_BYTORDA == 'little':
            format = np.dtype('i').newbyteorder('<')
            bits = 16
        elif acqp_GO_raw_data_format == 'GO_32BIT_FLOAT' and acqp_BYTORDA == 'little':
            format = np.dtype('f4').newbyteorder('<')
            bits = 32
        elif acqp_GO_raw_data_format == 'GO_32BIT_SGN_INT' and acqp_BYTORDA == 'big':
            format = np.dtype('i4').newbyteorder('>')
            bits = 32
        elif acqp_GO_raw_data_format == 'GO_16BIT_SGN_INT' and acqp_BYTORDA == 'big':
            format = np.dtype('i').newbyteorder('>')
            bits = 16
        elif acqp_GO_raw_data_format == 'GO_32BIT_FLOAT' and acqp_BYTORDA == 'big':
            format = np.dtype('f4').newbyteorder('>')
            bits = 32
        else:
            format = np.dtype('i4').newbyteorder('<')
            print('Data format not specified correctly, set to int32, little endian')
            bits = 32

        if acqp_GO_block_size == 'Standard_KBlock_Format':
            dimBlock = int(np.ceil(float(dimAcq0)*dimCh*(bits/8)/1024)*1024/(bits/8))
        else:
            dimBlock = dimAcq0 * dimCh

        return format, bits, dimBlock, dimZ, dimR, dimAcq0, dimAcqHigh, dimCh, dimA

    def bruker_requires(self, minCondition, fileType):
            """
            pvtools original function to control the presence of an essential parameters
            in a dataobject's parameter defined by fileType

            Parameters
            ----------
            dataobject
            minCondition (tuple of strings)
            fileType (string)

            Returns
            -------
            all_here (bool)
            """
            all_here = True
            for conditionElement in minCondition:
                condition = 'self' + '.' + fileType + '.' + conditionElement
                try:
                    eval(condition)
                except AttributeError:
                    print('ERROR: ', fileType, ' file does not contain essential parameter: ', conditionElement)
                    all_here = False
            return all_here

class ParamGroup(object):

    def __init__(self,path):

        params = self.read_bruker_param_file(self, path=path)

        super().__setattr__('params', self.read_bruker_param_file(self, path=path))

    def getDict(self):
        return self.params

    def __setattr__(self, key, value):
        self.params[key] = value

    def __getattr__(self, key):
        if key.startswith('__') and key.endswith('__'):
            return super().__getattr__(key)
        return self.params[key]

    def __getitem__(self, key):
        return getattr(self, key)


    def toMat(self):
        #TODO implement saving to .mat file
        pass

    def proc_value(self):
        pass

    def get_sizes_tuple(self, value_string):
        pass

    def proc_value_clean(self,value_string):
        try:
            return int(value_string)
        except:
            try:
                return float(value_string)
            except:
                return value_string.replace("<","").replace(">","")

    def proc_array(self,value_string):
        sizes = value_string.split(")")[0].replace("(", "")
        sizes = sizes.lstrip().rstrip()

        sizes = sizes.split(",")
        sizes_list = []
        for size in sizes:
            sizes_list.append(int(size))

        if "<" in value_string:
            sizes_list[-1] = 1

        data_string = value_string[value_string.find(")") + 1:]
        data_string = data_string.lstrip().rstrip()

        # get rid of double spaces
        data_string = data_string.replace("  ", " ")

        if "<" in data_string:
            data_string = data_string.replace("<","")
            data_string = data_string.replace(" ","")
            data_list = data_string.split(">")
            data_list = data_list[0:-1]
        else:
            data_list = data_string.split(" ")

        try:
            # if this fails, the data list contains system constants as strings
            float(data_list[0])
            format_ = "float"
            value = np.zeros(np.prod(sizes_list), dtype=np.float32)
        except:
            format_ = "string"
            value = []

        for i in range(0, len(data_list)):

            if format_ == 'float':
                try:
                    value[i] = float(data_list[i])
                except ValueError:
                    print("Unexpected format")
            else:
                value.append(data_list[i])

        if format_ == 'float':
            if len(data_list) > 1:
                return np.reshape(value, tuple(sizes_list))
            else:
                return value[0]
        else:
            if sizes_list[0] > 1:
                return value
            else:
                return value[0]

    def proc_nested_list(self,value_string):
        sizes = value_string.split(")")[0].replace("(", "")
        data_string = value_string[value_string.find(")") + 1:]
        sizes = sizes.lstrip().rstrip()
        sizes = sizes.replace(" ","")
        data_string = data_string.lstrip().rstrip()

        sizes_list = []
        sizes_list = sizes.split(",")

        # if entry is tuple of undefined size
        if data_string == '':
            data_string = '('+sizes+')'
            sizes_list = [len(sizes_list)]
        else:
            for i in range(0,len(sizes_list)):
                sizes_list[i] = int(sizes_list[i])

        if value_string.startswith("<"):
            sizes_list[-1] = 1





        values = []
        for i in range(0, sizes_list[0]):

            pos = data_string.find(") (")

            if pos>0:
                data_frac = data_string[1:pos]
            else:
                data_frac = data_string[1:-1]

            data_frac = data_frac.replace(" ","")
            value = data_frac.split(',')
            for j in range(0, len(value)):
                value[j] = self.proc_value_clean(value[j])

            values.append(value)

            # data is shortened
            data_string = data_string[pos + 1:]
            data_string = data_string.lstrip()

        return values


    def proc_entry(self,value_string):
        if "(" not in value_string:
            return self.proc_value_clean(value_string)
        elif value_string.startswith("(") and not value_string.endswith(")"):
            return self.proc_array(value_string)
        elif value_string.startswith("(") and value_string.endswith(")"):
            return  self.proc_nested_list(value_string)
        else:
            print("aha!")




    def read_bruker_param_file(self,fs=None,path=None):

        params ={}

        with open(path) as f:
            content = f.readlines()


        for line in content:
            if line.__contains__("$$"):
                content.remove(line)

        # todo this is obviously a nonsense, but it does not work any other way
        for line in content:
            if line.__contains__("$$"):
                content.remove(line)

        content_string = ""

        for line in content:
            content_string = content_string + line.replace("\n", " ")

        content = content_string.split("##")

        for line in content:
            # is some parameter
            if line.startswith("$"):
                line = line.replace("$","")
                key_end = line.find("=")
                key = line[0:key_end]
                val = line[key_end+1:]
                params[key] = self.proc_entry(val.rstrip())

        return params

class FS(object):
    '''
    author: Martin Vít
    '''
    def __init__(self):
        super().__init__()

    def open(self, file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None):
        return builtins.open(file, mode, buffering, encoding, errors, newline, closefd, opener)

    def listdir(self, path):
        return listdir(path)

    def walk(self, top, topdown=True, onerror=None, followlinks=False):
        return walk(top, topdown, onerror, followlinks)
