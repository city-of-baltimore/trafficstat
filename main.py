"""Main driver for the traffic stat scripts"""
import argparse

from src.trafficstat.enrich_data import Enrich
from src.trafficstat.crash_data_ingestor import CrashDataReader
from src.trafficstat.ms2generator import WorksheetMaker

parser = argparse.ArgumentParser(description='Traffic Data Parser')
subparsers = parser.add_subparsers(dest='subparser_name', help='sub-command help')

# Enrich
parser_enrich = subparsers.add_parser('enrich', help='Adds census tract information and cleans roadway information in '
                                                     'the roadway tables')

# Parse
parser_parse = subparsers.add_parser('parse', help='Parse ACRS xml crash data files in the specified directory, and '
                                                   'insert them into a database')
parser_parse.add_argument('-c', '--conn_str', default='sqlite:///crash.db',
                          help='Custom database connection string (default: sqlite:///crash.db)')
parser_parse.add_argument('-d', '--directory', help='Directory containing ACRS XML files to parse')

# Generate
parser_generate = subparsers.add_parser('ms2export', help='Generate CSV files that MS2 uses to import crash data. Pulls '
                                                         'from the DOT_DATA database')


args = parser.parse_args()

if args.subparser_name == 'enrich':
    enricher = Enrich()
    enricher.geocode_acrs()
    enricher.geocode_acrs_sanitized()
    enricher.clean_road_names()

if args.subparser_name == 'parse':
    cls = CrashDataReader(args.conn_str)
    cls.read_crash_data(dir_name=args.directory)

if args.subparser_name == 'ms2export':
    ws_maker = WorksheetMaker()
    with ws_maker:
        ws_maker.add_crash_worksheet()
        ws_maker.add_person_worksheet()
        ws_maker.add_ems_worksheet()
        ws_maker.add_vehicle_worksheet()
        ws_maker.add_road_circum()
