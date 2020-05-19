import sqlite3
import pandas as pd
import numpy as np
import pickle
import ee

# given a range of latitudes and longitudes, a fire database dataframe, and a desired resolution, this function
# will linearly partition the geodata into smaller grids
def extract_localized_wildfires(minLat, maxLat, minLong, maxLong, df, lat_resolution=None, long_resolution=None, resolution=None):
    import numpy as np
    
    assert (lat_resolution != None and long_resolution != None) or resolution != None
    if resolution != None:
        long_resolution = resolution
        lat_resolution = resolution

    longitude_range = np.linspace(maxLong, minLong, long_resolution + 1)
    latitude_range = np.linspace(minLat, maxLat, lat_resolution + 1)

    datapoints = {}
    for row in range(resolution):
        for col in range(resolution):
            rel = df[df["LATITUDE"] >= latitude_range[row]]
            rel = rel[rel["LATITUDE"] < latitude_range[row + 1]]
            rel = rel[rel["LONGITUDE"] <= longitude_range[col]]
            rel = rel[rel["LONGITUDE"] > longitude_range[col + 1]]
            datapoints[(row, col)] = rel

    return datapoints

def download_timeseries_image(minLat, maxLat, minLong, maxLong, lat_resolution=None, long_resolution=None, resolution=None):
    assert (lat_resolution != None and long_resolution != None) or resolution != None
    if resolution != None:
        long_resolution = resolution
        lat_resolution = resolution

    landsat = ee.ImageCollection("LANDSAT/LE07/C01/T1").filterDate('1999-01-01', '2002-12-31').select(['B1', 'B2', 'B3'])
    print(landsat)
    geometry = ee.Geometry.Rectangle([116.2621, 39.8412, 116.4849, 40.01236])
    landsat
    path = landsat.getDownloadUrl({
        'scale': 30,
        'region': geometry
    })
    print(path)


    return None

# asyncronously initialize the earth engine
ee.Initialize()

# load the initial fire dataset
cnx = sqlite3.connect('./us_wildfire_dataset/FPA_FOD_20170508.sqlite')
df = pd.read_sql_query("SELECT DISCOVERY_DATE, LATITUDE, LONGITUDE, FIRE_SIZE, STATE FROM fires", cnx)

# constrain the searches to California, and fix the date/time format
df = df[df["STATE"] == "CA"]
df['Date'] = pd.to_datetime(df['DISCOVERY_DATE'], unit='D', origin='julian')
df = df.drop("DISCOVERY_DATE", 1)

#print(extract_localized_wildfires(34, 36, -118, -116, df, resolution=15)[(0, 2)])

download_timeseries_image(0, 0, 0, 0, resolution=1)

# # save the dataframe to disk
# with open("./us_wildfire_dataset/ca_fires_raw.pkl", "wb") as f:
#     pickle.dump(df, f, protocol=pickle.HIGHEST_PROTOCOL)