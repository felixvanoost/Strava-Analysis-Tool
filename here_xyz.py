"""here_xyz.py

Uploads and manages the geospatial data from Strava activities with the HERE XYZ
mapping platform.

Functions:
upload_geo_data()

Felix van Oost 2022
"""

# Standard library
import geojson
import json
import pathlib
import sys

# Third-party
from xyzspaces import IML
from xyzspaces.iml.credentials import Credentials


HERE_CATALOG_ID = "strava-analysis-tool"
HERE_LAYER_ID = "strava-activity-data"


def _get_here_iml(here_creds_file_path: pathlib.Path) -> IML:
    """
    Return an IML object for the HERE interactive map layer that belongs to the
    Strava Analysis Tool. Create a new IML if one does not exist,

    Arguments:
    here_creds_file_path - Path of the file containing the HERE platform
                           credentials.
    """

    # Get the HERE platform credentials
    credentials = Credentials.from_credentials_file(here_creds_file_path)

    # Attempt to load an instance of the existing interactive map layer (if
    # one exists)
    try:
        print("[HERE] Locating the HERE interactive map layer for Strava "
              "Analysis Tool")

        iml = IML.from_catalog_hrn_and_layer_id(
        catalog_hrn=f"hrn:here:data:::{HERE_CATALOG_ID}",
        layer_id=HERE_LAYER_ID,
        credentials=credentials)

        print("[HERE] Found an existing HERE interactive map layer with ID "
              f"'{HERE_LAYER_ID}'")
    except Exception as error:
        print("[HERE] No existing HERE interactive map layer found. Creating a "
              "new catalog and IML for Strava Analysis Tool.")

        # Attempt to create a new catalog and IML for Strava Analysis Tool
        try:
            layer_details = {
            "id": HERE_LAYER_ID,
            "name": "Strava Activity Data",
            "summary": "Strava Activity Data",
            "description": "Strava data collected by Strava Analysis Tool",
            "layerType": "interactivemap",
            "interactiveMapProperties": {},
            }

            iml = IML.new(
            catalog_id=HERE_CATALOG_ID,
            catalog_name="Strava Analysis Tool",
            catalog_summary="Strava Analysis Tool",
            catalog_description="Strava data collected by Strava Analysis "
                                "Tool",
            layer_details=layer_details,
            credentials=credentials,
            )

            print(f"[HERE] Created a new catalog with ID '{HERE_CATALOG_ID}' "
                  f"and interactive map layer with ID '{HERE_LAYER_ID}'")
        except Exception as error:
            sys.exit(f'[ERROR]: HERE returned the following error: {error}')

    return iml


def upload_geo_data(geo_data_file_path: pathlib.Path, here_creds_file_path: pathlib.Path):
    """
    Upload the geospatial activity data to an interactive mapping layer (IML)
    on the HERE platform. This layer can be used by the map created in HERE
    Studio.

    Arguments:
    geo_data_file_path - Path of the file containing the geospatial activity
                         data in GeoJSON format.
    here_creds_file_path - Path of the file containing the HERE platform
                           credentials.
    """

    # Get a HERE IML object for the Strava Analysis Tool layer
    iml = _get_here_iml(here_creds_file_path=here_creds_file_path)

    # Read the contents of the geo data file
    with geo_data_file_path.open('r', encoding='utf-8') as geo_data_file:
        geo_data = geojson.load(geo_data_file)

        if geo_data:
            # Upload all the data
            iml.layer.write_features(features=geo_data)
