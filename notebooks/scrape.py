import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

from bs4 import BeautifulSoup

### Section 1

def extract_full_advertisement_details(ad_soup, ad_url, keywords):
    # Ad soup goes in, Advertisement object comes out  
    
    # Body section
    ad_body_container = ad_soup.find("section", class_="show-more-less-html")
    # Add more code here for extracting additional details from the ad body if needed
    
    # Return the extracted details (modify as needed based on your requirements)
    return ad_body_container.get_text(strip=True) if ad_body_container else None



# Ask for user input
location = input("Enter the location of the file: ")
jobtype = input("Enter the job type: ")
total_jobs = int(input("Enter the number of jobs to scrape: "))
output_file = input("Enter the output file name(only name with .csv): ")

url = f"https://www.linkedin.com/jobs/{jobtype}-jobs/?location={location}"


# Set up the WebDriver with the start-maximized option
options = webdriver.EdgeOptions()
options.add_argument("start-maximized")
driver = webdriver.Edge(options=options)



driver.get(url)


job_titles = []
job_companies = []
job_locations = []
job_links = []
job_descriptions = []

print("Scraping jobs...")


# Infinite scroll
while len(job_titles) < total_jobs:
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        print("Scrolling to the bottom of the page...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for page to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if new_height == last_height:
            break
        
        last_height = new_height

    # Parse page source with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Extract data
    job_title_elements = driver.find_elements(by="class name", value="base-search-card__title")
    job_titles += [element.text for element in job_title_elements]

    job_company_elements = driver.find_elements(by="class name", value="base-search-card__subtitle")
    job_companies += [element.text for element in job_company_elements]

    job_location_elements = driver.find_elements(by="class name", value="job-search-card__location")
    job_locations += [element.text for element in job_location_elements]

    job_link_elements = driver.find_elements(by="class name", value="base-card__full-link")
    job_links += [element.get_attribute("href") for element in job_link_elements]
    
    # job description
    for link in job_links:
        driver.get(link)
        ad_soup = BeautifulSoup(driver.page_source, 'html.parser')
        job_descriptions.append(extract_full_advertisement_details(ad_soup, link, jobtype))
        time.sleep(2)

    print(f'Total Jobs Extracted: {len(job_titles)}')
    print(f'Total titles: {len(job_title_elements)}')
    print(f'Total companies: {len(job_company_elements)}')
    print(f'Total locations: {len(job_location_elements)}')
    print(f'Total links: {len(job_link_elements)}')
    print(f'Total descriptions: {len(job_descriptions)}')

    # append what we scraped till now to the `jobs.csv` file and save this file to disk
    print("Saving to CSV...")
    jobsss = {
        'Job Title': job_titles,
        'Company': job_companies,
        'Location': job_locations,
        'Description': job_descriptions, # add this line to the dictionary
        'Link': job_links,
    }
    df = pd.DataFrame.from_dict(jobsss, orient='index')
    df = df.transpose()
    
    # Use mode='a' to append to the existing file
    csv_file = f'{output_file}.csv'
    df.to_csv(csv_file, mode='a', header=False, index=False)
    print(f'Saved to CSV. Total jobs: {len(df)}')

    try:
        # Use WebDriverWait with ExpectedConditions to wait for the button to be clickable
        button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "infinite-scroller__show-more-button"))
        )
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "infinite-scroller__show-more-button"))
        )
        button.click()
        print("Clicking 'Show More' button...")
    except (NoSuchElementException, ElementNotInteractableException):
        # No more "Show More" button or button not interactable, break the loop
        print("No more 'Show More' button. Stopping...")
        break

# Close the WebDriver
driver.quit()

print("Job scraping completed. Check 'jobs.csv' for the results.")

