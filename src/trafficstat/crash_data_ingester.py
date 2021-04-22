"""Processes unprocessed data in the network share that holds crash data"""
import argparse
import collections.abc
import glob
import inspect
import os
import shutil
from collections import OrderedDict
from datetime import datetime, time
from sqlite3 import Connection as SQLite3Connection
from typing import List, Mapping, Optional, Union
from xml.parsers.expat import ExpatError

import xmltodict  # type: ignore
from balt_geocoder import Geocoder
from loguru import logger
from pandas import to_datetime  # type: ignore
from pandas.errors import OutOfBoundsDatetime  # type: ignore
from sqlalchemy import create_engine, event as sqlalchemyevent, inspect as sqlalchemyinspect  # type: ignore
from sqlalchemy.engine import Engine  # type: ignore
from sqlalchemy.exc import IntegrityError  # type: ignore
from sqlalchemy.ext.declarative import DeclarativeMeta  # type: ignore
from sqlalchemy.orm import Session  # type: ignore
from sqlalchemy.sql import text  # type: ignore
from pyvin import DecodedVIN, VIN  # type: ignore

from .crash_data_schema import Approval, Base, Crash, Circumstance, CitationCode, CommercialVehicle, \
    CrashDiagram, DamagedArea, Ems, Event, PdfReport, Person, PersonInfo, Roadway, TowedUnit, Vehicle, VehicleUse, \
    Witness
from .crash_data_types import ApprovalDataType, CrashDataType, CircumstanceType, CitationCodeType, \
    CommercialVehicleType, CrashDiagramType, DamagedAreaType, DriverType, EmsType, EventType, NonMotoristType, \
    PassengerType, PdfReportDataType, PersonType, ReportDocumentType, ReportPhotoType, RoadwayType, TowedUnitType, \
    VehicleType, VehicleUseType, WitnessType
from .creds import GAPI
from .xmlsanitizer import sanitize_xml_str


@sqlalchemyevent.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):  # pylint:disable=unused-argument
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


def check_and_log(check_dict: str):
    """Logs the function entry, and checks the check_dict argument for nullness"""

    def _check_and_log(func):
        def wrapper(*_args, **_kwargs):
            logger.info('Entering {}', func.__name__)

            # handle positional or keyword args
            args_name = inspect.getfullargspec(func)[0]
            args_dict = dict(zip(args_name, _args))
            args_dict.update(**_kwargs)
            self = args_dict['self']

            if self.is_element_nil(args_dict[check_dict]):
                logger.warning('No data')
                return False

            return func(*_args, **_kwargs)

        return wrapper

    return _check_and_log


