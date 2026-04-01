"""@bruin

name: ingestion.library_locations
type: python
image: python:3.11
connection: GCP_ETL

materialization:
  type: table
  strategy: create+replace

columns:
  - name: branch
    type: string
    description: The branch name of the library
  - name: service_hours
    type: string
    description: The service hours for each library branch
  - name: address
    type: string
    description: The address line of the library branch
  - name: city
    type: string
    description: The city where the library branch is located
  - name: state
    type: text
    description: The state where the library branch is located
  - name: zip
    type: string
    description: The zip code of the library branch location
  - name: phone
    type: string
    description: The phone number for the library branch
  - name: website
    type: string
    description: The website URL for the library branch
  - name: branch_email
    type: string
    description: The email address for the library branch
  - name: location  
    type: text
    description: The text of json with 3 keys lattitude, longitude, human_address
  - name: extracted_at
    type: timestamp
    description: The timestamp when the data was extracted from the source system for lineage purposes
 
@bruin"""


import os
import json
import pandas as pd
import requests
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from requests.auth import HTTPBasicAuth
from io import BytesIO
import time

def materialize():
    """
    Fetch Chicago Park District event data from the API endpoint.
    
    - Reads CHI_API environment variables
    - Fetches a csv from the API endpoint and loads it into a DataFrame
    - Returns  DataFrame with extracted_at timestamp
    """

    basic = HTTPBasicAuth(os.getenv('CHI_API_ID'), os.getenv('CHI_API_SECRET'))
    url = "https://data.cityofchicago.org/api/v3/views/x8fc-8rcq/export.csv"
    names = ['branch', 'service_hours', 'address', 'city', 'state', 'zip', 'phone', 'website', 'branch_email', 'location']  
    datatypes = {
        'branch': 'string',
        'service_hours': 'string',
        'address': 'string',
        'city': 'string',
        'state': 'string',
        'zip': 'string',
        'phone': 'string',
        'website': 'string',
        'branch_email': 'string',
        'location': 'string'
    }

   
    max_retries = 5
    for attempt in range(max_retries):
        try:
          file = requests.post(url, auth=basic, timeout = 10)
          if file.status_code == 200:
            break
          if file.status_code != 200:
            raise Exception(f"Error fetching data: {file.status_code} - {file.text}")
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            if attempt < max_retries - 1:
                print("Retrying...")
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise Exception("Max retries reached. Failed to fetch data.")
    df = pd.read_csv(BytesIO(file.content), names = names, dtype = datatypes, skiprows = [0])
    if df.empty:
        print("concern:  datafile empty, moving on.")
    print (f"Fetched {len(df)} records")
    # Add extracted_at timestamp for lineage
    df['extracted_at'] = datetime.utcnow().isoformat()
    return df


