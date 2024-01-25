#Script that grabs image links for one shoe model from kickscrew.com and fills a csv with the links
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
import csv

#open logfile in append mode
logfile = open('shoe_collection_log.txt', 'a')

#write inputted string to logfile
def log(content):
    logfile.write(content)
    logfile.write('\n')
    logfile.flush()


#using selenium with chrome webdriver
options = webdriver.ChromeOptions()

#headless doesnt open browser
options.add_argument("--headless")


driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

#ask user for shoe to search
shoe_model = input("Enter a shoe to search: ")

#log message
log("Searching for shoe: {}".format(shoe_model))

#for csv header replace spaces with _
header_shoe = shoe_model.replace(" ", "_")
csv_header = [header_shoe]

#name csv after current shoe
csv_name = "{}.csv".format(header_shoe)

#create csv file if doesnt exist, otherwise open in append format
if not Path(csv_name).exists():
    with open(csv_name, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(csv_header)

#replace spaces with '%20' for url format
shoe_model = shoe_model.replace(" ", "%20")

#start at this page
page_number = 1

#loop until no more images left
while True:
    #url of current page
    url = "https://www.kickscrew.com/search?q={query}&page={pnum}&hitsPerPage=64".format(query = shoe_model, pnum = page_number)

    #log url with cur page number to track if error
    log("[INFO] url: {}".format( url))

    #open url with driver
    driver.get(url)

    #in console print out every 5 pages to know its running
    if page_number % 5 == 0:
        print("On page {pnum}, contnuing...".format(pnum = page_number))


    #set up explicit wait for 1 second
    wait = WebDriverWait(driver, 1)

    #flag to check if its been through all pages
    shoes_found = 0
    try:
        #wait one second to make sure all img are loaded
        image_elements = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'img')))

        #loop through all image elements
        for image in image_elements:
            src = image.get_attribute('src')

            #make sure image link is in format of shoe, not other images on page
            if src and 'https://cdn.shopify.com/s/files' in src:
                shoes_found = 1
                #create list of size 1 for writerow
                temp_list = []
                temp_list.append(src)
                #add image link to csv
                with open(csv_name, 'a', newline='') as csvfile:
                    csv_writer = csv.writer(csvfile)
                    csv_writer.writerow(temp_list)

        #when no shoe images on page, break out of loop and end program
        if shoes_found == 0:
            log("[INFO] search ended on page {pnum}".format(pnum = page_number))
            print("search ended on page {pnum}".format(pnum = page_number))
            break

        #increase page number
        page_number = page_number + 1

    except TimeoutException:
        print("Timed out waiting for images to load")
        log("[Error] timeout exception")
        break

driver.quit()
