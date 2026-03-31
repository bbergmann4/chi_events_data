"""@bruin

name: ingestion.park_events
type: python
image: python:3.11
connection: GCP_ETL

materialization:
  type: table
  strategy: merge
  unique_key: [requestor, organization, park_number, reservation_start_date, reservation_end]

columns:
  - name: requestor
    type: string
    description: Requestor, person requesting event
  - name: organization
    type: string
    description: Organization requesting event
  - name: park_number
    type: integer
    description: The park number where the event occurred
  - name: park_facility_name
    type: string
    description: The name of the park facility where the event will occur
  - name: reservation_start_date
    type: timestamp
    description: The start date and time of the reservation
  - name: reservation_end_date
    type: timestamp
    description: The end date and time of the reservation
  - name: event_type
    type: string
    description: The type of event 
  - name: event_description
    type: string
    description: A description of the event
  - name: permit_status
    type: string
    description: Pending,Tentative, Approved, Stage Denied, Denied, Cancelled
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
    url = "https://data.cityofchicago.org/api/v3/views/pk66-w54g/export.csv"
    names = ['requestor', 'organization', 'park_number', 'park_facility_name', 'reservation_start_date', 'reservation_end_date', 'event_type', 'event_description', 'permit_status']
    datatypes = {
        'requestor': 'string',
        'organization': 'string',
        'park_number': 'Int64',
        'park_facility_name': 'string',
        #'reservation_start_date': 'datetime64[ns]',
        #'reservation_end_date': 'datetime64[ns]',
        'event_type': 'string',
        'event_description': 'string',
        'permit_status': 'string'
    }
    file = requests.post(url, auth=basic)
    if file.status_code != 200:
        raise Exception(f"Error fetching data: {file.status_code} - {file.text}")

    df = pd.read_csv(BytesIO(file.content), names = names, skiprows = [0], dtype=datatypes, parse_dates=['reservation_start_date', 'reservation_end_date'])
    if df.empty:
        raise Exception("Error fetching data:  datafile empty")
    
    df['extracted_at'] = datetime.utcnow().isoformat()

    print (f"Fetched {len(df)} records")
    # Add extracted_at timestamp for lineage
    return df


