"""
Populates the tables with census tract data. This can be run whenever there is empty census tract information, as it
only repopulates entries that are missing census data. The census tract information is used by the PowerBI dashboards to
generate maps of hotspots

To use this, the acrs_roadway_sanitized database needs to have the following columns added:
CENSUS_TRACT (nvarchar(25)),
ROAD_NAME_CLEAN (nvarchar(50)),
REFERENCE_ROAD_NAME_CLEAN (nvarchar(50))
"""
import argparse
import re

from arcgis.geocoding import reverse_geocode  # type: ignore
from arcgis.gis import GIS  # type: ignore
from loguru import logger
from sqlalchemy import create_engine  # type: ignore
from sqlalchemy.orm import Session  # type: ignore
from typing import Tuple

from ._merge import insert_or_update
from .crash_data_schema import RoadwaySanitized

GIS()


class Enrich:
    """Handles data enrichment of the sanitized crash data from the Maryland State Highway Administration"""

    def __init__(self, conn_str: str):
        logger.info(f"Creating db with connection string: {conn_str}")
        self.engine = create_engine(conn_str, echo=True, future=True)

    def geocode_acrs_sanitized(self) -> None:
        """
        Fills in the CENSUS_TRACT column in acrs_roadway_sanitized
        :return: None
        """
        with Session(self.engine) as session:
            qry = session.query(RoadwaySanitized.REPORT_NO,
                                RoadwaySanitized.X_COORDINATES,
                                RoadwaySanitized.Y_COORDINATES).filter(RoadwaySanitized.CENSUS_TRACT.is_(None))

        for row in qry.all():
            try:
                geocode_result = reverse_geocode([row[1], row[2]])
            except RuntimeError as err:
                logger.error(f"Runtime error: {err}")
                continue

            if geocode_result is not None and geocode_result.get('census_tract'):
                insert_or_update(RoadwaySanitized(
                    REPORT_NO=row[0],
                    CENSUS_TRACT=geocode_result['census_tract'],
                ), self.engine)
            else:
                logger.warning('No census tract for sanitized roadway: {row}', row=row)

    def get_cleaned_location(self) -> None:
        """Intelligently analyzes the road_name and reference_road_name to determine the location of the crash"""
        with Session(self.engine) as session:
            qry = session.query(RoadwaySanitized.REPORT_NO,
                                RoadwaySanitized.ROAD_NAME,
                                RoadwaySanitized.REFERENCE_ROAD_NAME).filter(RoadwaySanitized.ROAD_NAME_CLEAN.is_(None))

        for row in qry.all():
            # Take care of special cases wth Ft Mchenry tunnel and 295, where we want to just dump them at spots
            if 'FORT MCHENRY' in row[1].upper() or 'FT MCHENRY' in row[1].upper():
                road_name_clean = '1200 Frankfurst Ave'
                ref_road_name_clean = None
            elif row[1] in ('295', '295 SOUTH', '295 NORTH', '295 NB', '295 SB', '295 NORTH BOUND', '295 NORTHBOUND',
                            '295 SOUTH BOUND', '295 SOUTHBOUND'):
                road_name_clean = '2700 Waterview'
                ref_road_name_clean = None
            else:
                road_name_clean, ref_road_name_clean = self.clean_road_names(row[1], row[2])

            if road_name_clean == ref_road_name_clean:
                road_name_clean = row[1]
                ref_road_name_clean = None

            if road_name_clean or ref_road_name_clean:
                insert_or_update(RoadwaySanitized(
                    ROAD_NAME_CLEAN=road_name_clean,
                    REFERENCE_ROAD_NAME_CLEAN=ref_road_name_clean,
                    REPORT_NO=row[0]
                ), self.engine)

    def clean_road_names(self, road_name, ref_road_name) -> Tuple[str, str]:
        """
        Cleans and standarizes the road names
        :return:
        """
        road_name_clean = ''
        ref_road_name_clean = ''
        if isinstance(road_name, str):
            road = re.search(r'(\d+\s+)?([NnEeSsWw](\.\s|\s|\.))?([^(]*)?', road_name)
            road_name_clean = self._word_replacer(road.group(4)) if road is not None else ''
        if isinstance(ref_road_name, str):
            road = re.search(r'(\d+\s+)?([NnEeSsWw](\.\s|\s|\.))?([^(]*)?', ref_road_name)
            ref_road_name_clean = self._word_replacer(road.group(4)) if road is not None else ''

        return road_name_clean, ref_road_name_clean

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
    parser = argparse.ArgumentParser(description='Cleans and enhances the sanitzed crash data we get from the SHA. This'
                                                 ' can be run after the yearly data is imported.')
    parser.add_argument('-c', '--conn_str', help='Custom database connection string',
                        default='mssql+pyodbc://balt-sql311-prd/DOT_DATA?driver=ODBC Driver 17 for SQL Server')
    args = parser.parse_args()

    enricher = Enrich(args.conn_str)
    enricher.geocode_acrs_sanitized()
    enricher.clean_road_names()
