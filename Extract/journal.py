from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


options = Options()
options.headless = False 
driver = webdriver.Firefox(options=options)

base_url = "https://www.scimagojr.com/journalrank.php?country=MA&year="


def download_for_year(year):
    url = f"{base_url}{year}"
    driver.get(url)
    
    try:
      
        download_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//a[@class="button" and contains(@href, "xls")]'))
        )
     
        download_button.click()
       
        time.sleep(10)  
    
    except Exception as e:
        print(f"Erreur lors du téléchargement pour l'année {year}: {e}")


for year in range(2008, 2024):
    download_for_year(year)

driver.quit()
