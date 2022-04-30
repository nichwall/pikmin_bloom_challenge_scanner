#!/bin/python3

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector, Button, RadioButtons

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

# Given an image, figure out how many pixels wide
# each column is and relative positions of notable
# features
def calculate_partition_dimensions(full_image):
    pass

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
    # Clean up similar rows
    for i in range(len(heart_y_coord)-1):
        if abs(heart_y_coord[i] - heart_y_coord[i+1]) < 5:
            heart_y_coord[i+1] = heart_y_coord[i]
    heart_y_coord = np.unique( heart_y_coord )

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
    partition_top = heart_y_coord - 220

    # Partition bottom
    # down ~20
    partition_bot = heart_y_coord + 30

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
    files = glob.glob(custom_template_dir+"color_*.jpg")
    for file in files:
        color = file.split("color_")[-1].split("_")[0]
        color_templates[color].append( rgb2gray(imread( file )) )

    return color_templates

def load_maturity_templates():
    # Set up template dictionary
    maturity_templates = {}
    for key in ["bare", "bud", "leaf", "normal", "rare"]:
        maturity_templates[key] = []

    # Load templates and convert to grayscale
    template_dir = "../templates/"
    # Get all mappings
    files = glob.glob(template_dir+"maturity*")
    for file in files:
        maturity = file.split("maturity_")[-1].split("_")[0]
        maturity_templates[maturity].append( rgb2gray(imread( file )[...,0:3]) )

    # Load custom maturity templates
    custom_template_dir = "../templates/custom/"
    # Get all custom mapping files
    files = glob.glob(custom_template_dir+"maturity_*.jpg")
    for file in files:
        maturity = file.split("maturity_")[-1].split("_")[0]
        maturity_templates[maturity].append( rgb2gray(imread( file )) )

    return maturity_templates

def load_decor_templates():
    # Set up template dictionary
    decor_templates = {}
    for key in ["yes"]:
        decor_templates[key] = []

    # Load custom decor templates
    custom_template_dir = "../templates/custom/"
    # Get all custom mapping files
    files = glob.glob(custom_template_dir+"decor_*.jpg")
    for file in files:
        decor = file.split("decor_")[-1].split("_")[0]
        decor_templates[decor].append( rgb2gray(imread( file )) )

    return decor_templates


# Store user defined pikmin attributes
def store_pikmin_attribute(templates, attribute_name, key, image):
    # Sanitize key
    key = ''.join([i for i in key if i.isalpha()]).lower()
    # Figure out how many templates already exist for this pikmin
    count = len(templates[key])
    # Name of file to save in
    fname = f"../templates/custom/{attribute_name}_{key}_{str(count)}.jpg"
    # Save file
    imsave(fname, image)

    return key

# Prompt user to select the maturity of the pikmin
# for better performance
def prompt_user_maturity(image, maturity_templates):
    def onselect_function(eclick, erelease):
        # Obtain (xmin, xmax, ymin, ymax) values
        # for rectangle selector box using extent attribute.
        extent = rect_selector.extents
        ax.set_xlim(extent[0], extent[1])
        ax.set_ylim(extent[3], extent[2])
    def submit_classification(val):
        # Close window once user presses "Classify"
        plt.close()

    # Run in loop in case user closes window
    #while True:
    # Display
    #plt.ion()
    fix, ax = plt.subplots()
    ax.imshow(image)
    plt.title("Classify Maturity")

    # Create radio
    rax = plt.axes([0.1, 0.15, 0.2, 0.2])
    radio_button = RadioButtons(rax, ["bare", "leaf", "bud", "normal", "rare"])

    # Create button
    bax = plt.axes([0.5, 0.15, 0.2, 0.2])
    submit = Button(bax, "Classify")
    submit.on_clicked(submit_classification)

    # Rect selector for zooming
    rect_selector = RectangleSelector(ax, onselect_function, button=[1])

    # Wait for user to "Classify"
    plt.show()
    maturity = radio_button.value_selected

    # Extract feature
    x_lim = ax.get_xlim()
    y_lim = ax.get_ylim()
    template_to_add = image[ round(y_lim[1]):round(y_lim[0]),
                             round(x_lim[0]):round(x_lim[1]), :]

    # Store and return maturity
    maturity = store_pikmin_attribute(maturity_templates, "maturity", maturity, template_to_add)
    plt.close()
    return maturity



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
    color = store_pikmin_attribute(color_templates, "color", color, pikmin_image[170:200,20:140,:])

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
    for y,x in peak_local_max(results[0], threshold_abs=0.9, exclude_border=10):
        full_heart_locations.append(x)
    if len(full_heart_locations) != 0:
        last_full_position = max(full_heart_locations)
    else:
        last_full_position = 0

    # Get X coordinate of left heart
    try:
        heart_x_coord = np.unique( np.transpose(heart_locations)[1] )
        heart_x_coord.sort()
        left_heart = heart_x_coord[0]

        # Check if last full position is full or empty by
        # checking if Green channel is less than 150
        x_pos = heart_x_coord[-1] + 6
        y_pos = heart_locations[0][0] + 4
        is_empty = pikmin_image[y_pos,x_pos,1] > 150

        # Convert to number of hearts
        if left_heart < 43:
            # Check if last heart is a full heart
            if last_full_position > 105 and not is_empty:
                # Check RGB of center of this heart to see
                # if it's full or empty
                return 4
            else:
                return 3
        # TODO need to check if these are actually one friendship lower
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

