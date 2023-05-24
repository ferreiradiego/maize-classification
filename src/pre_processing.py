## --- Import the packages and functions
from tools.functions import *
import os
import shutil
import glob
import matplotlib.pyplot as plt
### ---

## --- Definitions, parameters and directory paths

quality = ['com_defeitos', 'sem_defeitos']
sample = ['Amostra1', 'Amostra2', 'Amostra3', 'Amostra4', 'Amostra5']
sub_sample = ['50', '60', '70', '80', '90', '100']

# X and Y limits to crop the images
x_start = 50
x_end = 1100
y_start = 250
y_end = 1300

# Directory paths of original images
# [origin, destination]
original_paths = ['img/dataset/original/', 'img/dataset/original/todas/']

# Directory paths of pre processed images
path_original_images    = original_paths[1]
hsv_path                = r'img/dataset/pre_processada/hsv/'
rgb_path                = r'img/dataset/pre_processada/rgb/'
gray_path               = r'img/dataset/pre_processada/gray/'
hist_path               = r'img/dataset/pre_processada/hist/'

## ---

## --- STEP 1: Initial preparation of the dataset, label the images according to the number of defects and the quantity of grains in the sample.

# Loop over all possible combinations of sample and sub_sample
for i, s in enumerate(sample):
    for ss in sub_sample:
        
        # Loop over both quality items
        for q, q_num in zip(quality, [1, 6]):
            
            # Define the path to the directory containing the images for the current combination of quality, sample, and sub_sample
            path = os.path.join(original_paths[0], q, s, ss)
            
            # Get a list of all filenames in the directory that ends with '.jpg'
            image_filenames = [filename for filename in os.listdir(path) if filename.endswith('.jpg')]
            
            # Loop over all image filenames in the current directory
            for j, filename in enumerate(image_filenames):
                
                # Define the destination filename using an f-string that incorporates the values of i, ss, and j, and also includes the corresponding quality item and a running number
                dst = os.path.join(original_paths[1], f'a{i+q_num}_{ss}_{j+1}.jpg')
                
                # Copy the current file from the source directory to the destination directory
                shutil.copy(os.path.join(path, filename), dst)

## ---

## --- STEP 2: Perform the preprocessing

# This line uses the glob module to get a list of all .jpg files in the path_original_images directory
images_filenames = glob.glob(f'{path_original_images}*.jpg')
# This line reads each image in the 'images_filenames' list in BGR format
images_bgr = [cv2.imread(img_path) for img_path in images_filenames]

# Process each image individually
for img_path, img_bgr in zip(images_filenames, images_bgr):

    # Extracts the file name
    img_name = os.path.basename(img_path)

    ## Origin and destiny paths
    full_destiny_path_hsv = os.path.join(hsv_path, img_name)
    full_destiny_path_rgb = os.path.join(rgb_path, img_name)
    full_destiny_path_gray = os.path.join(gray_path, img_name)
    full_destiny_path_hist = os.path.join(hist_path, img_name)
    ## ---

    ## Convert image to other color spaces and remove background
    new_bgr, new_hsv, gray = convert_images(img_bgr, True)
    ## ---

    ## Crop the image
    new_bgr = crop_image(new_bgr, x_start, x_end, y_start, y_end)
    ## ---

    # Convert image to other color spaces
    new_bgr, new_hsv, gray = convert_images(new_bgr, False)
    # ---

    ## Calculate histogram
    # hist = cv2.calcHist([gray], [0], None, [256], [1, 256])
    ## ---

    ## Save all images
    # plt.clf()
    # plt.bar(range(256), hist.ravel(), color='gray')
    # plt.savefig(full_destiny_path_hist)
    cv2.imwrite(full_destiny_path_rgb, new_bgr)
    # cv2.imwrite(full_destiny_path_hsv, new_hsv)
    cv2.imwrite(full_destiny_path_gray, gray)
    ## ---

## ---

## --- STEP 3: Prepare dataset and Perform the preprocessing (only for Amostra6)

quality_item = 'sem_defeitos'
sample_item = 'Amostra6'

# Loop over all sub_samples
for ss in sub_sample:

    # Define the path to the directory containing the images for the current combination of quality, sample, and sub_sample
    path = os.path.join(original_paths[0], quality_item, sample_item, ss)

    # Get a list of all filenames in the directory that ends with '.jpg'
    image_filenames = [filename for filename in os.listdir(path) if filename.endswith('.jpg')]

    # Loop over all image filenames in the current directory and copy them to the destination directory
    for j, filename in enumerate(image_filenames):
        dst = os.path.join(original_paths[1], f'a11_{ss}_{j+1}.jpg')
        shutil.copy(os.path.join(path, filename), dst)

# Read all JPG images in the directory that start with 'a11' and store them in a list
images_filenames = glob.glob(f'{path_original_images}a11*.jpg')
images_bgr = [cv2.imread(img_path) for img_path in images_filenames]

for img_path, img_bgr in zip(images_filenames, images_bgr):

    img_name = os.path.basename(img_path)

    ## Origin and destiny paths
    full_destiny_path_hsv = os.path.join(hsv_path, img_name)
    full_destiny_path_rgb = os.path.join(rgb_path, img_name)
    full_destiny_path_gray = os.path.join(gray_path, img_name)
    full_destiny_path_hist = os.path.join(hist_path, img_name)
    ## ---

    ##  ---------------

    ## Convert image to other color spaces
    new_bgr, new_hsv, gray = convert_images(img_bgr, True)
    ## ---

    ## Set lower and upper bounds for thresholding
    lower_bound = np.array([20, 20, 80])
    upper_bound = np.array([255, 255, 255])

    ## Apply thresholding to the BGR image
    thresh = cv2.inRange(new_bgr, lower_bound, upper_bound)

    ## Define kernel for erosion and apply it to the thresholded image
    kernel = np.ones((15,15), np.uint8)
    erosion = cv2.erode(thresh, kernel, iterations=3)

    ## Define kernel for dilation and apply it to the eroded image
    kernel = np.ones((17,17), np.uint8)
    dilation = cv2.dilate(erosion, kernel, iterations=5)

    # Create a mask with the result of the dilation
    mask = cv2.bitwise_not(dilation)

    # Apply the mask to the BGR image
    result = cv2.bitwise_and(new_bgr, new_bgr, mask=mask)
    
    ##  ---------------

    ## Crop the image
    result = crop_image(result, 20, 1200, 200, 1600)
    ## ---

    # Convert image to other color spaces
    new_bgr, new_hsv, gray = convert_images(result, False)
    # ---

    # Calculate histogram
    # hist = cv2.calcHist([gray], [0], None, [256], [1, 256])
    # ---

    ## Save all images
    # plt.clf()
    # plt.bar(range(256), hist.ravel(), color='gray')
    # plt.savefig(full_destiny_path_hist)
    cv2.imwrite(full_destiny_path_rgb, new_bgr)
    # cv2.imwrite(full_destiny_path_hsv, new_hsv)
    cv2.imwrite(full_destiny_path_gray, gray)
    ## ---

## ---