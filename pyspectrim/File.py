import h5py

from os.path import basename


def getH5Id(object):
    if object.__class__.__name__ == 'File':
        return object.filename.rsplit('.',1)[0]
    elif object.__class__.__name__ == 'Group':
        return object.file.filename.rsplit('.',1)[0]  + object.name
    elif object.__class__.__name__ == 'Dataset':
        return object.file.filename.rsplit('.',1)[0]  + object.name


def getH5Name(object):
    if object.__class__.__name__ == 'File':
        return basename(object.filename)
    elif object.__class__.__name__ == 'Group':
        return object.name
    elif object.__class__.__name__ == 'Dataset':
        return object.name

class File(h5py.File):
    def __init__(self, app, path):
        try:
            super(File, self).__init__(path, 'r')
        except:
            print("File not mounted")
            return
