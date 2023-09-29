# DateTime
import time
from datetime import datetime

# Selenium
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException

# SQL Server PYODBC
import pyodbc as odbc

DRIVER_NAME = 'Hidden'      # Database information is hidden for security reasons
SERVER_NAME = 'Hidden'
DATABASE_NAME = 'Hidden'

connection_string = f"""
    DRIVER={{{DRIVER_NAME}}};
    SERVER={SERVER_NAME};
    DATABASE={DATABASE_NAME};
    Trust_Connection=yes;
"""
conn = odbc.connect(connection_string)
cursor = conn.cursor()

# Constants
ITEMS_PER_PAGE = 32
MAX_ADS = 4

# Set Browser Driver
s = Service('Hidden')   # Browser driver is hidden for security reasons

# Set Options (Headless, No Images)
o = Options()
o.add_argument('--headless')
o.set_preference('permissions.default.image', 2)

# Set webdriver
driver = webdriver.Firefox(service= s, options= o)

# Get the number of pages
driver.get('https://www.mec.ca/en/products/packs-and-bags/backpacking-packs/c/1338')
time.sleep(2)
numTents = driver.find_element('css selector', '.findify-components-search--query').get_property('innerHTML').lstrip('Showing ').rstrip(' results')
numPages = round(int(numTents) / ITEMS_PER_PAGE) + 1

# Iterate through the number of pages
for i in range(numPages) :
    if i != 0 :
        driver.get(f'https://www.mec.ca/en/products/packs-and-bags/backpacking-packs/c/1338?offset={i * 32}')
        time.sleep(2)

    # Output the name and price of every item on the page
    for i in range(1, ITEMS_PER_PAGE + MAX_ADS) :
        try :
            # Scrape name and price
            name = driver.find_element('css selector', f'li.findify-components-common--grid__column:nth-child({i}) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > h3:nth-child(1)').get_property('innerHTML').replace("'", "''")
            price = driver.find_element('css selector', f'li.findify-components-common--grid__column:nth-child({i}) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > div:nth-child(3) > span:nth-child(1)').get_property('innerHTML').split(" ")[0]
            
            command = f"SELECT productID FROM products WHERE name = '{name}';"

            cursor.execute(command)

            productID = cursor.fetchone()

            if not productID :
                cursor.execute(f"INSERT INTO products(name, category) VALUES ('{name}', 'Backpacks');")
                cursor.execute(command)
                productID = cursor.fetchone()[0]
            else :
                productID = productID[0]

            cursor.execute("INSERT INTO product_price(productID, price, datetime) VALUES (?, ?, ?);", productID, price, f'{datetime.now():%Y-%m-%d %H:%M:%S}')
        except NoSuchElementException :
            pass

# Commit and close connection to DB
cursor.commit()
conn.close()