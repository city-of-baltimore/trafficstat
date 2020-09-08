"""
Populates the 'sanitized' tables with census tract data. This only need to be run after a
yearly dump of ACRS data is ingested into the _sanitized databases. The census tract information is used by the PowerBI
dashboards to generate maps of hotspots
"""
import pyodbc

from tqdm import tqdm
from bcgeocoder import Geocoder  # pylint:disable=import-error
from .creds import GAPI

conn = pyodbc.connect(r'Driver={SQL Server};Server=balt-sql311-prd;Database=DOT_DATA;Trusted_Connection=yes;')
cursor = conn.cursor()

cursor.execute("""
SELECT [REPORT_NO], [X_COORDINATES], [Y_COORDINATES] 
FROM [acrs_roadway_sanitized]
WHERE [CENSUS_TRACT] IS NULL
""")

geocoder = Geocoder(GAPI)
with geocoder:
    for row in tqdm(cursor.fetchall()):
        geocode_result = geocoder.reverse_geocode(row[1], row[2])

        if geocode_result is None:
            continue

        cursor.execute("""
                UPDATE [acrs_roadway_sanitized]
                SET CENSUS_TRACT = ?
                WHERE REPORT_NO = ?
                """, geocode_result.get('Census Tract'), row[0])
        cursor.commit()
