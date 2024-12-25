from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from azure.storage.blob import BlobServiceClient
import requests
import time
import io
import os
from dotenv import load_dotenv, dotenv_values


# Load environment variables
load_dotenv()
account_name = os.getenv("account_name")
account_key = os.getenv("account_key")
container_name = "raw"

# Initialize Azure Blob Service Client
blob_service_client = BlobServiceClient(
    account_url=f"https://{account_name}.blob.core.windows.net", 
    credential=account_key
)

# Selenium setup
options = Options()
options.headless = False  # Set to True to run browser in headless mode
driver = webdriver.Firefox(options=options)

base_url = "https://www.scimagojr.com/journalrank.php?country=MA&year="

# Function to download and upload data for a specific year
def download_for_year(year):
    url = f"{base_url}{year}"
    driver.get(url)

    try:
        # Wait for the download button to be clickable
        download_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//a[@class="button" and contains(@href, "xls")]'))
        )

        # Get the file URL (rather than downloading locally)
        file_url = download_button.get_attribute("href")
        
        # Fetch the content of the file
        response = requests.get(file_url)
        response.raise_for_status()  # Ensure successful response

        # Upload directly to Azure Data Lake
        blob_name = f"journal_rankings/{year}.xls"
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        blob_client.upload_blob(io.BytesIO(response.content), overwrite=True)
        print(f"Uploaded data for year {year} to Azure Data Lake.")

    except Exception as e:
        print(f"Error processing year {year}: {e}")

# Loop through the years and process each
for year in range(2008, 2024):
    download_for_year(year)

# Close the Selenium driver
driver.quit()
