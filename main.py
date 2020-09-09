"""Main driver for the traffic stat scripts"""
import argparse

from trafficstat.backfill_census_tracts import geocode_acrs, geocode_acrs_sanitized
from trafficstat.crash_data_ingestor import CrashDataReader

parser = argparse.ArgumentParser(description='Traffic Data Parser')
parser.add_argument('-c', '--censustracts', action='store_true',
                    help='Adds census tract information to the acrs_roadway and acrs_roadway_sanitized tables')
parser.add_argument('-p', '--parsecrashdata',
                    help='Parse ACRS xml crash data files in the specified directory, and insert them into the '
                         'DOT_DATA database')

args = parser.parse_args()

if args.censustracts:
    geocode_acrs()
    geocode_acrs_sanitized()

if args.parsecrashdata:
    cls = CrashDataReader()
    cls.read_directory(args.parsecrashdata)
