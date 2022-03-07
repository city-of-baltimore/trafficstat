"""
Populates the tables with census tract data. This can be run whenever there is empty census tract information, as it
only repopulates entries that are missing census data. The census tract information is used by the PowerBI dashboards to
generate maps of hotspots

To use this, the acrs_roadway_sanitized database needs to have the following columns added:
CENSUS_TRACT (nvarchar(25)),
ROAD_NAME_CLEAN (nvarchar(50)),
REFERENCE_ROAD_NAME_CLEAN (nvarchar(50))
CRASH_LOCATION (nvarchar(max))
"""
import argparse
import re
from typing import Tuple

import requests
from arcgis.geocoding import reverse_geocode  # type: ignore
from arcgis.gis import GIS  # type: ignore
from loguru import logger
from sqlalchemy import create_engine  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ._merge import insert_or_update
from .ms2generator_schema import Base, RoadwaySanitized

GIS()


class Enrich:
    """Handles data enrichment of the sanitized crash data from the Maryland State Highway Administration"""

    def __init__(self, conn_str: str):
        logger.info(f'Creating db with connection string: {conn_str}')
        self.engine = create_engine(conn_str, echo=True, future=True)

        with self.engine.begin() as connection:
            Base.metadata.create_all(connection)

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
            if not (row[1] and row[2]):
                # we can't reverse geocode if we dont have lat/long
                continue

            try:
                geocode_result = reverse_geocode([row[1], row[2]])
            except RuntimeError as err:
                logger.error(f'Runtime error: {err}')
                continue

            address = geocode_result.get('address').get('Address')
            city = geocode_result.get('address').get('City')
            state = geocode_result.get('address').get('Region')
            req = requests.get(f'https://geocoding.geo.census.gov/geocoder/geographies/address?'
                               f'street={address}&city={city}&state={state}&benchmark=Public_AR_Census2020&'
                               f'vintage=Census2020_Census2020&layers=10&format=json')
            if not req.json():
                continue

            if req.json().get('result') and req.json().get('result').get('addressMatches'):
                insert_or_update(RoadwaySanitized(
                    REPORT_NO=row[0],
                    CENSUS_TRACT=req.json().get('result').get('addressMatches')[0].get('geographies').get(
                        'Census Blocks')[0].get('TRACT'),
                ), self.engine)
            else:
                logger.warning('No census tract for sanitized roadway: {row}', row=row)

    def get_cleaned_location(self) -> None:
        """Intelligently analyzes the road_name and reference_road_name to determine the location of the crash"""
        with Session(self.engine) as session:
            qry = session.query(RoadwaySanitized.REPORT_NO,
                                RoadwaySanitized.ROAD_NAME,
                                RoadwaySanitized.REFERENCE_ROAD_NAME).filter(RoadwaySanitized.ROAD_NAME_CLEAN.is_(None))

        tunnel_names = ('FORT MCHENRY', 'FT MCHENRY', 'HARBOR TUNNEL')
        parkway_names = ('295', '295 SOUTH', '295 NORTH', '295 NB', '295 SB', '295 NORTH BOUND', '295 NORTHBOUND',
                         '295 SOUTH BOUND', '295 SOUTHBOUND')

        for row in qry.all():
            if not row[1]:
                # if there is no road_name, then we can't clean it
                continue

            # Take care of special cases wth Ft Mchenry tunnel and 295, where we want to just dump them at spots
            road_name = row[1].upper()
            ref_road_name = row[2].upper()

            if any(x in y for x in tunnel_names for y in (road_name, ref_road_name)):
                road_name_clean = '1200 FRANKFURST AVE'
                ref_road_name_clean = None
            elif any(x in y for x in parkway_names for y in (road_name, ref_road_name)):
                road_name_clean = '2700 WATERVIEW AVE'
                ref_road_name_clean = None
            else:
                road_name_clean, ref_road_name_clean = self.clean_road_names(row[1], row[2])

            if road_name_clean == ref_road_name_clean:
                road_name_clean = row[1]
                ref_road_name_clean = None

            cleaned_location = road_name_clean \
                if ref_road_name_clean is None \
                else f'{road_name_clean} & {ref_road_name_clean}'

            if road_name_clean or ref_road_name_clean:
                insert_or_update(RoadwaySanitized(
                    ROAD_NAME_CLEAN=road_name_clean,
                    REFERENCE_ROAD_NAME_CLEAN=ref_road_name_clean,
                    CRASH_LOCATION=cleaned_location,
                    REPORT_NO=row[0]
                ), self.engine)

    def clean_road_names(self, road_name, ref_road_name) -> Tuple[str, str]:
        """
        Cleans and standarizes the road names
        :return:
        """
        road_name_clean: str = ''
        ref_road_name_clean: str = ''
        if isinstance(road_name, str):
            # We need two rounds of cleaning just because of instances like '1900 BLK OF W PRATT ST'
            road_name = self._word_replacer(road_name)
            road = re.search(r'(\d+\s+)?([NnEeSsWw](\.\s|\s|\.))?([^(]*)?', road_name)
            road_name_clean = self._word_replacer(road.group(4)) if road is not None else ''
        if isinstance(ref_road_name, str):
            ref_road_name = self._word_replacer(ref_road_name)
            road = re.search(r'(\d+\s+)?([NnEeSsWw](\.\s|\s|\.))?([^(]*)?', ref_road_name)
            ref_road_name_clean = self._word_replacer(road.group(4)) if road is not None else ''

        return road_name_clean, ref_road_name_clean

    @staticmethod
    def _word_replacer(address: str) -> str:
        """Does some standard address cleanup"""
        address = address.upper()
        for orig, repl in [('JONES FALLS EXPWY', 'I-83'),
                           (' CONNECOR', ' CONNECTOR'),
                           (' STREET', ' ST'),
                           (' PARKWAY', ' PKWY'),
                           (' WAY', ' WY'),
                           (' LANE', ' LN'),
                           (' AVENUE', ' AVE'),
                           (' ROAD', ' RD'),
                           ('.', ''),
                           ('UNIT BLK OF', ''), ('UNIT BLOCK OF', ''),
                           ('UNIT BLK', ''), ('UNIT BLOCK', ''),
                           ('BLK OF', ''), ('BLOCK OF', ''),
                           ('BLK', ''), ('BLOCK', '')
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
    enricher.get_cleaned_location()
