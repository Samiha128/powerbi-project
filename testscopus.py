from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
from dotenv import load_dotenv, dotenv_values
from selenium.webdriver.common.keys import Keys
import requests
from azure.storage.blob import BlobServiceClient
import io

# Load environment variables
load_dotenv()
email = os.getenv("email")
password = os.getenv("password")
account_name = os.getenv("account_name")
account_key = os.getenv("account_key")
container_name = "raw"

# Initialize Azure Blob Service Client
blob_service_client = BlobServiceClient(
    account_url=f"https://{account_name}.blob.core.windows.net", 
    credential=account_key
)

load_dotenv()
email = os.getenv("email")
password = os.getenv("password")
options = Options()
options.headless = False  
driver = webdriver.Firefox(options=options)

try:
    driver.get("https://id.elsevier.com/as/authorization.oauth2?platSite=SC%2Fscopus&ui_locales=en-US&scope=openid+profile+email+els_auth_info+els_analytics_info+urn%3Acom%3Aelsevier%3Aidp%3Apolicy%3Aproduct%3Aindv_identity&els_policy=idp_policy_indv_identity_plus&response_type=code&redirect_uri=https%3A%2F%2Fwww.scopus.com%2Fauthredirect.uri%3FtxGid%3Dc8a47371f6fa06e7c4dc1f039d810077&state=userLogin%7CtxId%3D332F25148AF1138B4443269C002A9E33.i-01517864e45725ab6%3A5&authType=SINGLE_SIGN_IN&prompt=login&client_id=SCOPUS")
    wait = WebDriverWait(driver, 10)
    print("Ouverture de la page Scopus...")

    # Login process
    email_input = wait.until(EC.presence_of_element_located((By.ID, "bdd-email")))
    email_input.send_keys(email)
    print("Email saisi.")
    email_next_button = driver.find_element(By.ID, "bdd-elsPrimaryBtn")
    email_next_button.click()
    print("Bouton 'Suivant' cliqué après email.")
  
    try:
        accept_cookies_button = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
        accept_cookies_button.click()
        print("Cookies acceptés.")
    except Exception as e:
        print("Le bouton d'acceptation des cookies n'a pas été trouvé ou n'est pas cliquable :", str(e))
    
    time.sleep(20)

    password_input = wait.until(EC.presence_of_element_located((By.ID, "bdd-password")))
    password_input.send_keys(password)
    print("Mot de passe saisi.")
   
    password_next_button = driver.find_element(By.ID, "bdd-elsPrimaryBtn")
    password_next_button.click()
    print("Connexion effectuée.")
   
    time.sleep(20)

    # Set up filter and search (similar to the original code)
    affiliation_dropdown = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "Select-module__vDMww")))
    affiliation_dropdown.click()  
    affiliation_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//option[@label='Affiliation country' and @value='AFFILCOUNTRY']")))
    affiliation_option.click()
    print("Sélecteur 'Affiliation country' cliqué.")
    time.sleep(5)
    search_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[data-testid='search-field-input']")))
    search_field.send_keys("Morocco")
   
    search_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and contains(@class, 'Button-module__nc6_8')]")))
    search_button.click()
    time.sleep(20)

    # Setting the range of years
    from_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[data-testid='input-range-from']")))
    from_field.clear()
    from_field.send_keys("2009")
    to_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[data-testid='input-range-to']")))
    to_field.clear()
    to_field.send_keys("2025")
    apply_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='apply-facet-range']")))
    apply_button.click()
    
    wait = WebDriverWait(driver, 10)

    # Value pairs for export
    value_pairs = [(1, 20000), (20001, 40001), (40002, 60002), (60003, 80003),(80004,100004)]  

    for pair in value_pairs:
        print(f"Enregistrement des valeurs {pair[0]} et {pair[1]}...")

        # Clicking export and CSV buttons
        export_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Export' and contains(@class, 'Typography-module__lVnit')]")))
        export_button.click()
        print("Bouton 'Export' cliqué.")
        
        csv_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='CSV' and contains(@class, 'Typography-module__lVnit')]")))
        csv_button.click()
        print("Bouton 'CSV' cliqué.")
        
        time.sleep(20)

        # Fill range filters
        radio_button = wait.until(EC.element_to_be_clickable((By.ID, "select-range")))
        radio_button.click()
        print("Bouton radio 'select-range' cliqué.")
        time.sleep(10)
        
        # Update the fields with the range values
        disabled_field = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div/div[3]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[1]/table/tbody/tr/td[2]/div/div/div[2]/div/div/section/div[1]/div/div/div[1]/div/div/div/div/div/div/div[1]/div/label/input')
        driver.execute_script("arguments[0].removeAttribute('disabled');", disabled_field)

        disabled_field_2 = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div/div[3]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[1]/table/tbody/tr/td[2]/div/div/div[2]/div/div/section/div[1]/div/div/div[1]/div/div/div/div/div/div/div[2]/div/label/input')
        driver.execute_script("arguments[0].removeAttribute('disabled');", disabled_field_2)

        ActionChains(driver).move_to_element(disabled_field).click().perform()
        disabled_field.clear()
        disabled_field.send_keys(str(pair[0]))
        disabled_field.send_keys(Keys.TAB)
        print(f"La valeur '{pair[0]}' a été saisie dans le premier champ.")
        time.sleep(2)

        ActionChains(driver).move_to_element(disabled_field_2).click().perform()
        disabled_field_2.clear()
        disabled_field_2.send_keys(str(pair[1]))
        disabled_field_2.send_keys(Keys.TAB)
        print(f"La valeur '{pair[1]}' a été saisie dans le second champ.")
        time.sleep(2)

        # Filter and apply actions
        filter_buttons = [
            "/html/body/div[1]/div/div[1]/div/div/div[3]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[1]/table/tbody/tr/td[2]/div/div/div[2]/div/div/section/div[1]/div/div/div[2]/div/div[3]/span/label/input",
            "/html/body/div[1]/div/div[1]/div/div/div[3]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[1]/table/tbody/tr/td[2]/div/div/div[2]/div/div/section/div[1]/div/div/div[2]/div/div[2]/span/label/input",
            "/html/body/div[1]/div/div[1]/div/div/div[3]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[1]/table/tbody/tr/td[2]/div/div/div[2]/div/div/section/div[1]/div/div/div[2]/div/div[4]/span/label/input",
            "/html/body/div[1]/div/div[1]/div/div/div[3]/micro-ui/document-search-results-page/div[1]/section[2]/div/div[2]/div/div[2]/div/div[1]/table/tbody/tr/td[2]/div/div/div[2]/div/div/section/div[1]/div/div/div[2]/div/div[5]/span/label/input"
        ]

        for xpath in filter_buttons:
            filter_button = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            filter_button.click()
            print(f"Filtre avec XPath {xpath} cliqué.")
            time.sleep(1)

        # Final export click
        export_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='submit-export-button']")))
        export_button.click()
        print(f"Bouton 'Export' cliqué pour les valeurs {pair[0]} et {pair[1]}.")
        time.sleep(60)

        # After export, download and upload CSV directly
        file_url = driver.current_url  # Assuming the download URL is the same
        response = requests.get(file_url)
        
        # Upload the CSV file directly to Azure
        blob_name = f"scopus_exports/{pair[0]}-{pair[1]}.csv"
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.upload_blob(io.BytesIO(response.content), overwrite=True)
        print(f"File uploaded to Azure Data Lake with name: {blob_name}")
        time.sleep(10)

finally:
    driver.quit()
