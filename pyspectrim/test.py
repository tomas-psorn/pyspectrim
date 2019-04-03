import cv2
import numpy as np

img = np.zeros((256,256), np.uint8)

print (img.shape)


img_c = cv2.applyColorMap(img,cv2.COLORMAP_BONE)

print(img_c.shape)