"""geo.py

Exports geospatial data for all Strava activities in GeoJSON format.

Functions:
get_address()
export_geo_data_file()

Felix van Oost 2021
"""

# Standard library
import datetime

# Third-party
from geopandas import GeoDataFrame
from geopy.geocoders import Nominatim
import pandas
import polyline
from shapely.geometry import Point, LineString


def _decode_polyline(x: pandas.Series) -> list:
    """
    Convert a Google polyline into a list of coordinates.

    Arguments:
    A Google polyline as a pandas Series.

    Return:
    A list of decoded coordinates from the polyline.
    """

    # Check for both null and empty polyline strings
    if not x['polyline'] or x['polyline'] is None:
        map_coordinates = None
    else:
        map_coordinates = polyline.decode(x['polyline'])

    return map_coordinates


def _create_shapely_point(coordinates: pandas.Series) -> Point:
    """
    Convert a pair of coordinates into a Shapely point.

    Arguments:
    A pair of coordinates as a pandas Series.

    Return:
    A Shapely point representing the coordinates.
    """

    return [Point(y, x) for x, y in coordinates]


def get_address(coordinates: list) -> dict:
    """
    Get the address of a location from the given coordinates using reverse
    geocoding.

    Arguments:
    coordinates - The coordinates to convert into an address.
    """

    # Use the OpenStreetMap Nominatim service
    geolocator = Nominatim(user_agent="Strava Analysis Tool", timeout=10)

    # Get the address for the given coordinates using the reverse geocoder
    address = geolocator.reverse(coordinates).raw['address']

    return address


def export_geo_data_file(file_path: str, activity_dataframe: pandas.DataFrame):
    """
    Export a GeoJSON-encoded file of geospatial data from all activities.

    The exported file contains the name, ID, type, distance, total
    elevation gain, and a LineString representing the trace of each
    activity.

    Arguments:
    file_path - The path of the file to export the geospatial activity
                data to.
    activity_dataframe - A pandas DataFrame containing the activity data.
    """

    print('[Geo]: Processing geospatial data')

    # Create a copy of the activity DataFrame containing only real
    # outdoor (non-trainer and non-virtual) activities
    exclude_list = ['VirtualRide', 'VirtualRun']
    activity_map_df = (activity_dataframe.loc[(activity_dataframe['trainer'] == False) &
                                              (~activity_dataframe['type']
                                              .isin(exclude_list))].copy())

    # Format the activity start dates and moving / elapsed times
    activity_map_df.loc[:, 'moving_time_formatted'] = (activity_map_df['moving_time']
        .apply(lambda x: str(datetime.timedelta(seconds=x))))
    activity_map_df.loc[:, 'elapsed_time_formatted'] = (activity_map_df['elapsed_time']
        .apply(lambda x: str(datetime.timedelta(seconds=x))))

    # Convert the activity polylines into coordinates
    activity_map_df.loc[:, 'map_coordinates'] = (activity_map_df.loc[:, 'map']
                                                        .apply(_decode_polyline))

    # Select only activities with geospatial data
    activity_map_df = activity_map_df.loc[activity_map_df['map_coordinates']
                                                        .isnull() == False]

    # Convert the coordinates into Shapely points
    activity_map_df.loc[:, 'map_points'] = (activity_map_df.loc[:, 'map_coordinates']
                                                   .apply(_create_shapely_point))

    # Convert the Shapely points into LineStrings
    activity_map_df.loc[:, 'map_linestring'] = (activity_map_df.loc[:, 'map_points']
                                                       .apply(LineString))

    # Convert the activity distances from m to km
    activity_map_df.loc[:, 'distance'] = activity_map_df.loc[:, 'distance'] / 1000

    # Create a pandas GeoDataFrame from the activities map DataFrame and
    # format the column names
    activity_map_gdf = GeoDataFrame(activity_map_df[['name',
                                                     'id',
                                                     'type',
                                                     'start_date_local',
                                                     'description',
                                                     'distance',
                                                     'moving_time_formatted',
                                                     'total_elevation_gain',
                                                     'map_linestring']],
                                    geometry='map_linestring')
    activity_map_gdf.rename(columns={'start_date_local': 'local start date',
                                     'distance': 'distance (km)',
                                     'moving_time_formatted': 'moving time',
                                     'total_elevation_gain': 'total elevation gain (m)'},
                            inplace=True)

    # Export the GeoDataFrame to a file in GeoJSON format
    print('[Geo]: Exporting geospatial data to {}'.format(file_path))
    activity_map_gdf.to_file(file_path, driver='GeoJSON', encoding='utf8')
