from enum import Enum

class COMPLEX_PART(Enum):
    ABS, PHASE, RE, IM = range(4)

class VIEW_ORIENT(Enum):
    TRANS, SAG, CORR = range(3)

class IND_PHYS(Enum):
    IND, PHYS = range(2)

class POINT_TRANS(Enum):
    LIN, POW, LOG = range(3)