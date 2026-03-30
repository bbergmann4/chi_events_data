"""@bruin

name: ingestion.park_locations
type: python
image: python:3.11
connection: GCP_ETL

materialization:
  type: table
  strategy: create+replace

columns:
  - name: the_geom
    type: string
    description: text of point datatype with park location coordinates
  - name: objectid_1
    type: string
    description: Unique identifier for each park facility
  - name: park
    type: string
    description: The name of the park
  - name: park_number
    type: integer
    description: The park number associated with the facility
  - name: facility_n
    type: string
    description: The name of the park facility
  - name: facility_t
    type: string
    description: The type of park facility INDOOR, OUTDOOR, or SPECIAL
  - name: x_coord
    type: float
    description: The x coordinate of the park facility location
  - name: y_coord
    type: float
    description: The y coordinate of the park facility location
  - name: gisobjid
    type: integer
    description: Unique identifier for each park facility in GIS system
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

def materialize():
    """
    Fetch Chicago Park District event data from the API endpoint.
    
    - Reads CHI_API environment variables
    - Fetches event data from the API in batches of 500 records until no more data is available or a safety offset limit is reached
    - Returns concatenated DataFrame with extracted_at timestamp
    """

    basic = HTTPBasicAuth(os.getenv('CHI_API_ID'), os.getenv('CHI_API_SECRET'))
    url = "https://data.cityofchicago.org/api/v3/views/eix4-gf83/export.csv"
    df = pd.DataFrame({
        'the_geom': pd.Series(dtype='string'),
        'objectid_1': pd.Series(dtype='string'),
        'park': pd.Series(dtype='string'),
        'park_number': pd.Series(dtype='int'),
        'facility_n': pd.Series(dtype='string'),
        'facility_t': pd.Series(dtype='string'),
        'x_coord': pd.Series(dtype='float'),
        'y_coord': pd.Series(dtype='float'),
        'gisobjid': pd.Series(dtype='int')
    })
    names = ['the_geom', 'objectid_1', 'park', 'park_number', 'facility_n', 'facility_t', 'x_coord', 'y_coord', 'gisobjid']  
    file = requests.post(url, auth=basic)
    if file.status_code != 200:
        raise Exception(f"Error fetching data: {file.status_code} - {file.text}")
    batch_df = pd.read_csv(BytesIO(file.content), names = names, skiprows = [0])
    if batch_df.empty:
        print("concern:  datafile empty, moving on.")
    df = pd.concat([df, batch_df], ignore_index=True)
    print (f"Fetched {len(batch_df)} records, uploading {len(df)} records")
    # Add extracted_at timestamp for lineage
    df['extracted_at'] = datetime.utcnow().isoformat()
    return df


