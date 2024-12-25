import requests
import json
import time
import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
import io

# Load environment variables
load_dotenv()

# Get variables from .env
api_key = os.getenv("api_key")
account_name = os.getenv("account_name")
container_name = os.getenv("container_name")
account_key = os.getenv("account_key")

# Initialize Azure Blob Service Client
blob_service_client = BlobServiceClient(
    account_url=f"https://{account_name}.blob.core.windows.net",
    credential=account_key
)

# Elsevier API query parameters
query = "affiliation country:Morocco"
url = "http://api.elsevier.com/content/search/scopus"
headers = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

count = 25
offset = 0
all_results = []
request_count = 0
max_requests = 5703

while request_count < max_requests:
    query_url = f"{url}?query={query}&apiKey={api_key}&count={count}&start={offset}"

    response = requests.get(query_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        items = data.get("search-results", {}).get("entry", [])

        filtered_items = []
        for item in items:
            filtered_data = {
                "prism:url": item.get("prism:url"),
                "dc:identifier": item.get("dc:identifier"),
                "eid": item.get("eid"),
                "dc:title": item.get("dc:title"),
                "dc:creator": item.get("dc:creator"),
                "prism:publicationName": item.get("prism:publicationName"),
                "prism:issn": item.get("prism:issn"),
                "prism:eIssn": item.get("prism:eIssn"),
                "prism:volume": item.get("prism:volume"),
                "prism:issueIdentifier": item.get("prism:issueIdentifier"),
                "prism:pageRange": item.get("prism:pageRange"),
                "prism:coverDate": item.get("prism:coverDate"),
                "prism:coverDisplayDate": item.get("prism:coverDisplayDate"),
                "prism:doi": item.get("prism:doi"),
                "citedby-count": item.get("citedby-count"),
                "affiliation": item.get("affiliation"),
                "prism:aggregationType": item.get("prism:aggregationType"),
                "subtype": item.get("subtype"),
                "subtypeDescription": item.get("subtypeDescription"),
                "source-id": item.get("source-id"),
                "openaccess": item.get("openaccess"),
                "openaccessFlag": item.get("openaccessFlag"),
            }
            filtered_items.append(filtered_data)

        all_results.extend(filtered_items)

        if len(items) < count:
            break
        else:
            offset += count
            request_count += 1
            time.sleep(2)
    else:
        print(f"Erreur {response.status_code}: {response.text}")
        break


json_data = json.dumps(all_results, indent=4, ensure_ascii=False)

blob_name = "scopus_exports/morocco_affiliations.json"
blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
blob_client.upload_blob(io.BytesIO(json_data.encode()), overwrite=True)

print(f"File uploaded to Azure Data Lake with name: {blob_name}")
