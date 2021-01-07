"""Processes unprocessed data in the network share that holds crash data"""
# pylint:disable=too-many-lines
#
import inspect
import logging
import os
import shutil
import traceback
from collections import OrderedDict
from typing import List, Mapping, Optional, Sequence, Union

import xmltodict  # type: ignore
from pandas import to_datetime  # type: ignore
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from trafficstat.crash_data_types import ApprovalDataType, CrashDataType, CircumstanceType, CitationCodeType, \
    CommercialVehicleType, CrashDiagramType, DamagedAreaType, DriverType, EmsType, EventType, NonMotoristType, \
    PassengerType, PdfReportDataType, PersonType, ReportDocumentType, ReportPhotoType, RoadwayType, SqlExecuteType, \
    TowedUnitType, VehicleType, VehicleUseType, WitnessType
from trafficstat.crash_data_types import Crashes, Base

# The 'unsubscriptable-object' disable is because of issue https://github.com/PyCQA/pylint/issues/3882 with subscripting
# Optional. When thats fixed, we can remove those disables.

LOGGER = logging.getLogger(__name__)


def check_and_log(check_dict: str):
    """Logs the function entry, and checks the check_dict argument for nullness"""

    def _check_and_log(func):
        def wrapper(*args, **kwargs):
            logging.info("Entering %s", func.__name__)

            # handle positional or keyword args
            args_name = inspect.getfullargspec(func)[0]
            args_dict = dict(zip(args_name, args))
            args_dict.update(**kwargs)
            self = args_dict['self']

            if self.is_element_nil(args_dict[check_dict]):
                LOGGER.warning('No data')
                return False

            return func(*args, **kwargs)

        return wrapper

    return _check_and_log


