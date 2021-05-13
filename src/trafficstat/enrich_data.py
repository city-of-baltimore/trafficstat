"""
Populates the tables with census tract data. This can be run whenever there is empty census tract information, as it
only repopulates entries that are missing census data. The census tract information is used by the PowerBI dashboards to
generate maps of hotspots

To use this, the acrs_roadway_sanitized database needs to have the following columns added:
CENSUS_TRACT (nvarchar(25)),
ROAD_NAME_CLEAN (nvarchar(50)),
REFERENCE_ROAD_NAME_CLEAN (nvarchar(50))
"""
import re
from typing import List, Optional, Tuple

import pyodbc  # type: ignore
from loguru import logger
from tqdm import tqdm  # type: ignore

from balt_geocoder.geocoder import APIFatalError, Geocoder
from balt_geocoder.geocodio_types import GeocodeResult
from .creds import GAPI


class Enrich:
    """Handles data enrichment of the sanitized crash data from the Maryland State Highway Administration"""
    def __init__(self):
        conn = pyodbc.connect(r'Driver={SQL Server};Server=balt-sql311-prd;Database=DOT_DATA;Trusted_Connection=yes;')
        self.cursor = conn.cursor()

    def geocode_acrs_sanitized(self) -> None:
        """
        Fills in the CENSUS_TRACT column in acrs_roadway_sanitized
        :return: None
        """
        self.cursor.execute("""
        SELECT [REPORT_NO], [X_COORDINATES], [Y_COORDINATES]
        FROM [acrs_roadway_sanitized]
        WHERE [CENSUS_TRACT] IS NULL
        """)

        data: List[Tuple[str, str]] = []
        geocoder: Geocoder = Geocoder(GAPI)
        with geocoder:
            try:
                for row in tqdm(self.cursor.fetchall()):
                    try:
                        geocode_result: Optional[GeocodeResult] = geocoder.reverse_geocode(row[1], row[2])
                    except RuntimeError as err:
                        logger.error("Runtime error: {err}", err=err)
                        continue

                    if geocode_result is not None and geocode_result.get('census_tract'):
                        data.append((geocode_result['census_tract'], row[0]))
                        continue

                    logger.warning('No census tract for sanitized roadway: {row}', row=row)
            except APIFatalError as apierr:
                logger.error("API error: {apierr}", apierr=apierr)

        if data:
            self.cursor.executemany("""
                    UPDATE [acrs_roadway_sanitized]
                    SET CENSUS_TRACT = ?
                    WHERE REPORT_NO = ?
                    """, data)
            self.cursor.commit()

    def clean_road_names(self) -> None:
        """
        Cleans and standarizes the road names
        :return:
        """
        self.cursor.execute("""
        SELECT [REPORT_NO], [ROAD_NAME], [REFERENCE_ROAD_NAME]
        FROM [acrs_roadway_sanitized]
        WHERE [ROAD_NAME_CLEAN] IS NULL
        """)

        data: List[Tuple[str, str, str]] = []
        for row in tqdm(self.cursor.fetchall()):
            road_name_clean = ''
            ref_road_name_clean = ''
            if isinstance(row[1], str):
                road = re.search(r'(\d+\s+)?([NnEeSsWw](\.\s|\s|\.))?([^(]*)?', row[1])
                road_name_clean = self._word_replacer(road.group(4)) if road is not None else ''
            if isinstance(row[2], str):
                road = re.search(r'(\d+\s+)?([NnEeSsWw](\.\s|\s|\.))?([^(]*)?', row[2])
                ref_road_name_clean = self._word_replacer(road.group(4)) if road is not None else ''

            if road_name_clean or ref_road_name_clean:
                data.append((road_name_clean, ref_road_name_clean, row[0]))

        if data:
            self.cursor.executemany("""
                UPDATE [acrs_roadway_sanitized]
                SET ROAD_NAME_CLEAN = ?, REFERENCE_ROAD_NAME_CLEAN = ?
                WHERE REPORT_NO = ?
                """, data)
            self.cursor.commit()

    @staticmethod
    def _word_replacer(address: str) -> str:
        """Does some standard address cleanup"""
        address = address.upper()
        for orig, repl in [(" CONNECOR", " CONNECTOR"),
                           (" STREET", " ST"),
                           (" PARKWAY", " PKWY"),
                           (" WAY", " WY"),
                           (" LANE", " LN"),
                           (" AVENUE", " AVE"),
                           (" ROAD", " RD"),
                           (".", ""),
                           ("UNIT BLK OF", ""), ("UNIT BLOCK OF", ""),
                           ("UNIT BLK", ""), ("UNIT BLOCK", ""),
                           ("BLK OF", ""), ("BLOCK OF", ""),
                           ("BLK", ""), ("BLOCK", "")
                           ]:
            address = address.replace(orig, repl)

        return address.strip()


if __name__ == '__main__':
    enricher = Enrich()
    enricher.geocode_acrs_sanitized()
    enricher.clean_road_names()
