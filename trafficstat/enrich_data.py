"""
Populates the tables with census tract data. This can be run whenever there is empty census tract information, as it
only repopulates entries that are missing census data. The census tract information is used by the PowerBI dashboards to
generate maps of hotspots

To use this, the acrs_roadway_sanitized database needs to have the following columns added:
CENSUS_TRACT (nvarchar(25)),
ROAD_NAME_CLEAN (nvarchar(50)),
REFERENCE_ROAD_NAME_CLEAN (nvarchar(50))
"""
from tqdm import tqdm
import pyodbc
import re

from bcgeocoder import Geocoder  # pylint:disable=import-error
from .creds import GAPI

conn = pyodbc.connect(r'Driver={SQL Server};Server=balt-sql311-prd;Database=DOT_DATA;Trusted_Connection=yes;')
cursor = conn.cursor()


def geocode_acrs():
    """
    Fills in the CENSUS_TRACT column in acrs_roadway
    :return: None
    """
    cursor.execute("""
        SELECT [ROADID], [ROAD_NAME], [REFERENCE_ROADNAME]
        FROM [acrs_roadway]
        WHERE [CENSUS_TRACT] IS NULL AND ROAD_NAME != ''
    """)

    data = []
    geocoder = Geocoder(GAPI)
    with geocoder:
        for row in tqdm(cursor.fetchall()):
            if row[2] != '':
                geocode_result = geocoder.geocode("{} and {}, Baltimore, Maryland".format(row[1], row[2]))
            else:
                geocode_result = geocoder.geocode("{}, Baltimore, Maryland".format(row[1]))
            if geocode_result is None:
                continue

            data.append((geocode_result.get('Census Tract'), row[0]))

    if data:
        cursor.executemany("""
                UPDATE [acrs_roadway]
                SET CENSUS_TRACT = ?
                WHERE ROADID = ?
        """, data)
        cursor.commit()


def geocode_acrs_sanitized():
    """
    Fills in the CENSUS_TRACT column in acrs_roadway_sanitized
    :return: None
    """
    cursor.execute("""
    SELECT [REPORT_NO], [X_COORDINATES], [Y_COORDINATES]
    FROM [acrs_roadway_sanitized]
    WHERE [CENSUS_TRACT] IS NULL
    """)

    data = []
    geocoder = Geocoder(GAPI)
    with geocoder:
        for row in tqdm(cursor.fetchall()):
            geocode_result = geocoder.reverse_geocode(row[1], row[2])

            if geocode_result is None:
                continue

            data.append((geocode_result.get('Census Tract'), row[0]))

    if data:
        cursor.executemany("""
                UPDATE [acrs_roadway_sanitized]
                SET CENSUS_TRACT = ?
                WHERE REPORT_NO = ?
                """, data)
        cursor.commit()


def clean_road_names():
    """
    Cleans and standarizes the road names
    :return:
    """
    cursor.execute("""
    SELECT [REPORT_NO], [ROAD_NAME], [REFERENCE_ROAD_NAME]
    FROM [acrs_roadway_sanitized]
    WHERE [ROAD_NAME_CLEAN] IS NULL
    """)

    data = []
    for row in tqdm(cursor.fetchall()):
        if isinstance(row[1], str):
            road = re.search(r'(\d+\s+)?([NnEeSsWw](\.\s|\s|\.))?([^(]*)?', row[1])
            road_name_clean = _word_replacer(road.group(4))
        if isinstance(row[2], str):
            road = re.search(r'(\d+\s+)?([NnEeSsWw](\.\s|\s|\.))?([^(]*)?', row[2])
            ref_road_name_clean = _word_replacer(road.group(4))

        if road_name_clean or ref_road_name_clean:
            data.append((road_name_clean, ref_road_name_clean, row[0]))

    if data:
        cursor.executemany("""
            UPDATE [acrs_roadway_sanitized]
            SET ROAD_NAME_CLEAN = ?, REFERENCE_ROAD_NAME_CLEAN = ?
            WHERE REPORT_NO = ?
            """, data)
        cursor.commit()


def _word_replacer(address):
    """Does some standard address cleanup"""
    address = address.upper()
    for orig, repl in [(" CONNECOR", " CONNECTOR"), (" STREET", " ST"), (" PARKWAY", " PKWY"), (" WAY", " WY"),
                       ("LANE", "LN"), (".", "")]:
        address = address.replace(orig, repl)

    return address.strip()