class CrashDataReader:
    """ Reads a directory of ACRS crash data files"""

    def __init__(self, conn_str: str, geocodio_api_key: Optional[str] = None, pickle_filename: str = 'geo.pickle',
                 pickle_filename_rev: str = 'geo_rev.pickle'):
        """
        Reads a directory of XML ACRS crash files, and returns an iterator of the parsed data
        :param conn_str: sqlalchemy connection string (IE sqlite:///crash.db)
        """
        logger.info('Creating db with connection string: {}', conn_str)
        self.engine = create_engine(conn_str, echo=True, future=True)

        with self.engine.begin() as connection:
            Base.metadata.create_all(connection)

        if geocodio_api_key is None:
            geocodio_api_keys: List[str] = GAPI
        else:
            geocodio_api_keys = [geocodio_api_key]
        self.geocoder = Geocoder(geocodio_api_keys, pickle_filename, pickle_filename_rev) if geocodio_api_keys else None

    def _insert_or_update(self, insert_obj: DeclarativeMeta, identity_insert=False):
        """
        A safe way for the sqlalchemy
        :param insert_obj:
        :param identity_insert:
        :return:
        """
        session = Session(bind=self.engine, future=True)
        if identity_insert:
            session.execute(text('SET IDENTITY_INSERT {} ON'.format(insert_obj.__tablename__)))

        session.add(insert_obj)
        try:
            session.commit()
            logger.debug('Successfully inserted object: {}', insert_obj)
        except IntegrityError as insert_err:
            session.rollback()

            if '(544)' in insert_err.args[0]:
                # This is a workaround for an issue with sqlalchemy not properly setting IDENTITY_INSERT on for SQL
                # Server before we insert values in the primary key. The error is:
                # (pyodbc.IntegrityError) ('23000', "[23000] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]
                # Cannot insert explicit value for identity column in table <table name> when IDENTITY_INSERT is set to
                # OFF. (544) (SQLExecDirectW)")
                self._insert_or_update(insert_obj, True)

            elif '(2627)' in insert_err.args[0] or 'UNIQUE constraint failed' in insert_err.args[0]:
                # Error 2627 is the Sql Server error for inserting when the primary key already exists. 'UNIQUE
                # constraint failed' is the same for Sqlite
                cls_type = type(insert_obj)

                qry = session.query(cls_type)

                primary_keys = [i.key for i in sqlalchemyinspect(cls_type).primary_key]
                for primary_key in primary_keys:
                    qry = qry.filter(cls_type.__dict__[primary_key] == insert_obj.__dict__[primary_key])

                update_vals = {k: v for k, v in insert_obj.__dict__.items()
                               if not k.startswith('_') and k not in primary_keys}
                if update_vals:
                    qry.update(update_vals)
                    try:
                        session.commit()
                        logger.debug('Successfully inserted object: {}', insert_obj)
                    except IntegrityError as update_err:
                        logger.error('Unable to insert object: {}\nError: {}', insert_obj, update_err)

            else:
                raise AssertionError('Expected error 2627 or "UNIQUE constraint failed". Got {}'.format(insert_err)) \
                    from insert_err
        finally:
            if identity_insert:
                session.execute(text('SET IDENTITY_INSERT {} OFF'.format(insert_obj.__tablename__)))
            session.close()

    def read_crash_data(self, dir_name: Optional[str] = None, recursive: bool = False, file_name: Optional[str] = None,  # pylint:disable=too-many-arguments
                        copy: bool = True, sanitize: bool = False
                        ) -> None:
        """
        Reads the ACRS crash data files
        :param dir_name: Directory to process. All XML files in the directory will be processed.
        :param recursive: Recursive search, as passed to glob.glob. Only applicable to dir_name arg
        :param file_name: Full path to the file to process
        :param copy: All processed ACRS xml files will be copied to .processed folder
        :param sanitize: All processed ACRS xml files will be sanitized of PII.
        """
        if dir_name:
            for acrs_file in glob.glob(os.path.join(dir_name, '*.xml'), recursive=recursive):
                self.read_crash_data(recursive=recursive, file_name=acrs_file, copy=copy, sanitize=sanitize)

        if file_name:
            if os.path.exists(file_name):
                self._read_file(file_name, sanitize=sanitize)
                if copy:
                    try:
                        self._file_move(file_name, os.path.join(os.path.dirname(file_name), '.processed'))
                    except PermissionError as err:
                        logger.error('Unable to copy file: {}', err)

    def _read_file(self, file_name: str, sanitize: bool = False) -> None:  # pylint:disable=too-many-branches
        logger.info('Processing {}', file_name)
        with open(file_name, encoding='utf-8') as acrs_file:
            crash_file: Optional[str] = acrs_file.read()
            if sanitize:
                crash_file = sanitize_xml_str(crash_file)

        if crash_file is None:
            return

        # These files have non ascii at the beginning that causes parse errors
        offset = crash_file.find('<?xml')
        try:
            root = xmltodict.parse(crash_file[offset:],
                                   force_list={'ACRSPERSON', 'ACRSVEHICLE', 'CIRCUMSTANCE', 'CITATIONCODE',
                                               'DAMAGEDAREA', 'DRIVER', 'EMS', 'EVENT', 'NONMOTORIST', 'PASSENGER',
                                               'PDFREPORT', 'REPORTDOCUMENT', 'REPORTPHOTO', 'TOWEDUNIT', 'VEHICLEUSE',
                                               'WITNESS'})
        except ExpatError as err:
            logger.error('Unable to parse file {}. Parse error: {}', file_name, err)
            return

        crash_dict = root['REPORT']

        if crash_dict.get('ROADWAY'):
            self._read_roadway_data(crash_dict['ROADWAY'])

        # The following requires acrs_roadway for its relationships
        if not self._read_main_crash_data(crash_dict):
            return

        # The following require acrs_crash for their relationships
        if crash_dict.get('APPROVALDATA'):
            self._read_approval_data(crash_dict['APPROVALDATA'])

        if crash_dict.get('DIAGRAM'):
            self._read_crash_diagrams_data(crash_dict['DIAGRAM'])

        if crash_dict.get('EMSes') and crash_dict.get('EMSes', {}).get('EMS'):
            self._read_ems_data(crash_dict['EMSes']['EMS'])

        if crash_dict.get('People') and crash_dict.get('People', {}).get('ACRSPERSON'):
            self._read_acrs_person_data(crash_dict['People']['ACRSPERSON'])

        if crash_dict.get('PDFREPORTs') and crash_dict.get('PDFREPORTs', {}).get('PDFREPORT'):
            self._read_pdf_data(crash_dict['PDFREPORTs']['PDFREPORT'])

        if crash_dict.get('REPORTDOCUMENTs') and crash_dict.get('REPORTDOCUMENTs', {}).get('REPORTDOCUMENT'):
            self._read_report_documents_data(crash_dict['REPORTDOCUMENTs']['REPORTDOCUMENT'])

        if crash_dict.get('REPORTPHOTOes') and crash_dict.get('REPORTPHOTOes', {}).get('REPORTPHOTO'):
            self._read_report_photos_data(crash_dict['REPORTPHOTOes']['REPORTPHOTO'])

        # These require acrs_crash and acrs_person
        if crash_dict.get('VEHICLEs') and crash_dict.get('VEHICLEs', {}).get('ACRSVEHICLE'):
            self._read_acrs_vehicle_data(crash_dict['VEHICLEs']['ACRSVEHICLE'])

        if crash_dict.get('NONMOTORISTs') and crash_dict.get('NONMOTORISTs', {}).get('NONMOTORIST'):
            self._read_person_info_data(crash_dict['NONMOTORISTs']['NONMOTORIST'])

        if crash_dict.get('WITNESSes') and crash_dict.get('WITNESSes', {}).get('WITNESS'):
            self._read_witness_data(crash_dict['WITNESSes']['WITNESS'])

        # These require acrs_crash, acrs_vehicle, and acrs_person
        if crash_dict.get('CIRCUMSTANCES') and crash_dict.get('CIRCUMSTANCES', {}).get('CIRCUMSTANCE'):
            self._read_circumstance_data(crash_dict['CIRCUMSTANCES']['CIRCUMSTANCE'])

    @staticmethod
    def _file_move(file_name: str, processed_dir: str) -> bool:
        """
        File copy with automatic renaming during retry
        :param file_name: File to copy to processed_dir
        :param processed_dir: Directory to copy file into
        """
        if not os.path.exists(processed_dir):
            os.mkdir(processed_dir)

        if not os.path.exists(os.path.join(processed_dir, os.path.basename(file_name))):
            shutil.move(file_name, processed_dir)
            return True

        # Otherwise we need to figure out another filename
        i = 1
        while i < 6:
            # retry copy operation up to 5 times
            dst_filename = '{}_{}'.format(os.path.join(processed_dir, os.path.basename(file_name)), i)
            if not os.path.exists(os.path.join(processed_dir, dst_filename)):
                shutil.move(file_name, dst_filename)
                return True
            i += 1

        logger.error('Error moving file. It will not be moved to the processed directory: {}', file_name)
        return False

    @check_and_log('crash_dict')
    def _read_main_crash_data(self, crash_dict: CrashDataType) -> bool:
        """ Populates the acrs_crashes table """
        crash_time_str = self.get_single_attr('CRASHTIME', crash_dict)
        if isinstance(crash_time_str, str) and len(crash_time_str.split('T')) > 1:
            crash_time: Optional[time] = time.fromisoformat(crash_time_str.split('T')[1])
        elif crash_time_str is None:
            crash_time = None
        else:
            crash_time = time.fromisoformat(crash_time_str)

        latitude = self.get_single_attr('LATITUDE', crash_dict)
        longitude = self.get_single_attr('LONGITUDE', crash_dict)
        census_tract = None

        if not (latitude and longitude):
            logger.error('Unable to get latitude and longitude')
        else:
            if not self.geocoder:
                logger.error('Unable to geocode because the geocoder is invalid')
            else:
                geo = self.geocoder.reverse_geocode(float(latitude), float(longitude))
                if not geo:
                    logger.error('Unable to reverse geocode {}/{}'.format(latitude, longitude))
                else:
                    census_tract = geo.get('census_tract')

        self._insert_or_update(
            Crash(
                ACRSREPORTTIMESTAMP=self.to_datetime_sql(self.get_single_attr('ACRSREPORTTIMESTAMP', crash_dict)),
                AGENCYIDENTIFIER=self.get_single_attr('AGENCYIDENTIFIER', crash_dict),
                AGENCYNAME=self.get_single_attr('AGENCYNAME', crash_dict),
                AREA=self.get_single_attr('AREA', crash_dict),
                CENSUS_TRACT=census_tract,
                COLLISIONTYPE=self.get_single_attr('COLLISIONTYPE', crash_dict),
                CONMAINCLOSURE=self.get_single_attr('CONMAINCLOSURE', crash_dict),
                CONMAINLOCATION=self.get_single_attr('CONMAINLOCATION', crash_dict),
                CONMAINWORKERSPRESENT=self.convert_to_bool(self.get_single_attr('CONMAINWORKERSPRESENT', crash_dict)),
                CONMAINZONE=self.convert_to_bool(self.get_single_attr('CONMAINZONE', crash_dict)),
                CRASHDATE=self.to_datetime_sql(self.get_single_attr('CRASHDATE', crash_dict)),
                CRASHTIME=crash_time,
                CURRENTASSIGNMENT=self.get_single_attr('CURRENTASSIGNMENT', crash_dict),
                CURRENTGROUP=self.get_single_attr('CURRENTGROUP', crash_dict),
                DEFAULTASSIGNMENT=self.get_single_attr('DEFAULTASSIGNMENT', crash_dict),
                DEFAULTGROUP=self.get_single_attr('DEFAULTGROUP', crash_dict),
                DOCTYPE=self.get_single_attr('DOCTYPE', crash_dict),
                FIXEDOBJECTSTRUCK=self.get_single_attr('FIXEDOBJECTSTRUCK', crash_dict),
                HARMFULEVENTONE=self.get_single_attr('HARMFULEVENTONE', crash_dict),
                HARMFULEVENTTWO=self.get_single_attr('HARMFULEVENTTWO', crash_dict),
                HITANDRUN=self.convert_to_bool(self.get_single_attr('HITANDRUN', crash_dict)),
                INSERTDATE=self.to_datetime_sql(self.get_single_attr('INSERTDATE', crash_dict)),
                INTERCHANGEAREA=self.get_single_attr('INTERCHANGEAREA', crash_dict),
                INTERCHANGEIDENTIFICATION=self.get_single_attr('INTERCHANGEIDENTIFICATION', crash_dict),
                INTERSECTIONTYPE=self.get_single_attr('INTERSECTIONTYPE', crash_dict),
                INVESTIGATINGOFFICERUSERNAME=self.get_single_attr('INVESTIGATINGOFFICERUSERNAME', crash_dict),
                INVESTIGATOR=self.get_single_attr('INVESTIGATOR', crash_dict),
                JUNCTION=self.get_single_attr('JUNCTION', crash_dict),
                LANEDIRECTION=self.get_single_attr('LANEDIRECTION', crash_dict),
                LANENUMBER=self.get_single_attr('LANENUMBER', crash_dict),
                LANETYPE=self.get_single_attr('LANETYPE', crash_dict),
                LATITUDE=latitude,
                LIGHT=self.get_single_attr('LIGHT', crash_dict),
                LOCALCASENUMBER=self.get_single_attr('LOCALCASENUMBER', crash_dict),
                LOCALCODES=self.get_single_attr('LOCALCODES', crash_dict),
                LONGITUDE=longitude,
                MILEPOINTDIRECTION=self.get_single_attr('MILEPOINTDIRECTION', crash_dict),
                MILEPOINTDISTANCE=self.get_single_attr('MILEPOINTDISTANCE', crash_dict),
                MILEPOINTDISTANCEUNITS=self.get_single_attr('MILEPOINTDISTANCEUNITS', crash_dict),
                NARRATIVE=self.get_single_attr('NARRATIVE', crash_dict),
                NONTRAFFIC=self.convert_to_bool(self.get_single_attr('NONTRAFFIC', crash_dict)),
                NUMBEROFLANES=self.get_single_attr('NUMBEROFLANES', crash_dict),
                OFFROADDESCRIPTION=self.get_single_attr('OFFROADDESCRIPTION', crash_dict),
                PHOTOSTAKEN=self.convert_to_bool(self.get_single_attr('PHOTOSTAKEN', crash_dict)),
                RAMP=self.get_single_attr('RAMP', crash_dict),
                REPORTCOUNTYLOCATION=self.get_single_attr('REPORTCOUNTYLOCATION', crash_dict),
                REPORTNUMBER=self.get_single_attr('REPORTNUMBER', crash_dict),
                REPORTTYPE=self.get_single_attr('REPORTTYPE', crash_dict),
                ROADALIGNMENT=self.get_single_attr('ROADALIGNMENT', crash_dict),
                ROADCONDITION=self.get_single_attr('ROADCONDITION', crash_dict),
                ROADDIVISION=self.get_single_attr('ROADDIVISION', crash_dict),
                ROADGRADE=self.get_single_attr('ROADGRADE', crash_dict),
                ROADID=self.get_single_attr('ROADID', crash_dict),
                SCHOOLBUSINVOLVEMENT=self.get_single_attr('SCHOOLBUSINVOLVEMENT', crash_dict),
                STATEGOVERNMENTPROPERTYNAME=self.get_single_attr('STATEGOVERNMENTPROPERTYNAME', crash_dict),
                SUPERVISOR=self.get_single_attr('SUPERVISOR', crash_dict),
                SUPERVISORUSERNAME=self.get_single_attr('SUPERVISORUSERNAME', crash_dict),
                SUPERVISORYDATE=self.to_datetime_sql(self.get_single_attr('SUPERVISORYDATE', crash_dict)),
                SURFACECONDITION=self.get_single_attr('SURFACECONDITION', crash_dict),
                TRAFFICCONTROL=self.get_single_attr('TRAFFICCONTROL', crash_dict),
                TRAFFICCONTROLFUNCTIONING=self.convert_to_bool(
                    self.get_single_attr('TRAFFICCONTROLFUNCTIONING', crash_dict)),
                UPDATEDATE=self.to_datetime_sql(self.get_single_attr('UPDATEDATE', crash_dict)),
                UPLOADVERSION=self.get_single_attr('UPLOADVERSION', crash_dict),
                VERSIONNUMBER=self.get_single_attr('VERSIONNUMBER', crash_dict),
                WEATHER=self.get_single_attr('WEATHER', crash_dict)
            ))

        return True

    @check_and_log('approval_dict')
    def _read_approval_data(self, approval_dict: ApprovalDataType) -> None:
        """
        Populates the acrs_approval table
        :param approval_dict: The ordereddict contained in the APPROVALDATA tag
        """
        self._insert_or_update(
            Approval(
                AGENCY=self.get_single_attr('AGENCY', approval_dict),
                APPROVALDATE=self.to_datetime_sql(self.get_single_attr('APPROVALDATE', approval_dict)),
                CADSENT=self.get_single_attr('CADSENT', approval_dict),
                CADSENT_DATE=self.to_datetime_sql(self.get_single_attr('CADSENT_DATE', approval_dict)),
                CC_NUMBER=self.get_single_attr('CC_NUMBER', approval_dict),
                DATE_INITIATED2=self.to_datetime_sql(self.get_single_attr('DATE_INITIATED2', approval_dict)),
                GROUP_NUMBER=self.get_single_attr('GROUP_NUMBER', approval_dict),
                HISTORICALAPPROVALDATAs=self.get_single_attr('HISTORICALAPPROVALDATAs', approval_dict),
                INCIDENT_DATE=self.to_datetime_sql(self.get_single_attr('INCIDENT_DATE', approval_dict)),
                INVESTIGATOR=self.get_single_attr('INVESTIGATOR', approval_dict),
                REPORT_TYPE=self.get_single_attr('REPORT_TYPE', approval_dict),
                SEQ_GUID=self.get_single_attr('SEQ_GUID', approval_dict),
                STATUS_CHANGE_DATE=self.to_datetime_sql(self.get_single_attr('STATUS_CHANGE_DATE', approval_dict)),
                STATUS_ID=self.get_single_attr('STATUS_ID', approval_dict),
                STEP_NUMBER=self.get_single_attr('STEP_NUMBER', approval_dict),
                TR_USERNAME=self.get_single_attr('TR_USERNAME', approval_dict),
                UNIT_CODE=self.get_single_attr('UNIT_CODE', approval_dict)
            ))

    @check_and_log('circumstance_dict')
    def _read_circumstance_data(self, circumstance_dict: List[CircumstanceType]) -> None:
        """
        Populates the acrs_circumstances table
        :param circumstance_dict: List of CIRCUMSTANCE tags contained in the CIRCUMSTANCES tag
        """
        for circumstance in circumstance_dict:
            self._insert_or_update(
                Circumstance(
                    CIRCUMSTANCECODE=self.get_single_attr('CIRCUMSTANCECODE', circumstance),
                    CIRCUMSTANCEID=self.get_single_attr('CIRCUMSTANCEID', circumstance),
                    CIRCUMSTANCETYPE=self.get_single_attr('CIRCUMSTANCETYPE', circumstance),
                    PERSONID=self._validate_uniqueidentifier(self.get_single_attr('PERSONID', circumstance)),
                    REPORTNUMBER=self.get_single_attr('REPORTNUMBER', circumstance),
                    VEHICLEID=self._validate_uniqueidentifier(self.get_single_attr('VEHICLEID', circumstance))
                ))

    @check_and_log('citation_dict')
    def _read_citation_data(self, citation_dict: List[CitationCodeType]) -> None:
        """ Populates the acrs_citation_codes table """
        for citation in citation_dict:
            citation_no = self.get_single_attr('CITATIONNUMBER', citation)
            if isinstance(citation_no, str):
                citation_no = citation_no.upper()
            if not citation_no == 'PENDING':
                self._insert_or_update(
                    CitationCode(
                        CITATIONNUMBER=citation_no,
                        PERSONID=self._validate_uniqueidentifier(self.get_single_attr('PERSONID', citation)),
                        REPORTNUMBER=self.get_single_attr('REPORTNUMBER', citation)
                    ))

    @check_and_log('crash_diagram_dict')
    def _read_crash_diagrams_data(self, crash_diagram_dict: CrashDiagramType) -> None:
        """
        Populates the acrs_crash_diagrams table
        :param crash_diagram_dict: OrderedDict from the DIAGRAM tag
        """
        self._insert_or_update(
            CrashDiagram(
                CRASHDIAGRAM=self.get_single_attr('CRASHDIAGRAM', crash_diagram_dict),
                CRASHDIAGRAMNATIVE=self.get_single_attr('CRASHDIAGRAMNATIVE', crash_diagram_dict),
                REPORTNUMBER=self.get_single_attr('REPORTNUMBER', crash_diagram_dict),
            ))

    @check_and_log('ems_dict')
    def _read_ems_data(self, ems_dict: List[EmsType]) -> None:
        """
        Populates the acrs_ems table from the EMSes tag
        :param ems_dict: List of OrderedDicts contained in the EMSes tag
        """
        for ems in ems_dict:
            self._insert_or_update(
                Ems(
                    EMSTRANSPORTATIONTYPE=self.get_single_attr('EMSTRANSPORTATIONTYPE', ems),
                    EMSUNITNUMBER=self.get_single_attr('EMSUNITNUMBER', ems),
                    INJUREDTAKENBY=self.get_single_attr('INJUREDTAKENBY', ems),
                    INJUREDTAKENTO=self.get_single_attr('INJUREDTAKENTO', ems),
                    REPORTNUMBER=self.get_single_attr('REPORTNUMBER', ems)
                ))

    @check_and_log('commvehicle_dict')
    def _read_commercial_vehicle_data(self, commvehicle_dict: CommercialVehicleType) -> None:
        """
        Populates the acrs_commercial_vehicle table
        :param commvehicle_dict: The dictionary of the ACRSVEHICLE
        :return:
        """
        self._insert_or_update(
            CommercialVehicle(
                BODYTYPE=self.get_single_attr('BODYTYPE', commvehicle_dict),
                BUSUSE=self.get_single_attr('BUSUSE', commvehicle_dict),
                CARRIERCLASSIFICATION=self.get_single_attr('CARRIERCLASSIFICATION', commvehicle_dict),
                CITY=self.get_single_attr('CITY', commvehicle_dict),
                CONFIGURATION=self.get_single_attr('CONFIGURATION', commvehicle_dict),
                COUNTRY=self.get_single_attr('COUNTRY', commvehicle_dict),
                DOTNUMBER=self.get_single_attr('DOTNUMBER', commvehicle_dict),
                GVW=self.get_single_attr('GVW', commvehicle_dict),
                HAZMATCLASS=self.get_single_attr('HAZMATCLASS', commvehicle_dict),
                HAZMATNAME=self.get_single_attr('HAZMATNAME', commvehicle_dict),
                HAZMATNUMBER=self.get_single_attr('HAZMATNUMBER', commvehicle_dict),
                HAZMATSPILL=self.get_single_attr('HAZMATSPILL', commvehicle_dict),
                MCNUMBER=self.get_single_attr('MCNUMBER', commvehicle_dict),
                NAME=self.get_single_attr('NAME', commvehicle_dict),
                NUMBEROFAXLES=self.get_single_attr('NUMBEROFAXLES', commvehicle_dict),
                PLACARDVISIBLE=self.get_single_attr('PLACARDVISIBLE', commvehicle_dict),
                POSTALCODE=self.get_single_attr('POSTALCODE', commvehicle_dict),
                STATE=self.get_single_attr('STATE', commvehicle_dict),
                STREET=self.get_single_attr('STREET', commvehicle_dict),
                VEHICLEID=self.get_single_attr('VEHICLEID', commvehicle_dict),
                WEIGHT=self.get_single_attr('WEIGHT', commvehicle_dict),
                WEIGHTUNIT=self.get_single_attr('WEIGHTUNIT', commvehicle_dict)
            ))

    @check_and_log('event_dict')
    def _read_event_data(self, event_dict: List[EventType]) -> None:
        """
        Populates the acrs_events table from the EVENTS tag
        :param event_dict: The dictionary of the ACRSVEHICLE
        """
        for event in event_dict:
            self._insert_or_update(
                Event(
                    EVENTID=self.get_single_attr('EVENTID', event),
                    EVENTSEQUENCE=self.get_single_attr('EVENTSEQUENCE', event),
                    EVENTTYPE=self.get_single_attr('EVENTTYPE', event),
                    VEHICLEID=self._validate_uniqueidentifier(self.get_single_attr('VEHICLEID', event))
                ))

    @check_and_log('pdfreport_dict')
    def _read_pdf_data(self, pdfreport_dict: List[PdfReportDataType]) -> None:
        """
        Populates the acrs_pdf_report table from the PDFREPORTs tag
        :param pdfreport_dict: List of OrderedDicts from the PDFREPORTs tag
        """
        for report in pdfreport_dict:
            self._insert_or_update(
                PdfReport(
                    CHANGEDBY=self.get_single_attr('CHANGEDBY', report),
                    DATESTATUSCHANGED=self.to_datetime_sql(self.get_single_attr('DATESTATUSCHANGED', report)),
                    PDFREPORT1=self.get_single_attr('PDFREPORT1', report),
                    PDF_ID=self.get_single_attr('PDF_ID', report),
                    REPORTNUMBER=self.get_single_attr('REPORTNUMBER', report),
                    STATUS=self.get_single_attr('STATUS', report)
                ))

    @check_and_log('person_dict')
    def _read_acrs_person_data(self, person_dict: List[PersonType]) -> None:
        """
        Processes the ACRSPERSON tag contents
        :param person_dict: OrderedDict from the PERSON, OWNER, PASSENGER, or NONMOTORIST tags
        """
        for person in person_dict:
            self._insert_or_update(
                Person(
                    ADDRESS=self.get_single_attr('ADDRESS', person),
                    CITY=self.get_single_attr('CITY', person),
                    COMPANY=self.get_single_attr('COMPANY', person),
                    COUNTRY=self.get_single_attr('COUNTRY', person),
                    COUNTY=self.get_single_attr('COUNTY', person),
                    DLCLASS=self.get_single_attr('DLCLASS', person),
                    DLNUMBER=self.get_single_attr('DLNUMBER', person),
                    DLSTATE=self.get_single_attr('DLSTATE', person),
                    DOB=self.to_datetime_sql(self.get_single_attr('DOB', person)),
                    FIRSTNAME=self.get_single_attr('FIRSTNAME', person),
                    HOMEPHONE=self.get_single_attr('HOMEPHONE', person),
                    LASTNAME=self.get_single_attr('LASTNAME', person),
                    MIDDLENAME=self.get_single_attr('MIDDLENAME', person),
                    OTHERPHONE=self.get_single_attr('OTHERPHONE', person),
                    PERSONID=self._validate_uniqueidentifier(self.get_single_attr('PERSONID', person)),
                    RACE=self.get_single_attr('RACE', person),
                    REPORTNUMBER=self.get_single_attr('REPORTNUMBER', person),
                    SEX=self.get_single_attr('SEX', person),
                    STATE=self.get_single_attr('STATE', person),
                    ZIP=self.get_single_attr('ZIP', person)
                ))

            if person.get('CITATIONCODES') and person.get('CITATIONCODES', {}).get('CITATIONCODE'):
                self._read_citation_data(person['CITATIONCODES']['CITATIONCODE'])

    @check_and_log('person_dict')
    def _read_person_info_data(
            self,
            person_dict: Union[List[DriverType], List[PassengerType], List[NonMotoristType]]
    ) -> None:
        """
        Populates the acrs_person_info table.
        :param person_dict: Contains the list of OrderedDicts contained in the drivers, passengers and nonmotorists tags
        """
        for person in person_dict:
            report_no = ''
            if person.get('PERSON'):
                self._read_acrs_person_data([person['PERSON']])
                report_no = self.get_single_attr('REPORTNUMBER', person['PERSON']) or ''

            if report_no == '':
                raise AssertionError('No report number')

            person_type = None
            if self.get_single_attr('PEDESTRIANTYPE', person):
                person_type = 'P'
            elif self.get_single_attr('SEAT', person):
                person_type = 'O'
            elif not self.get_single_attr('PEDESTRIANTYPE', person) and not self.get_single_attr('SEAT', person):
                person_type = 'D'

            if person_type is None:
                logger.warning('Unable to determine person_type')

            self._insert_or_update(
                PersonInfo(
                    AIRBAGDEPLOYED=self.get_single_attr('AIRBAGDEPLOYED', person),
                    ALCOHOLTESTINDICATOR=self.get_single_attr('ALCOHOLTESTINDICATOR', person),
                    ALCOHOLTESTTYPE=self.get_single_attr('ALCOHOLTESTTYPE', person),
                    ATFAULT=self.convert_to_bool(self.get_single_attr('ATFAULT', person)),
                    BAC=self.get_single_attr('BAC', person),
                    CONDITION=self.get_single_attr('CONDITION', person),
                    CONTINUEDIRECTION=self.get_single_attr('CONTINUEDIRECTION', person),
                    DRIVERDISTRACTEDBY=self.get_single_attr('DRIVERDISTRACTEDBY', person),
                    DRUGTESTINDICATOR=self.get_single_attr('DRUGTESTINDICATOR', person),
                    DRUGTESTRESULT=self.get_single_attr('DRUGTESTRESULT', person),
                    EJECTION=self.get_single_attr('EJECTION', person),
                    EMSRUNREPORTNUMBER=self.get_single_attr('EMSRUNREPORTNUMBER', person),
                    EMSUNITNUMBER=self.get_single_attr('EMSUNITNUMBER', person),
                    EQUIPMENTPROBLEM=self.get_single_attr('EQUIPMENTPROBLEM', person),
                    GOINGDIRECTION=self.get_single_attr('GOINGDIRECTION', person),
                    HASCDL=self.convert_to_bool(self.get_single_attr('HASCDL', person)),
                    INJURYSEVERITY=self.get_single_attr('INJURYSEVERITY', person),
                    PEDESTRIANACTIONS=self.get_single_attr('PEDESTRIANACTIONS', person),
                    PEDESTRIANLOCATION=self.get_single_attr('PEDESTRIANLOCATION', person),
                    PEDESTRIANMOVEMENT=self.get_single_attr('PEDESTRIANMOVEMENT', person),
                    PEDESTRIANOBEYTRAFFICSIGNAL=self.get_single_attr('PEDESTRIANOBEYTRAFFICSIGNAL', person),
                    PEDESTRIANTYPE=self.get_single_attr('PEDESTRIANTYPE', person),
                    PEDESTRIANVISIBILITY=self.get_single_attr('PEDESTRIANVISIBILITY', person),
                    PERSONID=self._validate_uniqueidentifier(self.get_single_attr('PERSONID', person)),
                    PERSONTYPE=person_type,
                    REPORTNUMBER=report_no,
                    SAFETYEQUIPMENT=self.get_single_attr('SAFETYEQUIPMENT', person),
                    SEAT=self.get_single_attr('SEAT', person),
                    SEATINGLOCATION=self.get_single_attr('SEATINGLOCATION', person),
                    SEATINGROW=self.get_single_attr('SEATINGROW', person),
                    SUBSTANCEUSE=self.get_single_attr('SUBSTANCEUSE', person),
                    UNITNUMBERFIRSTSTRIKE=self.get_single_attr('UNITNUMBERFIRSTSTRIKE', person),
                    VEHICLEID=self._validate_uniqueidentifier(self.get_single_attr('VEHICLEID', person))
                ))

    @check_and_log('reportdoc_dict')
    def _read_report_documents_data(self, reportdoc_dict: List[ReportDocumentType]):
        """Populates the acrs_report_docs table. Currently a stub until we get the schema or example data for this"""

    @check_and_log('reportphotos_dict')
    def _read_report_photos_data(self, reportphotos_dict: List[ReportPhotoType]):
        """Populates the acrs_report_photos table. Currently a stub until we get the schema or example data for this"""

    @check_and_log('roadway_dict')
    def _read_roadway_data(self, roadway_dict: RoadwayType) -> None:
        """
        Populates the acrs_roadway table. Expects the ROADWAY tag contents
        :param roadway_dict: OrderedDict from the ROADWAY tag
        """
        self._insert_or_update(
            Roadway(
                COUNTY=self.get_single_attr('COUNTY', roadway_dict),
                LOGMILE_DIR=self.get_single_attr('LOGMILE_DIR', roadway_dict),
                MILEPOINT=self.get_single_attr('MILEPOINT', roadway_dict),
                MUNICIPAL=self.get_single_attr('MUNICIPAL', roadway_dict),
                MUNICIPAL_AREA_CODE=self.get_single_attr('MUNICIPAL_AREA_CODE', roadway_dict),
                REFERENCE_MUNI=self.get_single_attr('REFERENCE_MUNI', roadway_dict),
                REFERENCE_ROADNAME=self.get_single_attr('REFERENCE_ROADNAME', roadway_dict),
                REFERENCE_ROUTE_NUMBER=self.get_single_attr('REFERENCE_ROUTE_NUMBER', roadway_dict),
                REFERENCE_ROUTE_SUFFIX=self.get_single_attr('REFERENCE_ROUTE_SUFFIX', roadway_dict),
                REFERENCE_ROUTE_TYPE=self.get_single_attr('REFERENCE_ROUTE_TYPE', roadway_dict),
                ROADID=self.get_single_attr('ROADID', roadway_dict),
                ROAD_NAME=self.get_single_attr('ROAD_NAME', roadway_dict),
                ROUTE_NUMBER=self.get_single_attr('ROUTE_NUMBER', roadway_dict),
                ROUTE_SUFFIX=self.get_single_attr('ROUTE_SUFFIX', roadway_dict),
                ROUTE_TYPE=self.get_single_attr('ROUTE_TYPE', roadway_dict)
            ))

    @check_and_log('towed_dict')
    def _read_towed_vehicle_data(self, towed_dict: List[TowedUnitType]) -> None:
        """
        Populates the acrs_towed_unit table
        :param towed_dict: The list of OrderedDicts that comes from the TOWEDUNITs tag
        """
        for towed_unit in towed_dict:
            if towed_unit.get('OWNER'):
                self._read_acrs_person_data([towed_unit['OWNER']])

            self._insert_or_update(
                TowedUnit(
                    INSURANCEPOLICYNUMBER=self.get_single_attr('INSURANCEPOLICYNUMBER', towed_unit),
                    INSURER=self.get_single_attr('INSURER', towed_unit),
                    LICENSEPLATENUMBER=self.get_single_attr('LICENSEPLATENUMBER', towed_unit),
                    LICENSEPLATESTATE=self.get_single_attr('LICENSEPLATESTATE', towed_unit),
                    OWNERID=self._validate_uniqueidentifier(self.get_single_attr('OWNERID', towed_unit)),
                    TOWEDID=self._validate_uniqueidentifier(self.get_single_attr('TOWEDID', towed_unit)),
                    UNITNUMBER=self.get_single_attr('UNITNUMBER', towed_unit),
                    VEHICLEID=self._validate_uniqueidentifier(self.get_single_attr('VEHICLEID', towed_unit)),
                    VEHICLEMAKE=self.get_single_attr('VEHICLEMAKE', towed_unit),
                    VEHICLEMODEL=self.get_single_attr('VEHICLEMODEL', towed_unit),
                    VEHICLEYEAR=self.get_single_attr('VEHICLEYEAR', towed_unit),
                    VIN=self.get_single_attr('VIN', towed_unit)
                ))

    @check_and_log('vehicle_dict')
    def _read_acrs_vehicle_data(self, vehicle_dict: List[VehicleType]) -> None:
        """
        Populates the acrs_vehicles table
        :param vehicle_dict: List of OrderedDicts from the ACRSVEHICLE tag
        """
        for vehicle in vehicle_dict:
            vin = self.get_single_attr('VIN', vehicle)
            vehicle_lookup = VIN(vin)
            if not vehicle_lookup:
                # just to make the rest of the logic work when there is no return
                vehicle_lookup = DecodedVIN({'Make': None, 'Model': None, 'ModelYear': None})

            self._insert_or_update(
                Vehicle(
                    CONTINUEDIRECTION=self.get_single_attr('CONTINUEDIRECTION', vehicle),
                    DAMAGEEXTENT=self.get_single_attr('DAMAGEEXTENT', vehicle),
                    DRIVERLESSVEHICLE=self.convert_to_bool(self.get_single_attr('DRIVERLESSVEHICLE', vehicle)),
                    EMERGENCYMOTORVEHICLEUSE=self.convert_to_bool(
                        self.get_single_attr('EMERGENCYMOTORVEHICLEUSE', vehicle)),
                    FIRE=self.convert_to_bool(self.get_single_attr('FIRE', vehicle)),
                    FIRSTIMPACT=self.get_single_attr('FIRSTIMPACT', vehicle),
                    GOINGDIRECTION=self.get_single_attr('GOINGDIRECTION', vehicle),
                    HITANDRUN=self.convert_to_bool(self.get_single_attr('HITANDRUN', vehicle)),
                    INSURANCEPOLICYNUMBER=self.get_single_attr('INSURANCEPOLICYNUMBER', vehicle),
                    INSURER=self.get_single_attr('INSURER', vehicle),
                    LICENSEPLATENUMBER=self.get_single_attr('LICENSEPLATENUMBER', vehicle),
                    LICENSEPLATESTATE=self.get_single_attr('LICENSEPLATESTATE', vehicle),
                    MAINIMPACT=self.get_single_attr('MAINIMPACT', vehicle),
                    MOSTHARMFULEVENT=self.get_single_attr('MOSTHARMFULEVENT', vehicle),
                    OWNERID=self._validate_uniqueidentifier(self.get_single_attr('OWNERID', vehicle)),
                    PARKEDVEHICLE=self.convert_to_bool(self.get_single_attr('PARKEDVEHICLE', vehicle)),
                    REGISTRATIONEXPIRATIONYEAR=self.get_single_attr('REGISTRATIONEXPIRATIONYEAR', vehicle),
                    REPORTNUMBER=self.get_single_attr('REPORTNUMBER', vehicle),
                    SFVEHICLEINTRANSPORT=self.get_single_attr('SFVEHICLEINTRANSPORT', vehicle),
                    SPEEDLIMIT=self.get_single_attr('SPEEDLIMIT', vehicle),
                    TOWEDUNITTYPE=self.get_single_attr('TOWEDUNITTYPE', vehicle),
                    UNITNUMBER=self.get_single_attr('UNITNUMBER', vehicle),
                    VEHICLEBODYTYPE=self.get_single_attr('VEHICLEBODYTYPE', vehicle),
                    VEHICLEID=self._validate_uniqueidentifier(self.get_single_attr('VEHICLEID', vehicle)),
                    VEHICLEMAKE=getattr(vehicle_lookup, 'Make') or self.get_single_attr('VEHICLEMAKE', vehicle),
                    VEHICLEMODEL=getattr(vehicle_lookup, 'Model') or self.get_single_attr('VEHICLEMODEL', vehicle),
                    VEHICLEMOVEMENT=self.get_single_attr('VEHICLEMOVEMENT', vehicle),
                    VEHICLEREMOVEDBY=self.get_single_attr('VEHICLEREMOVEDBY', vehicle),
                    VEHICLEREMOVEDTO=self.get_single_attr('VEHICLEREMOVEDTO', vehicle),
                    VEHICLETOWEDAWAY=self.get_single_attr('VEHICLETOWEDAWAY', vehicle),
                    VEHICLEYEAR=getattr(vehicle_lookup, 'ModelYear') or self.get_single_attr('VEHICLEYEAR', vehicle),
                    VIN=vin
                ))

            if vehicle.get('DAMAGEDAREAs') and vehicle.get('DAMAGEDAREAs', {}).get('DAMAGEDAREA'):
                self._read_damaged_areas_data(vehicle['DAMAGEDAREAs']['DAMAGEDAREA'])

            if vehicle.get('DRIVERs') and vehicle.get('DRIVERs', {}).get('DRIVER'):
                self._read_person_info_data(vehicle['DRIVERs']['DRIVER'])

            if vehicle.get('PASSENGERs') and vehicle.get('PASSENGERs', {}).get('PASSENGER'):
                self._read_person_info_data(vehicle['PASSENGERs']['PASSENGER'])

            if vehicle.get('OWNER'):
                self._read_acrs_person_data([vehicle['OWNER']])

            if vehicle.get('COMMERCIALVEHICLE'):
                self._read_commercial_vehicle_data(vehicle['COMMERCIALVEHICLE'])

            if vehicle.get('EVENTS') and vehicle.get('EVENTS', {}).get('EVENT'):
                self._read_event_data(vehicle['EVENTS']['EVENT'])

            if vehicle.get('VEHICLEUSEs') and vehicle.get('VEHICLEUSEs', {}).get('VEHICLEUSE'):
                self._read_acrs_vehicle_use_data(vehicle.get('VEHICLEUSEs', {})['VEHICLEUSE'])

            if vehicle.get('TOWEDUNITs') and vehicle.get('TOWEDUNITs', {}).get('TOWEDUNIT'):
                self._read_towed_vehicle_data(vehicle['TOWEDUNITs']['TOWEDUNIT'])

    @check_and_log('vehicleuse_dict')
    def _read_acrs_vehicle_use_data(self, vehicleuse_dict: List[VehicleUseType]) -> None:
        """
        Populates acrs_vehicle_use table
        :param vehicleuse_dict: The dictionary of the ACRSVEHICLE from the VEHICLEUSEs tag
        """
        for vehicleuse in vehicleuse_dict:
            self._insert_or_update(
                VehicleUse(
                    ID=self.get_single_attr('ID', vehicleuse),
                    VEHICLEID=self._validate_uniqueidentifier(self.get_single_attr('VEHICLEID', vehicleuse)),
                    VEHICLEUSECODE=self.get_single_attr('VEHICLEUSECODE', vehicleuse)
                ))

    @check_and_log('damaged_dict')
    def _read_damaged_areas_data(self, damaged_dict: List[DamagedAreaType]) -> None:
        """
        Populates the acrs_damaged_areas table. Expects to be passed the OrderedDict of DAMAGEDAREAs
        :param damaged_dict: The dictionary of the ACRSVEHICLE
        """
        for damagedarea in damaged_dict:
            self._insert_or_update(
                DamagedArea(
                    DAMAGEID=self.get_single_attr('DAMAGEID', damagedarea),
                    IMPACTTYPE=self.get_single_attr('IMPACTTYPE', damagedarea),
                    VEHICLEID=self._validate_uniqueidentifier(self.get_single_attr('VEHICLEID', damagedarea))
                ))

    @check_and_log('witness_dict')
    def _read_witness_data(self, witness_dict: List[WitnessType]) -> None:
        """
        Populates the acrs_witnesses table
        :param witness_dict: The list of OrderedDicts from the WITNESSes tag
        """
        for witness in witness_dict:
            if witness.get('PERSON'):
                self._read_acrs_person_data([witness['PERSON']])

            self._insert_or_update(
                Witness(
                    PERSONID=self._validate_uniqueidentifier(self.get_single_attr('PERSONID', witness)),
                    REPORTNUMBER=self.get_single_attr('REPORTNUMBER', witness)
                ))

    @staticmethod
    def is_element_nil(element: Optional[OrderedDict]) -> bool:
        """
        Checks if a tag is nil, because xmltodict returns an ordereddict with a nil element
        :param element: (ordereddict) The ordereddict to check for nil
        :return: True if its nil, False otherwise
        """
        if not element:
            return True

        if not isinstance(element, OrderedDict):
            return False

        return (len(element) == 1) and \
            isinstance(element, OrderedDict) and \
            element.get('@i:nil') == 'true'

    @staticmethod
    def convert_to_bool(val: Union[None, str, bool]) -> Optional[int]:
        """
        Converts the XML style 'y', 'n', and 'u' (unknown) to a bit value
        :param val: Value to convert to a bool
        :return: Either True, False, or None (if the input was empty or 'u' for unknown)
        """
        if val is None:
            return None

        if isinstance(val, bool):
            return int(val)

        val = val.lower()
        if val not in ['y', 'n', 'u']:
            raise AssertionError('Expected y or n and got {}'.format(val))
        if val == 'u':
            return None
        return int(bool(val == 'y'))

    @staticmethod
    def _validate_uniqueidentifier(uid: Optional[str]) -> Optional[str]:
        """Checks for null uniqueidentifiers"""
        if not uid:
            return None
        return uid

    def get_single_attr(self, tag: str, crash_data: Mapping) -> Optional[str]:
        """
        Gets a single element from the XML document we loaded. It errors if there are more that one of those type of tag
        :param tag:
        :param crash_data:
        :return:
        """
        if crash_data is None:
            return None

        if crash_data.get(tag) is None or self.is_element_nil(crash_data.get(tag)):
            return None

        if not isinstance(crash_data.get(tag), str) and isinstance(crash_data.get(tag), collections.abc.Iterable):
            raise AssertionError('Expected {} to have only a single element'.format(tag))
        return crash_data.get(tag)

    @staticmethod
    def to_datetime_sql(dt_str: Optional[str]) -> Optional[datetime]:
        """Converts a date string to the pandas starndard format, and returns None (instead of NaT) if invalid"""
        try:
            return to_datetime(dt_str)
        except OutOfBoundsDatetime:
            return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse ACRS xml crash data files in the specified directory, and '
                                                 'insert them into a database')
    parser.add_argument('-c', '--conn_str', default='sqlite:///crash.db',
                              help='Custom database connection string (default: sqlite:///crash.db)')
    parser.add_argument('-d', '--directory', help='Directory containing ACRS XML files to parse. If quotes are '
                                                  'required in the path (if there are spaces), use double quotes.')
    parser.add_argument('-f', '--file',
                              help='Path to a single file to process. If quotes are required in the path '
                                   '(if there are spaces), use double quotes.')
    parser.add_argument('-s', '--sanitize', action='store_true',
                              help='Sanitize the data from PII while being imported')

    args = parser.parse_args()

    cls = CrashDataReader(args.conn_str)
    if not (args.directory or args.file):
        logger.error('Must specify either a directory or file to process')
    if args.directory:
        cls.read_crash_data(dir_name=args.directory, sanitize=args.sanitize)
    if args.file:
        if not os.path.exists(args.file):
            logger.error('File does not exist: {}'.format(args.file))
        cls.read_crash_data(file_name=args.file, sanitize=args.sanitize)
