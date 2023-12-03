import variables
import csv
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import logging

logging.basicConfig(level=logging.ERROR)
logging.getLogger().setLevel(logging.ERROR)

# Chrome driver
driver = webdriver.Chrome('C:/Users/azizm/chromedriver')

driver.get('https://www.linkedin.com/')
sleep(2)

# Login to LinkedIn
username = driver.find_element(By.NAME, 'session_key')
username.send_keys(variables.my_username)  # username field
password = driver.find_element(By.NAME, 'session_password')
password.send_keys(variables.my_password)  # password field
log_in_button = driver.find_element(
    By.CLASS_NAME, 'sign-in-form__submit-btn--full-width')  # submit button
log_in_button.click()

# Define the search query
query = variables.query
base_url = 'https://www.google.com/search?q='
url = base_url + query

# Define the number of pages to scrape
num_pages = variables.num_pages

# Counting scraped profiles
sc = 1

# Loop over the pages of search results
for i in range(12, num_pages):
    print('Google Page ' + str(i))
    # Navigate to the current page of search results
    if i == 0:
        driver.get(url)
    else:
        next_page_url = url + '&start=' + str(i * 10)
        driver.get(next_page_url)
        sleep(10)

    # Extract the profile URLs from the search results
    linkedin_users_urls_list = driver.find_elements(
        By.XPATH, '//div[@class="yuRUbf"]/a[@href]')
    profile_urls = [users.get_attribute("href").replace('tn.', '')
                    for users in linkedin_users_urls_list]

    # # Shuffle the order of the profiles before scraping
    # random.shuffle(profile_urls)

    # Scrape the profile data
    fields = ['Name', 'Education', 'Experiences']
    with open(variables.file_name, 'a', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        if i == 0:
            writer.writerow(fields)

        for profile in profile_urls:
            driver.get(profile)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            try:
                WebDriverWait(driver, 5).until(EC.presence_of_element_located(
                    (By.CLASS_NAME, 'text-heading-xlarge')))
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                name = soup.select_one('.text-heading-xlarge')
                name = name.get_text().strip() if name else 'No Result'
            except TimeoutException:
                name = 'No Result'

            # Get education (ESPRIT)
            driver.get(profile + '/details/education')
            education = []
            try:
                WebDriverWait(driver, 5).until(EC.presence_of_element_located(
                    (By.CLASS_NAME, 'pvs-list__paged-list-item')))
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                educ_sections = soup.find_all(
                    "li", "pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated")
                if educ_sections:
                    for ed in educ_sections:
                        if 'ESPRIT' in ed.get_text():
                            education_details_list = ed.select(
                                'li span.visually-hidden')
                            education.append(' '.join([ed.get_text().strip(
                            ) for ed in education_details_list]) if education_details_list else 'No Result')
                else:
                    education.append('No Result')
            except TimeoutException:
                print('Timeout while waiting for educations to load')
                desc = 'No Result'

            # Get experiences
            driver.get(profile + '/details/experience')
            try:
                WebDriverWait(driver, 5).until(EC.presence_of_element_located(
                    (By.CLASS_NAME, 'pvs-list__paged-list-item')))
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                experiences = []
                exp_sections = soup.find_all(
                    "li", "pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated")
                if exp_sections:
                    print(str(sc) + ' Experiences found')
                    sc += 1
                    for exp in exp_sections:
                        job_desc_list = exp.select('li span.visually-hidden')
                        if job_desc_list:
                            desc = ''
                            for jd in job_desc_list:
                                if (len(jd.get_text().strip()) > 100):
                                    desc += jd.get_text().strip() + '\n'
                        else:
                            desc = 'No Result'
                        experiences.append(desc)
                else:
                    print('No experiences found')
                writer.writerow(
                    [name, '\n'.join(education), '\n'.join(experiences)])
            except TimeoutException:
                print('Timeout while waiting for experiences to load')
