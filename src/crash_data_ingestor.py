"""Processes unprocessed data in the network share that holds crash data"""
# pylint:disable=too-many-lines
import logging
import os
import shutil
import traceback
from collections import OrderedDict
from typing import Optional, List, Sequence, Union, Tuple, Any

from pandas import to_datetime  # type: ignore
import pyodbc  # type: ignore
import xmltodict  # type: ignore

from . import crash_data_types

# The 'unsubscriptable-object' disable is because of issue https://github.com/PyCQA/pylint/issues/3882 with subscripting
# Optional. When thats fixed, we can remove those disables.

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


class CrashDataReader:  # pylint:disable=too-many-instance-attributes
    """ Reads a directory of ACRS crash data files"""

    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.root: Optional[str] = None  # pylint:disable=unsubscriptable-object ; see comment at top
        conn = pyodbc.connect(r'Driver={SQL Server};Server=balt-sql311-prd;Database=DOT_DATA;Trusted_Connection=yes;')
        self.cursor = conn.cursor()

        # Table names
        self.approval_table = 'acrs_approval'
        self.circumstance_table = 'acrs_circumstances'
        self.citation_codes_table = 'acrs_citation_codes'
        self.crash_diagrams_table = 'acrs_crash_diagrams'
        self.crashes_table = 'acrs_crashes'
        self.commercial_vehicles_table = 'acrs_commercial_vehicles'
        self.damaged_areas_table = 'acrs_damaged_areas'
        self.ems_table = 'acrs_ems'
        self.events_table = 'acrs_events'
        self.pdf_table = 'acrs_pdf_report'
        self.person_table = 'acrs_person'
        self.person_info_table = 'acrs_person_info'
        self.roadway_table = 'acrs_roadway'
        self.towed_unit_table = 'acrs_towed_unit'
        self.vehicle_table = 'acrs_vehicles'
        self.vehicle_users_table = 'acrs_vehicle_uses'
        self.witnesses_table = 'acrs_witnesses'

    def read_directory(self, path: str = '//balt-fileld-srv.baltimore.city/GIS/DOT-BPD') -> None:
        """
        Reads a directory of XML ACRS crash files, and returns an iterator of the parsed data
        :param path: Path to search for XML files
        :return:
        """
        processed_folder = os.path.join(path, 'processed')
        if not os.path.exists(processed_folder):
            os.mkdir(processed_folder)

        for acrs_file in os.listdir(path):
            if acrs_file.endswith('.xml'):
                self.read_crash_data(os.path.join(path, acrs_file), processed_folder)

    def _read_file(self, file_name: str) -> crash_data_types.CrashDataType:
        with open(file_name, encoding='utf-8') as acrs_file:
            crash_file = acrs_file.read()

        # Some of these files have non ascii at the beginning that causes parse errors
        offset = crash_file.find('<?xml')
        self.root = xmltodict.parse(crash_file[offset:])
        self.root.pop('@xmlns:i')
        self.root.pop('@xmlns')
        return self.root['REPORT']

    def read_crash_data(self, file_name: str, processed_dir: str) -> bool:
        """
        Reads the ACRS crash data files
        :param processed_dir: Directory to move the ACRS file after being processed
        :param file_name: Full path to the file to process
        :return: True if the file was inserted into the database, false if there was an error
        """
        self.log.info('Processing %s', file_name)
        crash_dict = self._read_file(file_name)

        # use short circuit logic to cut this off early if any of these fail
        self._read_approval_data(crash_dict.pop('APPROVALDATA'))
        self._read_circumstance_data(crash_dict.pop('CIRCUMSTANCES'))
        self._read_crash_diagrams_data(crash_dict.pop('DIAGRAM'))
        self._read_ems_data(crash_dict.pop('EMSes'))
        self._read_pdf_data(crash_dict.pop('PDFREPORTs'))
        self._read_report_documents_data(crash_dict.pop('REPORTDOCUMENTs'))
        self._read_report_photos_data(crash_dict.pop('REPORTPHOTOes'))
        self._read_roadway_data(crash_dict.pop('ROADWAY'))
        self._read_acrs_person_data(crash_dict.pop('People'))
        self._read_acrs_vehicle_data(crash_dict.pop('VEHICLEs'))
        self._read_person_info_data(crash_dict.pop('NONMOTORISTs'), 'NONMOTORIST')
        self._read_witness_data(crash_dict.pop('WITNESSes'))
        self._read_main_crash_data(crash_dict)

        if len(crash_dict) == 0:
            self.log.debug('Crash dict is fully processed')
        else:
            self.log.info('REMAINING ELEMENTS: %s', crash_dict)

        self._file_move(file_name, processed_dir)
        return True

    def _file_move(self, file_name, processed_dir):
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
                    self.log.error('Error moving file. It will not be moved to the processed directory: %s', file_name)

    def _read_main_crash_data(self, crash_dict: crash_data_types.CrashDataType) -> bool:
        """ Populates the acrs_crashes table """
        self.log.debug('Processing main crash data')

        if self.is_element_nil(crash_dict):
            self.log.warning('No data in the main crash data')
            return False

        data = [
            self.get_single_attr('ACRSREPORTTIMESTAMP', crash_dict),
            self.get_single_attr('AGENCYIDENTIFIER', crash_dict),
            self.get_single_attr('AGENCYNAME', crash_dict),
            self.get_single_attr('AREA', crash_dict),
            self.get_single_attr('COLLISIONTYPE', crash_dict),
            self.get_single_attr('CONMAINCLOSURE', crash_dict),
            self.get_single_attr('CONMAINLOCATION', crash_dict),
            self._convert_to_bool(self.get_single_attr('CONMAINWORKERSPRESENT', crash_dict)),
            self.get_single_attr('CONMAINZONE', crash_dict),
            self._convert_to_date(self.get_single_attr('CRASHDATE', crash_dict)),
            self.get_single_attr('CRASHTIME', crash_dict),
            self.get_single_attr('CURRENTASSIGNMENT', crash_dict),
            self.get_single_attr('CURRENTGROUP', crash_dict),
            self.get_single_attr('DEFAULTASSIGNMENT', crash_dict),
            self.get_single_attr('DEFAULTGROUP', crash_dict),
            self.get_single_attr('DOCTYPE', crash_dict),
            self.get_single_attr('FIXEDOBJECTSTRUCK', crash_dict),
            self.get_single_attr('HARMFULEVENTONE', crash_dict),
            self.get_single_attr('HARMFULEVENTTWO', crash_dict),
            self._convert_to_bool(self.get_single_attr('HITANDRUN', crash_dict)),
            self.get_single_attr('INSERTDATE', crash_dict),
            self.get_single_attr('INTERCHANGEAREA', crash_dict),
            self.get_single_attr('INTERCHANGEIDENTIFICATION', crash_dict),
            self.get_single_attr('INTERSECTIONTYPE', crash_dict),
            self.get_single_attr('INVESTIGATINGOFFICERUSERNAME', crash_dict),
            self.get_single_attr('INVESTIGATOR', crash_dict),
            self.get_single_attr('JUNCTION', crash_dict),
            self.get_single_attr('LANEDIRECTION', crash_dict),
            self.get_single_attr('LANENUMBER', crash_dict),
            self.get_single_attr('LANETYPE', crash_dict),
            self.get_single_attr('LATITUDE', crash_dict),
            self.get_single_attr('LIGHT', crash_dict),
            self.get_single_attr('LOCALCASENUMBER', crash_dict),
            self.get_single_attr('LOCALCODES', crash_dict),
            self.get_single_attr('LONGITUDE', crash_dict),
            self.get_single_attr('MILEPOINTDIRECTION', crash_dict),
            self.get_single_attr('MILEPOINTDISTANCE', crash_dict),
            self.get_single_attr('MILEPOINTDISTANCEUNITS', crash_dict),
            self.get_single_attr('NARRATIVE', crash_dict),
            self._convert_to_bool(self.get_single_attr('NONTRAFFIC', crash_dict)),
            self.get_single_attr('NUMBEROFLANES', crash_dict),
            self.get_single_attr('OFFROADDESCRIPTION', crash_dict),
            self._convert_to_bool(self.get_single_attr('PHOTOSTAKEN', crash_dict)),
            self.get_single_attr('RAMP', crash_dict),
            self.get_single_attr('REPORTCOUNTYLOCATION', crash_dict),
            self.get_single_attr('REPORTNUMBER', crash_dict),
            self.get_single_attr('REPORTTYPE', crash_dict),
            self.get_single_attr('ROADALIGNMENT', crash_dict),
            self.get_single_attr('ROADCONDITION', crash_dict),
            self.get_single_attr('ROADDIVISION', crash_dict),
            self.get_single_attr('ROADGRADE', crash_dict),
            self.get_single_attr('ROADID', crash_dict),
            self.get_single_attr('SCHOOLBUSINVOLVEMENT', crash_dict),
            self.get_single_attr('STATEGOVERNMENTPROPERTYNAME', crash_dict),
            self.get_single_attr('SUPERVISOR', crash_dict),
            self.get_single_attr('SUPERVISORUSERNAME', crash_dict),
            self.get_single_attr('SUPERVISORYDATE', crash_dict),
            self.get_single_attr('SURFACECONDITION', crash_dict),
            self.get_single_attr('TRAFFICCONTROL', crash_dict),
            self._convert_to_bool(self.get_single_attr('TRAFFICCONTROLFUNCTIONING', crash_dict)),
            self.get_single_attr('UPDATEDATE', crash_dict),
            self.get_single_attr('UPLOADVERSION', crash_dict),
            self.get_single_attr('VERSIONNUMBER', crash_dict),
            self.get_single_attr('WEATHER', crash_dict)
        ]

        ret: bool = True
        if data:
            ret = self._safe_sql_execute(
                """
                MERGE {table_name} USING (
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
                ON ({table_name}.REPORTNUMBER = vals.REPORTNUMBER)
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
                """.format(table_name=self.crashes_table), data)

        return ret

    def _read_approval_data(self,
                            approval_dict: Optional[crash_data_types.ApprovalDataType]  # pylint:disable=unsubscriptable-object ; see comment at top
                            ) -> bool:
        """
        Populates the acrs_approval table
        :param approval_dict: The ordereddict contained in the APPROVALDATA tag
        """
        self.log.debug('Processing approval data')

        if self.is_element_nil(approval_dict):
            self.log.warning('No approval data')
            return False

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
                MERGE {table_name} USING (
                VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ) AS vals (AGENCY, DATE, CADSENT, CADSENT_DATE, CC_NUMBER, DATE_INITIATED2, GROUP_NUMBER,
                HISTORICALAPPROVALDATA, INCIDENT_DATE, INVESTIGATOR, REPORT_TYPE, SEQ_GUID, STATUS_CHANGE_DATE,
                STATUS_ID, STEP_NUMBER, TR_USERNAME, UNIT_CODE)
                ON ({table_name}.SEQ_GUID = vals.SEQ_GUID AND
                    {table_name}.CC_NUMBER = vals.CC_NUMBER)
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
                """.format(table_name=self.approval_table), data
            )

        return ret

    def _read_circumstance_data(
            self,
            circumstance_dict: Optional[List[crash_data_types.CircumstancesType]]  # pylint:disable=unsubscriptable-object ; see comment at top
            ) -> bool:
        """
        Populates the acrs_circumstances table
        :param circumstance_dict: List of CIRCUMSTANCE tags contained in the CIRCUMSTANCES tag
        """
        self.log.debug('Processing circumstance data')

        if self.is_element_nil(circumstance_dict):
            self.log.warning('No circumstance data')
            return False

        data = []
        for circumstance in self.get_multiple_attr('CIRCUMSTANCE', circumstance_dict):
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
                MERGE {table_name} USING (
                VALUES
                    (?, ?, ?, ?, ?, ?)
                ) as vals (CIRCUMSTANCECODE, CIRCUMSTANCEID, CIRCUMSTANCETYPE, PERSONID, REPORTNUMBER, VEHICLEID)
                ON ({table_name}.CIRCUMSTANCEID = vals.CIRCUMSTANCEID AND
                    {table_name}.REPORTNUMBER = vals.REPORTNUMBER)
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
                """.format(table_name=self.circumstance_table), data
            )

        return ret

    def _read_citation_data(self, citation_dict: List[crash_data_types.CitationType]) -> bool:
        """ Populates the acrs_citation_codes table """
        self.log.debug('Processing citation data')

        if self.is_element_nil(citation_dict):
            self.log.warning('No citation data')
            return False

        data = []
        for citation in self.get_multiple_attr('CITATIONCODE', citation_dict):
            data.append((
                self.get_single_attr('CITATIONNUMBER', citation),
                self._validate_uniqueidentifier(self.get_single_attr('PERSONID', citation)),
                self.get_single_attr('REPORTNUMBER', citation)
            ))

        ret: bool = True
        if data:
            ret = self._safe_sql_executemany(
                """
                MERGE {table_name} USING (
                VALUES
                    (?, ?, ?)
                ) as vals (CITATIONNUMBER, PERSONID, REPORTNUMBER)
                ON ({table_name}.CITATIONNUMBER = vals.CITATIONNUMBER AND
                    {table_name}.REPORTNUMBER = vals.REPORTNUMBER AND
                    {table_name}.PERSONID = vals.PERSONID
                )
                WHEN NOT MATCHED THEN
                    INSERT (CITATIONNUMBER, PERSONID, REPORTNUMBER)
                    VALUES (vals.CITATIONNUMBER, vals.PERSONID, vals.REPORTNUMBER);
                """.format(table_name=self.citation_codes_table), data
            )

        return ret

    def _read_crash_diagrams_data(self,
                                  crash_diagram_dict: Optional[crash_data_types.CrashDiagramType]  # pylint:disable=unsubscriptable-object ; see comment at top
                                  ) -> bool:
        """
        Populates the acrs_crash_diagrams table
        :param crash_diagram_dict: OrderedDict from the DIAGRAM tag
        """
        self.log.debug('Processing crash diagrams data')

        if self.is_element_nil(crash_diagram_dict):
            self.log.warning('No crash diagrams data')
            return False

        data = [
            self.get_single_attr('CRASHDIAGRAM', crash_diagram_dict),
            self.get_single_attr('CRASHDIAGRAMNATIVE', crash_diagram_dict),
            self.get_single_attr('REPORTNUMBER', crash_diagram_dict),
        ]

        ret: bool = True
        if data:
            ret = self._safe_sql_execute(
                """
                MERGE {table_name} USING (
                VALUES
                    (?, ?, ?)
                ) as vals (CRASHDIAGRAM, CRASHDIAGRAMNATIVE, REPORTNUMBER)
                ON ({table_name}.REPORTNUMBER = vals.REPORTNUMBER)
                WHEN MATCHED THEN
                    UPDATE SET
                    CRASHDIAGRAM = vals.CRASHDIAGRAM,
                    CRASHDIAGRAMNATIVE = vals.CRASHDIAGRAMNATIVE
                WHEN NOT MATCHED THEN
                    INSERT (CRASHDIAGRAM, CRASHDIAGRAMNATIVE, REPORTNUMBER)
                    VALUES (vals.CRASHDIAGRAM, vals.CRASHDIAGRAMNATIVE, vals.REPORTNUMBER);
                """.format(table_name=self.crash_diagrams_table), data
            )

        return ret

    def _read_ems_data(self,
                       ems_dict: Optional[List[crash_data_types.EmsType]]  # pylint:disable=unsubscriptable-object ; see comment at top
                       ) -> bool:
        """
        Populates the acrs_ems table from the EMSes tag
        :param ems_dict: List of OrderedDicts contained in the EMSes tag
        """
        self.log.debug('Processing EMS data')

        if self.is_element_nil(ems_dict):
            self.log.warning('No EMS data')
            return False

        data = []
        for ems in self.get_multiple_attr('EMS', ems_dict):
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
                MERGE {table_name} USING (
                VALUES
                    (?, ?, ?, ?, ?)
                ) as vals (EMSTRANSPORTATIONTYPE, EMSUNITNUMBER, INJUREDTAKENBY, INJUREDTAKENTO, REPORTNUMBER)
                ON ({table_name}.EMSUNITNUMBER = vals.EMSUNITNUMBER AND
                    {table_name}.REPORTNUMBER = vals.REPORTNUMBER)
                WHEN MATCHED THEN
                    UPDATE SET
                    {table_name}.EMSTRANSPORTATIONTYPE = vals.EMSTRANSPORTATIONTYPE,
                    {table_name}.INJUREDTAKENBY = vals.INJUREDTAKENBY,
                    {table_name}.INJUREDTAKENTO = vals.INJUREDTAKENTO
                WHEN NOT MATCHED THEN
                INSERT (EMSTRANSPORTATIONTYPE, EMSUNITNUMBER, INJUREDTAKENBY, INJUREDTAKENTO, REPORTNUMBER)
                VALUES (vals.EMSTRANSPORTATIONTYPE, vals.EMSUNITNUMBER, vals.INJUREDTAKENBY, vals.INJUREDTAKENTO,
                vals.REPORTNUMBER);
                """.format(table_name=self.ems_table), data
            )

        return ret

    def _read_commercial_vehicle_data(self,
                                      commvehicle_dict: crash_data_types.CommercialVehiclesType  # pylint:disable=unsubscriptable-object ; see comment at top
                                      ) -> bool:
        """
        Populates the acrs_commercial_vehicle table
        :param commvehicle_dict: The dictionary of the ACRSVEHICLE
        :return:
        """
        self.log.debug('Processing commercial vehicle data')

        if self.is_element_nil(commvehicle_dict):
            self.log.warning('No commercial vehicle data')
            return False

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
                MERGE {table_name} USING (
                VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ) as vals (BODYTYPE, BUSUSE, CARRIERCLASSIFICATION, CITY, CONFIGURATION, COUNTRY, DOTNUMBER, GVW,
                HAZMATCLASS, HAZMATNAME, HAZMATNUMBER, HAZMATSPILL, MCNUMBER, NAME, NUMBEROFAXLES, PLACARDVISIBLE,
                POSTALCODE, STATE, STREET, VEHICLEID, WEIGHT, WEIGHTUNIT)
                ON ({table_name}.VEHICLEID = vals.VEHICLEID)
                WHEN MATCHED THEN
                    UPDATE SET
                    {table_name}.BODYTYPE = vals.BODYTYPE,
                    {table_name}.BUSUSE = vals.BUSUSE,
                    {table_name}.CARRIERCLASSIFICATION = vals.CARRIERCLASSIFICATION,
                    {table_name}.CITY = vals.CITY,
                    {table_name}.CONFIGURATION = vals.CONFIGURATION,
                    {table_name}.COUNTRY = vals.COUNTRY,
                    {table_name}.DOTNUMBER = vals.DOTNUMBER,
                    {table_name}.GVW = vals.GVW,
                    {table_name}.HAZMATCLASS = vals.HAZMATCLASS,
                    {table_name}.HAZMATNAME = vals.HAZMATNAME,
                    {table_name}.HAZMATNUMBER = vals.HAZMATNUMBER,
                    {table_name}.HAZMATSPILL = vals.HAZMATSPILL,
                    {table_name}.MCNUMBER = vals.MCNUMBER,
                    {table_name}.NAME = vals.NAME,
                    {table_name}.NUMBEROFAXLES = vals.NUMBEROFAXLES,
                    {table_name}.PLACARDVISIBLE = vals.PLACARDVISIBLE,
                    {table_name}.POSTALCODE = vals.POSTALCODE,
                    {table_name}.STATE = vals.STATE,
                    {table_name}.STREET = vals.STREET,
                    {table_name}.WEIGHT = vals.WEIGHT,
                    {table_name}.WEIGHTUNIT = vals.WEIGHTUNIT
                WHEN NOT MATCHED THEN
                    INSERT (BODYTYPE, BUSUSE, CARRIERCLASSIFICATION, CITY, CONFIGURATION, COUNTRY, DOTNUMBER, GVW,
                        HAZMATCLASS, HAZMATNAME, HAZMATNUMBER, HAZMATSPILL, MCNUMBER, NAME, NUMBEROFAXLES,
                        PLACARDVISIBLE, POSTALCODE, STATE, STREET, VEHICLEID, WEIGHT, WEIGHTUNIT)
                    VALUES (vals.BODYTYPE, vals.BUSUSE, vals.CARRIERCLASSIFICATION, vals.CITY, vals.CONFIGURATION,
                        vals.COUNTRY, vals.DOTNUMBER, vals.GVW, vals.HAZMATCLASS, vals.HAZMATNAME, vals.HAZMATNUMBER,
                        vals.HAZMATSPILL, vals.MCNUMBER, vals.NAME, vals.NUMBEROFAXLES, vals.PLACARDVISIBLE,
                        vals.POSTALCODE, vals.STATE, vals.STREET, vals.VEHICLEID, vals.WEIGHT, vals.WEIGHTUNIT);
                """.format(table_name=self.commercial_vehicles_table), data
            )

        return ret

    def _read_event_data(self,
                         event_dict: Optional[List[crash_data_types.EventType]]  # pylint:disable=unsubscriptable-object ; see comment at top
                         ) -> bool:
        """
        Populates the acrs_events table from the EVENTS tag
        :param event_dict: The dictionary of the ACRSVEHICLE
        """
        self.log.debug('Processing event data')

        if self.is_element_nil(event_dict):
            self.log.warning('No event data')
            return False

        data = []
        for event in self.get_multiple_attr('EVENT', event_dict):
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
                MERGE {table_name} USING (
                VALUES
                    (?, ?, ?, ?)
                ) as vals (EVENTID, EVENTSEQUENCE, EVENTTYPE, VEHICLEID)
                ON ({table_name}.EVENTID = vals.EVENTID AND
                    {table_name}.VEHICLEID = vals.VEHICLEID)
                WHEN MATCHED THEN
                    UPDATE SET
                    {table_name}.EVENTSEQUENCE = vals.EVENTSEQUENCE,
                    {table_name}.EVENTTYPE = vals.EVENTTYPE
                WHEN NOT MATCHED THEN
                    INSERT (EVENTID, EVENTSEQUENCE, EVENTTYPE, VEHICLEID)
                    VALUES (vals.EVENTID, vals.EVENTSEQUENCE, vals.EVENTTYPE, vals.VEHICLEID);
                """.format(table_name=self.events_table), data
            )

        return ret

    def _read_pdf_data(self,
                       pdfreport_dict: Optional[List[crash_data_types.PdfReportData]]  # pylint:disable=unsubscriptable-object ; see comment at top
                       ) -> bool:
        """
        Populates the acrs_pdf_report table from the PDFREPORTs tag
        :param pdfreport_dict: List of OrderedDicts from the PDFREPORTs tag
        """
        self.log.debug('Processing PDF data')

        if self.is_element_nil(pdfreport_dict):
            self.log.warning('No PDF data')
            return False

        data = []
        for report in self.get_multiple_attr('PDFREPORT', pdfreport_dict):
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
                MERGE {table_name} USING (
                VALUES
                    (?, ?, ?, ?, ?, ?)
                ) as vals (CHANGEDBY, DATESTATUSCHANGED, PDFREPORT1, PDF_ID, REPORTNUMBER, STATUS)
                ON ({table_name}.PDF_ID = vals.PDF_ID AND
                    {table_name}.REPORTNUMBER = vals.REPORTNUMBER)
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
                """.format(table_name=self.pdf_table), data
            )

        return ret

    def _read_acrs_person_data(self,
                               person_dict: Optional[crash_data_types.PersonType]  # pylint:disable=unsubscriptable-object ; see comment at top
                               ) -> bool:
        """
        Processes the ACRSPERSON tag contents
        :param person_dict: OrderedDict from the PERSON, OWNER, PASSENGER, or NONMOTORIST tags
        """
        self.log.debug('Processing person data')

        if self.is_element_nil(person_dict):
            self.log.warning('No person data')
            return False

        citation_codes: List[crash_data_types.CitationType] = person_dict.pop('CITATIONCODES')
        if citation_codes:
            self._read_citation_data(citation_codes)

        data = [
            self.get_single_attr('ADDRESS', person_dict),
            self.get_single_attr('CITY', person_dict),
            self.get_single_attr('COMPANY', person_dict),
            self.get_single_attr('COUNTRY', person_dict),
            self.get_single_attr('COUNTY', person_dict),
            self.get_single_attr('DLCLASS', person_dict),
            self.get_single_attr('DLNUMBER', person_dict),
            self.get_single_attr('DLSTATE', person_dict),
            self.get_single_attr('DOB', person_dict),
            self.get_single_attr('FIRSTNAME', person_dict),
            self.get_single_attr('HOMEPHONE', person_dict),
            self.get_single_attr('LASTNAME', person_dict),
            self.get_single_attr('MIDDLENAME', person_dict),
            self.get_single_attr('OTHERPHONE', person_dict),
            self._validate_uniqueidentifier(self.get_single_attr('PERSONID', person_dict)),
            self.get_single_attr('RACE', person_dict),
            self.get_single_attr('REPORTNUMBER', person_dict),
            self.get_single_attr('SEX', person_dict),
            self.get_single_attr('STATE', person_dict),
            self.get_single_attr('ZIP', person_dict)
        ]

        ret: bool = True
        if data:
            ret = self._safe_sql_execute(
                """
                MERGE {table_name} USING (
                VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ) as vals (ADDRESS, CITY, COMPANY, COUNTRY, COUNTY, DLCLASS, DLNUMBER, DLSTATE, DOB, FIRSTNAME,
                HOMEPHONE, LASTNAME, MIDDLENAME, OTHERPHONE, PERSONID, RACE, REPORTNUMBER, SEX, STATE, ZIP)
                ON ({table_name}.REPORTNUMBER = vals.REPORTNUMBER AND
                    {table_name}.PERSONID = vals.PERSONID)
                WHEN MATCHED THEN
                    UPDATE SET
                    {table_name}.ADDRESS = vals.ADDRESS,
                    {table_name}.CITY = vals.CITY,
                    {table_name}.COMPANY = vals.COMPANY,
                    {table_name}.COUNTRY = vals.COUNTRY,
                    {table_name}.COUNTY = vals.COUNTY,
                    {table_name}.DLCLASS = vals.DLCLASS,
                    {table_name}.DLNUMBER = vals.DLNUMBER,
                    {table_name}.DLSTATE = vals.DLSTATE,
                    {table_name}.DOB = vals.DOB,
                    {table_name}.FIRSTNAME = vals.FIRSTNAME,
                    {table_name}.HOMEPHONE = vals.HOMEPHONE,
                    {table_name}.LASTNAME = vals.LASTNAME,
                    {table_name}.MIDDLENAME = vals.MIDDLENAME,
                    {table_name}.OTHERPHONE = vals.OTHERPHONE,
                    {table_name}.PERSONID = vals.PERSONID,
                    {table_name}.RACE = vals.RACE,
                    {table_name}.REPORTNUMBER = vals.REPORTNUMBER,
                    {table_name}.SEX = vals.SEX,
                    {table_name}.STATE = vals.STATE,
                    {table_name}.ZIP = vals.ZIP
                WHEN NOT MATCHED THEN
                    INSERT (ADDRESS, CITY, COMPANY, COUNTRY, COUNTY, DLCLASS, DLNUMBER, DLSTATE, DOB, FIRSTNAME,
                    HOMEPHONE, LASTNAME, MIDDLENAME, OTHERPHONE, PERSONID, RACE, REPORTNUMBER, SEX, STATE, ZIP)
                    VALUES (vals.ADDRESS, vals.CITY, vals.COMPANY, vals.COUNTRY, vals.COUNTY, vals.DLCLASS,
                    vals.DLNUMBER, vals.DLSTATE, vals.DOB, vals.FIRSTNAME, vals.HOMEPHONE, vals.LASTNAME,
                    vals.MIDDLENAME, vals.OTHERPHONE, vals.PERSONID, vals.RACE, vals.REPORTNUMBER, vals.SEX, vals.STATE,
                    vals.ZIP);
                """.format(table_name=self.person_table), data
            )

        return ret

    def _read_person_info_data(
            self,
            person_dict: Optional[List[crash_data_types.PersonInfoType]], tag: str  # pylint:disable=unsubscriptable-object ; see comment at top
            ) -> bool:
        """
        Populates the acrs_person_info table.
        :param person_dict: Contains the list of OrderedDicts contained in the drivers, passengers and nonmotorists tags
        :param tag: The many tag to iterate over. Should be either DRIVER, PASSENGER or NONMOTORIST
        """
        self.log.debug('Processing person info data')

        assert tag in ['DRIVER', 'PASSENGER', 'NONMOTORIST']

        if self.is_element_nil(person_dict):
            logging.error('No person data to load')
            return False

        data = []
        for person in self.get_multiple_attr(tag, person_dict):
            report_no = self.get_single_attr('REPORTNUMBER', person.get('PERSON'))
            if not self._read_acrs_person_data(person.get('PERSON')):
                return False

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
                MERGE {table_name} USING (
                VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ) AS vals (AIRBAGDEPLOYED, ALCOHOLTESTINDICATOR, ALCOHOLTESTTYPE, ATFAULT, BAC, CONDITION,
                CONTINUEDIRECTION, DRIVERDISTRACTEDBY, DRUGTESTINDICATOR, DRUGTESTRESULT, EJECTION, EMSRUNREPORTNUMBER,
                EMSUNITNUMBER, EQUIPMENTPROBLEM, GOINGDIRECTION, HASCDL, INJURYSEVERITY, PEDESTRIANACTIONS,
                PEDESTRIANLOCATION, PEDESTRIANMOVEMENT, PEDESTRIANOBEYTRAFFICSIGNAL, PEDESTRIANTYPE,
                PEDESTRIANVISIBILITY, PERSONID, REPORTNUMBER, SAFETYEQUIPMENT, SEAT, SEATINGLOCATION, SEATINGROW,
                SUBSTANCEUSE, UNITNUMBERFIRSTSTRIKE, VEHICLEID)
                ON ({table_name}.EMSRUNREPORTNUMBER = vals.EMSRUNREPORTNUMBER AND
                {table_name}.PERSONID = vals.PERSONID AND
                {table_name}.VEHICLEID = vals.VEHICLEID)
                WHEN MATCHED THEN
                    UPDATE SET
                    {table_name}.AIRBAGDEPLOYED = vals.AIRBAGDEPLOYED,
                    {table_name}.ALCOHOLTESTINDICATOR = vals.ALCOHOLTESTINDICATOR,
                    {table_name}.ALCOHOLTESTTYPE = vals.ALCOHOLTESTTYPE,
                    {table_name}.ATFAULT = vals.ATFAULT,
                    {table_name}.BAC = vals.BAC,
                    {table_name}.CONDITION = vals.CONDITION,
                    {table_name}.CONTINUEDIRECTION = vals.CONTINUEDIRECTION,
                    {table_name}.DRIVERDISTRACTEDBY = vals.DRIVERDISTRACTEDBY,
                    {table_name}.DRUGTESTINDICATOR = vals.DRUGTESTINDICATOR,
                    {table_name}.DRUGTESTRESULT = vals.DRUGTESTRESULT,
                    {table_name}.EJECTION = vals.EJECTION,
                    {table_name}.EMSRUNREPORTNUMBER = vals.EMSRUNREPORTNUMBER,
                    {table_name}.EMSUNITNUMBER = vals.EMSUNITNUMBER,
                    {table_name}.EQUIPMENTPROBLEM = vals.EQUIPMENTPROBLEM,
                    {table_name}.GOINGDIRECTION = vals.GOINGDIRECTION,
                    {table_name}.HASCDL = vals.HASCDL,
                    {table_name}.INJURYSEVERITY = vals.INJURYSEVERITY,
                    {table_name}.PEDESTRIANACTIONS = vals.PEDESTRIANACTIONS,
                    {table_name}.PEDESTRIANLOCATION = vals.PEDESTRIANLOCATION,
                    {table_name}.PEDESTRIANMOVEMENT = vals.PEDESTRIANMOVEMENT,
                    {table_name}.PEDESTRIANOBEYTRAFFICSIGNAL = vals.PEDESTRIANOBEYTRAFFICSIGNAL,
                    {table_name}.PEDESTRIANTYPE = vals.PEDESTRIANTYPE,
                    {table_name}.PEDESTRIANVISIBILITY = vals.PEDESTRIANVISIBILITY,
                    {table_name}.PERSONID = vals.PERSONID,
                    {table_name}.REPORTNUMBER = vals.REPORTNUMBER,
                    {table_name}.SAFETYEQUIPMENT = vals.SAFETYEQUIPMENT,
                    {table_name}.SEAT = vals.SEAT,
                    {table_name}.SEATINGLOCATION = vals.SEATINGLOCATION,
                    {table_name}.SEATINGROW = vals.SEATINGROW,
                    {table_name}.SUBSTANCEUSE = vals.SUBSTANCEUSE,
                    {table_name}.UNITNUMBERFIRSTSTRIKE = vals.UNITNUMBERFIRSTSTRIKE,
                    {table_name}.VEHICLEID = vals.VEHICLEID
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
                """.format(table_name=self.person_info_table), data
            )

        return ret

    def _read_report_documents_data(
            self,
            reportdoc_dict: Optional[List[crash_data_types.ReportDocument]]):  # pylint:disable=unsubscriptable-object ; see comment at top
        """Populates the acrs_report_docs table. Currently a stub until we get the schema or example data for this"""

    def _read_report_photos_data(self,
                                 reportphotos_dict: Optional[List[crash_data_types.ReportPhoto]]):  # pylint:disable=unsubscriptable-object ; see comment at top
        """Populates the acrs_report_photos table. Currently a stub until we get the schema or example data for this"""

    def _read_roadway_data(self,
                           roadway_dict: Optional[crash_data_types.RoadwayType]) -> bool:  # pylint:disable=unsubscriptable-object ; see comment at top
        """
        Populates the acrs_roadway table. Expects the ROADWAY tag contents
        :param roadway_dict: OrderedDict from the ROADWAY tag
        """
        self.log.debug('Processing roadway data')

        if self.is_element_nil(roadway_dict):
            self.log.warning('No roadway data')
            return False

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
                MERGE {table_name} USING (
                VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ) as vals ( COUNTY, LOGMILE_DIR, MILEPOINT, MUNICIPAL, MUNICIPAL_AREA_CODE, REFERENCE_MUNI,
                REFERENCE_ROADNAME, REFERENCE_ROUTE_NUMBER, REFERENCE_ROUTE_SUFFIX, REFERENCE_ROUTE_TYPE, ROADID,
                ROAD_NAME, ROUTE_NUMBER, ROUTE_SUFFIX, ROUTE_TYPE)
                ON ({table_name}.roadid = vals.roadid )
                WHEN MATCHED THEN
                    UPDATE SET
                    {table_name}.COUNTY = vals.COUNTY,
                    {table_name}.LOGMILE_DIR = vals.LOGMILE_DIR,
                    {table_name}.MILEPOINT = vals.MILEPOINT,
                    {table_name}.MUNICIPAL = vals.MUNICIPAL,
                    {table_name}.MUNICIPAL_AREA_CODE = vals.MUNICIPAL_AREA_CODE,
                    {table_name}.REFERENCE_MUNI = vals.REFERENCE_MUNI,
                    {table_name}.REFERENCE_ROADNAME = vals.REFERENCE_ROADNAME,
                    {table_name}.REFERENCE_ROUTE_NUMBER = vals.REFERENCE_ROUTE_NUMBER,
                    {table_name}.REFERENCE_ROUTE_SUFFIX = vals.REFERENCE_ROUTE_SUFFIX,
                    {table_name}.REFERENCE_ROUTE_TYPE = vals.REFERENCE_ROUTE_TYPE,
                    {table_name}.ROAD_NAME = vals.ROAD_NAME,
                    {table_name}.ROUTE_NUMBER = vals.ROUTE_NUMBER,
                    {table_name}.ROUTE_SUFFIX = vals.ROUTE_SUFFIX,
                    {table_name}.ROUTE_TYPE = vals.ROUTE_TYPE
                WHEN NOT MATCHED THEN
                    INSERT (COUNTY, LOGMILE_DIR, MILEPOINT, MUNICIPAL, MUNICIPAL_AREA_CODE, REFERENCE_MUNI,
                        REFERENCE_ROADNAME, REFERENCE_ROUTE_NUMBER, REFERENCE_ROUTE_SUFFIX, REFERENCE_ROUTE_TYPE,
                        ROADID, ROAD_NAME, ROUTE_NUMBER, ROUTE_SUFFIX, ROUTE_TYPE)
                    VALUES (vals.COUNTY, vals.LOGMILE_DIR, vals.MILEPOINT, vals.MUNICIPAL, vals.MUNICIPAL_AREA_CODE,
                        vals.REFERENCE_MUNI, vals.REFERENCE_ROADNAME, vals.REFERENCE_ROUTE_NUMBER,
                        vals.REFERENCE_ROUTE_SUFFIX, vals.REFERENCE_ROUTE_TYPE, vals.ROADID, vals.ROAD_NAME,
                        vals.ROUTE_NUMBER, vals.ROUTE_SUFFIX, vals.ROUTE_TYPE);
                """.format(table_name=self.roadway_table), data
            )

        return ret

    def _read_towed_vehicle_data(self, towed_dict: List[crash_data_types.TowedUnitType]) -> bool:
        """
        Populates the acrs_towed_unit table
        :param towed_dict: The list of OrderedDicts that comes from the TOWEDUNITs tag
        """
        self.log.debug('Processing the towed unit data')

        if self.is_element_nil(towed_dict):
            self.log.warning('No towed unit data')
            return False

        data = []
        for towed_unit in self.get_multiple_attr('TOWEDUNIT', towed_dict):
            self._read_acrs_person_data(towed_unit.get('OWNER'))

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
                MERGE {table_name} USING (
                VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ) as vals (INSURANCEPOLICYNUMBER, INSURER, LICENSEPLATENUMBER, LICENSEPLATESTATE, OWNERID, TOWEDID,
                UNITNUMBER, VEHICLEID, VEHICLEMAKE, VEHICLEMODEL, VEHICLEYEAR, VIN)
                ON ({table_name}.TOWEDID = vals.TOWEDID AND
                    {table_name}.VEHICLEID = vals.VEHICLEID AND
                    {table_name}.OWNERID = vals.OWNERID
                )
                WHEN MATCHED THEN
                    UPDATE SET
                    {table_name}.INSURANCEPOLICYNUMBER = vals.INSURANCEPOLICYNUMBER,
                    {table_name}.INSURER = vals.INSURER,
                    {table_name}.LICENSEPLATENUMBER = vals.LICENSEPLATENUMBER,
                    {table_name}.LICENSEPLATESTATE = vals.LICENSEPLATESTATE,
                    {table_name}.OWNERID = vals.OWNERID,
                    {table_name}.TOWEDID = vals.TOWEDID,
                    {table_name}.UNITNUMBER = vals.UNITNUMBER,
                    {table_name}.VEHICLEID = vals.VEHICLEID,
                    {table_name}.VEHICLEMAKE = vals.VEHICLEMAKE,
                    {table_name}.VEHICLEMODEL = vals.VEHICLEMODEL,
                    {table_name}.VEHICLEYEAR = vals.VEHICLEYEAR,
                    {table_name}.VIN = vals.VIN
                WHEN NOT MATCHED THEN
                    INSERT (INSURANCEPOLICYNUMBER, INSURER, LICENSEPLATENUMBER, LICENSEPLATESTATE, OWNERID, TOWEDID,
                    UNITNUMBER, VEHICLEID, VEHICLEMAKE, VEHICLEMODEL, VEHICLEYEAR, VIN)
                    VALUES (vals.INSURANCEPOLICYNUMBER, vals.INSURER, vals.LICENSEPLATENUMBER, vals.LICENSEPLATESTATE,
                    vals.OWNERID, vals.TOWEDID, vals.UNITNUMBER, vals.VEHICLEID, vals.VEHICLEMAKE, vals.VEHICLEMODEL,
                    vals.VEHICLEYEAR, vals.VIN);
                """.format(table_name=self.towed_unit_table), data
            )

        return ret

    def _read_acrs_vehicle_data(self,
                                vehicle_dict: Optional[List[crash_data_types.VehicleType]]  # pylint:disable=unsubscriptable-object ; see comment at top
                                ) -> bool:
        """
        Populates the acrs_vehicles table
        :param vehicle_dict: List of OrderedDicts from the ACRSVEHICLE tag
        """
        self.log.debug('Processing vehicle data')

        if self.is_element_nil(vehicle_dict):
            self.log.warning('No vehicle data')
            return False

        data = []
        for vehicle in self.get_multiple_attr('ACRSVEHICLE', vehicle_dict):
            self._read_damaged_areas_data(vehicle.pop('DAMAGEDAREAs'))
            self._read_person_info_data(vehicle.pop('DRIVERs'), 'DRIVER')
            self._read_person_info_data(vehicle.pop('PASSENGERs'), 'PASSENGER')
            self._read_acrs_person_data(vehicle.pop('OWNER'))
            self._read_commercial_vehicle_data(vehicle.pop('COMMERCIALVEHICLE'))
            self._read_event_data(vehicle.pop('EVENTS'))
            self._read_acrs_vehicle_use_data(vehicle.pop('VEHICLEUSEs'))
            self._read_towed_vehicle_data(vehicle.pop('TOWEDUNITs'))

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
                MERGE {table_name} USING (
                VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ) as vals (CONTINUEDIRECTION, DAMAGEEXTENT, DRIVERLESSVEHICLE, EMERGENCYMOTORVEHICLEUSE,
                FIRE, FIRSTIMPACT, GOINGDIRECTION, HITANDRUN, INSURANCEPOLICYNUMBER, INSURER, LICENSEPLATENUMBER,
                LICENSEPLATESTATE, MAINIMPACT, MOSTHARMFULEVENT, OWNERID, PARKEDVEHICLE, REGISTRATIONEXPIRATIONYEAR,
                REPORTNUMBER, SFVEHICLEINTRANSPORT, SPEEDLIMIT, TOWEDUNITTYPE, UNITNUMBER, VEHICLEBODYTYPE, VEHICLEID,
                VEHICLEMAKE, VEHICLEMODEL, VEHICLEMOVEMENT, VEHICLEREMOVEDBY, VEHICLEREMOVEDTO, VEHICLETOWEDAWAY,
                VEHICLEYEAR, VIN)
                ON ({table_name}.REPORTNUMBER = vals.REPORTNUMBER AND
                    {table_name}.VEHICLEID = vals.VEHICLEID)
                WHEN MATCHED THEN
                    UPDATE SET
                    {table_name}.CONTINUEDIRECTION = vals.CONTINUEDIRECTION,
                    {table_name}.DAMAGEEXTENT = vals.DAMAGEEXTENT,
                    {table_name}.DRIVERLESSVEHICLE = vals.DRIVERLESSVEHICLE,
                    {table_name}.EMERGENCYMOTORVEHICLEUSE = vals.EMERGENCYMOTORVEHICLEUSE,
                    {table_name}.FIRE = vals.FIRE,
                    {table_name}.FIRSTIMPACT = vals.FIRSTIMPACT,
                    {table_name}.GOINGDIRECTION = vals.GOINGDIRECTION,
                    {table_name}.HITANDRUN = vals.HITANDRUN,
                    {table_name}.INSURANCEPOLICYNUMBER = vals.INSURANCEPOLICYNUMBER,
                    {table_name}.INSURER = vals.INSURER,
                    {table_name}.LICENSEPLATENUMBER = vals.LICENSEPLATENUMBER,
                    {table_name}.LICENSEPLATESTATE = vals.LICENSEPLATESTATE,
                    {table_name}.MAINIMPACT = vals.MAINIMPACT,
                    {table_name}.MOSTHARMFULEVENT = vals.MOSTHARMFULEVENT,
                    {table_name}.OWNERID = vals.OWNERID,
                    {table_name}.PARKEDVEHICLE = vals.PARKEDVEHICLE,
                    {table_name}.REGISTRATIONEXPIRATIONYEAR = vals.REGISTRATIONEXPIRATIONYEAR,
                    {table_name}.SFVEHICLEINTRANSPORT = vals.SFVEHICLEINTRANSPORT,
                    {table_name}.SPEEDLIMIT = vals.SPEEDLIMIT,
                    {table_name}.TOWEDUNITTYPE = vals.TOWEDUNITTYPE,
                    {table_name}.UNITNUMBER = vals.UNITNUMBER,
                    {table_name}.VEHICLEBODYTYPE = vals.VEHICLEBODYTYPE,
                    {table_name}.VEHICLEMAKE = vals.VEHICLEMAKE,
                    {table_name}.VEHICLEMODEL = vals.VEHICLEMODEL,
                    {table_name}.VEHICLEMOVEMENT = vals.VEHICLEMOVEMENT,
                    {table_name}.VEHICLEREMOVEDBY = vals.VEHICLEREMOVEDBY,
                    {table_name}.VEHICLEREMOVEDTO = vals.VEHICLEREMOVEDTO,
                    {table_name}.VEHICLETOWEDAWAY = vals.VEHICLETOWEDAWAY,
                    {table_name}.VEHICLEYEAR = vals.VEHICLEYEAR,
                    {table_name}.VIN = vals.VIN
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
                """.format(table_name=self.vehicle_table), data
            )

        return ret

    def _read_acrs_vehicle_use_data(self, vehicleuse_dict: List[crash_data_types.VehicleUseType]) -> bool:
        """
        Populates acrs_vehicle_use table
        :param vehicleuse_dict: The dictionary of the ACRSVEHICLE from the VEHICLEUSEs tag
        """
        self.log.debug('Processing vehicle use data')

        if self.is_element_nil(vehicleuse_dict):
            self.log.warning('No vehicle use data')
            return False

        data = []
        for vehicleuse in self.get_multiple_attr('VEHICLEUSE', vehicleuse_dict):
            data.append((
                self.get_single_attr('ID', vehicleuse),
                self._validate_uniqueidentifier(self.get_single_attr('VEHICLEID', vehicleuse)),
                self.get_single_attr('VEHICLEUSECODE', vehicleuse)
            ))

        ret: bool = True
        if data:
            ret = self._safe_sql_executemany(
                """
                MERGE {table_name} USING (
                VALUES
                    (?, ?, ?)
                ) as vals (ID, VEHICLEID, VEHICLEUSECODE)
                ON ({table_name}.ID = vals.ID AND
                    {table_name}.VEHICLEID = vals.VEHICLEID)
                WHEN MATCHED THEN
                    UPDATE SET
                    {table_name}.VEHICLEUSECODE = vals.VEHICLEUSECODE
                WHEN NOT MATCHED THEN
                INSERT (ID, VEHICLEID, VEHICLEUSECODE)
                VALUES (vals.ID, vals.VEHICLEID, vals.VEHICLEUSECODE);
                """.format(table_name=self.vehicle_users_table), data
            )

        return ret

    def _read_damaged_areas_data(self, damaged_dict: List[crash_data_types.DamagedAreasType]) -> bool:
        """
        Populates the acrs_damaged_areas table. Expects to be passed the OrderedDict of DAMAGEDAREAs
        :param damaged_dict: The dictionary of the ACRSVEHICLE
        """
        self.log.debug("Processing damaged areas data")

        if self.is_element_nil(damaged_dict):
            self.log.warning("No damaged area data")
            return False

        data = []
        for damagedarea in self.get_multiple_attr('DAMAGEDAREA', damaged_dict):
            data.append((
                self.get_single_attr('DAMAGEID', damagedarea),
                self.get_single_attr('IMPACTTYPE', damagedarea),
                self._validate_uniqueidentifier(self.get_single_attr('VEHICLEID', damagedarea))
            ))

        ret: bool = True
        if data:
            self._safe_sql_executemany(
                """
                MERGE {table_name} USING (
                VALUES
                    (?, ?, ?)
                ) as vals (DAMAGEID, IMPACTTYPE, VEHICLEID)
                ON ({table_name}.DAMAGEID = vals.DAMAGEID AND
                    {table_name}.VEHICLEID = vals.VEHICLEID)
                WHEN MATCHED THEN
                    UPDATE SET
                    IMPACTTYPE = vals.IMPACTTYPE
                WHEN NOT MATCHED THEN
                    INSERT (DAMAGEID, IMPACTTYPE, VEHICLEID)
                    VALUES (vals.DAMAGEID, vals.IMPACTTYPE, vals.VEHICLEID);
                """.format(table_name=self.damaged_areas_table), data)

        return ret

    def _read_witness_data(self,
                           witness_dict: Optional[List[crash_data_types.WitnessType]]  # pylint:disable=unsubscriptable-object ; see comment at top
                           ) -> bool:
        """
        Populates the acrs_witnesses table
        :param witness_dict: The list of OrderedDicts from the WITNESSes tag
        """
        self.log.debug('Processing witness data')

        if self.is_element_nil(witness_dict):
            self.log.warning('No witness data')
            return False

        data = []
        for witness in self.get_multiple_attr('WITNESS', witness_dict):
            if not self._read_acrs_person_data(witness.get('PERSON')):
                return False

            data.append((
                self._validate_uniqueidentifier(self.get_single_attr('PERSONID', witness)),
                self.get_single_attr('REPORTNUMBER', witness)
            ))

        ret: bool = True
        if data:
            ret = self._safe_sql_executemany(
                """
                MERGE {table_name} USING (
                VALUES
                    (?, ?)
                ) as vals (PERSONID, REPORTNUMBER)
                ON ({table_name}.PERSONID = vals.PERSONID AND
                    {table_name}.REPORTNUMBER = vals.REPORTNUMBER)
                WHEN NOT MATCHED THEN
                    INSERT (PERSONID, REPORTNUMBER)
                    VALUES (vals.PERSONID, vals.REPORTNUMBER);
                """.format(table_name=self.witnesses_table), data
            )

        return ret

    @staticmethod
    def is_element_nil(element: OrderedDict) -> bool:
        """
        Checks if a tag is nil, because xmltodict returns an ordereddict with a nil element
        :param element: (ordereddict) The ordereddict to check for nil
        :return: True if its nil, False otherwise
        """
        if not element:
            return True

        return (len(element) == 1) and \
            isinstance(element, OrderedDict) and \
            element.get('@i:nil') == 'true'  # pylist:disable=isinstance-second-argument-not-valid-type ; see comment

    @staticmethod
    def _convert_to_date(val: str) -> str:
        """Converts XML datetime to sql date (YYYY-MM-DDThh:mm:ss.fffffff with optional microseconds to YYYYMMDD"""
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
        assert val in ['y', 'n', 'u'], 'Expected y or n and got {}'.format(val)
        if val == 'u':
            return None
        return int(bool(val == 'y'))

    @staticmethod
    def _validate_uniqueidentifier(uid: Optional[str]) -> Optional[str]:  # pylint:disable=unsubscriptable-object ; see comment at top
        """Checks for null uniqueidentifiers"""
        if not uid:
            return None
        return uid

    def _safe_sql_execute(self, query: str, data: crash_data_types.SqlExecuteType) -> bool:
        return self._safe_sql(query, data, False)

    def _safe_sql_executemany(self, query: str, data: crash_data_types.SqlExecuteType) -> bool:
        return self._safe_sql(query, data, True)

    def _safe_sql(self,
                  query: str,
                  data: Sequence[Union[Tuple[Any], Any]],  # pylint:disable=unsubscriptable-object ; see comment at top
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
            self.log.error('SQL data error: %s\nError: %s', data, err)
            traceback.print_stack()
            return False

        self.cursor.commit()
        return True

    def get_single_attr(self,
                        tag: str,
                        crash_data: Union[None, OrderedDict, str]  # pylint:disable=unsubscriptable-object ; see comment at top
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

        assert isinstance(crash_data.get(tag), str), 'Expected {} to have only a single element'.format(tag)
        return crash_data.get(tag)

    @staticmethod
    def get_multiple_attr(tag: str, crash_data: crash_data_types.AttrElement) -> crash_data_types.MultipleAttrElement:
        """
        Generator that processes a one or many tag so that we can easily insert it into a database
        :param tag: string or list of tag to parse. List should have hierarchy of tags relative to the crash_data
        data structure, with the last element being the 'multiple' attribute that should be returned as a list
        IE ['firstlevel', 'secondlevel', 'thirdlevel', ...]
        :param crash_data: Output of xmltodict.parse with the crash data xml files
        :return: List of ordereddicts with the referenced tag or an empty list if there is no valid return
        """
        if crash_data is None:
            return []

        if isinstance(crash_data.get(tag), list):
            return crash_data.get(tag)

        return [crash_data.get(tag)]
