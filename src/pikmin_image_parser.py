#!/bin/python3

import numpy as np
import matplotlib.pyplot as plt

from skimage.io import imread
from skimage.feature import match_template
from skimage.feature import peak_local_max
from skimage.color import rgb2gray

from scipy import stats


# Load templates and return in an array
def load_heart_templates():
    # Load templates
    template_full  = imread("template_full_heart.png")
    template_half  = imread("template_half_heart.png")
    template_empty = imread("template_empty_heart.png")

    # Convert to grayscale
    template_full_gray = rgb2gray(template_full)
    template_half_gray = rgb2gray(template_half)
    template_empty_gray = rgb2gray(template_empty)

    # Return array of images
    return [template_full_gray,
            template_half_gray,
            template_empty_gray]


# Accepts path of image to scan
def get_heart_locations(image_path):
    # Load image and convert to grayscale
    image = imread(image_path)
    image_gray = rgb2gray(image)

    # Find templates in image
    results = []
    heart_templates = load_heart_templates()
    for template in heart_templates:
        result_full  = match_template(image_gray, template)
        results.append(result_full)

    # Show image
    fig = plt.figure(figsize=(1,1))
    ax1 = plt.subplot(1,1,1)
    ax1.imshow(image, cmap=plt.cm.gray)

    # Get heart locations and draw them on the image
    heart_locations = []
    for template_result in results:
        template_h, template_w = heart_templates[0].shape
        for x,y in peak_local_max(template_result, threshold_abs=0.9, exclude_border=20):
            rect = plt.Rectangle((y, x), template_w, template_h, edgecolor='g', facecolor='none')
            ax1.add_patch(rect)
            heart_locations.append([x,y])

    # Get Y coordinate of top of hearts
    heart_y_coord = np.unique( np.transpose(heart_locations)[0] )
    heart_y_coord.sort()

    # TODO get rid of this image plotting
    plt.show()

    return heart_y_coord


# Partitions an image into an array of pikmen based on
# heart Y location
# 
# Returns array of pikmin images
def partition_image(image_path, heart_y_coord):
    # Get distance between Y coordinates to determine how
    # tall a partition should be
    heart_y_dist = stats.mode( np.diff(heart_y_coord) )[0][0]
    print(f"Heart Y distance (pixels): {heart_y_dist}")

    # Partition top
    # up ~200
    partition_top = heart_y_coord - 200

    # Partition bottom
    # down ~20
    partition_bot = heart_y_coord + 20

    # Get image shape
    # Load image
    image = imread(image_path)
    print(f"Image shape: {image.shape}")

    # Iterate through pikmin for cropping
    # TODO these partitions need to be changed dynamically for screen size
    partition_sides = [25, 185, 350, 515, 675, 845]
    pikmin_images = []
    for row_idx in range(len(heart_y_coord)):
        for col_idx in range(len(partition_sides)-1):
            pikmin_image = image[partition_top[row_idx]:partition_bot[row_idx], partition_sides[col_idx]:partition_sides[col_idx+1]]
            pikmin_images.append(pikmin_image)

    return pikmin_images

# Determine what color the pikmin is
# based on the name
def get_pikmin_color_by_name(pikmin_image):
    # Load color templates

heart_y_coord = get_heart_locations("full_hearts.jpg")
partition_image("full_hearts.jpg", heart_y_coord)

