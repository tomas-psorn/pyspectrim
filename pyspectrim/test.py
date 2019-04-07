import cv2
import numpy as np
from scipy.interpolate import griddata

x_ax = np.linspace(0.0,1.0,5)
y_ax = np.linspace(3.0,2.0, 5)

data = np.array([[1,1,1,1,1],
                [2,2,2,2,2],
                [3,3,3,3,3],
                [4,4,4,4,4],
                [5,5,5,5,5]])

X, Y = np.meshgrid(x_ax, y_ax)
X = np.reshape(X,(25,))
Y = np.reshape(Y,(25,))

points = np.zeros((25,2))
points[:,0] = X
points[:,1] = Y

data = np.reshape(data,(25,1))

X_querry = np.linspace(0.0,1.0,5)
Y_querry = 2.7 * np.ones_like(X_querry)

z = griddata(points, data, (X_querry, Y_querry), method='linear')

print(z)


