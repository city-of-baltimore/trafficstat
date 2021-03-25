"""Pulls data from the datbase for viewing"""
import base64
import csv
import ctypes as ct
import os
from binascii import Error

from loguru import logger
from sqlalchemy import create_engine  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from trafficstat.crash_data_schema import CrashDiagram, PdfReport

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
        crash_diagram = session.query(CrashDiagram.CRASHDIAGRAM).filter(CrashDiagram.REPORTNUMBER == report_no).first()
        crash_pdf = session.query(PdfReport.PDFREPORT1).filter(PdfReport.REPORTNUMBER == report_no).first()

        output_jpg = os.path.join(output_dir, "{}.jpg".format(report_no))
        logger.debug('Writing crash diagram image for report {} to {}', report_no, output_jpg)

        with open(output_jpg, 'wb') as cd_file:
            try:
                cd_file.write(base64.b64decode(crash_diagram[0]))
            except Error:
                logger.critical("Unable to parse the crash diagram image for {}", report_no)

        output_pdf = os.path.join(output_dir, "{}.pdf".format(report_no))
        logger.debug('Writing crash diagram pdf for report {} to {}', report_no, output_pdf)

        with open(output_pdf, 'wb') as cd_file:
            try:
                cd_file.write(base64.b64decode(crash_pdf[0]))
            except Error:
                logger.critical("Unable to parse the crash diagram pdf for {}", report_no)
