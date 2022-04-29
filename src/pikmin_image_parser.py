#!/bin/python3

import numpy as np
import matplotlib.pyplot as plt

from skimage.io import imread, imsave
from skimage.feature import match_template
from skimage.feature import peak_local_max
from skimage.color import rgb2gray

from scipy import stats

import csv
import glob


# Load templates and return in an array
def load_heart_templates():
    # Load templates and convert to grayscale
    heart_templates = {}
    for key in ["full", "half", "three_quarter", "empty"]:
        heart_templates[key] = rgb2gray(imread("../templates/template_"+key+"_heart.png")[...,0:3])

    # Return array of templates
    return heart_templates


# Accepts path of image to scan
def get_heart_locations(image):
    # Load image and convert to grayscale
    image_gray = rgb2gray(image)

    # Find templates in image
    results = []
    heart_templates = load_heart_templates()
    for key, val in heart_templates.items():
        results.append( match_template(image_gray, val) )

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
def partition_image(image, heart_y_coord):
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
    print(f"Image shape: {image.shape}")

    # Iterate through pikmin for cropping
    # TODO these partitions need to be changed dynamically for screen size
    partition_sides = [25, 185, 350, 515, 675, 845]
    pikmin_images = []
    for row_idx in range(len(heart_y_coord)):
        for col_idx in range(len(partition_sides)-1):
            # Check if too far up the page
            if partition_top[row_idx] < 0:
                continue

            pikmin_image = image[partition_top[row_idx]:partition_bot[row_idx], partition_sides[col_idx]:partition_sides[col_idx+1]]
            pikmin_images.append(pikmin_image)

    return pikmin_images

# Load user named pikmin
def get_pikmin_color_map():
    # Get standard color name map
    color_templates = {}

    for key in ["red", "yellow", "blue", "purple", "white", "winged"]:
        color_templates[key] = [rgb2gray(imread("../templates/color_"+key+".png")[...,0:3])]

    #####################
    # Set up custom color name map
    #####################

    # Set up variables
    custom_template_dir = "../templates/custom/"
    # Get all custom mapping files
    files = glob.glob(custom_template_dir+"*.jpg")
    for file in files:
        color = file.split("_")[1].split(".")[0]
        color_templates[color].append( rgb2gray(imread( file )) )

    return color_templates

# Store custom named pikmin for future use
def store_pikmin_color_by_name(color_templates, color, image):
    # Sanitize the color
    color = ''.join([i for i in color if i.isalpha()]).lower()
    # Figure out how many templates already exist for this pikmin
    color_count = len(color_templates[color])
    # Name of file to save in
    fname = "../templates/custom/" + str(color_count) + "_" + color + ".jpg"
    # Save file
    imsave(fname, image)

    return color


# Determine what color the pikmin is
# based on the name
def get_pikmin_color_by_name(pikmin_image):
    # Load color templates and convert to grayscale
    color_templates = get_pikmin_color_map()

    # Convert to grayscale
    image_gray = rgb2gray(pikmin_image)

    # Determine which has a match
    for key, val in color_templates.items():
        for mapping in val:
            result = match_template(image_gray, mapping)
            if len( peak_local_max(result, threshold_abs=0.9, exclude_border=20) ) > 0:
                return key

    # If no match, ask user for input
    plt.ion()
    plt.figure()
    plt.imshow(pikmin_image)
    plt.show()

    color = input("What color is this pikmin?")
    plt.close()

    # Store name of color of pikmin
    color = store_pikmin_color_by_name(color_templates, color, pikmin_image[150:180,20:140,:])

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
        results.append( match_template(image_gray, val) )


    # Get all heart locations
    heart_locations = []
    for template_result in results:
        template_h, template_w = heart_templates["full"].shape
        for x,y in peak_local_max(template_result, threshold_abs=0.9, exclude_border=10):
            heart_locations.append([x,y])
    # Get full heart locations
    full_heart_locations = []
    for x,y in peak_local_max(results[0], threshold_abs=0.9, exclude_border=10):
        full_heart_locations.append(y)
    if len(full_heart_locations) != 0:
        last_full_position = max(full_heart_locations)
    else:
        last_full_position = 0


    # Get X coordinate of left heart
    try:
        heart_x_coord = np.unique( np.transpose(heart_locations)[1] )
        heart_x_coord.sort()
        left_heart = heart_x_coord[0]
        #print(f"Heart locations: {heart_x_coord}")

        # Convert to number of hearts
        # TODO this does not detect whether the last heart is empty
        if left_heart < 43:
            # Check if last heart is a full heart
            if last_full_position > 105:
                return 4
            else:
                return 3
        elif left_heart < 57:
            return 2
        elif left_heart < 67:
            return 1
        else:
            return 0
    except:
        plt.ion()
        plt.figure()
        plt.imshow(pikmin_image)
        plt.show()
        heart_count = int(input("How many hearts? (-1 for nothing)"))
        plt.close()

        return heart_count

def crop_image(image_path):
    # TODO need to change this to detect the top and bottom
    # of selection screen for someone else's phone

    # Load image and crop top/bottom
    image = imread(image_path)
    print(image.shape)
    cropped = image[410:1650,:,:]

    return cropped


if __name__ == "__main__":
    #path_to_image = "../screenshots/white_not_full.jpg"
    path_to_image = "../screenshots/full_hearts.jpg"
    #path_to_image = "../screenshots/small_hearts.jpg"

    cropped = crop_image(path_to_image)

    heart_y_coord = get_heart_locations(cropped)
    pikmin_images = partition_image(cropped, heart_y_coord)

    print(len(pikmin_images))

    for i in range(len(pikmin_images)):
        pikmin_hearts = get_pikmin_heart_icon_count( pikmin_images[i] )

        # If no hearts were found, this is because it's hidden behind
        # a button or cut off the screen
        if (pikmin_hearts < 0):
            continue

        color = get_pikmin_color_by_name( pikmin_images[i] )
        print(f"Pikmin {str(i).rjust(2)} is {color.rjust(7)} with {pikmin_hearts} heart icons")


