"""@bruin

name: ingestion.library_events
type: python
image: python:3.11
connection: GCP_ETL

materialization:
  type: table
  strategy: merge
  unique_key: [event_page, title, start, location_name] 

columns:
  - name: title
    type: string
    description: The title of the library event
  - name: description
    type: string
    description: A description of the library event
  - name: event_types
    type: string
    description: The type of library event, multiple seperated by pipe
  - name: event_audiences 
    type: string
    description: The audience for the library event, multiple seperated by pipe
  - name: event_languages
    type: string
    description: The language of the library event, multiple seperated by pipe
  - name: event_page
    type: string
    description: The page URL for the library event
  - name: location_name
    type: string
    description: The name of the location where the event will occur
  - name: location_details
    type: string
    description: Details about the location where the event will occur
  - name: start
    type: timestamp
    description: The start date and time of the event
  - name: end
    type: timestamp
    description: The end date and time of the event
  - name: featured
    type: boolean
    description: Whether the event is featured
  - name: cancelled
    type: boolean
    description: Whether the event is cancelled
  - name: recurring
    type: boolean
    description: Whether the event is recurring
  - name: registration_starts
    type: timestamp
    description: The start date and time for event registration
  - name: registration_ends
    type: timestamp
    description: The end date and time for event registration
  - name: extracted_at
    type: timestamp  
    description: The timestamp when the data was extracted from the source system for lineage purposes

@bruin"""


import os
import json
import pandas as pd
import requests
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth
from io import BytesIO

def materialize():
    """
    Fetch Chicago Park District event data from the API endpoint.
    
    - Reads CHI_API environment variables
    - Fetches event data from the API in batches of 500 records until no more data is available or a safety offset limit is reached
    - Returns concatenated DataFrame with extracted_at timestamp
    """

    basic = HTTPBasicAuth(os.getenv('CHI_API_ID'), os.getenv('CHI_API_SECRET'))
    url = "https://data.cityofchicago.org/api/v3/views/vsdy-d8k7/export.csv"
    names = ['title', 'description', 'event_types', 'event_audiences', 'event_languages', 'event_page', 'location_name', 'location_details', 'start', 'end', 'featured', 'cancelled', 'recurring', 'registration_starts', 'registration_ends']
    datatypes = {'title': 'string',
                 'description': 'string',
                 'event_types': 'string',
                 'event_audiences': 'string',
                 'event_languages': 'string',
                 'event_page': 'string',
                 'location_name': 'string',
                 'location_details': 'string',
                 #'start': 'datetime64[ns]',
                 #'end': 'datetime64[ns]',
                 'featured': 'bool',
                 'cancelled': 'bool',
                 'recurring': 'bool' #,
                 #'registration_starts': 'datetime64[ns]',
                 #'registration_ends': 'datetime64[ns]'
                }
    file = requests.post(url, auth=basic)
    if file.status_code != 200:
        raise Exception(f"Error fetching data: {file.status_code} - {file.text}")

    df = pd.read_csv(BytesIO(file.content),  names = names,  skiprow = [0], dtype=datatypes, parse_dates=['start', 'end', 'registration_starts', 'registration_ends'], true_values=['TRUE', '1'], false_values=['FALSE', '', None, '0'] )

    if df.empty:
        raise Exception("Error fetching data:  datafile empty")
    
    df['extracted_at'] = datetime.utcnow().isoformat()

    print (f"Fetched {len(df)} records")
    # Add extracted_at timestamp for lineage
    return df


