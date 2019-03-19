import h5py


class File(h5py.File):
    def __init__(self, app, path):
        try:
            super(File, self).__init__(path, 'r')
        except:
            print("File not mounted")
            return
