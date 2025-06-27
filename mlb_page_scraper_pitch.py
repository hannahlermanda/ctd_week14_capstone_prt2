from time import sleep
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

#Set up the URLS to be scraped
base_url = "https://www.baseball-almanac.com/"
main_url = base_url + "pimenu.shtml"

#Try-Except block
try:
    #Retrieve the URL
    driver.get(main_url)
    #Let the page load
    sleep(2)

    #Find all of the link with anchor <a> elements
    all_links = driver.find_elements(By.CSS_SELECTOR, 'a')
    #Start with an empty list to iterate through
    career_links = []
    #Iterate
    for link in all_links:
        #Look for the links that literally have 'career'
        if link.text.strip().lower() == 'career':
            #If they have 'career', get their href
            href = link.get_attribute('href')
            #If the href starts with the base_url (https://www.baseball-almanac.com/) + pitching/ then add it to career_links list
            if href and href.startswith(base_url + "pitching/"):
                career_links.append(href)

    #How many links were found
    print(f"Found {len(career_links)} career pages.")

    #For every URL in the career_links list
    for url in career_links:
        #Visit the URL via the scraper
        driver.get(url)
        #Wait for the page to fully load
        sleep(2)

        #Find the main data table inside div.ba-table to extract the data
        try:
            #Find the necessary nested elements
            table_div = driver.find_element(By.CSS_SELECTOR, 'div.ba-table')
            table = table_div.find_element(By.TAG_NAME, 'table')
            rows = table.find_elements(By.TAG_NAME, 'tr')

            #Start off with an empty list for the headers (of the tables since they differ per page) and the data
            headers = []
            data = []

            #For every row in the table
            for row in rows:
                #Check to see if it has the 'td' tag
                cols = row.find_elements(By.TAG_NAME, 'td')
                if not cols:
                    continue
                #Run text strip on every cell in the rows of the columns from inside the table cells; put them in a list called cell_texts
                cell_texts = [col.text.strip() for col in cols]
                #Grab the class of the rows in the columns to prepare for check if it has the 'banner' class
                classes = [col.get_attribute("class") for col in cols]

                #If all of the cells in a row have the class of 'banner'
                if all("banner" in c for c in classes):
                    #Make it the header row of the csv
                    headers = cell_texts
                #If the header rows match the number of cells in a row, append the text of the cells to the data list
                elif headers and len(cell_texts) == len(headers):
                    data.append(cell_texts)

            if headers and data:
                #Create a dataframe with headers on top of the columns
                df = pd.DataFrame(data, columns=headers)
                #Name the files the name of the page and clean it
                page_title = driver.title.split("|")[0].strip().replace(" ", "_").replace("/", "_")
                #Actually name the csv file with page_title
                df.to_csv(f"{page_title}.csv", index=False)
                #Notify the user of the creation of the csv file
                print(f"Saved {page_title}.csv with {len(df)} rows.")
            else:
                #If no data is found on the URL, notify the user
                print(f"No valid data found on: {url}")

        except Exception as e:
            print(f"Error parsing table at {url}: {e}")

finally:
    #Close the browser connection
    driver.quit()
