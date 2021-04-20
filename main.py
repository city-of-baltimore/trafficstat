"""Main driver for the traffic stat scripts"""
import argparse
import os
import sys
from loguru import logger

from trafficstat.enrich_data import Enrich
from trafficstat.crash_data_ingester import CrashDataReader
from trafficstat.ms2generator import WorksheetMaker
from trafficstat.viewer import get_crash_diagram

handlers = [
    {'sink': sys.stdout, 'format': '{time} - {message}', 'colorize': True, 'backtrace': True, 'diagnose': True},
    {'sink': os.path.join('logs', 'file-{time}.log'), 'colorize': True, 'serialize': True, 'backtrace': True,
     'diagnose': True, 'rotation': '1 week', 'retention': '3 months', 'compression': 'zip'},
]

logger.configure(handlers=handlers)

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
parser_parse.add_argument('-d', '--directory', help='Directory containing ACRS XML files to parse. If quotes are '
                                                    'required in the path (if there are spaces), use double quotes.')
parser_parse.add_argument('-f', '--file', help='Path to a single file to process. If quotes are required in the path '
                                               '(if there are spaces), use double quotes.')

# Generate
parser_generate = subparsers.add_parser('ms2export', help='Generate CSV files that MS2 uses to import crash data. Pulls'
                                                          ' from the DOT_DATA database')

# Viewer
parser_viewer = subparsers.add_parser('viewer', help='Parses crash diagram data from the database. Writes the image to '
                                                     'disk')
parser_viewer.add_argument('-r', '--report_no', required=True, help='Report number to parse')
parser_viewer.add_argument('-d', '--output_dir', default=os.getcwd(), help='Directory to write the file to.')
parser_viewer.add_argument('-c', '--conn_str',
                           default='mssql+pyodbc://balt-sql311-prd/DOT_DATA?driver=ODBC Driver 17 for SQL Server',
                           help='Custom database connection string (default: sqlite:///crash.db)')

args = parser.parse_args()

if args.subparser_name == 'enrich':
    enricher = Enrich()
    enricher.geocode_acrs_sanitized()
    enricher.clean_road_names()

if args.subparser_name == 'parse':
    cls = CrashDataReader(args.conn_str)
    if not (args.directory or args.file):
        logger.error('Must specify either a directory or file to process')
    if args.directory:
        cls.read_crash_data(dir_name=args.directory)
    if args.file:
        if not os.path.exists(args.file):
            logger.error('File does not exist: {}'.format(args.file))
        cls.read_crash_data(file_name=args.file)

if args.subparser_name == 'ms2export':
    ws_maker = WorksheetMaker(
        conn_str='mssql+pyodbc://balt-sql311-prd/DOT_DATA?driver=ODBC Driver 17 for SQL Server')
    with ws_maker:
        ws_maker.add_crash_worksheet()
        ws_maker.add_person_worksheet()
        ws_maker.add_ems_worksheet()
        ws_maker.add_vehicle_worksheet()
        ws_maker.add_road_circum()

if args.subparser_name == 'viewer':
    get_crash_diagram(args.report_no, args.conn_str, args.output_dir)