# Determine whether a pikmin has been selected for the challenge
# based on average color of bottom line of partitioned area
# 
# TODO definitely need to figure out a better way to do this for
#      other sized images
def check_if_selected(image):
    # Get last line of section
    cropped_bottom = list(image[-1,:,0])

    # Get left half and right, ignoring middle in case pikmin
    # below is sticking up
    section_length = int(len(cropped_bottom)/4)
    left_pixels  = cropped_bottom[0:section_length]
    right_pixels = cropped_bottom[-section_length:]

    # Average the parts to see if not white
    left_avg = np.average(left_pixels)
    right_avg = np.average(right_pixels)

    threshold = 248
    return left_avg < threshold and right_avg < threshold

# Determine what the maturity of the pikmin is
def get_maturity(pikmin_image):
    maturity_templates = load_maturity_templates()

    # Convert to grayscale
    sub_image = pikmin_image[0:100,:,:]
    image_gray = rgb2gray(sub_image)

    # Determine which has a match
    match_count = {}
    for key, val in maturity_templates.items():
        match_count[key] = 0
        for mapping in val:
            result = match_template(image_gray, mapping)
            peaks = peak_local_max(result, threshold_abs=0.9, exclude_border=5)
            match_count[key] += len( peaks )

    # Check if any matches
    if max(match_count.values()) < 1:
        return prompt_user_maturity(sub_image, maturity_templates)
    else:
        return max(match_count, key=match_count.get)

def identify_image(path_to_image):
    # Crop image to get rid of location/system buttons
    cropped = crop_image(path_to_image)

    # Get heart locations and partition image
    heart_y_coord = get_heart_locations(cropped)
    pikmin_images = partition_image(cropped, heart_y_coord)

    for i in range(len(pikmin_images)):
        pikmin_hearts = get_pikmin_heart_icon_count( pikmin_images[i] )

        # If no hearts were found, this is because it's hidden behind
        # a button or cut off the screen
        if (pikmin_hearts < 0):
            continue

        color = get_pikmin_color_by_name( pikmin_images[i] )
        is_selected = check_if_selected( pikmin_images[i] )
        maturity = get_maturity( pikmin_images[i] )
        # TODO get decor
        print(f"Pikmin {str(i).rjust(2)} is a {color.rjust(7)} with {maturity.rjust(6)} and {pikmin_hearts} heart icons : Selected = {is_selected}")

    # TODO save data to CSV
    # TODO create function to compare to other screenshots


if __name__ == "__main__":
    #identify_image("../screenshots/white_not_full.jpg")
    #identify_image("../screenshots/full_hearts.jpg")
    #identify_image("../screenshots/small_hearts.jpg")
    #identify_image("../screenshots/blue_leaves.jpg")
    files = glob.glob("../screenshots/*.jpg")
    for file in files:
        print(f" Identifying {file}")
        identify_image(file)


