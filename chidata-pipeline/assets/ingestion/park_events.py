"""@bruin

name: ingestion.park_events
type: python
image: python:3.11
connection: GCP_ETL

materialization:
  type: table
  strategy: merge
  unique_key: [requestor_, organization, park_number, reservation_start_date, reservation_end]

columns:
  - name: requestor_
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
    df = pd.DataFrame({
        'requestor_': pd.Series(dtype='string'),
        'organization': pd.Series(dtype='string'),
        'park_number': pd.Series(dtype='int'),
        'park_facility_name': pd.Series(dtype='string'),
        'reservation_start_date': pd.Series(dtype='datetime64[ns]'),
        'reservation_end_date': pd.Series(dtype='datetime64[ns]'),
        'event_type': pd.Series(dtype='string'),
        'event_description': pd.Series(dtype='string'),
        'permit_status': pd.Series(dtype='string')
    })
    names = ['requestor_', 'organization', 'park_number', 'park_facility_name', 'reservation_start_date', 'reservation_end_date', 'event_type', 'event_description', 'permit_status']

    file = requests.post(url, auth=basic)
    if file.status_code != 200:
        raise Exception(f"Error fetching data: {file.status_code} - {file.text}")

    batch_df = pd.read_csv(BytesIO(file.content), names = names, skiprows = [0], parse_dates=['reservation_start_date', 'reservation_end_date'])
    if batch_df.empty:
        print("concern:  datafile empty, moving on.")
    df = pd.concat([df, batch_df], ignore_index=True)
    print (f"Fetched {len(batch_df)} records, uploading {len(df)} records")
    # Add extracted_at timestamp for lineage
    df['extracted_at'] = datetime.utcnow().isoformat()
    return df


