# Libraries
import requests
from datetime import date
import json
import pandas as pd

# EXTRACT & LOAD DATA

# Fetch API Data
# Create functions so it can easily reusable
def fetch_eq_api(params):
    """Fetch the earthquake data from USGS API"""
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    r = requests.get(url, params=params)

    # Check if the api call worked (200 = Success)
    if r.status_code == 200:
        print(f"Fetch success: {r.status_code}")
        return r.json()
    else:
        print(f"Fetch FAILED: {r.status_code}")
        return None

# the minmagnitude = 5.0 cause from USGS classified the start of moderate earthquake, less than that is light and minor 
params = {
    'format': 'geojson',
    'starttime': '2026-01-01',
    'endtime': date.today().isoformat(),
    'minmagnitude': 5.0
}

response_dicts = fetch_eq_api(params=params)
print(response_dicts.keys())
print(response_dicts['metadata'])

# create readable data and inspect what's in it
preview_dicts = response_dicts.copy()

if 'features' in preview_dicts:
    preview_dicts['features'] = preview_dicts['features'][:1]
    
print(json.dumps(preview_dicts, indent=4))

# found out the data we need is in features, then pass it to variable response_dict
response_dict = response_dicts['features']
print(len(response_dict))

# cause the data is nested, we can't just pass it to the pandas dataframe
# Flatten the nested JSON into a clean list of dictionaries
clean_data = []

for eq in response_dict:
    clean_data.append({
        "magnitude": eq["properties"]["mag"],
        "place": eq["properties"]["place"],
        "time": eq["properties"]["time"],
        "longitude": eq["geometry"]["coordinates"][0],
        "latitude": eq["geometry"]["coordinates"][1],
        "depth": eq["geometry"]["coordinates"][2]
    })

print(len(clean_data))

# Turn it into a Pandas DataFrame
df = pd.DataFrame(clean_data)

# inspect
print(df.head())
print(df.describe())
print(df.info())

# Convert the date datatype to datetime
df['time'] = pd.to_datetime(df['time'], unit='ms')

# Create a df copy for analysis
df_clean = df.copy()

# inspect
print(df_clean.head())
print(df_clean.describe())
print(df_clean.info())

# VISUALIZATION

# 1. World Map
# 2. Indo Map
# 3. Eq over time ytd
# 4. Eq monthly trend
# 5. Top 10 Biggest Eq 2026 ytd
