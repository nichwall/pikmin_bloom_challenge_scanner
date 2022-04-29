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
    # Load templates and convert to grayscale
    heart_templates = {}
    for key in ["full", "half", "three_quarter", "empty"]:
        heart_templates[key] = rgb2gray(imread("../templates/template_"+key+"_heart.png")[...,0:3])

    # Return array of templates
    return heart_templates


# Accepts path of image to scan
def get_heart_locations(image_path):
    # Load image and convert to grayscale
    image = imread(image_path)
    image_gray = rgb2gray(image)

    # Find templates in image
    results = []
    heart_templates = load_heart_templates()
    for key, val in heart_templates.items():
        result_full  = match_template(image_gray, val)
        results.append(result_full)

    # Show image
    fig = plt.figure(figsize=(1,1))
    ax1 = plt.subplot(1,1,1)
    ax1.imshow(image, cmap=plt.cm.gray)

    # Get heart locations and draw them on the image
    heart_locations = []
    for template_result in results:
        template_h, template_w = heart_templates["full"].shape
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
    partition_bot = heart_y_coord + 30

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
    # Load color templates and convert to grayscale
    color_templates = {}
    for key in ["red", "yellow", "blue", "purple", "white", "winged"]:
        color_templates[key] = rgb2gray(imread("../templates/color_"+key+".png")[...,0:3])

    # Convert to grayscale
    image_gray = rgb2gray(pikmin_image)

    # Determine which has a match
    for key, val in color_templates.items():
        result = match_template(image_gray, val)
        if len( peak_local_max(result, threshold_abs=0.9, exclude_border=20) ) > 0:
            return key

    # If no match, ask user for input
    plt.ion()
    plt.figure()
    plt.imshow(pikmin_image)
    plt.show()

    color = input("What color is this pikmin?")
    plt.close()

    return color


# Determine how many friendship hearts the Pikmin
# has. This is done by determining where the left side of the leftmost heart is
# and currently only returns how many heart icons there are
def get_pikmin_heart_icon_count(pikmin_image):
    image_gray = rgb2gray(pikmin_image)

    # Find templates in image
    results = []
    heart_templates = load_heart_templates()
    for key, val in heart_templates.items():
        result_full  = match_template(image_gray, val)
        results.append(result_full)


    # Get heart locations
    heart_locations = []
    for template_result in results:
        template_h, template_w = heart_templates["full"].shape
        for x,y in peak_local_max(template_result, threshold_abs=0.9, exclude_border=10):
            heart_locations.append([x,y])


    # Get X coordinate of top of hearts
    try:
        heart_x_coord = np.unique( np.transpose(heart_locations)[1] )
        heart_x_coord.sort()
        left_heart = heart_x_coord[0]
        #print(f"Heart locations: {heart_x_coord}")

        # Convert to number of hearts
        # TODO this does not detect whether the last heart is empty
        #      or whether the final heart is full (4 hearts)
        if left_heart < 43:
            return 4
        elif left_heart < 57:
            return 3
        elif left_heart < 67:
            return 2
        else:
            return 1
    except:
        plt.ion()
        plt.figure()
        plt.imshow(pikmin_image)
        plt.show()
        heart_count = int(input("How many hearts? (-1 for nothing)"))
        plt.close()

        return heart_count


path_to_image = "../screenshots/full_hearts.jpg"
#path_to_image = "../screenshots/small_hearts.jpg"

heart_y_coord = get_heart_locations(path_to_image)
pikmin_images = partition_image(path_to_image, heart_y_coord)

for i in range(len(pikmin_images)):
    pikmin_hearts = get_pikmin_heart_icon_count( pikmin_images[i] )

    # If no hearts were found, this is because it's hidden behind
    # a button or cut off the screen
    if (pikmin_hearts < 0):
        continue

    color = get_pikmin_color_by_name( pikmin_images[i] )
    print(f"Pikmin {str(i).rjust(2)} is {color.rjust(7)} with {pikmin_hearts} heart icons")


