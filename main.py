"""Main driver for the traffic stat scripts"""
import argparse

from src.enrich_data import geocode_acrs, geocode_acrs_sanitized, clean_road_names
from src.crash_data_ingestor import CrashDataReader
from src.ms2generator import WorksheetMaker

parser = argparse.ArgumentParser(description='Traffic Data Parser')
parser.add_argument('-e', '--enrich', action='store_true',
                    help='Adds census tract information and cleans roadway infromation in the roadway tables')
parser.add_argument('-p', '--parsecrashdata',
                    help='Parse ACRS xml crash data files in the specified directory, and insert them into the '
                         'DOT_DATA database')
parser.add_argument('-m', '--ms2', action='store_true',
                    help='Generate CSV files that MS2 uses to import crash data. Pulls from the DOT_DATA database')

args = parser.parse_args()

if args.enrich:
    geocode_acrs()
    geocode_acrs_sanitized()
    clean_road_names()

if args.parsecrashdata:
    cls = CrashDataReader(args.parsecrashdata)

if args.ms2:
    ws_maker = WorksheetMaker()
    with ws_maker:
        ws_maker.add_crash_worksheet()
        ws_maker.add_person_worksheet()
        ws_maker.add_ems_worksheet()
        ws_maker.add_vehicle_worksheet()
        ws_maker.add_road_circum()
