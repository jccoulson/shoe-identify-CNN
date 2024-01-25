#Script to go through csv file and download images from links into given directory
import requests
import csv
import pandas as pd
import os
def download_image(image_url, filename, shoe_model):
    #get request to image url
    response = requests.get(image_url)

    #check status response from request
    if response.status_code == 200:
        #add directory you want images to be saved to here
        directory = 'your/path/here/{shoe}_images'.format(shoe = shoe_model)
        full_path = os.path.join(directory,filename)

        #open specified image path and write response image into it
        with open(full_path, 'wb') as file:
            file.write(response.content)
        print(f"Image successfully downloaded: {filename}")
    else:
        print("Failed to download image")

#Enter shoe name into console that follows format of shoe image csv
shoe_model = input("Enter a shoe to download: ")
shoe_model = shoe_model.replace(" ", "_")
shoe_csv = "{}.csv".format(shoe_model)

#open csv
file = pd.read_csv(shoe_csv)

#new directory will be named after shoe model
directory = "{shoe}_images".format(shoe = shoe_model)

#Replaec with directory where your image csv is located
paren_dir = "/your/directory/here/"
path = os.path.join(paren_dir, directory)

#create dir if doesnt exist
if not os.path.exists(path):
    os.mkdir(path)

#look through csv and save each image
for index, row in file.iterrows():
    #each row is a image url
    image_url = row[shoe_model]
    #each image will be in format  `shoe`#.jpg
    file_name = '{shoe}{i}.jpg'.format(shoe = shoe_model, i = index)
    download_image(image_url, file_name, shoe_model)
