"""
File: data_utils.py
===================
These scripts serve as the work horses for the data extraction and data processing pipelines.
"""
import pandas as pd
import numpy as np
import geopandas
import datetime
import folium
import ee
import time
import dateutil
import tqdm


def filter_fire_df(df, state='CA', min_class=None, start_date=None, end_date=None, causes=None):

    # drop states
    df_filt = df[df.STATE == 'CA']
    df_filt = df_filt.drop(['STATE'], axis=1)

    # drop fire classes
    if min_class is not None:
        df_filt.FIRE_SIZE_CLASS = df_filt.FIRE_SIZE_CLASS.apply(ord)
        df_filt = df_filt[df_filt.FIRE_SIZE_CLASS >= ord(min_class)]

    # reformat dates
    df_filt.DISCOVERY_DATE = pd.to_datetime(df['DISCOVERY_DATE'], unit='D', origin='julian')
    df_filt.CONT_DATE = pd.to_datetime(df['CONT_DATE'], unit='D', origin='julian')

    # convert coordinates
    df_filt = geopandas.GeoDataFrame(df_filt, geometry=geopandas.points_from_xy(
        df_filt.LONGITUDE, df_filt.LATITUDE))
    df_filt = df_filt.drop(['LONGITUDE'], axis=1)
    df_filt = df_filt.drop(['LATITUDE'], axis=1)
    df_filt.insert(3, 'COORD', df_filt.pop('geometry'))

    # remove missing values
    df_filt = df_filt.dropna()

    # reformat head
    df_filt.columns = [
        'fpa_id', 'start_date', 'end_date', 'geometry',
        'name', 'size_class', 'size', 'cause'
    ]

    # sort by start dates
    df_filt = df_filt.sort_values(by='start_date')
    df_filt = df_filt.reset_index()

    df_filt.drop("index", axis=1, inplace=True)

    # create ISO string format columns
    df_filt["start_date_iso"] = df_filt["start_date"].apply(lambda x: x.to_pydatetime().isoformat())
    df_filt["end_date_iso"] = df_filt["end_date"].apply(lambda x: x.to_pydatetime().isoformat())

    # filter based on start_date and end_date
    if start_date is not None:
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        df_filt = df_filt[df_filt.apply(lambda x: x.start_date > start_date, axis=1)]
    if end_date is not None:
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        df_filt = df_filt[df_filt.apply(lambda x: x.end_date < end_date, axis=1)]

    # filter causes
    if causes is not None:
        df_filt = df_filt[df_filt["cause"].isin(causes)]

    return df_filt

# Define the URL format used for Earth Engine generated map tiles.


def Mapdisplay(center, dicc, Tiles="OpensTreetMap",zoom_start=10):
    '''
    :param center: Center of the map (Latitude and Longitude).
    :param dicc: Earth Engine Geometries or Tiles dictionary
    :param Tiles: Mapbox Bright,Mapbox Control Room,Stamen Terrain,Stamen Toner,stamenwatercolor,cartodbpositron.
    :zoom_start: Initial zoom level for the map.
    :return: A folium.Map object.
    '''

    EE_TILES = 'https://earthengine.googleapis.com/map/{mapid}/{{z}}/{{x}}/{{y}}?token={token}'

    mapViz = folium.Map(location=center,tiles=Tiles, zoom_start=zoom_start)
    for k,v in dicc.items():
        if ee.image.Image in [type(x) for x in v.values()]:
            folium.TileLayer(
                tiles = EE_TILES.format(**v),
                attr  = 'Google Earth Engine',
                overlay =True,
                name  = k
            ).add_to(mapViz)
        else:
            folium.GeoJson(
                data = v,
                name = k
            ).add_to(mapViz)
    mapViz.add_child(folium.LayerControl())
    return mapViz

def cloudMaskL457(image):
    """
    Cloud masking function fpr L7SR (satellite specific).
    From: https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LE07_C01_T1_SR
    and pain-stakingly converted to Python code...
    """

    qa = image.select('pixel_qa');
    # If the cloud bit (5) is set and the cloud confidence (7) is high
    # or the cloud shadow bit is set (3), then it's a bad pixel.
    cloud = qa.bitwiseAnd(1 << 5).And(qa.bitwiseAnd(1 << 7)).Or(qa.bitwiseAnd(1 << 3))
    # Remove edge pixels that don't occur in all bands
    mask2 = image.mask().reduce(ee.Reducer.min())
    return image.updateMask(cloud.Not()).updateMask(mask2)


def create_batches(label_data, max_batch_size = 100, num_time_series_iterations = 12):
  """
  Separate the label_data indices into manageable chunks for GEE. 
  100 seems to work, but we could try bumping this up.
  """

  num_datapoints = label_data.size().getInfo()
  indices = np.arange(num_datapoints)

  num_batches = (num_datapoints * num_time_series_iterations) // max_batch_size + 1

  return np.array_split(np.arange(label_data.size().getInfo()), num_batches)


def watch_task_list(tasks):
    for i, task in tqdm.tqdm(enumerate(tasks), total=len(tasks)):
        while task.active():
            time.sleep(2)
        if task.status()["state"] != "COMPLETED":
            print("Uh-oh. Task {} failed. {}".format(i, task.status()))


