"""Pulls data from the datbase for viewing"""
import argparse
import base64
import csv
import ctypes as ct
import os
from binascii import Error

from loguru import logger
from sqlalchemy import create_engine  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from .crash_data_schema import CrashDiagram, PdfReport

csv.field_size_limit(int(ct.c_ulong(-1).value // 2))


def get_crash_diagram(report_no: str, conn_str: str, output_dir: str) -> None:
    """
    Pulls the crash diagram for the specified report number from the database
    :param report_no: The report number for the crash diagram that should be pulled
    :param conn_str: The connection string to be used in the sql alchemy engine
    :param output_dir: The directory to write the crash diagram to
    :return: None
    """
    engine = create_engine(conn_str, echo=True, future=True)
    with Session(bind=engine, future=True) as session:
        # Generate the crash diagram image
        crash_diagram = session.query(CrashDiagram.CRASHDIAGRAM).filter(CrashDiagram.REPORTNUMBER == report_no).first()
        if crash_diagram:
            output_jpg = os.path.join(output_dir, f'{report_no}.jpg')
            logger.debug('Writing crash diagram image for report {} to {}', report_no, output_jpg)

            try:
                content = base64.b64decode(crash_diagram[0])
                with open(output_jpg, 'wb') as cd_file:
                    cd_file.write(content)
            except Error:
                logger.critical('Unable to parse the crash diagram image for {}', report_no)

        # Generate the PDF report
        crash_pdf = session.query(PdfReport.PDFREPORT1).filter(PdfReport.REPORTNUMBER == report_no).first()
        if crash_pdf:
            output_pdf = os.path.join(output_dir, f'{report_no}.pdf')
            logger.debug('Writing crash diagram pdf for report {} to {}', report_no, output_pdf)

            try:
                content = base64.b64decode(crash_pdf[0])
                with open(output_pdf, 'wb') as cd_file:
                    cd_file.write(content)
            except Error:
                logger.critical('Unable to parse the crash diagram pdf for {}', report_no)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parses crash diagram data from the database. Writes the image to '
                                                 'disk')
    parser.add_argument('-r', '--report_no', required=True, help='Report number to parse')
    parser.add_argument('-d', '--output_dir', default=os.getcwd(), help='Directory to write the file to.')
    parser.add_argument('-c', '--conn_str',
                        default='mssql+pyodbc://balt-sql311-prd/DOT_DATA?driver=ODBC Driver 17 for SQL Server',
                        help='Custom database connection string (default: sqlite:///crash.db)')

    args = parser.parse_args()

    get_crash_diagram(args.report_no, args.conn_str, args.output_dir)
