import cv2
import numpy as np

img = cv2.imread('test/sigma.png', cv2.IMREAD_GRAYSCALE)

b_hist, b_edges = np.histogram(np.asarray(img), bins=10)

print(b_edges)