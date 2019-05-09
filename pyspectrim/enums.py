from enum import Enum

class COMPLEX_PART(Enum):
    ABS, PHASE, RE, IM = range(4)

class VIEW_ORIENT(Enum):
    TRANS, SAG, CORR = range(3)

class IND_PHYS(Enum):
    IND, PHYS = range(2)

class POINT_TRANS(Enum):
    LIN, POW, LOG = range(3)

class COLOR_MAP(Enum):
    # this fits to opencv colormap codes
    GRAY, WINTER, JET = 1,3,2

    def __getitem__(self, item):
        # get value by name
        if item == 'GRAY':
            return self.GRAY
        elif item == 'WINTER':
            return self.WINTER
        elif item == 'JET':
            return self.JET