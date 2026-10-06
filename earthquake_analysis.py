# Libraries
import requests
from datetime import date
import json
import pandas as pd
import plotly.express as px

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
# dataframe = df_clean
df_clean['date_clean'] = df_clean['time'].dt.strftime('%Y-%m-%d')

title = "Global Distribution of Earthquakes (>= 5.0 Magnitude, 2026 YTD)"

fig = px.scatter_geo(
    data_frame=df_clean,
    lat='latitude',
    lon='longitude',
    title=title,
    size='magnitude',
    color='magnitude',
    color_continuous_scale='viridis',
    projection='natural earth',
    hover_name='place',
    hover_data={
        'magnitude': ': .1f',
        'date_clean': True,
        'latitude':': .2f',
        'longitude':': .2f'
    },
    labels={
        'date_clean': 'Date',
        'magnitude': 'Magnitude',
        'latitude': 'Latitude',
        'longitude': 'Longitude'
    },
    size_max=6,
    opacity=0.5,
)

fig.update_traces(marker_line_width=0)

fig.write_html("charts/01_eq_global_distribution.html")
fig.write_image("charts/01_eq_global_distribution.png", width=1200, height=700, scale=2)
fig.show()

# 2. Indonesia Map
# df_clean['date_clean'] = df_clean['time'].dt.strftime('%Y-%m-%d')
country_name = 'Indonesia'
df_indonesia = df_clean[df_clean['place'].str.contains(country_name, case=False, na=False)]

title = "Indonesia Distribution of Earthquakes (>= 5.0 Magnitude, 2026 YTD)"

fig = px.scatter_geo(
    data_frame=df_indonesia,
    lat='latitude',
    lon='longitude',
    title=title,
    size='magnitude',
    color='magnitude',
    color_continuous_scale='viridis',
    projection='natural earth',
    hover_name='place',
    hover_data={
        'magnitude': ': .1f',
        'date_clean': True,
        'latitude':': .2f',
        'longitude':': .2f'
    },
    labels={
        'date_clean': 'Date',
        'magnitude': 'Magnitude',
        'latitude': 'Latitude',
        'longitude': 'Longitude'
    },
    size_max=8,
)

fig.update_traces(marker_line_width=0)

fig.write_html("charts/02_eq_Indonesia.html")
fig.write_image("charts/02_eq_Indonesia.png", width=1200, height=700, scale=2)
fig.show()

# 3. Indonesia's Earthquake Over Time
# df_clean['date_clean'] = df_clean['time'].dt.strftime('%Y-%m-%d')
# country_name = 'Indonesia'
# df_indonesia = df_clean[df_clean['place'].str.contains(country_name, case=False, na=False)]

df_indonesia['place_clean'] = df_indonesia['place'].str.replace(', Indonesia', '', regex=False)
df_timeline = df_indonesia.sort_values('date_clean', ascending=True)

title = "Indonesia's Earthquakes Over Time (>= 5.0 Magnitude, 2026 YTD)"

fig = px.scatter(
    data_frame=df_timeline,
    x='date_clean',
    y='magnitude',
    title=title,
    size='magnitude',           
    color='magnitude',
    color_continuous_scale=['#d0dff9', '#1361e1', '#da2129'],
    hover_name='place',
    size_max=12,
    hover_data={
        'magnitude': ': .1f',
        'date_clean': '|%Y-%m-%d',
        'latitude':': .2f',
        'longitude':': .2f'
    },
    labels={
        'date_clean': 'Date',
        'magnitude': 'Magnitude',
        'latitude': 'Latitude',
        'longitude': 'Longitude'
    },
)

fig.update_xaxes(
    dtick="M1",         
    tickformat="%b",    
    ticklabelmode="instant"
)
fig.update_layout(xaxis_title=None, yaxis_title=None)
fig.update_traces(marker_line_width=0)

fig.write_html("charts/03_eq_ina_overtime.html")
fig.write_image("charts/03_eq_ina_overtime.png", width=1200, height=700, scale=2)
fig.show()

# 4. Monthly Trends
# df_clean['date_clean'] = df_clean['time'].dt.strftime('%Y-%m-%d')
# country_name = 'Indonesia'
# df_indonesia = df_clean[df_clean['place'].str.contains(country_name, case=False, na=False)]
# df_indonesia['place_clean'] = df_indonesia['place'].str.replace(', Indonesia', '', regex=False)
# df_timeline = df_indonesia.sort_values('date_clean', ascending=True)

df_timeline['month'] = pd.to_datetime(df_timeline['date_clean']).dt.to_period('M').astype(str)
monthly_trend = df_timeline.groupby(by='month').size().reset_index(name='count')

title = "Monthly Trend of Indonesia Earthquake (>= 5.0 Magnitude, 2026 YTD)"

fig = px.line(
    data_frame=monthly_trend,
    x='month',
    y='count',
    title=title,
    markers=True,
    hover_data={'count': True, 'month': True},
    labels={'count': 'Frequency'},
)

fig.update_xaxes(
    dtick="M1",         
    tickformat="%b",    
    ticklabelmode="instant"
)
fig.update_layout(xaxis_title=None, yaxis_title='Frequency')
fig.update_traces(
    line=dict(color='#1361e1', width=3),  # Change hex code for color and width for thickness
    marker=dict(size=8),                 # Optional: you can also resize the data point markers
)

fig.write_html("charts/04_eq_ina_monthlytrends.html")
fig.write_image("charts/04_eq_ina_monthlytrends.png", width=1200, height=700, scale=2)
fig.show()

# 5. Top 10 Biggest Eq 2026 ytd
# df_clean['date_clean'] = df_clean['time'].dt.strftime('%Y-%m-%d')
# country_name = 'Indonesia'
# df_indonesia = df_clean[df_clean['place'].str.contains(country_name, case=False, na=False)]
# df_indonesia['place_clean'] = df_indonesia['place'].str.replace(', Indonesia', '', regex=False)

df_top10 = df_indonesia.sort_values(by='magnitude', ascending=False).head(10)

title = "Indonesia's Top 10 Highest Magnitude Earthquake (>= 5.0 Magnitude, 2026 YTD)"

fig = px.bar(
    data_frame=df_top10,
    x='magnitude',
    y='place_clean',
    title=title,
    orientation='h',
    text='magnitude',
    color='magnitude',
    color_continuous_scale=['#d0dff9', '#1361e1'],
    hover_name='place',
    hover_data={
        'magnitude': ': .1f',
        'date_clean': '|%Y-%m-%d',
        'latitude':': .2f',
        'longitude':': .2f',
        'place_clean': False
    },
    labels={
        'date_clean': 'Date',
        'magnitude': 'Magnitude',
        'latitude': 'Latitude',
        'longitude': 'Longitude'
    },
)

fig.update_layout(xaxis_title='Magnitude', yaxis_title=None, coloraxis_showscale=False)
fig.update_yaxes(autorange='reversed')

fig.write_html("charts/05_eq_ina_top10.html")
fig.write_image("charts/05_eq_ina_top10.png", width=1200, height=700, scale=2)
fig.show()

