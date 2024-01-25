#This program resizes the shoe images with a bounding rectangle to have just the shoe subject. It then
#resizes the shoe with padding to desired resolution
import os
import glob
from PIL import Image
import cv2

def resize_with_padding(image, target_size):
    #find current image resolution
    original_aspect = image.width / image.height

    #find desired resolution based on previously specified deminsions
    new_aspect = target_size[0] / target_size[1]

    #check if image is wider or taller
    if original_aspect > new_aspect:
        #if wider adjust the height
        new_height = int(target_size[0] / original_aspect)
        #adding antialias from pillow to make resizing smoother
        image = image.resize((target_size[0], new_height), Image.ANTIALIAS)
    else:
        #if taller adjust the width
        new_width = int(target_size[1] * original_aspect)
        image = image.resize((new_width, target_size[1]), Image.ANTIALIAS)

    #create new image with white padding as background
    new_image = Image.new("RGB", target_size, "white")

    #paste new image into center of white background
    new_image.paste(image, ((target_size[0] - image.width) // 2, (target_size[1] - image.height) // 2))

    return new_image

#find all files with image extension and return as list
def find_images(base_directory):
    image_extensions = ['png', 'jpg', 'jpeg', 'bmp', 'gif']
    images = []

    for extension in image_extensions:
        images.extend(glob.glob(base_directory + '/**/*.' + extension, recursive=True))

    return images

def bounding_rect_crop(img):
    #convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    #use inverse binary thresholding to make subject white, and white background black
    _, thresh = cv2.threshold(gray, 254, 255, cv2.THRESH_BINARY_INV)

    #finding the contours against the black bg
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #largest contour will be the shoe
    subject_contour = max(contours, key=cv2.contourArea)

    #place bounding rectangle around shoe
    x, y, w, h = cv2.boundingRect(subject_contour)

    #crop the image to the bounding rectangle
    cropped_image = img[y:y+h, x:x+w]

    return cropped_image

def process_and_save_image(image_path, new_directory):
    #open and read image
    image = cv2.imread(image_path)

    #specify target resolution here in format width, height
    target_size = (190, 100)

    #crop around shoe only
    cropped_image = bounding_rect_crop(image)

    #convert from cv2 BGR to RGB for numpy
    rgb_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)

    #convert from numpy to PIL Image
    pil_image = Image.fromarray(rgb_image)

    #resize the image
    resized_image = resize_with_padding(pil_image, target_size)

    #save new image into directory
    new_image_path = os.path.join(new_directory, os.path.basename(image_path))
    resized_image.save(new_image_path)

#base directory
base_directory = '/your/directory/here'
#new base directory to ouput images
new_base_directory = '/your/directory/here_modified'

#store all image files in list
all_images = find_images(base_directory)

#process all images
for image_path in all_images:
    #new directory path
    sub_dir = os.path.dirname(image_path).replace(base_directory, new_base_directory)

    #create new dir if doesnt exist
    if not os.path.exists(sub_dir):
        os.makedirs(sub_dir)

    #process and save image into new dir
    process_and_save_image(image_path, sub_dir)
