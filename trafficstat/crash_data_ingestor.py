"""Processes unprocessed data in the network share that holds crash data"""
# pylint:disable=too-many-lines
import logging
import os
import shutil
import traceback
from collections import OrderedDict
from datetime import datetime

import xmltodict
import pyodbc

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


class CrashDataReader:
    """ Reads a directory of ACRS crash data files"""

    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.crash_dict = None
        self.root = None
        conn = pyodbc.connect(
            r'Driver={SQL Server};Server=balt-sql311-prd;Database=DOT_DATA;Trusted_Connection=yes;')
        self.cursor = conn.cursor()

    def read_directory(self, path='//balt-fileld-srv.baltimore.city/GIS/DOT-BPD'):
        """
        Reads a directory of XML ACRS crash files, and returns an iterator of the parsed data
        :param path: Path to search for XML files
        :return:
        """
        processed_folder = os.path.join(path, 'processed')
        if not os.path.exists(processed_folder):
            os.mkdir(processed_folder)

        for acrs_file in os.listdir(path):
            if acrs_file.endswith(".xml"):
                self.read_crash_data(os.path.join(path, acrs_file), processed_folder)

    def _read_file(self, file_name):
        with open(file_name, encoding='utf-8') as acrs_file:
            crash_file = acrs_file.read()

        # Some of these files have non ascii at the beginning that causes parse errors
        offset = crash_file.find('<?xml')
        self.root = xmltodict.parse(crash_file[offset:])
        self.crash_dict = self.root['REPORT']

    def read_crash_data(self, file_name, processed_dir):
        """
        Reads the ACRS crash data files
        :param processed_dir: Directory to move the ACRS file after being processed
        :param file_name: Full path to the file to process
        :return: True if the file was inserted into the database, false if there was an error
        """
        self.log.info('Processing %s', file_name)
        self._read_file(file_name)

        # use short circuit logic to cut this off early if any of these fail
        if not (self._read_approval_data() and
                self._read_circumstance_data() and
                self._read_crash_diagrams_data() and
                self._read_ems_data() and
                self._read_pdf_data() and
                self._read_roadway_data() and
                self._read_acrs_persons_data() and
                self._read_acrs_vehicle_data() and
                self._read_person_info_data('NONMOTORISTs', 'NONMOTORIST', self.crash_dict) and
                self._read_witness_data() and
                self._read_main_crash_data()):
            self.log.error("Critical failure on file %s", file_name)
            return False

        self.crash_dict.pop('@xmlns:i')
        self.crash_dict.pop('@xmlns')
        if len(self.crash_dict) == 0:
            self.log.debug("Crash dict is fully processed")
        else:
            self.log.info("REMAINING ELEMENTS: %s", self.crash_dict)

        try:
            shutil.move(file_name, processed_dir)
        except shutil.Error:
            self.log.error("Error moving file. It will not be moved to the processed directory: %s", file_name)
        return True

    def _read_main_crash_data(self):
        """ Populates the acrs_crashes table """
        data = [
            self.get_single_attr('ACRSREPORTTIMESTAMP', self.crash_dict),
            self.get_single_attr('AGENCYIDENTIFIER', self.crash_dict),
            self.get_single_attr('AGENCYNAME', self.crash_dict),
            self.get_single_attr('AREA', self.crash_dict),
            self.get_single_attr('COLLISIONTYPE', self.crash_dict),
            self.get_single_attr('CONMAINCLOSURE', self.crash_dict),
            self.get_single_attr('CONMAINLOCATION', self.crash_dict),
            self._convert_to_bool(self.get_single_attr('CONMAINWORKERSPRESENT', self.crash_dict)),
            self.get_single_attr('CONMAINZONE', self.crash_dict),
            self._convert_to_date(self.get_single_attr('CRASHDATE', self.crash_dict)),
            self.get_single_attr('CRASHTIME', self.crash_dict),
            self.get_single_attr('CURRENTASSIGNMENT', self.crash_dict),
            self.get_single_attr('CURRENTGROUP', self.crash_dict),
            self.get_single_attr('DEFAULTASSIGNMENT', self.crash_dict),
            self.get_single_attr('DEFAULTGROUP', self.crash_dict),
            self.get_single_attr('DOCTYPE', self.crash_dict),
            self.get_single_attr('FIXEDOBJECTSTRUCK', self.crash_dict),
            self.get_single_attr('HARMFULEVENTONE', self.crash_dict),
            self.get_single_attr('HARMFULEVENTTWO', self.crash_dict),
            self._convert_to_bool(self.get_single_attr('HITANDRUN', self.crash_dict)),
            self.get_single_attr('INSERTDATE', self.crash_dict),
            self.get_single_attr('INTERCHANGEAREA', self.crash_dict),
            # self.get_single_attr('INTERCHANGEIDENTIFICATION', self.crash_dict),
            self.get_single_attr('INTERSECTIONTYPE', self.crash_dict),
            self.get_single_attr('INVESTIGATINGOFFICERUSERNAME', self.crash_dict),
            # self.get_single_attr('INVESTIGATOR', self.crash_dict),
            self.get_single_attr('JUNCTION', self.crash_dict),
            self.get_single_attr('LANEDIRECTION', self.crash_dict),
            self.get_single_attr('LANENUMBER', self.crash_dict),
            self.get_single_attr('LANETYPE', self.crash_dict),
            self.get_single_attr('LATITUDE', self.crash_dict),
            self.get_single_attr('LIGHT', self.crash_dict),
            self.get_single_attr('LOCALCASENUMBER', self.crash_dict),
            self.get_single_attr('LOCALCODES', self.crash_dict),
            self.get_single_attr('LONGITUDE', self.crash_dict),
            self.get_single_attr('MILEPOINTDIRECTION', self.crash_dict),
            self.get_single_attr('MILEPOINTDISTANCE', self.crash_dict),
            self.get_single_attr('MILEPOINTDISTANCEUNITS', self.crash_dict),
            self.get_single_attr('NARRATIVE', self.crash_dict),
            self._convert_to_bool(self.get_single_attr('NONTRAFFIC', self.crash_dict)),
            self.get_single_attr('NUMBEROFLANES', self.crash_dict),
            self.get_single_attr('OFFROADDESCRIPTION', self.crash_dict),
            self._convert_to_bool(self.get_single_attr('PHOTOSTAKEN', self.crash_dict)),
            # self.get_single_attr('RAMP', self.crash_dict),
            self.get_single_attr('REPORTCOUNTYLOCATION', self.crash_dict),
            # REPORTDOCUMENTs
            self.get_single_attr('REPORTNUMBER', self.crash_dict),
            # REPORTPHOTOes
            self.get_single_attr('REPORTTYPE', self.crash_dict),
            self.get_single_attr('ROADALIGNMENT', self.crash_dict),
            self.get_single_attr('ROADCONDITION', self.crash_dict),
            self.get_single_attr('ROADDIVISION', self.crash_dict),
            self.get_single_attr('ROADGRADE', self.crash_dict),
            self.get_single_attr('ROADID', self.crash_dict),
            self.get_single_attr('SCHOOLBUSINVOLVEMENT', self.crash_dict),
            self.get_single_attr('STATEGOVERNMENTPROPERTYNAME', self.crash_dict),
            # self.get_single_attr('SUPERVISOR', self.crash_dict),
            self.get_single_attr('SUPERVISORUSERNAME', self.crash_dict),
            self._remove_microseconds(self.get_single_attr('SUPERVISORYDATE', self.crash_dict)),
            self.get_single_attr('SURFACECONDITION', self.crash_dict),
            self.get_single_attr('TRAFFICCONTROL', self.crash_dict),
            self._convert_to_bool(self.get_single_attr('TRAFFICCONTROLFUNCTIONING', self.crash_dict)),
            self.get_single_attr('UPDATEDATE', self.crash_dict),
            self.get_single_attr('UPLOADVERSION', self.crash_dict),
            self.get_single_attr('VERSIONNUMBER', self.crash_dict),
            self.get_single_attr('WEATHER', self.crash_dict)
        ]

        ret = self._safe_sql_execute(
            """
            MERGE acrs_crashes USING (
            VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                 ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ) AS vals (ACRSREPORTTIMESTAMP, AGENCYIDENTIFIER, AGENCYNAME, AREA, COLLISIONTYPE, CONMAINCLOSURE,
            CONMAINLOCATION, CONMAINWORKERSPRESENT, CONMAINZONE, CRASHDATE, CRASHTIME, CURRENTASSIGNMENT, CURRENTGROUP,
            DEFAULTASSIGNMENT, DEFAULTGROUP, DOCTYPE, FIXEDOBJECTSTRUCK, HARMFULEVENTONE, HARMFULEVENTTWO, HITANDRUN,
            INSERTDATE, INTERCHANGEAREA, INTERSECTIONTYPE, INVESTIGATINGOFFICERUSERNAME, JUNCTION, LANEDIRECTION,
            LANENUMBER, LANETYPE, LATITUDE, LIGHT, LOCALCASENUMBER, LOCALCODES, LONGITUDE, MILEPOINTDIRECTION,
            MILEPOINTDISTANCE, MILEPOINTDISTANCEUNITS, NARRATIVE, NONTRAFFIC, NUMBEROFLANES, OFFROADDESCRIPTION,
            PHOTOSTAKEN, REPORTCOUNTYLOCATION, REPORTNUMBER, REPORTTYPE, ROADALIGNMENT, ROADCONDITION, ROADDIVISION,
            ROADGRADE, ROADID, SCHOOLBUSINVOLVEMENT, STATEGOVERNMENTPROPERTYNAME, SUPERVISORUSERNAME, SUPERVISORYDATE,
            SURFACECONDITION, TRAFFICCONTROL, TRAFFICCONTROLFUNCTIONING, UPDATEDATE, UPLOADVERSION, VERSIONNUMBER,
            WEATHER)
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
                INTERSECTIONTYPE = vals.INTERSECTIONTYPE,
                INVESTIGATINGOFFICERUSERNAME = vals.INVESTIGATINGOFFICERUSERNAME,
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
                REPORTCOUNTYLOCATION = vals.REPORTCOUNTYLOCATION,
                REPORTTYPE = vals.REPORTTYPE,
                ROADALIGNMENT = vals.ROADALIGNMENT,
                ROADCONDITION = vals.ROADCONDITION,
                ROADDIVISION = vals.ROADDIVISION,
                ROADGRADE = vals.ROADGRADE,
                ROADID = vals.ROADID,
                SCHOOLBUSINVOLVEMENT = vals.SCHOOLBUSINVOLVEMENT,
                STATEGOVERNMENTPROPERTYNAME = vals.STATEGOVERNMENTPROPERTYNAME,
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
                HARMFULEVENTTWO, HITANDRUN, INSERTDATE, INTERCHANGEAREA, INTERSECTIONTYPE, INVESTIGATINGOFFICERUSERNAME,
                JUNCTION, LANEDIRECTION, LANENUMBER, LANETYPE, LATITUDE, LIGHT, LOCALCASENUMBER, LOCALCODES, LONGITUDE,
                MILEPOINTDIRECTION, MILEPOINTDISTANCE, MILEPOINTDISTANCEUNITS, NARRATIVE, NONTRAFFIC, NUMBEROFLANES,
                OFFROADDESCRIPTION, PHOTOSTAKEN, REPORTCOUNTYLOCATION, REPORTNUMBER, REPORTTYPE, ROADALIGNMENT,
                ROADCONDITION, ROADDIVISION, ROADGRADE, ROADID, SCHOOLBUSINVOLVEMENT, STATEGOVERNMENTPROPERTYNAME,
                SUPERVISORUSERNAME, SUPERVISORYDATE, SURFACECONDITION, TRAFFICCONTROL, TRAFFICCONTROLFUNCTIONING,
                UPDATEDATE, UPLOADVERSION, VERSIONNUMBER, WEATHER)
                VALUES (vals.ACRSREPORTTIMESTAMP, vals.AGENCYIDENTIFIER, vals.AGENCYNAME, vals.AREA, vals.COLLISIONTYPE,
                vals.CONMAINCLOSURE, vals.CONMAINLOCATION, vals.CONMAINWORKERSPRESENT, vals.CONMAINZONE, vals.CRASHDATE,
                vals.CRASHTIME, vals.CURRENTASSIGNMENT, vals.CURRENTGROUP, vals.DEFAULTASSIGNMENT, vals.DEFAULTGROUP,
                vals.DOCTYPE, vals.FIXEDOBJECTSTRUCK, vals.HARMFULEVENTONE, vals.HARMFULEVENTTWO, vals.HITANDRUN,
                vals.INSERTDATE, vals.INTERCHANGEAREA, vals.INTERSECTIONTYPE, vals.INVESTIGATINGOFFICERUSERNAME,
                vals.JUNCTION, vals.LANEDIRECTION, vals.LANENUMBER, vals.LANETYPE, vals.LATITUDE, vals.LIGHT,
                vals.LOCALCASENUMBER, vals.LOCALCODES, vals.LONGITUDE, vals.MILEPOINTDIRECTION, vals.MILEPOINTDISTANCE,
                vals.MILEPOINTDISTANCEUNITS, vals.NARRATIVE, vals.NONTRAFFIC, vals.NUMBEROFLANES,
                vals.OFFROADDESCRIPTION, vals.PHOTOSTAKEN, vals.REPORTCOUNTYLOCATION, vals.REPORTNUMBER,
                vals.REPORTTYPE, vals.ROADALIGNMENT, vals.ROADCONDITION, vals.ROADDIVISION, vals.ROADGRADE, vals.ROADID,
                vals.SCHOOLBUSINVOLVEMENT, vals.STATEGOVERNMENTPROPERTYNAME, vals.SUPERVISORUSERNAME,
                vals.SUPERVISORYDATE, vals.SURFACECONDITION, vals.TRAFFICCONTROL, vals.TRAFFICCONTROLFUNCTIONING,
                vals.UPDATEDATE, vals.UPLOADVERSION, vals.VERSIONNUMBER, vals.WEATHER);
            """, data)
        self._clean_element('REPORT', self.root)

        return ret

    def _read_approval_data(self):
        """ Populates the acrs_approval table """
        data = [
            self.get_single_attr(['APPROVALDATA', 'AGENCY'], self.crash_dict),
            self.get_single_attr(['APPROVALDATA', 'APPROVALDATE'], self.crash_dict),
            self.get_single_attr(['APPROVALDATA', 'CADSENT'], self.crash_dict),
            self.get_single_attr(['APPROVALDATA', 'CADSENT_DATE'], self.crash_dict),
            self.get_single_attr(['APPROVALDATA', 'CC_NUMBER'], self.crash_dict),
            self.get_single_attr(['APPROVALDATA', 'DATE_INITIATED2'], self.crash_dict),
            self.get_single_attr(['APPROVALDATA', 'GROUP_NUMBER'], self.crash_dict),
            self.get_single_attr(['APPROVALDATA', 'HISTORICALAPPROVALDATA'], self.crash_dict),
            self.get_single_attr(['APPROVALDATA', 'INCIDENT_DATE'], self.crash_dict),
            self.get_single_attr(['APPROVALDATA', 'INVESTIGATOR'], self.crash_dict),
            self.get_single_attr(['APPROVALDATA', 'REPORT_TYPE'], self.crash_dict),
            self.get_single_attr(['APPROVALDATA', 'SEQ_GUID'], self.crash_dict),
            self.get_single_attr(['APPROVALDATA', 'STATUS_CHANGE_DATE'], self.crash_dict),
            self.get_single_attr(['APPROVALDATA', 'STATUS_ID'], self.crash_dict),
            self.get_single_attr(['APPROVALDATA', 'STEP_NUMBER'], self.crash_dict),
            self.get_single_attr(['APPROVALDATA', 'TR_USERNAME'], self.crash_dict),
            self.get_single_attr(['APPROVALDATA', 'UNIT_CODE'], self.crash_dict)
        ]

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

        self._clean_element('APPROVALDATA', self.crash_dict)

        return ret

    def _read_circumstance_data(self):
        """ Populates the acrs_circumstances table """
        data = []
        for circumstance in self.get_multiple_attr(['CIRCUMSTANCES', 'CIRCUMSTANCE'], self.crash_dict):
            data.append((
                self.get_single_attr('CIRCUMSTANCECODE', circumstance),
                self.get_single_attr('CIRCUMSTANCEID', circumstance),
                self.get_single_attr('CIRCUMSTANCETYPE', circumstance),
                self._validate_uniqueidentifier(self.get_single_attr('PERSONID', circumstance)),
                self.get_single_attr('REPORTNUMBER', circumstance),
                self._validate_uniqueidentifier(self.get_single_attr('VEHICLEID', circumstance))
            ))

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
        self._clean_element('CIRCUMSTANCES', self.crash_dict)

        return ret

    def _read_citation_data(self, person):
        """ Populates the acrs_citation_codes table """
        if len(person) <= 1:
            return True

        data = []
        for citation in self.get_multiple_attr(['CITATIONCODES', 'CITATIONCODE'], person):
            data.append((
                self.get_single_attr('CITATIONNUMBER', citation),
                self._validate_uniqueidentifier(self.get_single_attr('PERSONID', citation)),
                self.get_single_attr('REPORTNUMBER', citation)
            ))

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
        self._clean_element('CITATIONCODES', person)

        return ret

    def _read_crash_diagrams_data(self):
        """ Populates the acrs_crash_diagrams table """
        data = [
            self.get_single_attr(['DIAGRAM', 'CRASHDIAGRAM'], self.crash_dict),
            self.get_single_attr(['DIAGRAM', 'CRASHDIAGRAMNATIVE'], self.crash_dict),
            self.get_single_attr(['DIAGRAM', 'REPORTNUMBER'], self.crash_dict),
        ]

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
        self._clean_element('DIAGRAM', self.crash_dict)

        return ret

    def _read_ems_data(self):
        """ Populates the acrs_ems table """
        data = []
        for ems in self.get_multiple_attr(['EMSes', 'EMS'], self.crash_dict):
            data.append((
                self.get_single_attr('EMSTRANSPORTATIONTYPE', ems),
                self.get_single_attr('EMSUNITNUMBER', ems),
                self.get_single_attr('INJUREDTAKENBY', ems),
                self.get_single_attr('INJUREDTAKENTO', ems),
                self.get_single_attr('REPORTNUMBER', ems)
            ))

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
        self._clean_element('EMSes', self.crash_dict)

        return ret

    def _read_commercial_vehicle_data(self, vehicleroot):
        """
        Populates the acrs_commercial_vehicle table
        :param vehicleroot: The dictionary of the ACRSVEHICLE
        :return:
        """
        if len(vehicleroot) <= 1:
            return True

        data = [
            self.get_single_attr('BODYTYPE', vehicleroot),
            self.get_single_attr('BUSUSE', vehicleroot),
            self.get_single_attr('CARRIERCLASSIFICATION', vehicleroot),
            self.get_single_attr('CITY', vehicleroot),
            self.get_single_attr('CONFIGURATION', vehicleroot),
            self.get_single_attr('COUNTRY', vehicleroot),
            self.get_single_attr('DOTNUMBER', vehicleroot),
            self.get_single_attr('GVW', vehicleroot),
            self.get_single_attr('HAZMATCLASS', vehicleroot),
            self.get_single_attr('HAZMATNAME', vehicleroot),
            self.get_single_attr('HAZMATNUMBER', vehicleroot),
            self.get_single_attr('HAZMATSPILL', vehicleroot),
            self.get_single_attr('MCNUMBER', vehicleroot),
            self.get_single_attr('NAME', vehicleroot),
            self.get_single_attr('NUMBEROFAXLES', vehicleroot),
            self.get_single_attr('PLACARDVISIBLE', vehicleroot),
            self.get_single_attr('POSTALCODE', vehicleroot),
            self.get_single_attr('STATE', vehicleroot),
            self.get_single_attr('STREET', vehicleroot),
            self.get_single_attr('VEHICLEID', vehicleroot),
            self.get_single_attr('WEIGHT', vehicleroot),
            self.get_single_attr('WEIGHTUNIT', vehicleroot)
        ]

        return self._safe_sql_execute(
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
                HAZMATCLASS, HAZMATNAME, HAZMATNUMBER, HAZMATSPILL, MCNUMBER, NAME, NUMBEROFAXLES, PLACARDVISIBLE,
                POSTALCODE, STATE, STREET, VEHICLEID, WEIGHT, WEIGHTUNIT)
                VALUES (vals.BODYTYPE, vals.BUSUSE, vals.CARRIERCLASSIFICATION, vals.CITY, vals.CONFIGURATION,
                vals.COUNTRY, vals.DOTNUMBER, vals.GVW, vals.HAZMATCLASS, vals.HAZMATNAME, vals.HAZMATNUMBER,
                vals.HAZMATSPILL, vals.MCNUMBER, vals.NAME, vals.NUMBEROFAXLES, vals.PLACARDVISIBLE, vals.POSTALCODE,
                vals.STATE, vals.STREET, vals.VEHICLEID, vals.WEIGHT, vals.WEIGHTUNIT);
            """, data
        )

    def _read_event_data(self, vehicleroot):
        """
        Populates the acrs_events table
        :param vehicleroot: The dictionary of the ACRSVEHICLE
        """
        if len(vehicleroot) <= 1:
            return True

        data = []
        for event in self.get_multiple_attr(['EVENTS', 'EVENT'], vehicleroot):
            data.append((
                self.get_single_attr('EVENTID', event),
                self.get_single_attr('EVENTSEQUENCE', event),
                self.get_single_attr('EVENTTYPE', event),
                self._validate_uniqueidentifier(self.get_single_attr('VEHICLEID', event))
            ))

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
        self._clean_element('EVENTS', vehicleroot)

        return ret

    def _read_pdf_data(self):
        """ Populates the acrs_pdf_report table """
        data = []
        for report in self.get_multiple_attr(['PDFREPORTs', 'PDFREPORT'], self.crash_dict):
            data.append((
                self.get_single_attr('CHANGEDBY', report),
                self.get_single_attr('DATESTATUSCHANGED', report),
                self.get_single_attr('PDFREPORT1', report),
                self.get_single_attr('PDF_ID', report),
                self.get_single_attr('REPORTNUMBER', report),
                self.get_single_attr('STATUS', report)
            ))

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
        self._clean_element('PDFREPORTs', self.crash_dict)

        return ret

    def _read_acrs_persons_data(self):
        """ Handles the multiple person tag at the root of self.crash_dict """
        for person in self.get_multiple_attr(['People', 'ACRSPERSON'], self.crash_dict):
            if not self._read_acrs_person_data(person):
                return False
        self._clean_element('People', self.crash_dict)
        return True

    def _read_acrs_person_data(self, persondata, tag_to_clean=None):
        """ Populates the acrs_person table
        :param persondata: Reference to the acrsperson data from xmltodict
        :param tag_to_clean: If specified, it cleans that tag, which should be the name of the person data tag
        :rtype: object None
        """
        if len(persondata) <= 1:
            return True

        if not self._read_citation_data(persondata):
            return False

        data = [
            self.get_single_attr('ADDRESS', persondata),
            self.get_single_attr('CITY', persondata),
            self.get_single_attr('COMPANY', persondata),
            self.get_single_attr('COUNTRY', persondata),
            self.get_single_attr('COUNTY', persondata),
            self.get_single_attr('DLCLASS', persondata),
            self.get_single_attr('DLNUMBER', persondata),
            self.get_single_attr('DLSTATE', persondata),
            self.get_single_attr('DOB', persondata),
            self.get_single_attr('FIRSTNAME', persondata),
            self.get_single_attr('HOMEPHONE', persondata),
            self.get_single_attr('LASTNAME', persondata),
            self.get_single_attr('MIDDLENAME', persondata),
            self.get_single_attr('OTHERPHONE', persondata),
            self._validate_uniqueidentifier(self.get_single_attr('PERSONID', persondata)),
            self.get_single_attr('RACE', persondata),
            self.get_single_attr('REPORTNUMBER', persondata),
            self.get_single_attr('SEX', persondata),
            self.get_single_attr('STATE', persondata),
            self.get_single_attr('ZIP', persondata)
        ]

        ret = self._safe_sql_execute(
            """
            MERGE acrs_person USING (
            VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ) as vals (ADDRESS, CITY, COMPANY, COUNTRY, COUNTY, DLCLASS, DLNUMBER, DLSTATE, DOB, FIRSTNAME, HOMEPHONE,
            LASTNAME, MIDDLENAME, OTHERPHONE, PERSONID, RACE, REPORTNUMBER, SEX, STATE, ZIP)
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
                INSERT (ADDRESS, CITY, COMPANY, COUNTRY, COUNTY, DLCLASS, DLNUMBER, DLSTATE, DOB, FIRSTNAME, HOMEPHONE,
                LASTNAME, MIDDLENAME, OTHERPHONE, PERSONID, RACE, REPORTNUMBER, SEX, STATE, ZIP)
                VALUES (vals.ADDRESS, vals.CITY, vals.COMPANY, vals.COUNTRY, vals.COUNTY, vals.DLCLASS, vals.DLNUMBER,
                vals.DLSTATE, vals.DOB, vals.FIRSTNAME, vals.HOMEPHONE, vals.LASTNAME, vals.MIDDLENAME, vals.OTHERPHONE,
                vals.PERSONID, vals.RACE, vals.REPORTNUMBER, vals.SEX, vals.STATE, vals.ZIP);
            """, data
        )

        if tag_to_clean:
            self._clean_element(tag_to_clean, persondata)

        return ret

    def _read_person_info_data(self, parent_tag, child_tag, persons):
        """
        Populates the acrs_person_info table. Applies for drivers, passengers and nonmotorists
        :param parent_tag: The parent tag of the multiple person tag to iterate over
        :param child_tag: The name of the tag that is repeated with the person information
        :param persons: The dictionary with the parent_tag as a top level tag
        """
        if len(persons) <= 1:
            return True

        data = []
        for person in self.get_multiple_attr([parent_tag, child_tag], persons):
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
                self.get_single_attr('REPORTNUMBER', person),
                self.get_single_attr('SAFETYEQUIPMENT', person),
                self.get_single_attr('SEAT', person),
                self.get_single_attr('SEATINGLOCATION', person),
                self.get_single_attr('SEATINGROW', person),
                self.get_single_attr('SUBSTANCEUSE', person),
                self.get_single_attr('UNITNUMBERFIRSTSTRIKE', person),
                self._validate_uniqueidentifier(self.get_single_attr('VEHICLEID', person))
            ))

        ret = self._safe_sql_executemany(
            """
            MERGE acrs_person_info USING (
            VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ) AS vals (AIRBAGDEPLOYED, ALCOHOLTESTINDICATOR, ALCOHOLTESTTYPE, ATFAULT, BAC, CONDITION,
            CONTINUEDIRECTION, DRIVERDISTRACTEDBY, DRUGTESTINDICATOR, DRUGTESTRESULT, EJECTION, EMSRUNREPORTNUMBER,
            EMSUNITNUMBER, EQUIPMENTPROBLEM, GOINGDIRECTION, HASCDL, INJURYSEVERITY, PEDESTRIANACTIONS,
            PEDESTRIANLOCATION, PEDESTRIANMOVEMENT, PEDESTRIANOBEYTRAFFICSIGNAL, PEDESTRIANTYPE, PEDESTRIANVISIBILITY,
            PERSONID, REPORTNUMBER, SAFETYEQUIPMENT, SEAT, SEATINGLOCATION, SEATINGROW, SUBSTANCEUSE,
            UNITNUMBERFIRSTSTRIKE, VEHICLEID)
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
                CONTINUEDIRECTION, DRIVERDISTRACTEDBY, DRUGTESTINDICATOR, DRUGTESTRESULT, EJECTION, EMSRUNREPORTNUMBER,
                EMSUNITNUMBER, EQUIPMENTPROBLEM, GOINGDIRECTION, HASCDL, INJURYSEVERITY, PEDESTRIANACTIONS,
                PEDESTRIANLOCATION, PEDESTRIANMOVEMENT, PEDESTRIANOBEYTRAFFICSIGNAL, PEDESTRIANTYPE,
                PEDESTRIANVISIBILITY, PERSONID, REPORTNUMBER, SAFETYEQUIPMENT, SEAT, SEATINGLOCATION, SEATINGROW,
                SUBSTANCEUSE, UNITNUMBERFIRSTSTRIKE, VEHICLEID)
                VALUES (vals.AIRBAGDEPLOYED, vals.ALCOHOLTESTINDICATOR, vals.ALCOHOLTESTTYPE, vals.ATFAULT, vals.BAC,
                vals.CONDITION, vals.CONTINUEDIRECTION, vals.DRIVERDISTRACTEDBY, vals.DRUGTESTINDICATOR,
                vals.DRUGTESTRESULT, vals.EJECTION, vals.EMSRUNREPORTNUMBER, vals.EMSUNITNUMBER, vals.EQUIPMENTPROBLEM,
                vals.GOINGDIRECTION, vals.HASCDL, vals.INJURYSEVERITY, vals.PEDESTRIANACTIONS, vals.PEDESTRIANLOCATION,
                vals.PEDESTRIANMOVEMENT, vals.PEDESTRIANOBEYTRAFFICSIGNAL, vals.PEDESTRIANTYPE,
                vals.PEDESTRIANVISIBILITY, vals.PERSONID, vals.REPORTNUMBER, vals.SAFETYEQUIPMENT, vals.SEAT,
                vals.SEATINGLOCATION, vals.SEATINGROW, vals.SUBSTANCEUSE, vals.UNITNUMBERFIRSTSTRIKE, vals.VEHICLEID);
            """, data
        )
        self._clean_element(parent_tag, persons)

        return ret

    def _read_roadway_data(self):
        """ Populates the acrs_roadway table """
        data = [
            self.get_single_attr(['ROADWAY', 'COUNTY'], self.crash_dict),
            self.get_single_attr(['ROADWAY', 'LOGMILE_DIR'], self.crash_dict),
            self.get_single_attr(['ROADWAY', 'MILEPOINT'], self.crash_dict),
            self.get_single_attr(['ROADWAY', 'MUNICIPAL'], self.crash_dict),
            self.get_single_attr(['ROADWAY', 'MUNICIPAL_AREA_CODE'], self.crash_dict),
            self.get_single_attr(['ROADWAY', 'REFERENCE_MUNI'], self.crash_dict),
            self.get_single_attr(['ROADWAY', 'REFERENCE_ROADNAME'], self.crash_dict),
            self.get_single_attr(['ROADWAY', 'REFERENCE_ROUTE_NUMBER'], self.crash_dict),
            self.get_single_attr(['ROADWAY', 'REFERENCE_ROUTE_SUFFIX'], self.crash_dict),
            self.get_single_attr(['ROADWAY', 'REFERENCE_ROUTE_TYPE'], self.crash_dict),
            self.get_single_attr(['ROADWAY', 'ROADID'], self.crash_dict),
            self.get_single_attr(['ROADWAY', 'ROAD_NAME'], self.crash_dict),
            self.get_single_attr(['ROADWAY', 'ROUTE_NUMBER'], self.crash_dict),
            self.get_single_attr(['ROADWAY', 'ROUTE_SUFFIX'], self.crash_dict),
            self.get_single_attr(['ROADWAY', 'ROUTE_TYPE'], self.crash_dict)
        ]

        ret = self._safe_sql_execute(
            """
            MERGE acrs_roadway USING (
            VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ) as vals ( COUNTY, LOGMILE_DIR, MILEPOINT, MUNICIPAL, MUNICIPAL_AREA_CODE, REFERENCE_MUNI,
            REFERENCE_ROADNAME, REFERENCE_ROUTE_NUMBER, REFERENCE_ROUTE_SUFFIX, REFERENCE_ROUTE_TYPE, ROADID, ROAD_NAME,
            ROUTE_NUMBER, ROUTE_SUFFIX, ROUTE_TYPE)
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
            REFERENCE_ROADNAME, REFERENCE_ROUTE_NUMBER, REFERENCE_ROUTE_SUFFIX, REFERENCE_ROUTE_TYPE, ROADID, ROAD_NAME,
            ROUTE_NUMBER, ROUTE_SUFFIX, ROUTE_TYPE)
                VALUES (vals.COUNTY, vals.LOGMILE_DIR, vals.MILEPOINT, vals.MUNICIPAL, vals.MUNICIPAL_AREA_CODE,
                vals.REFERENCE_MUNI, vals.REFERENCE_ROADNAME, vals.REFERENCE_ROUTE_NUMBER, vals.REFERENCE_ROUTE_SUFFIX,
                vals.REFERENCE_ROUTE_TYPE, vals.ROADID, vals.ROAD_NAME, vals.ROUTE_NUMBER, vals.ROUTE_SUFFIX,
                vals.ROUTE_TYPE);
            """, data
        )
        self._clean_element('ROADWAY', self.crash_dict)

        return ret

    def _read_towed_vehicle_data(self, vehicle):
        """
        Populates the acrs_towed_unit table
        :param vehicle:
        :return:
        """
        if len(vehicle) <= 1:
            return True

        data = []
        for towedunit in self.get_multiple_attr(['TOWEDUNITs', 'TOWEDUNIT'], vehicle):
            if not self._read_acrs_person_data(towedunit.get('OWNER')):
                return False

            data.append((
                self.get_single_attr('INSURANCEPOLICYNUMBER', towedunit),
                self.get_single_attr('INSURER', towedunit),
                self.get_single_attr('LICENSEPLATENUMBER', towedunit),
                self.get_single_attr('LICENSEPLATESTATE', towedunit),
                self._validate_uniqueidentifier(self.get_single_attr('OWNERID', towedunit)),
                self._validate_uniqueidentifier(self.get_single_attr('TOWEDID', towedunit)),
                self.get_single_attr('UNITNUMBER', towedunit),
                self._validate_uniqueidentifier(self.get_single_attr('VEHICLEID', towedunit)),
                self.get_single_attr('VEHICLEMAKE', towedunit),
                self.get_single_attr('VEHICLEMODEL', towedunit),
                self.get_single_attr('VEHICLEYEAR', towedunit),
                self.get_single_attr('VIN', towedunit)
            ))

        return self._safe_sql_executemany(
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

    def _read_acrs_vehicle_data(self):
        """ Populates the acrs_vehicles table """
        data = []
        for vehicle in self.get_multiple_attr(['VEHICLEs', 'ACRSVEHICLE'], self.crash_dict):

            # use short circuit logic to break out of this if any of these fail. Else, continue
            if not (self._read_damaged_areas_data(vehicle) and
                    self._read_person_info_data('DRIVERs', 'DRIVER', vehicle) and
                    self._read_person_info_data('PASSENGERs', 'PASSENGER', vehicle) and
                    self._read_acrs_person_data(vehicle.get('OWNER'), 'OWNER') and
                    self._read_commercial_vehicle_data(vehicle.get('COMMERCIALVEHICLE')) and
                    self._read_event_data(vehicle) and
                    self._read_acrs_vehicle_use_data(vehicle) and
                    self._read_towed_vehicle_data(vehicle)):
                self.log.error("Vehicle data insertion failed")
                return False

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
                INSERT (CONTINUEDIRECTION, DAMAGEEXTENT, DRIVERLESSVEHICLE, EMERGENCYMOTORVEHICLEUSE,
                FIRE, FIRSTIMPACT, GOINGDIRECTION, HITANDRUN, INSURANCEPOLICYNUMBER, INSURER, LICENSEPLATENUMBER,
                LICENSEPLATESTATE, MAINIMPACT, MOSTHARMFULEVENT, OWNERID, PARKEDVEHICLE, REGISTRATIONEXPIRATIONYEAR,
                REPORTNUMBER, SFVEHICLEINTRANSPORT, SPEEDLIMIT, TOWEDUNITTYPE, UNITNUMBER, VEHICLEBODYTYPE, VEHICLEID,
                VEHICLEMAKE, VEHICLEMODEL, VEHICLEMOVEMENT, VEHICLEREMOVEDBY, VEHICLEREMOVEDTO, VEHICLETOWEDAWAY,
                VEHICLEYEAR, VIN)
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
        self._clean_element('VEHICLEs', self.crash_dict)

        return ret

    def _read_acrs_vehicle_use_data(self, vehicleroot):
        """
        Populates acrs_vehicle_use table
        :param vehicleroot: The dictionary of the ACRSVEHICLE
        """
        if len(vehicleroot) <= 1:
            return True

        data = []
        for vehicleuse in self.get_multiple_attr(['VEHICLEUSEs', 'VEHICLEUSE'], vehicleroot):
            data.append((
                self.get_single_attr('ID', vehicleuse),
                self._validate_uniqueidentifier(self.get_single_attr('VEHICLEID', vehicleuse)),
                self.get_single_attr('VEHICLEUSECODE', vehicleuse)
            ))

        return self._safe_sql_executemany(
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

    def _read_damaged_areas_data(self, vehicleroot):
        """
        Populates the acrs_damaged_areas table. Expects to be passed the OrderedDict of DAMAGEDAREAs
        :param vehicleroot: The dictionary of the ACRSVEHICLE
        """
        if len(vehicleroot) <= 1:
            return True

        data = []
        for damagedarea in self.get_multiple_attr(['DAMAGEDAREAs', 'DAMAGEDAREA'], vehicleroot):
            data.append((
                self.get_single_attr('DAMAGEID', damagedarea),
                self.get_single_attr('IMPACTTYPE', damagedarea),
                self._validate_uniqueidentifier(self.get_single_attr('VEHICLEID', damagedarea))
            ))

        return self._safe_sql_executemany(
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
            """, data)

    def _read_witness_data(self):
        """ Populates the acrs_witnesses table """
        data = []
        for witness in self.get_multiple_attr(['WITNESSes', 'WITNESS'], self.crash_dict):
            if not self._read_acrs_person_data(witness.get('PERSON')):
                return False
            data.append((
                self._validate_uniqueidentifier(self.get_single_attr('PERSONID', witness)),
                self.get_single_attr('REPORTNUMBER', witness)
            ))

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
        self._clean_element('WITNESSes', self.crash_dict)

        return ret

    @staticmethod
    def is_nil(element):
        """
        Checks if a tag is nil, because xmltodict returns an ordereddict with a nil element
        :param element: (ordereddict) The ordereddict to check for nil
        :return: True if its nil, False otherwise
        """
        return (len(element) == 1) and isinstance(element, OrderedDict) and element.get('@i:nil') == 'true'

    @staticmethod
    def _convert_to_date(val):
        """Converts XML datetime to sql date (YYYY-MM-DDThh:mm:ss to YYYYMMDD"""
        converted = datetime.strptime(val, '%Y-%m-%dT%H:%M:%S')
        return converted.strftime('%Y%m%d')

    @staticmethod
    def _convert_to_bool(val):
        """
        Converts the XML style 'y', 'n', and 'u' (unknown) to a bit value
        :param val: Value to convert to a bool
        :return: Either True, False, or None (if the input was empty or 'u' for unknown)
        """
        if not val:
            return None

        val = val.lower()
        assert val in ['y', 'n', 'u'], "Expected y or n and got {}".format(val)
        if val == 'u':
            return None
        return int(bool(val == 'y'))

    @staticmethod
    def _remove_microseconds(val):
        """Converts ODBC canonical date format"""
        converted = datetime.strptime(val, '%Y-%m-%dT%H:%M:%S.%f')
        return converted.strftime('%Y-%m-%dT%H:%M:%S')

    @staticmethod
    def _validate_uniqueidentifier(uid):
        """Checks for null uniqueidentifiers"""
        if uid == '':
            return None
        return uid

    def _safe_sql_execute(self, query, data):
        return self._safe_sql(query, data, False)

    def _safe_sql_executemany(self, query, data):
        return self._safe_sql(query, data, True)

    def _safe_sql(self, query, data, many):
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
            if many:
                self.cursor.executemany(query, data)
            else:
                self.cursor.execute(query, data)
        except (pyodbc.ProgrammingError, pyodbc.DataError, pyodbc.IntegrityError) as err:
            self.log.error("SQL data error: %s\nError: %s\n%s", data, err, traceback.print_stack())
            return False

        self.cursor.commit()
        return True

    def get_single_attr(self, tag, crash_data):
        """
        Gets a single element from the XML document we loaded. It errors if there are more that one of those type of tag
        :param tag:
        :param crash_data:
        :return:
        """
        if crash_data is None:
            return ""

        if isinstance(tag, list):
            if len(tag) < 1:
                self.log.error("get_single_attr was passed an empty list")
                return ""

            if len(tag) > 1:
                attr = tag.pop(0)
                return self.get_single_attr(tag, crash_data.get(attr))

            if len(tag) == 1:
                attr = tag.pop(0)
                return self.get_single_attr(attr, crash_data)

        if crash_data.get(tag) is None or self.is_nil(crash_data.get(tag)):
            return ""

        assert isinstance(crash_data.get(tag), str), "Expected {} to have only a single element".format(tag)
        return crash_data.pop(tag)

    def get_multiple_attr(self, tag, crash_data):
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

        if isinstance(tag, list):
            if len(tag) < 1:
                self.log.error("get_multiple_attr was passed an empty list")
                return []

            if len(tag) > 1:
                attr = tag.pop(0)
                return self.get_multiple_attr(tag, crash_data.get(attr))

            if len(tag) == 1:
                attr = tag.pop(0)
                return self.get_multiple_attr(attr, crash_data)

        assert isinstance(crash_data, OrderedDict), "Expected data to be OrderedDict. Was {}".format(type(crash_data))
        if isinstance(crash_data.get(tag), list):
            return crash_data.get(tag)

        return [crash_data.get(tag)]

    def _clean_element(self, tag, data):
        """
        Removes empty elements from the main xmltodict data structure so its easier to see what elements weren't
        processed at the end
        :param tag: Tag to check for emptiness
        :param data: Dictionary that contains that tag
        :return: None
        """
        if data is None:
            return

        if tag in data.keys() and data.get(tag) is None:
            data.pop(tag)
            return

        if isinstance(data.get(tag), list):
            tmplist = []
            for i in data.get(tag):
                keys = [x for x in i.keys()]  # pylint:disable=unnecessary-comprehension; acts as a deep copy
                for key in keys:
                    self._clean_element(key, i)
                if i and len(i) != 0:
                    tmplist.append(i)
            data[tag][:] = tmplist
            return

        if not isinstance(data.get(tag), OrderedDict):
            return

        # we change the dict in iteration, so we need to make a copy of the keys list
        keys = [x for x in data.get(tag).keys()]  # pylint:disable=unnecessary-comprehension; acts as a deep copy
        for key in keys:
            if key == '@i:nil':
                data.get(tag).pop('@i:nil')
            else:
                self._clean_element(key, data.get(tag))

                if key in data.get(tag).keys() and (data.get(tag).get(key) is None or len(data.get(tag).get(key)) == 0):
                    data.get(tag).pop(key)

        if len(data.get(tag)) == 0:
            data.pop(tag)
