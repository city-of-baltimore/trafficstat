"""Main driver for the traffic stat scripts"""
import argparse

from trafficstat.backfill_census_tracts import geocode_acrs, geocode_acrs_sanitized
from trafficstat.crash_data_ingestor import CrashDataReader
from trafficstat.ms2generator import WorksheetMaker

parser = argparse.ArgumentParser(description='Traffic Data Parser')
parser.add_argument('-c', '--censustracts', action='store_true',
                    help='Adds census tract information to the acrs_roadway and acrs_roadway_sanitized tables')
parser.add_argument('-p', '--parsecrashdata',
                    help='Parse ACRS xml crash data files in the specified directory, and insert them into the '
                         'DOT_DATA database')
parser.add_argument('-m', '--ms2', action='store_true',
                    help='Generate CSV files that MS2 uses to import crash data. Pulls from the DOT_DATA database')

args = parser.parse_args()

if args.censustracts:
    geocode_acrs()
    geocode_acrs_sanitized()

if args.parsecrashdata:
    cls = CrashDataReader()
    cls.read_directory(args.parsecrashdata)

if args.ms2:
    ws_maker = WorksheetMaker()
    with ws_maker:
        ws_maker.add_crash_worksheet()
        ws_maker.add_person_worksheet()
        ws_maker.add_ems_worksheet()
        ws_maker.add_vehicle_worksheet()
