import numpy as np

class Plane2D(object):
    def __init__(self, x_axis=None, y_axis=None):
        self.x, self.y = np.meshgrid(x_axis, y_axis)
