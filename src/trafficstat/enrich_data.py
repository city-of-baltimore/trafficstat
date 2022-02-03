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

import pyodbc  # type: ignore
from arcgis.geocoding import reverse_geocode  # type: ignore
from arcgis.gis import GIS  # type: ignore
from loguru import logger
from sqlalchemy import create_engine # type: ignore
from sqlalchemy.orm import Session  # type: ignore

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
                logger.error("Runtime error: {err}", err=err)
                continue

            if geocode_result is not None and geocode_result.get('census_tract'):
                insert_or_update(RoadwaySanitized(
                    REPORT_NO=row[0],
                    CENSUS_TRACT=geocode_result['census_tract'],
                ), self.engine)
            else:
                logger.warning('No census tract for sanitized roadway: {row}', row=row)

    def clean_road_names(self) -> None:
        """
        Cleans and standarizes the road names
        :return:
        """
        with Session(self.engine) as session:
            qry = session.query(RoadwaySanitized.REPORT_NO,
                                RoadwaySanitized.ROAD_NAME,
                                RoadwaySanitized.REFERENCE_ROAD_NAME).filter(RoadwaySanitized.ROAD_NAME_CLEAN.is_(None))

        for row in qry.all():
            road_name_clean = ''
            ref_road_name_clean = ''
            if isinstance(row[1], str):
                road = re.search(r'(\d+\s+)?([NnEeSsWw](\.\s|\s|\.))?([^(]*)?', row[1])
                road_name_clean = self._word_replacer(road.group(4)) if road is not None else ''
            if isinstance(row[2], str):
                road = re.search(r'(\d+\s+)?([NnEeSsWw](\.\s|\s|\.))?([^(]*)?', row[2])
                ref_road_name_clean = self._word_replacer(road.group(4)) if road is not None else ''

            if road_name_clean or ref_road_name_clean:
                insert_or_update(RoadwaySanitized(
                    ROAD_NAME_CLEAN=road_name_clean,
                    REFERENCE_ROAD_NAME_CLEAN=ref_road_name_clean,
                    REPORT_NO=row[0]
                ), self.engine)

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
