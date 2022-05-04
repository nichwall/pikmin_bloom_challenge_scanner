# https://towardsdatascience.com/image-processing-with-python-template-matching-with-scikit-image-6e82fdd77b66

# https://stackoverflow.com/questions/61890630/find-location-of-a-symbol-on-an-image-with-python

import numpy as np
import matplotlib.pyplot as plt

from skimage.io import imread
from skimage.feature import match_template
from skimage.feature import peak_local_max
from skimage.color import rgb2gray

from scipy import stats

# Read images
image = imread("full_hearts.jpg")
#image = imread("small_hearts.jpg")
template_full  = imread("template_full_heart.png")
template_half  = imread("template_half_heart.png")
template_empty = imread("template_empty_heart.png")

# Convert to grayscale
image_gray = rgb2gray(image)
template_full_gray = rgb2gray(template_full)
template_half_gray = rgb2gray(template_half)
template_empty_gray = rgb2gray(template_empty)

# Find templates in image
result_full  = match_template(image_gray, template_full_gray)
result_half  = match_template(image_gray, template_half_gray)
result_empty = match_template(image_gray, template_empty_gray)

# Find best match
#ij = np.unravel_index(np.argmax(result), result.shape)
#x,y = ij[::-1]

# Set up figures
fig = plt.figure(figsize=(1, 1))
ax2 = plt.subplot(1, 1, 1)

# Plot template
#ax1.imshow(template, cmap=plt.cm.gray)
#ax1.set_axis_off()
#ax1.set_title('template')

# Plot matched boxes
ax2.imshow(image, cmap=plt.cm.gray)
ax2.set_axis_off()
ax2.set_title('image')
# highlight matched region
print(f" Template: {template_full.shape}")
hcoin, wcoin, pcoin = template_full.shape

full_heart_locations = []
# Find full hearts
for x,y in peak_local_max(result_full, threshold_abs=0.9, exclude_border=20):
    rect = plt.Rectangle((y, x), wcoin, hcoin, edgecolor='r', facecolor='none')
    ax2.add_patch(rect)
    full_heart_locations.append([x,y])
print(f" Full heart locations: {full_heart_locations}")
full_heart_y_vals = np.unique( np.transpose(full_heart_locations)[0] )
full_heart_y_vals.sort()
print(f" Full heart Y vals: {full_heart_y_vals}")
full_heart_dist = stats.mode(np.diff(full_heart_y_vals))[0][0]
print(f" Distance between rows: {full_heart_dist}")

# Find empty hearts
#print(f" Template: {template_empty.shape}")
hcoin, wcoin, pcoin = template_empty.shape
for x,y in peak_local_max(result_empty, threshold_abs=0.9, exclude_border=20):
    rect = plt.Rectangle((y, x), wcoin, hcoin, edgecolor='g', facecolor='none')
    ax2.add_patch(rect)
# Find half hearts
#print(f" Template: {template_half.shape}")
hcoin, wcoin, pcoin = template_empty.shape
for x,y in peak_local_max(result_half, threshold_abs=0.9, exclude_border=20):
    rect = plt.Rectangle((y, x), wcoin, hcoin, edgecolor='b', facecolor='none')
    ax2.add_patch(rect)

plt.show()


# TODO
# Heart detection mostly working
# Need to partition image
#   Determine heart counts in partition?
#   Determine if a selected pikmin?
# Crop top/bottom from image
# Determine duplicates between two images