class CrashDataReader:
    """ Reads a directory of ACRS crash data files"""

    def __init__(self, path: str = '//balt-fileld-srv.baltimore.city/GIS/DOT-BPD', conn_str='sqlite:///crash.db'):
        """
        Reads a directory of XML ACRS crash files, and returns an iterator of the parsed data
        :param path: Path to search for XML files
        :param path:
        """
        self.root: dict = {}
        self.engine = create_engine(conn_str, echo=True, future=True)

        with self.engine.begin() as connection:
            Base.metadata.create_all(connection)

        if path:
            processed_folder = os.path.join(path, 'processed')
            if not os.path.exists(processed_folder):
                os.mkdir(processed_folder)

            for acrs_file in os.listdir(path):
                if acrs_file.endswith('.xml'):
                    self.read_crash_data(os.path.join(path, acrs_file), processed_folder)

    def _read_file(self, file_name: str) -> CrashDataType:
        with open(file_name, encoding='utf-8') as acrs_file:
            crash_file = acrs_file.read()

        # Some of these files have non ascii at the beginning that causes parse errors
        offset = crash_file.find('<?xml')
        self.root = xmltodict.parse(crash_file[offset:],
                                    force_list={'ACRSPERSON', 'ACRSVEHICLE', 'CIRCUMSTANCE', 'CITATIONCODE',
                                                'DAMAGEDAREA', 'DRIVER', 'EMS', 'EVENT', 'NONMOTORIST', 'PASSENGER',
                                                'PDFREPORT', 'REPORTDOCUMENT', 'REPORTPHOTO', 'TOWEDUNIT', 'VEHICLEUSE',
                                                'WITNESS'})

        return self.root['REPORT']

    def read_crash_data(self, file_name: str,  # pylint:disable=too-many-branches
                        processed_dir: Optional[
                            str]) -> None:  # pylint:disable=unsubscriptable-object ; see comment at top
        """
        Reads the ACRS crash data files
        :param processed_dir: Directory to move the ACRS file after being processed
        :param file_name: Full path to the file to process
        :return: True if the file was inserted into the database, false if there was an error
        """
        LOGGER.info('Processing %s', file_name)
        crash_dict = self._read_file(file_name)

        if crash_dict.get('APPROVALDATA'):
            self._read_approval_data(crash_dict['APPROVALDATA'])

        if crash_dict.get('CIRCUMSTANCES') and crash_dict.get('CIRCUMSTANCES', {}).get('CIRCUMSTANCE'):
            self._read_circumstance_data(crash_dict['CIRCUMSTANCES']['CIRCUMSTANCE'])

        if crash_dict.get('DIAGRAM'):
            self._read_crash_diagrams_data(crash_dict['DIAGRAM'])

        if crash_dict.get('EMSes') and crash_dict.get('EMSes', {}).get('EMS'):
            self._read_ems_data(crash_dict['EMSes']['EMS'])

        if crash_dict.get('PDFREPORTs') and crash_dict.get('PDFREPORTs', {}).get('PDFREPORT'):
            self._read_pdf_data(crash_dict['PDFREPORTs']['PDFREPORT'])

        if crash_dict.get('REPORTDOCUMENTs') and crash_dict.get('REPORTDOCUMENTs', {}).get('REPORTDOCUMENT'):
            self._read_report_documents_data(crash_dict['REPORTDOCUMENTs']['REPORTDOCUMENT'])

        if crash_dict.get('REPORTPHOTOes') and crash_dict.get('REPORTPHOTOes', {}).get('REPORTPHOTO'):
            self._read_report_photos_data(crash_dict['REPORTPHOTOes']['REPORTPHOTO'])

        if crash_dict.get('ROADWAY'):
            self._read_roadway_data(crash_dict['ROADWAY'])

        if crash_dict.get('People') and crash_dict.get('People', {}).get('ACRSPERSON'):
            self._read_acrs_person_data(crash_dict['People']['ACRSPERSON'])

        if crash_dict.get('VEHICLEs') and crash_dict.get('VEHICLEs', {}).get('ACRSVEHICLE'):
            self._read_acrs_vehicle_data(crash_dict['VEHICLEs']['ACRSVEHICLE'])

        if crash_dict.get('NONMOTORISTs') and crash_dict.get('NONMOTORISTs', {}).get('NONMOTORIST'):
            self._read_person_info_data(crash_dict['NONMOTORISTs']['NONMOTORIST'])

        if crash_dict.get('WITNESSes') and crash_dict.get('WITNESSes', {}).get('WITNESS'):
            self._read_witness_data(crash_dict['WITNESSes']['WITNESS'])

        self._read_main_crash_data(crash_dict)

        if processed_dir:
            self._file_move(file_name, processed_dir)

    @staticmethod
    def _file_move(file_name, processed_dir):
        """File copy with automatic renaming during retry"""
        i = 0
        while i < 5:
            # retry copy operation up to 5 times
            try:
                if i == 0:
                    shutil.move(file_name, processed_dir)
                else:
                    dst_filename = '{}_{}'.format(os.path.join(processed_dir, os.path.basename(file_name)), i)
                    shutil.move(file_name, dst_filename)
                break
            except shutil.Error:
                i += 1
                if i >= 5:
                    LOGGER.error('Error moving file. It will not be moved to the processed directory: %s', file_name)

    @check_and_log('crash_dict')
    def _read_main_crash_data(self, crash_dict: CrashDataType) -> bool:
        """ Populates the acrs_crashes table """
        add = Crashes(
            ACRSREPORTTIMESTAMP=self.get_single_attr('ACRSREPORTTIMESTAMP', crash_dict),
            AGENCYIDENTIFIER=self.get_single_attr('AGENCYIDENTIFIER', crash_dict),
            AGENCYNAME=self.get_single_attr('AGENCYNAME', crash_dict),
            AREA=self.get_single_attr('AREA', crash_dict),
            COLLISIONTYPE=self.get_single_attr('COLLISIONTYPE', crash_dict),
            CONMAINCLOSURE=self.get_single_attr('CONMAINCLOSURE', crash_dict),
            CONMAINLOCATION=self.get_single_attr('CONMAINLOCATION', crash_dict),
            CONMAINWORKERSPRESENT=self._convert_to_bool(self.get_single_attr('CONMAINWORKERSPRESENT', crash_dict)),
            CONMAINZONE=self.get_single_attr('CONMAINZONE', crash_dict),
            CRASHDATE=self._convert_to_date(self.get_single_attr('CRASHDATE', crash_dict)),
            CRASHTIME=self.get_single_attr('CRASHTIME', crash_dict),
            CURRENTASSIGNMENT=self.get_single_attr('CURRENTASSIGNMENT', crash_dict),
            CURRENTGROUP=self.get_single_attr('CURRENTGROUP', crash_dict),
            DEFAULTASSIGNMENT=self.get_single_attr('DEFAULTASSIGNMENT', crash_dict),
            DEFAULTGROUP=self.get_single_attr('DEFAULTGROUP', crash_dict),
            DOCTYPE=self.get_single_attr('DOCTYPE', crash_dict),
            FIXEDOBJECTSTRUCK=self.get_single_attr('FIXEDOBJECTSTRUCK', crash_dict),
            HARMFULEVENTONE=self.get_single_attr('HARMFULEVENTONE', crash_dict),
            HARMFULEVENTTWO=self.get_single_attr('HARMFULEVENTTWO', crash_dict),
            HITANDRUN=self._convert_to_bool(self.get_single_attr('HITANDRUN', crash_dict)),
            INSERTDATE=self.get_single_attr('INSERTDATE', crash_dict),
            INTERCHANGEAREA=self.get_single_attr('INTERCHANGEAREA', crash_dict),
            INTERCHANGEIDENTIFICATION=self.get_single_attr('INTERCHANGEIDENTIFICATION', crash_dict),
            INTERSECTIONTYPE=self.get_single_attr('INTERSECTIONTYPE', crash_dict),
            INVESTIGATINGOFFICERUSERNAME=self.get_single_attr('INVESTIGATINGOFFICERUSERNAME', crash_dict),
            INVESTIGATOR=self.get_single_attr('INVESTIGATOR', crash_dict),
            JUNCTION=self.get_single_attr('JUNCTION', crash_dict),
            LANEDIRECTION=self.get_single_attr('LANEDIRECTION', crash_dict),
            LANENUMBER=self.get_single_attr('LANENUMBER', crash_dict),
            LANETYPE=self.get_single_attr('LANETYPE', crash_dict),
            LATITUDE=self.get_single_attr('LATITUDE', crash_dict),
            LIGHT=self.get_single_attr('LIGHT', crash_dict),
            LOCALCASENUMBER=self.get_single_attr('LOCALCASENUMBER', crash_dict),
            LOCALCODES=self.get_single_attr('LOCALCODES', crash_dict),
            LONGITUDE=self.get_single_attr('LONGITUDE', crash_dict),
            MILEPOINTDIRECTION=self.get_single_attr('MILEPOINTDIRECTION', crash_dict),
            MILEPOINTDISTANCE=self.get_single_attr('MILEPOINTDISTANCE', crash_dict),
            MILEPOINTDISTANCEUNITS=self.get_single_attr('MILEPOINTDISTANCEUNITS', crash_dict),
            NARRATIVE=self.get_single_attr('NARRATIVE', crash_dict),
            NONTRAFFIC=self._convert_to_bool(self.get_single_attr('NONTRAFFIC', crash_dict)),
            NUMBEROFLANES=self.get_single_attr('NUMBEROFLANES', crash_dict),
            OFFROADDESCRIPTION=self.get_single_attr('OFFROADDESCRIPTION', crash_dict),
            PHOTOSTAKEN=self._convert_to_bool(self.get_single_attr('PHOTOSTAKEN', crash_dict)),
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
            SUPERVISORYDATE=self.get_single_attr('SUPERVISORYDATE', crash_dict),
            SURFACECONDITION=self.get_single_attr('SURFACECONDITION', crash_dict),
            TRAFFICCONTROL=self.get_single_attr('TRAFFICCONTROL', crash_dict),
            TRAFFICCONTROLFUNCTIONING=self._convert_to_bool(
                self.get_single_attr('TRAFFICCONTROLFUNCTIONING', crash_dict)),
            UPDATEDATE=self.get_single_attr('UPDATEDATE', crash_dict),
            UPLOADVERSION=self.get_single_attr('UPLOADVERSION', crash_dict),
            VERSIONNUMBER=self.get_single_attr('VERSIONNUMBER', crash_dict),
            WEATHER=self.get_single_attr('WEATHER', crash_dict)
        )

        ret: bool = True
        if data:
            ret = self._safe_sql_execute(
                """
                MERGE acrs_crashes USING (
                VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                     ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ) AS vals (ACRSREPORTTIMESTAMP, AGENCYIDENTIFIER, AGENCYNAME, AREA, COLLISIONTYPE, CONMAINCLOSURE,
                CONMAINLOCATION, CONMAINWORKERSPRESENT, CONMAINZONE, CRASHDATE, CRASHTIME, CURRENTASSIGNMENT,
                CURRENTGROUP, DEFAULTASSIGNMENT, DEFAULTGROUP, DOCTYPE, FIXEDOBJECTSTRUCK, HARMFULEVENTONE,
                HARMFULEVENTTWO, HITANDRUN, INSERTDATE, INTERCHANGEAREA, INTERCHANGEIDENTIFICATION, INTERSECTIONTYPE,
                INVESTIGATINGOFFICERUSERNAME, INVESTIGATOR, JUNCTION, LANEDIRECTION, LANENUMBER, LANETYPE, LATITUDE,
                LIGHT, LOCALCASENUMBER, LOCALCODES, LONGITUDE, MILEPOINTDIRECTION, MILEPOINTDISTANCE,
                MILEPOINTDISTANCEUNITS, NARRATIVE, NONTRAFFIC, NUMBEROFLANES, OFFROADDESCRIPTION, PHOTOSTAKEN, RAMP,
                REPORTCOUNTYLOCATION, REPORTNUMBER, REPORTTYPE, ROADALIGNMENT, ROADCONDITION, ROADDIVISION, ROADGRADE,
                ROADID, SCHOOLBUSINVOLVEMENT, STATEGOVERNMENTPROPERTYNAME, SUPERVISOR, SUPERVISORUSERNAME,
                SUPERVISORYDATE, SURFACECONDITION, TRAFFICCONTROL, TRAFFICCONTROLFUNCTIONING, UPDATEDATE, UPLOADVERSION,
                VERSIONNUMBER, WEATHER)
                ON (acrs_crashes.REPORTNUMBER = vals.REPORTNUMBER)
                WHEN MATCHED THEN
                    UPDATE SET
                    ACRSREPORTTIMESTAMP = vals.ACRSREPORTTIMESTAMP,
                    AGENCYIDENTIFIER = vals.AGENCYIDENTIFIER,
                    AGENCYNAME = vals.AGENCYNAME,
                    AREA = vals.AREA,
                    COLLISIONTYPE = vals.COLLISIONTYPE,
                    CONMAINCLOSURE = vals.CONMAINCLOSURE,
                    CONMAINLOCATION = vals.CONMAINLOCATION,
                    CONMAINWORKERSPRESENT = vals.CONMAINWORKERSPRESENT,
                    CONMAINZONE = vals.CONMAINZONE,
                    CRASHDATE = vals.CRASHDATE,
                    CRASHTIME = vals.CRASHTIME,
                    CURRENTASSIGNMENT = vals.CURRENTASSIGNMENT,
                    CURRENTGROUP = vals.CURRENTGROUP,
                    DEFAULTASSIGNMENT = vals.DEFAULTASSIGNMENT,
                    DEFAULTGROUP = vals.DEFAULTGROUP,
                    DOCTYPE = vals.DOCTYPE,
                    FIXEDOBJECTSTRUCK = vals.FIXEDOBJECTSTRUCK,
                    HARMFULEVENTONE = vals.HARMFULEVENTONE,
                    HARMFULEVENTTWO = vals.HARMFULEVENTTWO,
                    HITANDRUN = vals.HITANDRUN,
                    INSERTDATE = vals.INSERTDATE,
                    INTERCHANGEAREA = vals.INTERCHANGEAREA,
                    INTERCHANGEIDENTIFICATION = vals.INTERCHANGEIDENTIFICATION,
                    INTERSECTIONTYPE = vals.INTERSECTIONTYPE,
                    INVESTIGATINGOFFICERUSERNAME = vals.INVESTIGATINGOFFICERUSERNAME,
                    INVESTIGATOR = vals.INVESTIGATOR,
                    JUNCTION = vals.JUNCTION,
                    LANEDIRECTION = vals.LANEDIRECTION,
                    LANENUMBER = vals.LANENUMBER,
                    LANETYPE = vals.LANETYPE,
                    LATITUDE = vals.LATITUDE,
                    LIGHT = vals.LIGHT,
                    LOCALCASENUMBER = vals.LOCALCASENUMBER,
                    LOCALCODES = vals.LOCALCODES,
                    LONGITUDE = vals.LONGITUDE,
                    MILEPOINTDIRECTION = vals.MILEPOINTDIRECTION,
                    MILEPOINTDISTANCE = vals.MILEPOINTDISTANCE,
                    MILEPOINTDISTANCEUNITS = vals.MILEPOINTDISTANCEUNITS,
                    NARRATIVE = vals.NARRATIVE,
                    NONTRAFFIC = vals.NONTRAFFIC,
                    NUMBEROFLANES = vals.NUMBEROFLANES,
                    OFFROADDESCRIPTION = vals.OFFROADDESCRIPTION,
                    PHOTOSTAKEN = vals.PHOTOSTAKEN,
                    RAMP = vals.RAMP,
                    REPORTCOUNTYLOCATION = vals.REPORTCOUNTYLOCATION,
                    REPORTTYPE = vals.REPORTTYPE,
                    ROADALIGNMENT = vals.ROADALIGNMENT,
                    ROADCONDITION = vals.ROADCONDITION,
                    ROADDIVISION = vals.ROADDIVISION,
                    ROADGRADE = vals.ROADGRADE,
                    ROADID = vals.ROADID,
                    SCHOOLBUSINVOLVEMENT = vals.SCHOOLBUSINVOLVEMENT,
                    STATEGOVERNMENTPROPERTYNAME = vals.STATEGOVERNMENTPROPERTYNAME,
                    SUPERVISOR = vals.SUPERVISOR,
                    SUPERVISORUSERNAME = vals.SUPERVISORUSERNAME,
                    SUPERVISORYDATE = vals.SUPERVISORYDATE,
                    SURFACECONDITION = vals.SURFACECONDITION,
                    TRAFFICCONTROL = vals.TRAFFICCONTROL,
                    TRAFFICCONTROLFUNCTIONING = vals.TRAFFICCONTROLFUNCTIONING,
                    UPDATEDATE = vals.UPDATEDATE,
                    UPLOADVERSION = vals.UPLOADVERSION,
                    VERSIONNUMBER = vals.VERSIONNUMBER,
                    WEATHER = vals.WEATHER
                WHEN NOT MATCHED THEN
                    INSERT (ACRSREPORTTIMESTAMP, AGENCYIDENTIFIER, AGENCYNAME, AREA, COLLISIONTYPE, CONMAINCLOSURE,
                        CONMAINLOCATION, CONMAINWORKERSPRESENT, CONMAINZONE, CRASHDATE, CRASHTIME, CURRENTASSIGNMENT,
                        CURRENTGROUP, DEFAULTASSIGNMENT, DEFAULTGROUP, DOCTYPE, FIXEDOBJECTSTRUCK, HARMFULEVENTONE,
                        HARMFULEVENTTWO, HITANDRUN, INSERTDATE, INTERCHANGEAREA, INTERCHANGEIDENTIFICATION,
                        INTERSECTIONTYPE, INVESTIGATINGOFFICERUSERNAME, INVESTIGATOR, JUNCTION, LANEDIRECTION,
                        LANENUMBER, LANETYPE, LATITUDE, LIGHT, LOCALCASENUMBER, LOCALCODES, LONGITUDE,
                        MILEPOINTDIRECTION, MILEPOINTDISTANCE, MILEPOINTDISTANCEUNITS, NARRATIVE, NONTRAFFIC,
                        NUMBEROFLANES, OFFROADDESCRIPTION, PHOTOSTAKEN, RAMP, REPORTCOUNTYLOCATION, REPORTNUMBER,
                        REPORTTYPE, ROADALIGNMENT, ROADCONDITION, ROADDIVISION, ROADGRADE, ROADID, SCHOOLBUSINVOLVEMENT,
                        STATEGOVERNMENTPROPERTYNAME, SUPERVISOR, SUPERVISORUSERNAME, SUPERVISORYDATE, SURFACECONDITION,
                        TRAFFICCONTROL, TRAFFICCONTROLFUNCTIONING, UPDATEDATE, UPLOADVERSION, VERSIONNUMBER, WEATHER)
                    VALUES (vals.ACRSREPORTTIMESTAMP, vals.AGENCYIDENTIFIER, vals.AGENCYNAME, vals.AREA,
                        vals.COLLISIONTYPE, vals.CONMAINCLOSURE, vals.CONMAINLOCATION, vals.CONMAINWORKERSPRESENT,
                        vals.CONMAINZONE, vals.CRASHDATE, vals.CRASHTIME, vals.CURRENTASSIGNMENT, vals.CURRENTGROUP,
                        vals.DEFAULTASSIGNMENT, vals.DEFAULTGROUP, vals.DOCTYPE, vals.FIXEDOBJECTSTRUCK,
                        vals.HARMFULEVENTONE, vals.HARMFULEVENTTWO, vals.HITANDRUN, vals.INSERTDATE,
                        vals.INTERCHANGEAREA, vals.INTERCHANGEIDENTIFICATION, vals.INTERSECTIONTYPE,
                        vals.INVESTIGATINGOFFICERUSERNAME, vals.INVESTIGATOR, vals.JUNCTION, vals.LANEDIRECTION,
                        vals.LANENUMBER, vals.LANETYPE, vals.LATITUDE, vals.LIGHT, vals.LOCALCASENUMBER,
                        vals.LOCALCODES, vals.LONGITUDE, vals.MILEPOINTDIRECTION, vals.MILEPOINTDISTANCE,
                        vals.MILEPOINTDISTANCEUNITS, vals.NARRATIVE, vals.NONTRAFFIC, vals.NUMBEROFLANES,
                        vals.OFFROADDESCRIPTION, vals.PHOTOSTAKEN, vals.RAMP, vals.REPORTCOUNTYLOCATION,
                        vals.REPORTNUMBER, vals.REPORTTYPE, vals.ROADALIGNMENT, vals.ROADCONDITION, vals.ROADDIVISION,
                        vals.ROADGRADE, vals.ROADID, vals.SCHOOLBUSINVOLVEMENT, vals.STATEGOVERNMENTPROPERTYNAME,
                        vals.SUPERVISOR, vals.SUPERVISORUSERNAME, vals.SUPERVISORYDATE, vals.SURFACECONDITION,
                        vals.TRAFFICCONTROL, vals.TRAFFICCONTROLFUNCTIONING, vals.UPDATEDATE, vals.UPLOADVERSION,
                        vals.VERSIONNUMBER, vals.WEATHER);
                """, data
            )

        return ret

    @check_and_log('approval_dict')
    def _read_approval_data(self, approval_dict: ApprovalDataType) -> bool:
        """
        Populates the acrs_approval table
        :param approval_dict: The ordereddict contained in the APPROVALDATA tag
        """
        data = [
            self.get_single_attr('AGENCY', approval_dict),
            self.get_single_attr('APPROVALDATE', approval_dict),
            self.get_single_attr('CADSENT', approval_dict),
            self.get_single_attr('CADSENT_DATE', approval_dict),
            self.get_single_attr('CC_NUMBER', approval_dict),
            self.get_single_attr('DATE_INITIATED2', approval_dict),
            self.get_single_attr('GROUP_NUMBER', approval_dict),
            self.get_single_attr('HISTORICALAPPROVALDATA', approval_dict),
            self.get_single_attr('INCIDENT_DATE', approval_dict),
            self.get_single_attr('INVESTIGATOR', approval_dict),
            self.get_single_attr('REPORT_TYPE', approval_dict),
            self.get_single_attr('SEQ_GUID', approval_dict),
            self.get_single_attr('STATUS_CHANGE_DATE', approval_dict),
            self.get_single_attr('STATUS_ID', approval_dict),
            self.get_single_attr('STEP_NUMBER', approval_dict),
            self.get_single_attr('TR_USERNAME', approval_dict),
            self.get_single_attr('UNIT_CODE', approval_dict)
        ]

        ret: bool = True
        if data:
            ret = self._safe_sql_execute(
                """
                MERGE acrs_approval USING (
                VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ) AS vals (AGENCY, DATE, CADSENT, CADSENT_DATE, CC_NUMBER, DATE_INITIATED2, GROUP_NUMBER,
                HISTORICALAPPROVALDATA, INCIDENT_DATE, INVESTIGATOR, REPORT_TYPE, SEQ_GUID, STATUS_CHANGE_DATE,
                STATUS_ID, STEP_NUMBER, TR_USERNAME, UNIT_CODE)
                ON (acrs_approval.SEQ_GUID = vals.SEQ_GUID AND
                    acrs_approval.CC_NUMBER = vals.CC_NUMBER)
                WHEN MATCHED THEN
                    UPDATE SET
                    AGENCY = vals.AGENCY,
                    DATE = vals.DATE,
                    CADSENT = vals.CADSENT,
                    CADSENT_DATE = vals.CADSENT_DATE,
                    DATE_INITIATED2 = vals.DATE_INITIATED2,
                    GROUP_NUMBER = vals.GROUP_NUMBER,
                    HISTORICALAPPROVALDATA = vals.HISTORICALAPPROVALDATA,
                    INCIDENT_DATE = vals.INCIDENT_DATE,
                    INVESTIGATOR = vals.INVESTIGATOR,
                    REPORT_TYPE = vals.REPORT_TYPE,
                    STATUS_CHANGE_DATE = vals.STATUS_CHANGE_DATE,
                    STATUS_ID = vals.STATUS_ID,
                    STEP_NUMBER = vals.STEP_NUMBER,
                    TR_USERNAME = vals.TR_USERNAME,
                    UNIT_CODE = vals.UNIT_CODE
                WHEN NOT MATCHED THEN
                    INSERT (AGENCY, DATE, CADSENT, CADSENT_DATE, CC_NUMBER, DATE_INITIATED2, GROUP_NUMBER,
                    HISTORICALAPPROVALDATA, INCIDENT_DATE, INVESTIGATOR, REPORT_TYPE, SEQ_GUID, STATUS_CHANGE_DATE,
                    STATUS_ID, STEP_NUMBER, TR_USERNAME, UNIT_CODE)
                    VALUES (vals.AGENCY, vals.DATE, vals.CADSENT, vals.CADSENT_DATE, vals.CC_NUMBER,
                    vals.DATE_INITIATED2, vals.GROUP_NUMBER, vals.HISTORICALAPPROVALDATA, vals.INCIDENT_DATE,
                    vals.INVESTIGATOR, vals.REPORT_TYPE, vals.SEQ_GUID, vals.STATUS_CHANGE_DATE, vals.STATUS_ID,
                    vals.STEP_NUMBER, vals.TR_USERNAME, vals.UNIT_CODE);
                """, data
            )

        return ret

    @check_and_log('circumstance_dict')
    def _read_circumstance_data(self, circumstance_dict: List[
        CircumstanceType]) -> bool:  # pylint:disable=unsubscriptable-object ; see comment at top
        """
        Populates the acrs_circumstances table
        :param circumstance_dict: List of CIRCUMSTANCE tags contained in the CIRCUMSTANCES tag
        """
        data = []
        for circumstance in circumstance_dict:
            data.append((
                self.get_single_attr('CIRCUMSTANCECODE', circumstance),
                self.get_single_attr('CIRCUMSTANCEID', circumstance),
                self.get_single_attr('CIRCUMSTANCETYPE', circumstance),
                self._validate_uniqueidentifier(self.get_single_attr('PERSONID', circumstance)),
                self.get_single_attr('REPORTNUMBER', circumstance),
                self._validate_uniqueidentifier(self.get_single_attr('VEHICLEID', circumstance))
            ))

        ret: bool = True
        if data:
            ret = self._safe_sql_executemany(
                """
                MERGE acrs_circumstances USING (
                VALUES
                    (?, ?, ?, ?, ?, ?)
                ) as vals (CIRCUMSTANCECODE, CIRCUMSTANCEID, CIRCUMSTANCETYPE, PERSONID, REPORTNUMBER, VEHICLEID)
                ON (acrs_circumstances.CIRCUMSTANCEID = vals.CIRCUMSTANCEID AND
                    acrs_circumstances.REPORTNUMBER = vals.REPORTNUMBER)
                WHEN MATCHED THEN
                    UPDATE SET
                    CIRCUMSTANCECODE = vals.CIRCUMSTANCECODE,
                    CIRCUMSTANCEID = vals.CIRCUMSTANCEID,
                    CIRCUMSTANCETYPE = vals.CIRCUMSTANCETYPE,
                    PERSONID = vals.PERSONID,
                    REPORTNUMBER = vals.REPORTNUMBER,
                    VEHICLEID = vals.VEHICLEID
                WHEN NOT MATCHED THEN
                    INSERT (CIRCUMSTANCECODE, CIRCUMSTANCEID, CIRCUMSTANCETYPE, PERSONID, REPORTNUMBER, VEHICLEID)
                    VALUES (vals.CIRCUMSTANCECODE, vals.CIRCUMSTANCEID, vals.CIRCUMSTANCETYPE, vals.PERSONID,
                    vals.REPORTNUMBER, vals.VEHICLEID );
                """, data
            )

        return ret

    @check_and_log('citation_dict')
    def _read_citation_data(self, citation_dict: List[CitationCodeType]) -> bool:
        """ Populates the acrs_citation_codes table """
        data = []
        for citation in citation_dict:
            data.append((
                self.get_single_attr('CITATIONNUMBER', citation),
                self._validate_uniqueidentifier(self.get_single_attr('PERSONID', citation)),
                self.get_single_attr('REPORTNUMBER', citation)
            ))

        ret: bool = True
        if data:
            ret = self._safe_sql_executemany(
                """
                MERGE acrs_citation_codes USING (
                VALUES
                    (?, ?, ?)
                ) as vals (CITATIONNUMBER, PERSONID, REPORTNUMBER)
                ON (acrs_citation_codes.CITATIONNUMBER = vals.CITATIONNUMBER AND
                    acrs_citation_codes.REPORTNUMBER = vals.REPORTNUMBER AND
                    acrs_citation_codes.PERSONID = vals.PERSONID
                )
                WHEN NOT MATCHED THEN
                    INSERT (CITATIONNUMBER, PERSONID, REPORTNUMBER)
                    VALUES (vals.CITATIONNUMBER, vals.PERSONID, vals.REPORTNUMBER);
                """, data
            )

        return ret

    @check_and_log('crash_diagram_dict')
    def _read_crash_diagrams_data(self, crash_diagram_dict: CrashDiagramType) -> bool:
        """
        Populates the acrs_crash_diagrams table
        :param crash_diagram_dict: OrderedDict from the DIAGRAM tag
        """
        data = [
            self.get_single_attr('CRASHDIAGRAM', crash_diagram_dict),
            self.get_single_attr('CRASHDIAGRAMNATIVE', crash_diagram_dict),
            self.get_single_attr('REPORTNUMBER', crash_diagram_dict),
        ]

        ret: bool = True
        if data:
            ret = self._safe_sql_execute(
                """
                MERGE acrs_crash_diagrams USING (
                VALUES
                    (?, ?, ?)
                ) as vals (CRASHDIAGRAM, CRASHDIAGRAMNATIVE, REPORTNUMBER)
                ON (acrs_crash_diagrams.REPORTNUMBER = vals.REPORTNUMBER)
                WHEN MATCHED THEN
                    UPDATE SET
                    CRASHDIAGRAM = vals.CRASHDIAGRAM,
                    CRASHDIAGRAMNATIVE = vals.CRASHDIAGRAMNATIVE
                WHEN NOT MATCHED THEN
                    INSERT (CRASHDIAGRAM, CRASHDIAGRAMNATIVE, REPORTNUMBER)
                    VALUES (vals.CRASHDIAGRAM, vals.CRASHDIAGRAMNATIVE, vals.REPORTNUMBER);
                """, data
            )

        return ret

    @check_and_log('ems_dict')
    def _read_ems_data(self,
                       ems_dict: List[EmsType]) -> bool:  # pylint:disable=unsubscriptable-object ; see comment at top
        """
        Populates the acrs_ems table from the EMSes tag
        :param ems_dict: List of OrderedDicts contained in the EMSes tag
        """
        data = []
        for ems in ems_dict:
            data.append((
                self.get_single_attr('EMSTRANSPORTATIONTYPE', ems),
                self.get_single_attr('EMSUNITNUMBER', ems),
                self.get_single_attr('INJUREDTAKENBY', ems),
                self.get_single_attr('INJUREDTAKENTO', ems),
                self.get_single_attr('REPORTNUMBER', ems)
            ))

        ret: bool = True
        if data:
            ret = self._safe_sql_executemany(
                """
                MERGE acrs_ems USING (
                VALUES
                    (?, ?, ?, ?, ?)
                ) as vals (EMSTRANSPORTATIONTYPE, EMSUNITNUMBER, INJUREDTAKENBY, INJUREDTAKENTO, REPORTNUMBER)
                ON (acrs_ems.EMSUNITNUMBER = vals.EMSUNITNUMBER AND
                    acrs_ems.REPORTNUMBER = vals.REPORTNUMBER)
                WHEN MATCHED THEN
                    UPDATE SET
                    acrs_ems.EMSTRANSPORTATIONTYPE = vals.EMSTRANSPORTATIONTYPE,
                    acrs_ems.INJUREDTAKENBY = vals.INJUREDTAKENBY,
                    acrs_ems.INJUREDTAKENTO = vals.INJUREDTAKENTO
                WHEN NOT MATCHED THEN
                INSERT (EMSTRANSPORTATIONTYPE, EMSUNITNUMBER, INJUREDTAKENBY, INJUREDTAKENTO, REPORTNUMBER)
                VALUES (vals.EMSTRANSPORTATIONTYPE, vals.EMSUNITNUMBER, vals.INJUREDTAKENBY, vals.INJUREDTAKENTO,
                vals.REPORTNUMBER);
                """, data
            )

        return ret

    @check_and_log('commvehicle_dict')
    def _read_commercial_vehicle_data(self, commvehicle_dict: CommercialVehicleType) -> bool:
        """
        Populates the acrs_commercial_vehicle table
        :param commvehicle_dict: The dictionary of the ACRSVEHICLE
        :return:
        """
        data = [
            self.get_single_attr('BODYTYPE', commvehicle_dict),
            self.get_single_attr('BUSUSE', commvehicle_dict),
            self.get_single_attr('CARRIERCLASSIFICATION', commvehicle_dict),
            self.get_single_attr('CITY', commvehicle_dict),
            self.get_single_attr('CONFIGURATION', commvehicle_dict),
            self.get_single_attr('COUNTRY', commvehicle_dict),
            self.get_single_attr('DOTNUMBER', commvehicle_dict),
            self.get_single_attr('GVW', commvehicle_dict),
            self.get_single_attr('HAZMATCLASS', commvehicle_dict),
            self.get_single_attr('HAZMATNAME', commvehicle_dict),
            self.get_single_attr('HAZMATNUMBER', commvehicle_dict),
            self.get_single_attr('HAZMATSPILL', commvehicle_dict),
            self.get_single_attr('MCNUMBER', commvehicle_dict),
            self.get_single_attr('NAME', commvehicle_dict),
            self.get_single_attr('NUMBEROFAXLES', commvehicle_dict),
            self.get_single_attr('PLACARDVISIBLE', commvehicle_dict),
            self.get_single_attr('POSTALCODE', commvehicle_dict),
            self.get_single_attr('STATE', commvehicle_dict),
            self.get_single_attr('STREET', commvehicle_dict),
            self.get_single_attr('VEHICLEID', commvehicle_dict),
            self.get_single_attr('WEIGHT', commvehicle_dict),
            self.get_single_attr('WEIGHTUNIT', commvehicle_dict)
        ]

        ret: bool = True
        if data:
            ret = self._safe_sql_execute(
                """
                MERGE acrs_commercial_vehicles USING (
                VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ) as vals (BODYTYPE, BUSUSE, CARRIERCLASSIFICATION, CITY, CONFIGURATION, COUNTRY, DOTNUMBER, GVW,
                HAZMATCLASS, HAZMATNAME, HAZMATNUMBER, HAZMATSPILL, MCNUMBER, NAME, NUMBEROFAXLES, PLACARDVISIBLE,
                POSTALCODE, STATE, STREET, VEHICLEID, WEIGHT, WEIGHTUNIT)
                ON (acrs_commercial_vehicles.VEHICLEID = vals.VEHICLEID)
                WHEN MATCHED THEN
                    UPDATE SET
                    acrs_commercial_vehicles.BODYTYPE = vals.BODYTYPE,
                    acrs_commercial_vehicles.BUSUSE = vals.BUSUSE,
                    acrs_commercial_vehicles.CARRIERCLASSIFICATION = vals.CARRIERCLASSIFICATION,
                    acrs_commercial_vehicles.CITY = vals.CITY,
                    acrs_commercial_vehicles.CONFIGURATION = vals.CONFIGURATION,
                    acrs_commercial_vehicles.COUNTRY = vals.COUNTRY,
                    acrs_commercial_vehicles.DOTNUMBER = vals.DOTNUMBER,
                    acrs_commercial_vehicles.GVW = vals.GVW,
                    acrs_commercial_vehicles.HAZMATCLASS = vals.HAZMATCLASS,
                    acrs_commercial_vehicles.HAZMATNAME = vals.HAZMATNAME,
                    acrs_commercial_vehicles.HAZMATNUMBER = vals.HAZMATNUMBER,
                    acrs_commercial_vehicles.HAZMATSPILL = vals.HAZMATSPILL,
                    acrs_commercial_vehicles.MCNUMBER = vals.MCNUMBER,
                    acrs_commercial_vehicles.NAME = vals.NAME,
                    acrs_commercial_vehicles.NUMBEROFAXLES = vals.NUMBEROFAXLES,
                    acrs_commercial_vehicles.PLACARDVISIBLE = vals.PLACARDVISIBLE,
                    acrs_commercial_vehicles.POSTALCODE = vals.POSTALCODE,
                    acrs_commercial_vehicles.STATE = vals.STATE,
                    acrs_commercial_vehicles.STREET = vals.STREET,
                    acrs_commercial_vehicles.WEIGHT = vals.WEIGHT,
                    acrs_commercial_vehicles.WEIGHTUNIT = vals.WEIGHTUNIT
                WHEN NOT MATCHED THEN
                    INSERT (BODYTYPE, BUSUSE, CARRIERCLASSIFICATION, CITY, CONFIGURATION, COUNTRY, DOTNUMBER, GVW,
                        HAZMATCLASS, HAZMATNAME, HAZMATNUMBER, HAZMATSPILL, MCNUMBER, NAME, NUMBEROFAXLES,
                        PLACARDVISIBLE, POSTALCODE, STATE, STREET, VEHICLEID, WEIGHT, WEIGHTUNIT)
                    VALUES (vals.BODYTYPE, vals.BUSUSE, vals.CARRIERCLASSIFICATION, vals.CITY, vals.CONFIGURATION,
                        vals.COUNTRY, vals.DOTNUMBER, vals.GVW, vals.HAZMATCLASS, vals.HAZMATNAME, vals.HAZMATNUMBER,
                        vals.HAZMATSPILL, vals.MCNUMBER, vals.NAME, vals.NUMBEROFAXLES, vals.PLACARDVISIBLE,
                        vals.POSTALCODE, vals.STATE, vals.STREET, vals.VEHICLEID, vals.WEIGHT, vals.WEIGHTUNIT);
                """, data
            )

        return ret

    @check_and_log('event_dict')
    def _read_event_data(self, event_dict: List[
        EventType]) -> bool:  # pylint:disable=unsubscriptable-object ; see comment at top
        """
        Populates the acrs_events table from the EVENTS tag
        :param event_dict: The dictionary of the ACRSVEHICLE
        """
        data = []
        for event in event_dict:
            data.append((
                self.get_single_attr('EVENTID', event),
                self.get_single_attr('EVENTSEQUENCE', event),
                self.get_single_attr('EVENTTYPE', event),
                self._validate_uniqueidentifier(self.get_single_attr('VEHICLEID', event))
            ))

        ret: bool = True
        if data:
            ret = self._safe_sql_executemany(
                """
                MERGE acrs_events USING (
                VALUES
                    (?, ?, ?, ?)
                ) as vals (EVENTID, EVENTSEQUENCE, EVENTTYPE, VEHICLEID)
                ON (acrs_events.EVENTID = vals.EVENTID AND
                    acrs_events.VEHICLEID = vals.VEHICLEID)
                WHEN MATCHED THEN
                    UPDATE SET
                    acrs_events.EVENTSEQUENCE = vals.EVENTSEQUENCE,
                    acrs_events.EVENTTYPE = vals.EVENTTYPE
                WHEN NOT MATCHED THEN
                    INSERT (EVENTID, EVENTSEQUENCE, EVENTTYPE, VEHICLEID)
                    VALUES (vals.EVENTID, vals.EVENTSEQUENCE, vals.EVENTTYPE, vals.VEHICLEID);
                """, data
            )

        return ret

    @check_and_log('pdfreport_dict')
    def _read_pdf_data(self, pdfreport_dict: List[PdfReportDataType]) -> bool:
        """
        Populates the acrs_pdf_report table from the PDFREPORTs tag
        :param pdfreport_dict: List of OrderedDicts from the PDFREPORTs tag
        """
        data = []
        for report in pdfreport_dict:
            data.append((
                self.get_single_attr('CHANGEDBY', report),
                self.get_single_attr('DATESTATUSCHANGED', report),
                self.get_single_attr('PDFREPORT1', report),
                self.get_single_attr('PDF_ID', report),
                self.get_single_attr('REPORTNUMBER', report),
                self.get_single_attr('STATUS', report)
            ))

        ret: bool = True
        if data:
            ret = self._safe_sql_executemany(
                """
                MERGE acrs_pdf_report USING (
                VALUES
                    (?, ?, ?, ?, ?, ?)
                ) as vals (CHANGEDBY, DATESTATUSCHANGED, PDFREPORT1, PDF_ID, REPORTNUMBER, STATUS)
                ON (acrs_pdf_report.PDF_ID = vals.PDF_ID AND
                    acrs_pdf_report.REPORTNUMBER = vals.REPORTNUMBER)
                WHEN MATCHED THEN
                    UPDATE SET
                    CHANGEDBY = vals.CHANGEDBY,
                    DATESTATUSCHANGED = vals.DATESTATUSCHANGED,
                    PDFREPORT1 = vals.PDFREPORT1,
                    STATUS = vals.STATUS
                WHEN NOT MATCHED THEN
                    INSERT (CHANGEDBY, DATESTATUSCHANGED, PDFREPORT1, PDF_ID, REPORTNUMBER, STATUS)
                    VALUES (vals.CHANGEDBY, vals.DATESTATUSCHANGED, vals.PDFREPORT1, vals.PDF_ID, vals.REPORTNUMBER,
                    vals.STATUS);
                """, data
            )

        return ret

    @check_and_log('person_dict')
    def _read_acrs_person_data(self, person_dict: List[PersonType]) -> bool:
        """
        Processes the ACRSPERSON tag contents
        :param person_dict: OrderedDict from the PERSON, OWNER, PASSENGER, or NONMOTORIST tags
        """
        data = []
        for person in person_dict:
            if person.get('CITATIONCODES') and person.get('CITATIONCODES', {}).get('CITATIONCODE'):
                self._read_citation_data(person['CITATIONCODES']['CITATIONCODE'])

            data.append((
                self.get_single_attr('ADDRESS', person),
                self.get_single_attr('CITY', person),
                self.get_single_attr('COMPANY', person),
                self.get_single_attr('COUNTRY', person),
                self.get_single_attr('COUNTY', person),
                self.get_single_attr('DLCLASS', person),
                self.get_single_attr('DLNUMBER', person),
                self.get_single_attr('DLSTATE', person),
                self.get_single_attr('DOB', person),
                self.get_single_attr('FIRSTNAME', person),
                self.get_single_attr('HOMEPHONE', person),
                self.get_single_attr('LASTNAME', person),
                self.get_single_attr('MIDDLENAME', person),
                self.get_single_attr('OTHERPHONE', person),
                self._validate_uniqueidentifier(self.get_single_attr('PERSONID', person)),
                self.get_single_attr('RACE', person),
                self.get_single_attr('REPORTNUMBER', person),
                self.get_single_attr('SEX', person),
                self.get_single_attr('STATE', person),
                self.get_single_attr('ZIP', person)
            ))

        ret: bool = True
        if data:
            ret = self._safe_sql_executemany(
                """
                MERGE acrs_person USING (
                VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ) as vals (ADDRESS, CITY, COMPANY, COUNTRY, COUNTY, DLCLASS, DLNUMBER, DLSTATE, DOB, FIRSTNAME,
                HOMEPHONE, LASTNAME, MIDDLENAME, OTHERPHONE, PERSONID, RACE, REPORTNUMBER, SEX, STATE, ZIP)
                ON (acrs_person.REPORTNUMBER = vals.REPORTNUMBER AND
                    acrs_person.PERSONID = vals.PERSONID)
                WHEN MATCHED THEN
                    UPDATE SET
                    acrs_person.ADDRESS = vals.ADDRESS,
                    acrs_person.CITY = vals.CITY,
                    acrs_person.COMPANY = vals.COMPANY,
                    acrs_person.COUNTRY = vals.COUNTRY,
                    acrs_person.COUNTY = vals.COUNTY,
                    acrs_person.DLCLASS = vals.DLCLASS,
                    acrs_person.DLNUMBER = vals.DLNUMBER,
                    acrs_person.DLSTATE = vals.DLSTATE,
                    acrs_person.DOB = vals.DOB,
                    acrs_person.FIRSTNAME = vals.FIRSTNAME,
                    acrs_person.HOMEPHONE = vals.HOMEPHONE,
                    acrs_person.LASTNAME = vals.LASTNAME,
                    acrs_person.MIDDLENAME = vals.MIDDLENAME,
                    acrs_person.OTHERPHONE = vals.OTHERPHONE,
                    acrs_person.PERSONID = vals.PERSONID,
                    acrs_person.RACE = vals.RACE,
                    acrs_person.REPORTNUMBER = vals.REPORTNUMBER,
                    acrs_person.SEX = vals.SEX,
                    acrs_person.STATE = vals.STATE,
                    acrs_person.ZIP = vals.ZIP
                WHEN NOT MATCHED THEN
                    INSERT (ADDRESS, CITY, COMPANY, COUNTRY, COUNTY, DLCLASS, DLNUMBER, DLSTATE, DOB, FIRSTNAME,
                    HOMEPHONE, LASTNAME, MIDDLENAME, OTHERPHONE, PERSONID, RACE, REPORTNUMBER, SEX, STATE, ZIP)
                    VALUES (vals.ADDRESS, vals.CITY, vals.COMPANY, vals.COUNTRY, vals.COUNTY, vals.DLCLASS,
                    vals.DLNUMBER, vals.DLSTATE, vals.DOB, vals.FIRSTNAME, vals.HOMEPHONE, vals.LASTNAME,
                    vals.MIDDLENAME, vals.OTHERPHONE, vals.PERSONID, vals.RACE, vals.REPORTNUMBER, vals.SEX, vals.STATE,
                    vals.ZIP);
                """, data
            )

        return ret

    @check_and_log('person_dict')
    def _read_person_info_data(
            self,
            person_dict: Union[List[DriverType], List[PassengerType], List[NonMotoristType]]
            # pylint:disable=unsubscriptable-object ; see comment at top
    ) -> bool:
        """
        Populates the acrs_person_info table.
        :param person_dict: Contains the list of OrderedDicts contained in the drivers, passengers and nonmotorists tags
        """
        data = []
        for person in person_dict:
            report_no = ''
            if person.get('PERSON'):
                self._read_acrs_person_data([person['PERSON']])
                report_no = self.get_single_attr('REPORTNUMBER', person['PERSON']) or ''

            data.append((
                self.get_single_attr('AIRBAGDEPLOYED', person),
                self.get_single_attr('ALCOHOLTESTINDICATOR', person),
                self.get_single_attr('ALCOHOLTESTTYPE', person),
                self._convert_to_bool(self.get_single_attr('ATFAULT', person)),
                self.get_single_attr('BAC', person),
                self.get_single_attr('CONDITION', person),
                self.get_single_attr('CONTINUEDIRECTION', person),
                self.get_single_attr('DRIVERDISTRACTEDBY', person),
                self.get_single_attr('DRUGTESTINDICATOR', person),
                self.get_single_attr('DRUGTESTRESULT', person),
                self.get_single_attr('EJECTION', person),
                self.get_single_attr('EMSRUNREPORTNUMBER', person),
                self.get_single_attr('EMSUNITNUMBER', person),
                self.get_single_attr('EQUIPMENTPROBLEM', person),
                self.get_single_attr('GOINGDIRECTION', person),
                self._convert_to_bool(self.get_single_attr('HASCDL', person)),
                self.get_single_attr('INJURYSEVERITY', person),
                self.get_single_attr('PEDESTRIANACTIONS', person),
                self.get_single_attr('PEDESTRIANLOCATION', person),
                self.get_single_attr('PEDESTRIANMOVEMENT', person),
                self.get_single_attr('PEDESTRIANOBEYTRAFFICSIGNAL', person),
                self.get_single_attr('PEDESTRIANTYPE', person),
                self.get_single_attr('PEDESTRIANVISIBILITY', person),
                self._validate_uniqueidentifier(self.get_single_attr('PERSONID', person)),
                report_no,
                self.get_single_attr('SAFETYEQUIPMENT', person),
                self.get_single_attr('SEAT', person),
                self.get_single_attr('SEATINGLOCATION', person),
                self.get_single_attr('SEATINGROW', person),
                self.get_single_attr('SUBSTANCEUSE', person),
                self.get_single_attr('UNITNUMBERFIRSTSTRIKE', person),
                self._validate_uniqueidentifier(self.get_single_attr('VEHICLEID', person))
            ))

        ret: bool = True
        if data:
            ret = self._safe_sql_executemany(
                """
                MERGE acrs_person_info USING (
                VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ) AS vals (AIRBAGDEPLOYED, ALCOHOLTESTINDICATOR, ALCOHOLTESTTYPE, ATFAULT, BAC, CONDITION,
                CONTINUEDIRECTION, DRIVERDISTRACTEDBY, DRUGTESTINDICATOR, DRUGTESTRESULT, EJECTION, EMSRUNREPORTNUMBER,
                EMSUNITNUMBER, EQUIPMENTPROBLEM, GOINGDIRECTION, HASCDL, INJURYSEVERITY, PEDESTRIANACTIONS,
                PEDESTRIANLOCATION, PEDESTRIANMOVEMENT, PEDESTRIANOBEYTRAFFICSIGNAL, PEDESTRIANTYPE,
                PEDESTRIANVISIBILITY, PERSONID, REPORTNUMBER, SAFETYEQUIPMENT, SEAT, SEATINGLOCATION, SEATINGROW,
                SUBSTANCEUSE, UNITNUMBERFIRSTSTRIKE, VEHICLEID)
                ON (acrs_person_info.EMSRUNREPORTNUMBER = vals.EMSRUNREPORTNUMBER AND
                acrs_person_info.PERSONID = vals.PERSONID AND
                acrs_person_info.VEHICLEID = vals.VEHICLEID)
                WHEN MATCHED THEN
                    UPDATE SET
                    acrs_person_info.AIRBAGDEPLOYED = vals.AIRBAGDEPLOYED,
                    acrs_person_info.ALCOHOLTESTINDICATOR = vals.ALCOHOLTESTINDICATOR,
                    acrs_person_info.ALCOHOLTESTTYPE = vals.ALCOHOLTESTTYPE,
                    acrs_person_info.ATFAULT = vals.ATFAULT,
                    acrs_person_info.BAC = vals.BAC,
                    acrs_person_info.CONDITION = vals.CONDITION,
                    acrs_person_info.CONTINUEDIRECTION = vals.CONTINUEDIRECTION,
                    acrs_person_info.DRIVERDISTRACTEDBY = vals.DRIVERDISTRACTEDBY,
                    acrs_person_info.DRUGTESTINDICATOR = vals.DRUGTESTINDICATOR,
                    acrs_person_info.DRUGTESTRESULT = vals.DRUGTESTRESULT,
                    acrs_person_info.EJECTION = vals.EJECTION,
                    acrs_person_info.EMSRUNREPORTNUMBER = vals.EMSRUNREPORTNUMBER,
                    acrs_person_info.EMSUNITNUMBER = vals.EMSUNITNUMBER,
                    acrs_person_info.EQUIPMENTPROBLEM = vals.EQUIPMENTPROBLEM,
                    acrs_person_info.GOINGDIRECTION = vals.GOINGDIRECTION,
                    acrs_person_info.HASCDL = vals.HASCDL,
                    acrs_person_info.INJURYSEVERITY = vals.INJURYSEVERITY,
                    acrs_person_info.PEDESTRIANACTIONS = vals.PEDESTRIANACTIONS,
                    acrs_person_info.PEDESTRIANLOCATION = vals.PEDESTRIANLOCATION,
                    acrs_person_info.PEDESTRIANMOVEMENT = vals.PEDESTRIANMOVEMENT,
                    acrs_person_info.PEDESTRIANOBEYTRAFFICSIGNAL = vals.PEDESTRIANOBEYTRAFFICSIGNAL,
                    acrs_person_info.PEDESTRIANTYPE = vals.PEDESTRIANTYPE,
                    acrs_person_info.PEDESTRIANVISIBILITY = vals.PEDESTRIANVISIBILITY,
                    acrs_person_info.PERSONID = vals.PERSONID,
                    acrs_person_info.REPORTNUMBER = vals.REPORTNUMBER,
                    acrs_person_info.SAFETYEQUIPMENT = vals.SAFETYEQUIPMENT,
                    acrs_person_info.SEAT = vals.SEAT,
                    acrs_person_info.SEATINGLOCATION = vals.SEATINGLOCATION,
                    acrs_person_info.SEATINGROW = vals.SEATINGROW,
                    acrs_person_info.SUBSTANCEUSE = vals.SUBSTANCEUSE,
                    acrs_person_info.UNITNUMBERFIRSTSTRIKE = vals.UNITNUMBERFIRSTSTRIKE,
                    acrs_person_info.VEHICLEID = vals.VEHICLEID
                WHEN NOT MATCHED THEN
                    INSERT (AIRBAGDEPLOYED, ALCOHOLTESTINDICATOR, ALCOHOLTESTTYPE, ATFAULT, BAC, CONDITION,
                        CONTINUEDIRECTION, DRIVERDISTRACTEDBY, DRUGTESTINDICATOR, DRUGTESTRESULT, EJECTION,
                        EMSRUNREPORTNUMBER, EMSUNITNUMBER, EQUIPMENTPROBLEM, GOINGDIRECTION, HASCDL, INJURYSEVERITY,
                        PEDESTRIANACTIONS, PEDESTRIANLOCATION, PEDESTRIANMOVEMENT, PEDESTRIANOBEYTRAFFICSIGNAL,
                        PEDESTRIANTYPE, PEDESTRIANVISIBILITY, PERSONID, REPORTNUMBER, SAFETYEQUIPMENT, SEAT,
                        SEATINGLOCATION, SEATINGROW, SUBSTANCEUSE, UNITNUMBERFIRSTSTRIKE, VEHICLEID)
                    VALUES (vals.AIRBAGDEPLOYED, vals.ALCOHOLTESTINDICATOR, vals.ALCOHOLTESTTYPE, vals.ATFAULT,
                        vals.BAC, vals.CONDITION, vals.CONTINUEDIRECTION, vals.DRIVERDISTRACTEDBY,
                        vals.DRUGTESTINDICATOR, vals.DRUGTESTRESULT, vals.EJECTION, vals.EMSRUNREPORTNUMBER,
                        vals.EMSUNITNUMBER, vals.EQUIPMENTPROBLEM, vals.GOINGDIRECTION, vals.HASCDL,
                        vals.INJURYSEVERITY, vals.PEDESTRIANACTIONS, vals.PEDESTRIANLOCATION, vals.PEDESTRIANMOVEMENT,
                        vals.PEDESTRIANOBEYTRAFFICSIGNAL, vals.PEDESTRIANTYPE, vals.PEDESTRIANVISIBILITY, vals.PERSONID,
                        vals.REPORTNUMBER, vals.SAFETYEQUIPMENT, vals.SEAT, vals.SEATINGLOCATION, vals.SEATINGROW,
                        vals.SUBSTANCEUSE, vals.UNITNUMBERFIRSTSTRIKE, vals.VEHICLEID);
                """, data
            )

        return ret

    @check_and_log('reportdoc_dict')
    def _read_report_documents_data(self, reportdoc_dict: List[
        ReportDocumentType]):  # pylint:disable=unsubscriptable-object ; see comment at top
        """Populates the acrs_report_docs table. Currently a stub until we get the schema or example data for this"""

    @check_and_log('reportphotos_dict')
    def _read_report_photos_data(self, reportphotos_dict: List[
        ReportPhotoType]):  # pylint:disable=unsubscriptable-object ; see comment at top
        """Populates the acrs_report_photos table. Currently a stub until we get the schema or example data for this"""

    @check_and_log('roadway_dict')
    def _read_roadway_data(self, roadway_dict: RoadwayType) -> bool:
        """
        Populates the acrs_roadway table. Expects the ROADWAY tag contents
        :param roadway_dict: OrderedDict from the ROADWAY tag
        """
        data = [
            self.get_single_attr('COUNTY', roadway_dict),
            self.get_single_attr('LOGMILE_DIR', roadway_dict),
            self.get_single_attr('MILEPOINT', roadway_dict),
            self.get_single_attr('MUNICIPAL', roadway_dict),
            self.get_single_attr('MUNICIPAL_AREA_CODE', roadway_dict),
            self.get_single_attr('REFERENCE_MUNI', roadway_dict),
            self.get_single_attr('REFERENCE_ROADNAME', roadway_dict),
            self.get_single_attr('REFERENCE_ROUTE_NUMBER', roadway_dict),
            self.get_single_attr('REFERENCE_ROUTE_SUFFIX', roadway_dict),
            self.get_single_attr('REFERENCE_ROUTE_TYPE', roadway_dict),
            self.get_single_attr('ROADID', roadway_dict),
            self.get_single_attr('ROAD_NAME', roadway_dict),
            self.get_single_attr('ROUTE_NUMBER', roadway_dict),
            self.get_single_attr('ROUTE_SUFFIX', roadway_dict),
            self.get_single_attr('ROUTE_TYPE', roadway_dict)
        ]

        ret: bool = True
        if data:
            ret = self._safe_sql_execute(
                """
                MERGE acrs_roadway USING (
                VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ) as vals ( COUNTY, LOGMILE_DIR, MILEPOINT, MUNICIPAL, MUNICIPAL_AREA_CODE, REFERENCE_MUNI,
                REFERENCE_ROADNAME, REFERENCE_ROUTE_NUMBER, REFERENCE_ROUTE_SUFFIX, REFERENCE_ROUTE_TYPE, ROADID,
                ROAD_NAME, ROUTE_NUMBER, ROUTE_SUFFIX, ROUTE_TYPE)
                ON (acrs_roadway.roadid = vals.roadid )
                WHEN MATCHED THEN
                    UPDATE SET
                    acrs_roadway.COUNTY = vals.COUNTY,
                    acrs_roadway.LOGMILE_DIR = vals.LOGMILE_DIR,
                    acrs_roadway.MILEPOINT = vals.MILEPOINT,
                    acrs_roadway.MUNICIPAL = vals.MUNICIPAL,
                    acrs_roadway.MUNICIPAL_AREA_CODE = vals.MUNICIPAL_AREA_CODE,
                    acrs_roadway.REFERENCE_MUNI = vals.REFERENCE_MUNI,
                    acrs_roadway.REFERENCE_ROADNAME = vals.REFERENCE_ROADNAME,
                    acrs_roadway.REFERENCE_ROUTE_NUMBER = vals.REFERENCE_ROUTE_NUMBER,
                    acrs_roadway.REFERENCE_ROUTE_SUFFIX = vals.REFERENCE_ROUTE_SUFFIX,
                    acrs_roadway.REFERENCE_ROUTE_TYPE = vals.REFERENCE_ROUTE_TYPE,
                    acrs_roadway.ROAD_NAME = vals.ROAD_NAME,
                    acrs_roadway.ROUTE_NUMBER = vals.ROUTE_NUMBER,
                    acrs_roadway.ROUTE_SUFFIX = vals.ROUTE_SUFFIX,
                    acrs_roadway.ROUTE_TYPE = vals.ROUTE_TYPE
                WHEN NOT MATCHED THEN
                    INSERT (COUNTY, LOGMILE_DIR, MILEPOINT, MUNICIPAL, MUNICIPAL_AREA_CODE, REFERENCE_MUNI,
                        REFERENCE_ROADNAME, REFERENCE_ROUTE_NUMBER, REFERENCE_ROUTE_SUFFIX, REFERENCE_ROUTE_TYPE,
                        ROADID, ROAD_NAME, ROUTE_NUMBER, ROUTE_SUFFIX, ROUTE_TYPE)
                    VALUES (vals.COUNTY, vals.LOGMILE_DIR, vals.MILEPOINT, vals.MUNICIPAL, vals.MUNICIPAL_AREA_CODE,
                        vals.REFERENCE_MUNI, vals.REFERENCE_ROADNAME, vals.REFERENCE_ROUTE_NUMBER,
                        vals.REFERENCE_ROUTE_SUFFIX, vals.REFERENCE_ROUTE_TYPE, vals.ROADID, vals.ROAD_NAME,
                        vals.ROUTE_NUMBER, vals.ROUTE_SUFFIX, vals.ROUTE_TYPE);
                """, data
            )

        return ret

    @check_and_log('towed_dict')
    def _read_towed_vehicle_data(self, towed_dict: List[TowedUnitType]) -> bool:
        """
        Populates the acrs_towed_unit table
        :param towed_dict: The list of OrderedDicts that comes from the TOWEDUNITs tag
        """
        data = []
        for towed_unit in towed_dict:
            if towed_unit.get('OWNER'):
                self._read_acrs_person_data([towed_unit['OWNER']])

            data.append((
                self.get_single_attr('INSURANCEPOLICYNUMBER', towed_unit),
                self.get_single_attr('INSURER', towed_unit),
                self.get_single_attr('LICENSEPLATENUMBER', towed_unit),
                self.get_single_attr('LICENSEPLATESTATE', towed_unit),
                self._validate_uniqueidentifier(self.get_single_attr('OWNERID', towed_unit)),
                self._validate_uniqueidentifier(self.get_single_attr('TOWEDID', towed_unit)),
                self.get_single_attr('UNITNUMBER', towed_unit),
                self._validate_uniqueidentifier(self.get_single_attr('VEHICLEID', towed_unit)),
                self.get_single_attr('VEHICLEMAKE', towed_unit),
                self.get_single_attr('VEHICLEMODEL', towed_unit),
                self.get_single_attr('VEHICLEYEAR', towed_unit),
                self.get_single_attr('VIN', towed_unit)
            ))

        ret: bool = True
        if data:
            ret = self._safe_sql_executemany(
                """
                MERGE acrs_towed_unit USING (
                VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ) as vals (INSURANCEPOLICYNUMBER, INSURER, LICENSEPLATENUMBER, LICENSEPLATESTATE, OWNERID, TOWEDID,
                UNITNUMBER, VEHICLEID, VEHICLEMAKE, VEHICLEMODEL, VEHICLEYEAR, VIN)
                ON (acrs_towed_unit.TOWEDID = vals.TOWEDID AND
                    acrs_towed_unit.VEHICLEID = vals.VEHICLEID AND
                    acrs_towed_unit.OWNERID = vals.OWNERID
                )
                WHEN MATCHED THEN
                    UPDATE SET
                    acrs_towed_unit.INSURANCEPOLICYNUMBER = vals.INSURANCEPOLICYNUMBER,
                    acrs_towed_unit.INSURER = vals.INSURER,
                    acrs_towed_unit.LICENSEPLATENUMBER = vals.LICENSEPLATENUMBER,
                    acrs_towed_unit.LICENSEPLATESTATE = vals.LICENSEPLATESTATE,
                    acrs_towed_unit.OWNERID = vals.OWNERID,
                    acrs_towed_unit.TOWEDID = vals.TOWEDID,
                    acrs_towed_unit.UNITNUMBER = vals.UNITNUMBER,
                    acrs_towed_unit.VEHICLEID = vals.VEHICLEID,
                    acrs_towed_unit.VEHICLEMAKE = vals.VEHICLEMAKE,
                    acrs_towed_unit.VEHICLEMODEL = vals.VEHICLEMODEL,
                    acrs_towed_unit.VEHICLEYEAR = vals.VEHICLEYEAR,
                    acrs_towed_unit.VIN = vals.VIN
                WHEN NOT MATCHED THEN
                    INSERT (INSURANCEPOLICYNUMBER, INSURER, LICENSEPLATENUMBER, LICENSEPLATESTATE, OWNERID, TOWEDID,
                    UNITNUMBER, VEHICLEID, VEHICLEMAKE, VEHICLEMODEL, VEHICLEYEAR, VIN)
                    VALUES (vals.INSURANCEPOLICYNUMBER, vals.INSURER, vals.LICENSEPLATENUMBER, vals.LICENSEPLATESTATE,
                    vals.OWNERID, vals.TOWEDID, vals.UNITNUMBER, vals.VEHICLEID, vals.VEHICLEMAKE, vals.VEHICLEMODEL,
                    vals.VEHICLEYEAR, vals.VIN);
                """, data
            )

        return ret

    @check_and_log('vehicle_dict')
    def _read_acrs_vehicle_data(self, vehicle_dict: List[
        VehicleType]) -> bool:  # pylint:disable=unsubscriptable-object ; see comment at top
        """
        Populates the acrs_vehicles table
        :param vehicle_dict: List of OrderedDicts from the ACRSVEHICLE tag
        """
        data = []
        for vehicle in vehicle_dict:
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

            data.append((
                self.get_single_attr('CONTINUEDIRECTION', vehicle),
                self.get_single_attr('DAMAGEEXTENT', vehicle),
                self._convert_to_bool(self.get_single_attr('DRIVERLESSVEHICLE', vehicle)),
                self._convert_to_bool(self.get_single_attr('EMERGENCYMOTORVEHICLEUSE', vehicle)),
                self._convert_to_bool(self.get_single_attr('FIRE', vehicle)),
                self.get_single_attr('FIRSTIMPACT', vehicle),
                self.get_single_attr('GOINGDIRECTION', vehicle),
                self._convert_to_bool(self.get_single_attr('HITANDRUN', vehicle)),
                self.get_single_attr('INSURANCEPOLICYNUMBER', vehicle),
                self.get_single_attr('INSURER', vehicle),
                self.get_single_attr('LICENSEPLATENUMBER', vehicle),
                self.get_single_attr('LICENSEPLATESTATE', vehicle),
                self.get_single_attr('MAINIMPACT', vehicle),
                self.get_single_attr('MOSTHARMFULEVENT', vehicle),
                self._validate_uniqueidentifier(self.get_single_attr('OWNERID', vehicle)),
                self._convert_to_bool(self.get_single_attr('PARKEDVEHICLE', vehicle)),
                self.get_single_attr('REGISTRATIONEXPIRATIONYEAR', vehicle),
                self.get_single_attr('REPORTNUMBER', vehicle),
                self.get_single_attr('SFVEHICLEINTRANSPORT', vehicle),
                self.get_single_attr('SPEEDLIMIT', vehicle),
                self.get_single_attr('TOWEDUNITTYPE', vehicle),
                self.get_single_attr('UNITNUMBER', vehicle),
                self.get_single_attr('VEHICLEBODYTYPE', vehicle),
                self._validate_uniqueidentifier(self.get_single_attr('VEHICLEID', vehicle)),
                self.get_single_attr('VEHICLEMAKE', vehicle),
                self.get_single_attr('VEHICLEMODEL', vehicle),
                self.get_single_attr('VEHICLEMOVEMENT', vehicle),
                self.get_single_attr('VEHICLEREMOVEDBY', vehicle),
                self.get_single_attr('VEHICLEREMOVEDTO', vehicle),
                self.get_single_attr('VEHICLETOWEDAWAY', vehicle),
                self.get_single_attr('VEHICLEYEAR', vehicle),
                self.get_single_attr('VIN', vehicle)

            ))

        ret: bool = True
        if data:
            ret = self._safe_sql_executemany(
                """
                MERGE acrs_vehicles USING (
                VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ) as vals (CONTINUEDIRECTION, DAMAGEEXTENT, DRIVERLESSVEHICLE, EMERGENCYMOTORVEHICLEUSE,
                FIRE, FIRSTIMPACT, GOINGDIRECTION, HITANDRUN, INSURANCEPOLICYNUMBER, INSURER, LICENSEPLATENUMBER,
                LICENSEPLATESTATE, MAINIMPACT, MOSTHARMFULEVENT, OWNERID, PARKEDVEHICLE, REGISTRATIONEXPIRATIONYEAR,
                REPORTNUMBER, SFVEHICLEINTRANSPORT, SPEEDLIMIT, TOWEDUNITTYPE, UNITNUMBER, VEHICLEBODYTYPE, VEHICLEID,
                VEHICLEMAKE, VEHICLEMODEL, VEHICLEMOVEMENT, VEHICLEREMOVEDBY, VEHICLEREMOVEDTO, VEHICLETOWEDAWAY,
                VEHICLEYEAR, VIN)
                ON (acrs_vehicles.REPORTNUMBER = vals.REPORTNUMBER AND
                    acrs_vehicles.VEHICLEID = vals.VEHICLEID)
                WHEN MATCHED THEN
                    UPDATE SET
                    acrs_vehicles.CONTINUEDIRECTION = vals.CONTINUEDIRECTION,
                    acrs_vehicles.DAMAGEEXTENT = vals.DAMAGEEXTENT,
                    acrs_vehicles.DRIVERLESSVEHICLE = vals.DRIVERLESSVEHICLE,
                    acrs_vehicles.EMERGENCYMOTORVEHICLEUSE = vals.EMERGENCYMOTORVEHICLEUSE,
                    acrs_vehicles.FIRE = vals.FIRE,
                    acrs_vehicles.FIRSTIMPACT = vals.FIRSTIMPACT,
                    acrs_vehicles.GOINGDIRECTION = vals.GOINGDIRECTION,
                    acrs_vehicles.HITANDRUN = vals.HITANDRUN,
                    acrs_vehicles.INSURANCEPOLICYNUMBER = vals.INSURANCEPOLICYNUMBER,
                    acrs_vehicles.INSURER = vals.INSURER,
                    acrs_vehicles.LICENSEPLATENUMBER = vals.LICENSEPLATENUMBER,
                    acrs_vehicles.LICENSEPLATESTATE = vals.LICENSEPLATESTATE,
                    acrs_vehicles.MAINIMPACT = vals.MAINIMPACT,
                    acrs_vehicles.MOSTHARMFULEVENT = vals.MOSTHARMFULEVENT,
                    acrs_vehicles.OWNERID = vals.OWNERID,
                    acrs_vehicles.PARKEDVEHICLE = vals.PARKEDVEHICLE,
                    acrs_vehicles.REGISTRATIONEXPIRATIONYEAR = vals.REGISTRATIONEXPIRATIONYEAR,
                    acrs_vehicles.SFVEHICLEINTRANSPORT = vals.SFVEHICLEINTRANSPORT,
                    acrs_vehicles.SPEEDLIMIT = vals.SPEEDLIMIT,
                    acrs_vehicles.TOWEDUNITTYPE = vals.TOWEDUNITTYPE,
                    acrs_vehicles.UNITNUMBER = vals.UNITNUMBER,
                    acrs_vehicles.VEHICLEBODYTYPE = vals.VEHICLEBODYTYPE,
                    acrs_vehicles.VEHICLEMAKE = vals.VEHICLEMAKE,
                    acrs_vehicles.VEHICLEMODEL = vals.VEHICLEMODEL,
                    acrs_vehicles.VEHICLEMOVEMENT = vals.VEHICLEMOVEMENT,
                    acrs_vehicles.VEHICLEREMOVEDBY = vals.VEHICLEREMOVEDBY,
                    acrs_vehicles.VEHICLEREMOVEDTO = vals.VEHICLEREMOVEDTO,
                    acrs_vehicles.VEHICLETOWEDAWAY = vals.VEHICLETOWEDAWAY,
                    acrs_vehicles.VEHICLEYEAR = vals.VEHICLEYEAR,
                    acrs_vehicles.VIN = vals.VIN
                WHEN NOT MATCHED THEN
                    INSERT (CONTINUEDIRECTION, DAMAGEEXTENT, DRIVERLESSVEHICLE, EMERGENCYMOTORVEHICLEUSE, FIRE,
                        FIRSTIMPACT, GOINGDIRECTION, HITANDRUN, INSURANCEPOLICYNUMBER, INSURER, LICENSEPLATENUMBER,
                        LICENSEPLATESTATE, MAINIMPACT, MOSTHARMFULEVENT, OWNERID, PARKEDVEHICLE,
                        REGISTRATIONEXPIRATIONYEAR, REPORTNUMBER, SFVEHICLEINTRANSPORT, SPEEDLIMIT, TOWEDUNITTYPE,
                        UNITNUMBER, VEHICLEBODYTYPE, VEHICLEID, VEHICLEMAKE, VEHICLEMODEL, VEHICLEMOVEMENT,
                        VEHICLEREMOVEDBY, VEHICLEREMOVEDTO, VEHICLETOWEDAWAY, VEHICLEYEAR, VIN)
                    VALUES (vals.CONTINUEDIRECTION, vals.DAMAGEEXTENT, vals.DRIVERLESSVEHICLE,
                        vals.EMERGENCYMOTORVEHICLEUSE, vals.FIRE, vals.FIRSTIMPACT, vals.GOINGDIRECTION, vals.HITANDRUN,
                        vals.INSURANCEPOLICYNUMBER, vals.INSURER, vals.LICENSEPLATENUMBER, vals.LICENSEPLATESTATE,
                        vals.MAINIMPACT, vals.MOSTHARMFULEVENT, vals.OWNERID, vals.PARKEDVEHICLE,
                        vals.REGISTRATIONEXPIRATIONYEAR, vals.REPORTNUMBER, vals.SFVEHICLEINTRANSPORT, vals.SPEEDLIMIT,
                        vals.TOWEDUNITTYPE, vals.UNITNUMBER, vals.VEHICLEBODYTYPE, vals.VEHICLEID, vals.VEHICLEMAKE,
                        vals.VEHICLEMODEL, vals.VEHICLEMOVEMENT, vals.VEHICLEREMOVEDBY, vals.VEHICLEREMOVEDTO,
                        vals.VEHICLETOWEDAWAY, vals.VEHICLEYEAR, vals.VIN);
                """, data
            )

        return ret

    @check_and_log('vehicleuse_dict')
    def _read_acrs_vehicle_use_data(self, vehicleuse_dict: List[VehicleUseType]) -> bool:
        """
        Populates acrs_vehicle_use table
        :param vehicleuse_dict: The dictionary of the ACRSVEHICLE from the VEHICLEUSEs tag
        """
        data = []
        for vehicleuse in vehicleuse_dict:
            data.append((
                self.get_single_attr('ID', vehicleuse),
                self._validate_uniqueidentifier(self.get_single_attr('VEHICLEID', vehicleuse)),
                self.get_single_attr('VEHICLEUSECODE', vehicleuse)
            ))

        ret: bool = True
        if data:
            ret = self._safe_sql_executemany(
                """
                MERGE acrs_vehicle_uses USING (
                VALUES
                    (?, ?, ?)
                ) as vals (ID, VEHICLEID, VEHICLEUSECODE)
                ON (acrs_vehicle_uses.ID = vals.ID AND
                    acrs_vehicle_uses.VEHICLEID = vals.VEHICLEID)
                WHEN MATCHED THEN
                    UPDATE SET
                    acrs_vehicle_uses.VEHICLEUSECODE = vals.VEHICLEUSECODE
                WHEN NOT MATCHED THEN
                INSERT (ID, VEHICLEID, VEHICLEUSECODE)
                VALUES (vals.ID, vals.VEHICLEID, vals.VEHICLEUSECODE);
                """, data
            )

        return ret

    @check_and_log('damaged_dict')
    def _read_damaged_areas_data(self, damaged_dict: List[DamagedAreaType]) -> bool:
        """
        Populates the acrs_damaged_areas table. Expects to be passed the OrderedDict of DAMAGEDAREAs
        :param damaged_dict: The dictionary of the ACRSVEHICLE
        """
        data = []
        for damagedarea in damaged_dict:
            data.append((
                self.get_single_attr('DAMAGEID', damagedarea),
                self.get_single_attr('IMPACTTYPE', damagedarea),
                self._validate_uniqueidentifier(self.get_single_attr('VEHICLEID', damagedarea))
            ))

        ret: bool = True
        if data:
            self._safe_sql_executemany(
                """
                MERGE acrs_damaged_areas USING (
                VALUES
                    (?, ?, ?)
                ) as vals (DAMAGEID, IMPACTTYPE, VEHICLEID)
                ON (acrs_damaged_areas.DAMAGEID = vals.DAMAGEID AND
                    acrs_damaged_areas.VEHICLEID = vals.VEHICLEID)
                WHEN MATCHED THEN
                    UPDATE SET
                    IMPACTTYPE = vals.IMPACTTYPE
                WHEN NOT MATCHED THEN
                    INSERT (DAMAGEID, IMPACTTYPE, VEHICLEID)
                    VALUES (vals.DAMAGEID, vals.IMPACTTYPE, vals.VEHICLEID);
                """, data
            )

        return ret

    @check_and_log('witness_dict')
    def _read_witness_data(self, witness_dict: List[
        WitnessType]) -> bool:  # pylint:disable=unsubscriptable-object ; see comment at top
        """
        Populates the acrs_witnesses table
        :param witness_dict: The list of OrderedDicts from the WITNESSes tag
        """
        data = []
        for witness in witness_dict:
            if witness.get('PERSON'):
                self._read_acrs_person_data([witness['PERSON']])

            data.append((
                self._validate_uniqueidentifier(self.get_single_attr('PERSONID', witness)),
                self.get_single_attr('REPORTNUMBER', witness)
            ))

        ret: bool = True
        if data:
            ret = self._safe_sql_executemany(
                """
                MERGE acrs_witnesses USING (
                VALUES
                    (?, ?)
                ) as vals (PERSONID, REPORTNUMBER)
                ON (acrs_witnesses.PERSONID = vals.PERSONID AND
                    acrs_witnesses.REPORTNUMBER = vals.REPORTNUMBER)
                WHEN NOT MATCHED THEN
                    INSERT (PERSONID, REPORTNUMBER)
                    VALUES (vals.PERSONID, vals.REPORTNUMBER);
                """, data
            )

        return ret

    @staticmethod
    def is_element_nil(
            element: Optional[OrderedDict]) -> bool:  # pylint:disable=unsubscriptable-object ; see comment at top
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
               element.get('@i:nil') == 'true'  # pylist:disable=isinstance-second-argument-not-valid-type ; see comment

    @staticmethod
    def _convert_to_date(val: Optional[str]) -> str:  # pylint:disable=unsubscriptable-object ; see comment at top
        """Converts XML datetime to sql date (YYYY-MM-DDThh:mm:ss.fffffff with optional microseconds to YYYYMMDD"""
        if val is None:
            return ''
        converted = to_datetime(val)
        return converted.strftime('%Y-%m-%d')

    @staticmethod
    def _convert_to_bool(val) -> Optional[int]:  # pylint:disable=unsubscriptable-object ; see comment at top
        """
        Converts the XML style 'y', 'n', and 'u' (unknown) to a bit value
        :param val: Value to convert to a bool
        :return: Either True, False, or None (if the input was empty or 'u' for unknown)
        """
        if not val:
            return None

        val = val.lower()
        if val not in ['y', 'n', 'u']:
            raise AssertionError('Expected y or n and got {}'.format(val))
        if val == 'u':
            return None
        return int(bool(val == 'y'))

    @staticmethod
    def _validate_uniqueidentifier(uid: Optional[str]) -> Optional[
        str]:  # pylint:disable=unsubscriptable-object ; see comment at top
        """Checks for null uniqueidentifiers"""
        if not uid:
            return None
        return uid

    def _safe_sql_execute(self, query: str, data: SqlExecuteType) -> bool:
        return self._safe_sql(query, data, False)

    def _safe_sql_executemany(self, query: str, data: SqlExecuteType) -> bool:
        return self._safe_sql(query, data, True)

    def _safe_sql(self,
                  query: str,
                  data: Sequence,
                  many: bool) -> bool:
        """
        Executes a sql query and checks for things that normally error out
        :param query: The query to run
        :param data: The list of data to use. For executemany, it should be a list of tuples. For execute, it should be
        a list of the data elements to insert
        :param many: True if executemany. False if execute
        :return: True if success. False if it failed.
        """
        if not data:
            return True

        try:
            print(query, data)
            if many:
                self.cursor.executemany(query, data)
            else:
                self.cursor.execute(query, data)
        except (pyodbc.ProgrammingError, pyodbc.DataError, pyodbc.IntegrityError) as err:
            LOGGER.error('SQL data error: %s\nError: %s\nQuery: %s', data, err, query)
            traceback.print_stack()
            return False

        self.cursor.commit()
        return True

    def get_single_attr(self,
                        tag: str,
                        crash_data: Mapping
                        ) -> Optional[str]:  # pylint:disable=unsubscriptable-object ; see comment at top
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

        if not isinstance(crash_data.get(tag), str):
            raise AssertionError('Expected {} to have only a single element'.format(tag))
        return crash_data.get(tag)
