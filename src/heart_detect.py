# Attempting to detect heart locations, following
# https://www.thepythoncode.com/article/detect-shapes-hough-transform-opencv-python

import numpy as np
import matplotlib.pyplot as plt
import cv2

plt.ion()

# Read image
#image = cv2.imread("full_hearts.jpg")
image = cv2.imread("small_hearts.jpg")
print(image.shape)

plt.figure()
# Need to reverse from BGR to RGB for showing image,
# but openCV assumes BGR for everything
screen = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
plt.imshow(screen)
plt.title("Original fixed")

# Convert to grayscale
grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Detect edges
edges = cv2.Canny(grayscale, 30, 100)

# Detect lines
lines = cv2.HoughLinesP(edges, 1, np.pi/180, 60, np.array([]), 50, 5)

# Draw lines
for line in lines:
    for x1, y1, x2, y2 in line:
        cv2.line(image, (x1,y1), (x2,y2), (20,220,20), 3)

plt.figure()
plt.imshow(image[...,::-1])
plt.title("Lines drawn")

input("Press Enter to close")
