# USGS Earthquake Analysis with Python

## Overview
This project explores seismic activity using the **USGS (United States Geological Survey) Earthquake API** using **Python**. I retrieve earthquake records, transform the API response with **Pandas**, and create interactive visualizations with **Plotly**.

## What I Explored
- Making **API requests** with Python using `requests`
- Handling and parsing **GeoJSON/JSON responses**
- Working with **query parameters** for API filtering and scope
- Transforming and cleaning data with **Pandas**
- Creating interactive geographical maps and charts with **Plotly**

## Data
The data comes from the **USGS Earthquake API**, tracking global and regional seismic activity.

- **Source:** USGS Earthquake API (GeoJSON Feed)
- **Period:** 2026 YTD (year-to-date)
- **Filter Criteria:** Magnitude $\ge$ 5.0 (focused on **moderate and larger earthquakes** as classified by the USGS, filtering out minor background micro-seismicity)
- **Focus Region:** Global & Indonesia

[USGS API Documentation](https://earthquake.usgs.gov/fdsnws/event/1/) provides the reference for the API endpoints, query parameters, and response structure used in this project.

## Process

```text
USGS Earthquake API
     ↓
Custom Python Function (`fetch_eq_api`)
     ↓
GeoJSON Response
     ↓
Pandas DataFrame
     ↓
Clean & Transform
     ↓
Plotly
     ↓
Interactive Visualizations & Previews
```

The project follows a structured workflow from retrieving API data to creating interactive charts:

1. **Extract** earthquake data using a custom Python function (`fetch_eq_api`) with built-in status checks
2. **Filter** records for moderate to major seismic events ($\ge$ 5.0 magnitude) for 2026 YTD
3. **Parse** the GeoJSON response into a Pandas DataFrame
4. **Clean and transform** the data, isolating global then regional subsets (`Indonesia`)
5. **Visualize** the results using Plotly, exporting charts as both interactive HTML files and PNG previews

## Code

The workflow is organized into three stages: **retrieving the data** from the USGS Earthquake API, **transforming it with Pandas**, and **creating visualizations** with Plotly.

### Libraries

The project uses the following Python libraries:

```python
import requests
from datetime import date
import json
import pandas as pd
import plotly.express as px
```

* **requests** for making API requests to the USGS GeoJSON feed
* **datetime** for handling datetime data type
* **json** for inspecting and handling JSON payloads
* **Pandas** for parsing, cleaning, and transforming the earthquake records into DataFrames
* **Plotly Express** for building interactive maps and charts

### 1. Building a Custom API Function

Before requesting any data, a custom function (`fetch_eq_api`) is build to handle the API call and verify the HTTP response status. This keeps the API call modular, readable, and reusable for future requests[cite: 2].

```python
def fetch_eq_api(params):
    """Fetch the earthquake data from USGS API"""

    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    r = requests.get(url, params=params)

    if r.status_code == 200:
        print(f"Fetch success: {r.status_code}")
        return r.json()
    else:
        print(f"Fetch FAILED: {r.status_code}")
        return None
```

### 2. Fetching API Data

With the function defined, **query parameters** is passed to the `fetch_eq_api` function to specify the format, date range, and magnitude threshold.

```python
params = {
    'format': 'geojson',
    'starttime': '2026-01-01',
    'endtime': date.today().isoformat(),
    'minmagnitude': 5.0
}

response_dicts = fetch_eq_api(params=params)
print(response_dicts.keys())
print(response_dicts['metadata'])
```
>*This request retrieves earthquake records in **GeoJSON** format starting from **January 1, 2026, to today,** filtering only magnitude of **5.0 or higher** (classified by the USGS as moderate-to-major earthquakes).*

### 3. Inspecting and Extracting the Payload

Inspect a single record, confirming that the data lives inside the `features` key so it can be passed to `response_dict`.

```python
preview_dicts = response_dicts.copy()

if 'features' in preview_dicts:
    preview_dicts['features'] = preview_dicts['features'][:1]
    
print(json.dumps(preview_dicts, indent=4))

# found out the data in feature, pass it to variable
response_dict = response_dicts['features']
```

### 4. Flattening Nested GeoJSON Data

The data we need is deeply nested under `properties` and `geometry`, it cannot be loaded directly into a Pandas DataFrame. Create a loop iterates through each event to extract the magnitude, location, timestamp, and coordinates into a clean list of flat dictionaries.

```python
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
```

### 5. Transforming and Preparing the DataFrame

The data is loaded into a **Pandas DataFrame** and inspected. The raw timestamps are converted into readable dates, and a clean copy (`df_clean`) is saved for analysis and visualization.

```python
df = pd.DataFrame(clean_data)
print(df.head())
print(df.info())
print(df.describe())

df['time'] = pd.to_datetime(df['time'], unit='ms')
df_clean = df.copy()
```
### Full Code

The complete Python script, including the **USGS API requests, GeoJSON parsing, data cleaning, and visualizations**, is available here:

[`earthquake_analysis.py`](earthquake_analysis.py)

The Jupyter Notebook version of the project, including the **code, outputs, and visualizations**, is available here:

[`earthquake_analysis.ipynb`](earthquake_analysis.ipynb)

## Visualizations

The cleaned climate data was visualized with **Matplotlib** to show daily temperature, rainfall, snowfall, and snow depth throughout 2026 YTD.

### Daily High and Low Temperature

This chart shows the daily **maximum and minimum temperatures** recorded at JFK Airport.

![Daily High and Low Temperature](charts/tmax_tmin.png)

```python
# Daily High vs Low Temperature
plt.style.use('seaborn-v0_8')

fig, ax = plt.subplots()
ax.plot(df_clean['date'], df_clean['TMAX'], color='red', linewidth=1)
ax.plot(df_clean['date'], df_clean['TMIN'], color='blue', linewidth=1)

ax.fill_between(df_clean['date'], df_clean['TMAX'], df_clean['TMIN'], facecolor='blue', alpha=0.1)

ax.set_title("Daily High and Low Temperature, 2026-YTD\nNew York, NY (JFK Airport Station)", fontsize=18)
ax.set_ylabel("Temperature (\u00b0C)", fontsize=12)
ax.tick_params(labelsize=12)
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
ax.legend(['Daily High', 'Daily Low'], fontsize=8, loc='upper right')

ax.set_xlim(
     df_clean['date'].min() - pd.Timedelta(days=3), 
     df_clean['date'].max()
)

max_temp = df_clean['TMAX'].max()
min_temp = df_clean['TMIN'].min()
max_date = df_clean.loc[df_clean['TMAX'].idxmax(), "date"]
min_date = df_clean.loc[df_clean['TMIN'].idxmin(), "date"]

ax.scatter(x=max_date, y=max_temp, c='black', edgecolors='none', s=36, zorder=3)
ax.scatter(x=min_date, y=min_temp, c='black', edgecolors='none', s=36, zorder=3)

ax.annotate(
    f"{max_temp:.1f}\u00b0C",
    xy=(max_date, max_temp),
    xytext=(5, -2),
    textcoords="offset points",
    fontsize=8
)
ax.annotate(
    f"{min_temp:.1f}\u00b0C",
    xy=(min_date, min_temp),
    xytext=(5, -2),
    textcoords="offset points",
    fontsize=8
)

plt.show()
```

### Daily Rainfall

This chart shows the daily **precipitation** recorded at JFK Airport.

![Daily Rainfall](charts/prcp.png)

```python
# Daily Rainfall
plt.style.use('seaborn-v0_8')

fig, ax = plt.subplots()
ax.plot(df_clean['date'], df_clean['PRCP'], color='blue', linewidth=1)

ax.set_title("Daily Rainfall, 2026-YTD\nNew York, NY (JFK Airport Station)", fontsize=18)
ax.set_ylabel("Precipitation (mm)", fontsize=12)
ax.tick_params(labelsize=12)
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))

ax.set_xlim(
     df_clean['date'].min() - pd.Timedelta(days=3), 
     df_clean['date'].max()
)

max_rain = df_clean['PRCP'].max()
max_date = df_clean.loc[df_clean['PRCP'].idxmax(), "date"]
ax.scatter(x=max_date, y=max_rain, c='red', edgecolors='none', s=36, zorder=3)

ax.annotate(
    f"{max_rain:.1f}mm",
    xy=(max_date, max_rain),
    xytext=(5, -2),
    textcoords="offset points",
    fontsize=8
)

plt.show()
```

### Daily Snowfall & Snow Depth

This visualization compares **daily snowfall** and **snow depth** using two side-by-side plots.

![Daily Snowfall & Snow Depth](charts/snow_snwd.png)

```python
# Daily Snowfall & Snow Depth
plt.style.use('seaborn-v0_8')

fig, ax = plt.subplots(1, 2, sharey=True)
ax[0].plot(df_clean['date'], df_clean['SNOW'], color='deepskyblue', linewidth=1)
ax[1].plot(df_clean['date'], df_clean['SNWD'], color='blue', linewidth=1)

ax[0].set_title("Daily Snowfall")
ax[0].set_ylabel("depth (mm)")

max_snow = df_clean['SNOW'].max()
max_date_snow = df_clean.loc[df_clean['SNOW'].idxmax(), "date"]
ax[0].scatter(x=max_date_snow, y=max_snow, c='red', edgecolors='none', s=36, zorder=3)
ax[0].annotate(
     f"{max_snow:.1f} mm", 
     xy=(max_date_snow, max_snow), 
     xytext=(5, 0), 
     textcoords="offset points", 
     fontsize=8
)

ax[1].set_title("Daily Snow Depth")

max_snwd = df_clean['SNWD'].max()
max_date_snwd = df_clean.loc[df_clean['SNWD'].idxmax(), "date"]
ax[1].scatter(x=max_date_snwd, y=max_snwd, c='red', edgecolors='none', s=36, zorder=3)
ax[1].annotate(
     f"{max_snwd:.1f} mm", 
     xy=(max_date_snwd, max_snwd), 
     xytext=(5, 0), 
     textcoords="offset points", 
     fontsize=8
)

for a in ax:
    a.xaxis.set_major_locator(mdates.MonthLocator())
    a.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    a.set_xlim(df_clean['date'].min() - pd.Timedelta(days=3), df_clean['date'].max())
    a.tick_params(axis='x', rotation=30, labelsize=8)
    a.tick_params(axis='y', labelsize=8)

fig.suptitle("Daily Snowfall vs Snow Depth, 2026-YTD\nNew York, NY (JFK Airport Station)", fontsize=18)
fig.tight_layout()

plt.show()
```

## Tools

* **Python** for API requests, data processing, and visualization
* **Requests** for accessing the NOAA Climate Data Online API
* **Pandas** for data transformation and cleaning
* **Matplotlib** for data visualization
* **VS Code** for development and project work
* **GitHub** for version control and portfolio hosting

## Limitations and Future Improvements

This project was primarily built to practice working with an external API and handling the resulting data with Python, so the current implementation keeps the workflow relatively straightforward.

There are a few areas that could be improved in the future:

* **Function-based structure:** The current script contains most of the workflow in a single file and could be broken into reusable functions for API requests, data transformation, and visualization.
* **Dynamic pagination:** The current implementation manually retrieves a second batch of records. This could be replaced with a loop that continues requesting data until all available records have been retrieved.
* **Reusable visualizations:** The plotting code could be organized into functions so similar charts can be generated with different variables or datasets.
* **API configuration:** Parameters such as the station, date range, and variables could be separated from the main logic to make the script easier to reuse for other locations or time periods.

These improvements would make the project **more reusable, maintainable, and flexible** while keeping the same core workflow.
