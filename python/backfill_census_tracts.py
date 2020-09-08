"""
Populates the 'sanitized' tables with census tract data. This only need to be run after a
yearly dump of ACRS data is ingested into the _sanitized databases. The census tract information is used by the PowerBI
dashboards to generate maps of hotspots
"""
import pyodbc

from tqdm import tqdm
from geocoder import Geocoder  # pylint:disable=import-error

GAPI = ['cef4a88adf83653e4664895545fa4ccddae4553',
        '7a040f60a3a75f00aaf505fa7640430f709f836',
        'a61ac248633f88358f53838cc6343804af05808',
        'b5e3aef165a4581b4681133181fbfe4b0afbbf6',
        '9541363393b1f6d9ffb9a75d594aba61936d453',
        '5e690f6530a4ccf6ec54f40ffa5424944ef955a',
        '2719c4e74b9f973c55aba60ae66f434e35b4cf4',
        '6922aa55f65b21fb606a50b5650af54f6a54054',
        '2b1243a65a3f3713f054646034f510a3b4426b5',
        'fb4bf636614f45693149d6656f1559b9d99f3fd',
        '489dd1f6d9f5aed1a912a4e89f6e15959368dd4',
        '91987d4680f85d61557f12144447f92212614d1',
        'aa8d8fad4fb56666a1fbd6daded640db8e545af',
        'c6f15b1566ccf6775c1471641b6c5ccf7cc41b6',
        'f56d784858ee7f6f67a6588a676ff8ead4f46d8',
        'f49a0563afb1f94317613596aa67574bb5f16aa',
        'fae7f676edad47f06f024756165345fda6fe077',
        '9d7d654f54e6353e8f337deeb7e63b74b3e666f',
        'dfc44865b5a63cc464b96fd663544fdfbf993f9',
        '9d5336446d6035d6f55d0df66049ff3d25ff495',
        '5e56056e74e6f45e554ffe6fe066ef56e60e66f',
        'f55db94d6e4656cc5556ecbb65f556455bf5aed']

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
