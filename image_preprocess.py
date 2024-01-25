#applying transformations on images to increase diversity in shoe image dataset
import cv2
import numpy as np
import os
from pathlib import Path

def remove_white_background(image):
    #convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #apply inverse binary treshold to make the white background black and the shoe white
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

    #largest contour is the shoe
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask = np.zeros_like(gray)

    #draw image onto mask
    cv2.drawContours(mask, contours, -1, (255), thickness=cv2.FILLED)

    #seperate image from mask
    result = cv2.bitwise_and(image, image, mask=mask)
    return result, mask


#turn the mask found previously into white background
def paste_on_white_background(image, mask):
    white_background = np.ones_like(image, dtype=np.uint8) * 255
    white_background[mask == 255] = image[mask == 255]
    return white_background

#smooth mask to make it cleaner
def smooth_mask(mask):
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=1)
    mask = cv2.dilate(mask, kernel, iterations=1)
    return mask

#create a mirrored directroy to input directory
def process_directory(input_dir, output_dir):
    #go through all files in input directory
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                image_path = os.path.join(root, file)
                output_subdir = root.replace(input_dir, output_dir)

                #create output directory if necissary
                Path(output_subdir).mkdir(parents=True, exist_ok=True)

                #apply image transformations on image
                process_image(image_path, output_subdir)

#brighten image at random rate
def brighten_image(image):
    alpha = np.random.uniform(1.1, 1.2)
    beta = np.random.uniform(10, 20)
    brightened = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return brightened

#dim image at random rate
def dim_image(image):
    alpha = np.random.uniform(0.8, 0.9)
    beta = np.random.uniform(-20, -10)
    dimmed = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return dimmed

#apply cv2 and custom image transformations on inputted image
def apply_transformations(image, mask):
    original_shoe = image
    gray_shoe = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    bright_shoe = brighten_image(image)
    dim_shoe = dim_image(image)

    flip_shoe = cv2.flip(image, 1)
    flip_gray_shoe = cv2.flip(gray_shoe, 1)
    flip_bright_shoe = cv2.flip(bright_shoe, 1)
    flip_dim_shoe = cv2.flip(dim_shoe, 1)

    return original_shoe, gray_shoe, bright_shoe, dim_shoe, flip_shoe, flip_gray_shoe, flip_bright_shoe, flip_dim_shoe

#process and save the inputted image
def process_image(image_path, output_subdir):
    #read in image
    image = cv2.imread(image_path)
    shoe, mask = remove_white_background(image)

    #remove jagged edges
    mask = smooth_mask(mask)

    #apply all the image transformations
    original_shoe, gray_shoe, bright_shoe, dim_shoe, flip_shoe, flip_gray_shoe, flip_bright_shoe, flip_dim_shoe = apply_transformations(shoe, mask)

    #need to convert grayscale to BGR
    gray_shoe = cv2.cvtColor(gray_shoe, cv2.COLOR_GRAY2BGR)
    flip_gray_shoe = cv2.cvtColor(flip_gray_shoe, cv2.COLOR_GRAY2BGR)

    #transfomrations and their file names
    transformations = {
        "original": original_shoe,
        "gray": gray_shoe,
        "bright": bright_shoe,
        "dim": dim_shoe,
        "flip": flip_shoe,
        "flip_gray": flip_gray_shoe,
        "flip_bright": flip_bright_shoe,
        "flip_dim": flip_dim_shoe
    }

    #image name without the extension
    base_name = os.path.splitext(os.path.basename(image_path))[0]

    #paste image on white background and save
    for transformation_name, transformed_image in transformations.items():
        use_mask = mask if 'flip' not in transformation_name else cv2.flip(mask, 1)
        final_image = paste_on_white_background(transformed_image, use_mask)
        output_filename = f"{base_name}_{transformation_name}.jpg"
        output_file_path = os.path.join(output_subdir, output_filename)
        cv2.imwrite(output_file_path, final_image)


#desired input/output paths
input_dir = '/your/input/directory/here'
output_dir = '/your/output/directory/here'

process_directory(input_dir, output_dir)
