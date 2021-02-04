"""Creates data files that MS2 can use to import data"""
import datetime
from loguru import logger
from typing import Dict, Optional
import uuid

import pyodbc  # type: ignore
import xlsxwriter  # type: ignore
from sqlalchemy import create_engine, select   # type: ignore
from sqlalchemy.sql.expression import join  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from trafficstat.ms2generator_schema import Base, CircumstanceSanitized, CitationCodeSanitized, CrashSanitized, \
    EmsSanitized, PersonSanitized, RoadwaySanitized, TrailerSanitized, VehicleSanitized


SEX = {
    '01': 'Male',
    '02': 'Female',
    '99': 'Unknown',
    'A9.99': 'BLANK VALUE FROM ACRS',
}

DIRECTION = {
    '00': 'NOT APPLICABLE',
    '01': 'NORTH',
    '02': 'SOUTH',
    '03': 'EAST',
    '04': 'WEST',
    '99': 'UNKNOWN',
    '05': 'North East',
    '06': 'South East',
    '07': 'South West',
    '08': 'North West',
    'A9.99': 'BLANK VALUE FROM ACRS',
}

REPORT_TYPE = {'01': 'Fatal Crash', '02': 'Injury Crash', '03': 'Property Damage Crash'}

# Applies to all code fields
TANG_MASTER = {
    '00': 'NOT APPLICABLE',
    '88': 'OTHER',
    '99': 'UNKNOWN',
    'A9.99': 'BLANK VALUE FROM ACRS',
    'A8.98': 'DISCONTINUED BY ACRS'
}

# VEHICLE
ACRS_VEHICLE = {
    '00': 'Not Applicable',
    '51': 'Brakes',
    '52': 'Tires',
    '53': 'Steering',
    '54': 'Lights',
    '55': 'Windows/Windshield',
    '56': 'Wheel(s)',
    '57': 'Trailer Uncoupling',
    '58': 'Cargo',
    '59': 'Engine Trouble',
    '80.88': 'Suspension',  # ACRS only (TANG: 48.88)
    '81.88': 'Mirrors',  # ACRS only (TANG: 50.88)
    '82.88': 'Wipers',  # ACRS only (TANG: 49.88)
    '83.88': 'Exhaust System',  # ACRS only (TANG: 76.88)
}

TANG_VEHICLE = {
    # '51': 'BRAKES',
    # '52': 'TIRES',
    # '53': 'STEERING',
    # '54': 'LIGHTS',
    # '55': 'WINDOWS/WINDSHIELD',
    # '56': 'WHEEL(S)',
    # '57': 'TRAILER COUPLING',
    # '58': 'CARGO',
    # '59': 'ENGINE TROUBLE',
    '48.88': 'SUSPENSION',  # TANG only (ACRS 80.88)
    '49.88': 'WIPERS',  # TANG only (ACRS 82.88)
    '50.88': 'MIRRORS',  # TANG only (ACRS 81.88)
    '84.88': 'OTHER VEHICLE DEFECT',  # Maps to ACRS code 88
    '76.88': 'EXHAUST SYSTEM',  # TANG only (ACRS 83.88)
    '85.88': 'EXHAUST SYSTEM',  # TANG only (ACRS 83.88)
}

# PERSON VALUES
ACRS_PERSON = {
    '00': 'Not Applicable',
    '01': 'Under Influence of Drugs',
    '02': 'Under Influence of Alcohol',
    '03': 'Under Influence of Medication',
    '04': 'Under Combined Influence',
    '05': 'Physical/Mental Difficulty',
    '06': 'Fell Asleep, Fainted, Etc.',
    '07': 'Failed to Give Full Time and Attention',
    '08': 'Did Not Comply with License Restrictions',
    '10': 'Improper Right Turn on Red',
    '11': 'Failed to Yield Right of Way',
    '12': 'Failed to Obey Stop Sign',
    '13': 'Failed to Obey Traffic Signal',
    '14': 'Failed to Obey Other Traffic Control',
    '15': 'Failed to Keep Right of Center',
    '16': 'Failed to Stop for School Bus',
    '17': 'Wrong Way on One Way Road',
    '18': 'Exceeded the Speed Limit',
    '19': 'Operator Using Cellular Phone',
    '20': 'Stopping in Lane/Roadway',
    '21': 'Too Fast for Conditions',
    '22': 'Followed Too Closely',
    '23': 'Improper Turn',
    '24': 'Improper Lane Change',
    '25': 'Improper Backing',
    '26': 'Improper Passing',
    '27': 'Improper Signal',
    '28': 'Improper Parking',
    '29': 'Interference/Obstruction by Passenger',
    '70.88': 'Ran Off the Road',
    '71.88': 'Disregarded Other Road Markings',
    '72.88': 'Operated Motor Vehicle in Erratic Reckless Manner',
    '73.88': 'Swerved or Avoided Vehicle or Object in Road',
    '74.88': 'Over Correcting Over Steering',
    '75.88': 'Other Improper Action',
    '76.88': 'Inattentive',
    '77.88': 'Failure to Obey Traffic Signs Signals or Officer',
    '78.88': 'Wrong Side of Road',
}

TANG_PERSON = {
    # '01': 'UNDER INFLUENCE OF DRUGS',
    # '02': 'UNDER INFLUENCE OF ALCOHOL',
    # '03': 'UNDER INFLUENCE OF MEDICATION',
    # '04': 'UNDER COMBINED INFLUENCE',
    # '05': 'PHYSICAL/MENTAL DIFFICULTY',
    # '06': 'FELL ASLEEP, FAINTED, ETC.',
    # '07': 'FAILED TO GIVE FULL TIME AND ATTENTION',
    # '08': 'DID NOT COMPLY WITH LICENSE RESTRICTIONS',
    '09': 'FAILURE TO DRIVE WITHIN A SINGLE LANE',  # TANG only
    # '10': 'IMPROPER RIGHT TURN ON RED',
    # '11': 'FAILED TO YIELD RIGHT OF WAY',
    # '12': 'FAILED TO OBEY STOP SIGN',
    # '13': 'FAILED TO OBEY TRAFFIC SIGNAL',
    # '14': 'FAILED TO OBEY OTHER TRAFFIC CONTROL',
    # '15': 'FAILED TO KEEP RIGHT OF CENTER',
    # '16': 'FAILED TO STOP FOR SCHOOL BUS',
    # '17': 'WRONG WAY ON ONE WAY ROAD',
    # '18': 'EXCEEDED THE SPEED LIMIT',
    # '19': 'OPERATOR USING CELLULAR PHONE',
    # '20': 'STOPPING IN A LANE/ROADWAY',
    # '21': 'TOO FAST FOR CONDITIONS',
    # '22': 'FOLLOWED TOO CLOSELY',
    # '23': 'IMPROPER TURN',
    # '24': 'IMPROPER LANE CHANGE',
    # '25': 'IMPROPER BACKING',
    # '26': 'IMPROPER PASSING',
    # '27': 'IMPROPER SIGNAL',
    # '28': 'IMPROPER PARKING',
    # '29': 'INTERFERENCE/OBSTRUCTION BY PASSENGER',
    '39.88': 'RAN OFF THE ROAD',  # TANG only (ACRS 70.88)
    '68.88': 'DISREGUARDED OTHER ROAD MARKINGS',  # TANG only (ACRS 71.88)
    '75.88': 'OPERATED MOTOR VEHICLE IN ERRATIC RECKLESS MANNER',  # TANG only (ACRS 72.88)
    '74.88': 'SWERVED OR AVOIDED VEHICLE OR OBJECT IN ROAD',  # TANG only (ACRS 73.88)
    '73.88': 'OVER CORRECTING OVER STEERING',  # TANG only (ACRS 74.88)
    '70.88': 'OTHER IMPROPER ACTION',  # TANG only (ACRS 75.88)
    '60.88': 'INATTENTIVE',  # TANG only (ACRS 76.88)
    '40.88': 'FAILURE TO OBEY TRAFFIC SIGNS SIGNALS OR OFFICER',  # TANG only (ACRS 77.88)
    '38.88': 'WRONG SIDE OF ROAD',  # TANG only (ACRS 78.88)
    '80.88': 'OTHER MOTORIST NON MOTORIST',  # Maps to ACRS code 88
}

# WEATHER
ACRS_WEATHER = {
    '00': 'Not Applicable',
    '41': 'Smog, Smoke',
    '42': 'Sleet, Hail, Freezing Rain',
    '43': 'Blowing Sand, Soil, Dirt',
    '44': 'Severe Crosswinds',
    '45': 'Rain, Snow',
    '46': 'Animal',
    '47': 'Vision Obstruction (including blinded by sun)',
}

TANG_WEATHER = {
    # '41': 'SMOG, SMOKE',
    # '42': 'SLEET, HAIL, FREEZ. RAIN',
    # '43': 'BLOWING SAND, SOIL, DIRT',
    # '44': 'SEVERE CROSSWINDS',
    # '45': 'RAIN, SNOW',
    # '46': 'ANIMAL',
    # '47': 'VISION OBSTRUCTION (INCL. BLINDED BY SUN)',
    '82.88': 'OTHER ENVIROMENTAL',  # Maps to ACRS code 88
}

# ROAD
ACRS_ROAD = {
    '00': 'Not Applicable',
    '61': 'Wet',
    '62': 'Icy or Snow-covered',
    '63': 'Debris or Obstruction',
    '64': 'Ruts, Holes, Bumps',
    '65': 'Road Under Construction/Maintenance',
    '66': 'Traffic Control Device Inoperative',
    '67': 'Shoulder Low, Soft, High',
    '76': 'Backup Due to Prior Crash',  # ACRS only (added April 2017)
    '77': 'Backup Due to Prior Non-Recurring Incident',  # ACRS only (added April 2017)
    '78': 'Backup Due to Regular Congestion',  # ACRS only (added April 2017)
    '79': 'Toll Booth/Plaza Related',  # ACRS only (added April 2017)
    '60.88': 'Non-highway Work',
    '68.88': 'Physical Obstruction(s)',
    '69.88': 'Worn, Travel-polished Surface',
}

TANG_ROAD = {
    # '61': 'WET',
    # '62': 'ICY OR SNOW-COVERED',
    # '63': 'DEBRIS OR OBSTRUCTION',
    # '64': 'RUTS, HOLES, BUMPS',
    # '65': 'ROAD UNDER CONSTRUCTION/MAINTENANCE',
    # '66': 'TRAFFIC CONTROL DEVICE INOPERATIVE',
    # '67': 'SHOULDERS LOW, SOFT, HIGH',
    '69.88': 'PHYSICAL OBSTRUCTION(S)',  # TANG only (ACRS 68.88)
    '71.88': 'WORN, TRAVEL-POLISHED SURFACE',  # TANG only (ACRS 69.88)
    '72.88': 'NON-HIGHWAY WORK',  # TANG only (ACRS 60.88)
    '83.88': 'OTHER ROAD CONDITION',  # Maps to ACRS code 88
}


class WorksheetMaker:  # pylint:disable=too-many-instance-attributes
    """Creates XLSX files with crash data from the DOT_DATA table for MS2"""

    def __init__(self, conn_str: str, workbook_name: str = 'BaltimoreCrash.xlsx'):
        logger.info("Creating db with connection string: {}", conn_str)
        self.engine = create_engine(conn_str, echo=True, future=True)

        with self.engine.begin() as connection:
            Base.metadata.create_all(connection)

        self.workbook = None
        self.workbook_name = workbook_name
        self.date_fmt = None

        self.person_circum_ws = None
        self.weather_circum_ws = None
        self.vehicle_circum_ws = None
        self.road_circum_ws = None

        self.road_circum_ws_row = None
        self.vehicle_circum_ws_row = None

        self.vehicle_id_dict = {}
        self.person_id_dict = {}

    def __enter__(self):
        self.workbook = xlsxwriter.Workbook(self.workbook_name)
        self.date_fmt = self.workbook.add_format({'num_format': 'mm/dd/yy'})

        # These have to exist, but do not need to be populated
        self.person_circum_ws = self.workbook.add_worksheet("PERSON_CIRCUM")
        self.weather_circum_ws = self.workbook.add_worksheet("WEATHER_CIRCUM")

        self.vehicle_circum_ws = self.workbook.add_worksheet("VEHICLE_CIRCUM")
        self.vehicle_circum_ws.write_row(0, 0, ("REPORT_NO", "CONTRIB_TYPE", "CONTRIB_CODE", "PERSON_ID", "VEHICLE_ID"))
        self.vehicle_circum_ws_row = 1

        self.road_circum_ws = self.workbook.add_worksheet("ROAD_CIRCUM")
        self.road_circum_ws.write_row(0, 0, ("REPORT_NO", "CONTRIB_TYPE", "CONTRIB_CODE", "PERSON_ID", "VEHICLE_ID"))
        self.road_circum_ws_row = 1

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.workbook.close()

    def add_crash_worksheet(self) -> None:
        """Generates the worksheet for the acrs_crash_sanitized table"""
        sql_cmd = """
            SELECT [acrs_crashes_sanitized].[LIGHT_CODE],
                   [acrs_crashes_sanitized].[COUNTY_NO],
                   [acrs_crashes_sanitized].[MUNI_CODE],
                   [acrs_crashes_sanitized].[JUNCTION_CODE],
                   [acrs_crashes_sanitized].[COLLISION_TYPE_CODE],
                   [acrs_crashes_sanitized].[SURF_COND_CODE],
                   [acrs_crashes_sanitized].[LANE_CODE],
                   [acrs_crashes_sanitized].[RD_COND_CODE],
                   [acrs_roadway_sanitized].[RD_DIV_CODE],
                   [acrs_crashes_sanitized].[FIX_OBJ_CODE],
                   [acrs_crashes_sanitized].[REPORT_NO],
                   [acrs_crashes_sanitized].[REPORT_TYPE_CODE] as REPORT_TYPE,
                   [acrs_crashes_sanitized].[WEATHER_CODE],
                   [acrs_crashes_sanitized].[ACC_DATE],
                   [acrs_crashes_sanitized].[ACC_TIME],
                   [acrs_crashes_sanitized].[LOC_CODE],
                   [acrs_crashes_sanitized].[SIGNAL_FLAG],
                   [acrs_crashes_sanitized].[C_M_ZONE_FLAG],
                   [acrs_crashes_sanitized].[AGENCY_CODE],
                   [acrs_crashes_sanitized].[AREA_CODE],
                   [acrs_crashes_sanitized].[HARM_EVENT_CODE1],
                   [acrs_crashes_sanitized].[HARM_EVENT_CODE2],
                   [acrs_roadway_sanitized].[ROUTE_NUMBER] as RTE_NO,
                   [acrs_roadway_sanitized].[ROUTE_TYPE_CODE],
                   [acrs_roadway_sanitized].[ROUTE_SUFFIX] as RTE_SUFFIX,
                   [acrs_roadway_sanitized].[LOG_MILE],
                   [acrs_roadway_sanitized].[LOGMILE_DIR_FLAG],
                   [acrs_roadway_sanitized].[ROAD_NAME] as MAINROAD_NAME,
                   [acrs_roadway_sanitized].[DISTANCE],
                   [acrs_roadway_sanitized].[FEET_MILES_FLAG],
                   [acrs_roadway_sanitized].[DISTANCE_DIR_FLAG],
                   [acrs_roadway_sanitized].[REFERENCE_NUMBER] as REFERENCE_NO,
                   [acrs_roadway_sanitized].[REFERENCE_TYPE_CODE],
                   [acrs_roadway_sanitized].[REFERENCE_SUFFIX],
                   [acrs_roadway_sanitized].[REFERENCE_ROAD_NAME],
                   [acrs_roadway_sanitized].[X_COORDINATES] as LATITUDE,
                   [acrs_roadway_sanitized].[Y_COORDINATES] as LONGITUDE
            FROM acrs_crashes_sanitized
            JOIN acrs_roadway_sanitized
            on acrs_crashes_sanitized.REPORT_NO = acrs_roadway_sanitized.REPORT_NO
        """

        def standardize_time(val: str) -> str:
            """ Convert int that is the 24 hour time into a standardized timestamp """

            val = str(val)

            try:
                val.index(":")
                return val
            except ValueError:
                val = val.zfill(4)
                return val[:2] + ":" + val[2:] + ":00"

        with Session(self.engine) as session:
            res = session.execute(select(CrashSanitized).join(RoadwaySanitized))

        """
        worksheet = self.workbook.add_worksheet("CRASH")

        # Build header row
        header_list = [i[0] for i in self.cursor.description]
        worksheet.write_row(0, 0, header_list)

        # Find the indexes of the special cases we need to deal with
        accident_date_index = header_list.index('ACC_DATE')
        accident_time_index = header_list.index('ACC_TIME')
        report_id_index = header_list.index('REPORT_TYPE')

        if accident_date_index == -1 or accident_time_index == -1:
            raise AssertionError("Unable to find all crash indexes")

        row_no = 1
        for row in self.cursor.fetchall():
            for element_no, _ in enumerate(row):

                # Deal with the special cases
                if element_no == accident_date_index:
                    worksheet.write(row_no, element_no, row[element_no].strftime('%m/%d/%Y'))
                elif element_no == accident_time_index:
                    worksheet.write(row_no, element_no, standardize_time(row[element_no]))
                elif element_no == report_id_index:
                    worksheet.write(row_no, element_no, REPORT_TYPE.get(row[element_no]))

                # Other cases
                elif isinstance(row[element_no], datetime.datetime):
                    worksheet.write(row_no, element_no, row[element_no], self.date_fmt)
                else:
                    worksheet.write(row_no, element_no, row[element_no])
            row_no += 1
        """

    def add_person_worksheet(self) -> None:
        """Generates the worksheet for the acrs_person_sanitized table"""
        sql_cmd = """
            SELECT SEX as SEX_CODE,
                   CONDITION_CODE,
                   INJ_SEVER_CODE,
                   REPORT_NO,
                   OCC_SEAT_POS_CODE,
                   PED_VISIBLE_CODE,
                   PED_LOCATION_CODE,
                   PED_OBEY_CODE,
                   PED_TYPE_CODE,
                   MOVEMENT_CODE,
                   PERSON_TYPE,
                   ALCO_TEST_CODE as ALCOHOL_TEST_CODE,
                   ALCO_TEST_TYPE_CODE as ALCOHOL_TESTTYPE_CODE,
                   DRUG_TEST_CODE,
                   DRUG_TEST_RESULT_FLAG as DRUG_TESTRESULT_CODE,
                   BAC as BAC_CODE,
                   FAULT_FLAG,
                   EQUIP_PROB_CODE,
                   SAF_EQUIP_CODE,
                   EJECT_CODE,
                   AIR_BAG_CODE as AIRBAG_DEPLOYED,
                   DRIVER_DOB as DATE_OF_BIRTH,
                   PERSON_ID,
                   STATE_CODE as LICENSE_STATE_CODE,
                   CLASS,
                   CDL_FLAG,
                   VEHICLE_ID,
                   EMS_UNIT_LABEL
            FROM acrs_person_sanitized"""

        with Session(self.engine) as session:
            res = session.execute(select(PersonSanitized))

        """    
        self.cursor.execute(sql_cmd)
        worksheet = self.workbook.add_worksheet("PERSON")

        # Build header row
        header_list = [i[0] for i in self.cursor.description]
        worksheet.write_row(0, 0, header_list)

        # Find the indexes of the special cases we need to deal with
        person_id_index = header_list.index('PERSON_ID')
        vehicle_id_index = header_list.index('VEHICLE_ID')
        sex_index = header_list.index('SEX_CODE')

        if person_id_index == -1 or vehicle_id_index == -1 or sex_index == -1:
            raise AssertionError("Unable to find person indexes")

        worksheet.write_row(0, 0, header_list)
        row_no = 1
        for row in self.cursor.fetchall():
            for element_no, _ in enumerate(row):
                # Deal with the special cases
                if element_no == person_id_index:
                    worksheet.write(row_no, element_no, self._get_person_uuid(row[element_no]))
                elif element_no == vehicle_id_index:
                    worksheet.write(row_no, element_no, self._get_vehicle_uuid(row[element_no]))
                elif element_no == sex_index:
                    worksheet.write(row_no, element_no, self._lookup_sex(row[element_no]))

                # Other cases
                elif isinstance(row[element_no], datetime.datetime):
                    worksheet.write(row_no, element_no, row[element_no], self.date_fmt)
                else:
                    worksheet.write(row_no, element_no, row[element_no])

            row_no += 1
        """

    def add_ems_worksheet(self) -> None:
        """Generates the worksheet for the acrs_ems_sanitized table"""
        with Session(self.engine) as session:
            res = session.execute(select(EmsSanitized))
        #self._create_worksheet("""
        #    SELECT REPORT_NO,
        #           EMS_UNIT_TAKEN_BY,
        #           EMS_UNIT_TAKEN_TO,
        #           EMS_UNIT_LABEL,
        #           EMS_TRANSPORT_TYPE_FLAG as EMS_TRANSPORT_TYPE
        #    FROM acrs_ems_sanitized
        #""", "EMS")

    def add_vehicle_worksheet(self) -> None:
        """Generates the worksheet for the acrs_vehicle_sanitized table"""
        sql_cmd = """
            SELECT HARM_EVENT_CODE,
                   CONTI_DIRECTION_CODE,
                   DAMAGE_CODE,
                   MOVEMENT_CODE,
                   VEHICLE_ID as VIN_NO,
                   REPORT_NO,
                   CV_BODY_TYPE_CODE,
                   VEH_YEAR,
                   VEH_MAKE,
                   COMMERCIAL_FLAG,
                   VEH_MODEL,
                   HZM_NAME as HZM_NUM,
                   TOWED_AWAY_FLAG,
                   NUM_AXLES,
                   GVW as GVW_CODE,
                   GOING_DIRECTION_CODE,
                   BODY_TYPE_CODE,
                   DRIVERLESS_FLAG,
                   FIRE_FLAG,
                   PARKED_FLAG,
                   SPEED_LIMIT,
                   HIT_AND_RUN_FLAG,
                   HAZMAT_SPILL_FLAG,
                   VEHICLE_ID,
                   TOWED_VEHICLE_CODE1 as TOWED_VEHICLE_CONFIG_CODE,
                   AREA_DAMAGED_CODE_IMP1,
                   AREA_DAMAGED_CODE1,
                   AREA_DAMAGED_CODE2,
                   AREA_DAMAGED_CODE3,
                   AREA_DAMAGED_CODE_MAIN
            FROM acrs_vehicles_sanitized
        """
        with Session(self.engine) as session:
            res = session.execute(select(VehicleSanitized))

        """
        self.cursor.execute(sql_cmd)
        worksheet = self.workbook.add_worksheet("VEHICLE")

        # Build header row
        header_list = [i[0] for i in self.cursor.description]
        worksheet.write_row(0, 0, header_list)

        # Find the indexes of the special cases we need to deal with
        report_no_index = header_list.index('REPORT_NO')
        vehicle_id_index = header_list.index('VEHICLE_ID')
        cont_dir_index = header_list.index('CONTI_DIRECTION_CODE')
        going_dir_index = header_list.index('GOING_DIRECTION_CODE')

        if report_no_index == -1 or vehicle_id_index == -1 or cont_dir_index == -1 or going_dir_index == -1:
            raise AssertionError("Unable to find vehicle index")

        row_no = 1
        for row in self.cursor.fetchall():
            self.add_vehicle_circum(row[report_no_index],
                                    row[vehicle_id_index],
                                    self.vehicle_id_dict[row[vehicle_id_index]])

            for element_no, _ in enumerate(row):

                # Deal with the special cases
                if element_no == vehicle_id_index:
                    worksheet.write(row_no, element_no, self._get_vehicle_uuid(row[element_no]))
                elif element_no == cont_dir_index:
                    worksheet.write(row_no, element_no, self._lookup_direction(row[element_no]))
                elif element_no == going_dir_index:
                    worksheet.write(row_no, element_no, self._lookup_direction(row[element_no]))

                # Other cases
                elif isinstance(row[element_no], datetime.datetime):
                    worksheet.write(row_no, element_no, row[element_no], self.date_fmt)
                else:
                    worksheet.write(row_no, element_no, row[element_no])

            row_no += 1
        """

    def add_vehicle_circum(self, report_no: str, vehicle_id: str, vehicle_uuid: str) -> None:
        """ Creates the vehicle_circum sheet"""
        with Session(self.engine) as session:
            res = session.execute(select(CircumstanceSanitized))
        #self.cursor.execute("""
        #    SELECT *
        #    FROM [acrs_circumstances_sanitized]
        #    WHERE [CONTRIB_FLAG] = 'V' AND
        #        [REPORT_NO] = ? AND
        #        [VEHICLE_ID] = ?
        #""", str(report_no), str(vehicle_id))

        """
        for row in self.cursor.fetchall():
            for contrib in set(row[1:5]):
                val = self._validate_vehicle_value(contrib)
                if val is not None:
                    self.vehicle_circum_ws.write_row(self.vehicle_circum_ws_row, 0,
                                                     (report_no,
                                                      'Vehicle',
                                                      self._validate_vehicle_value(contrib),
                                                      None,
                                                      vehicle_uuid))
                    self.vehicle_circum_ws_row += 1
        """

    def add_road_circum(self) -> None:
        """ Creates blank road_circum sheet"""
        with Session(self.engine) as session:
            res = session.execute(select(CircumstanceSanitized))
        #self.cursor.execute("""
        #    SELECT *
        #    FROM [acrs_circumstances_sanitized]
        #    WHERE [CONTRIB_FLAG] = 'R'
        #""")
        """
        for row in self.cursor.fetchall():
            for contrib in set(row[1:5]):
                val = self._validate_road_value(contrib)
                if val is not None:
                    self.road_circum_ws.write_row(self.road_circum_ws_row, 0,
                                                  (row[0],
                                                   'Road',
                                                   contrib,
                                                   None,
                                                   None))
                    self.road_circum_ws_row += 1
        """

    def _validate_vehicle_value(self, val: str) -> Optional[str]:
        """ Validates circumstance values for vehicles """
        master_dict = {}
        master_dict.update(TANG_VEHICLE)
        master_dict.update(TANG_MASTER)
        master_dict.update(ACRS_VEHICLE)

        ret = None
        try:
            ret = self._validate_value(val, master_dict)
        except AssertionError:
            print("Invalid vehicle value: ", val)

        return ret

    def _validate_person_value(self, val: str) -> Optional[str]:
        """ Validates circumstance values for persons """
        master_dict = {}
        master_dict.update(TANG_PERSON)
        master_dict.update(TANG_MASTER)
        master_dict.update(ACRS_PERSON)

        ret = None
        try:
            ret = self._validate_value(val, master_dict)
        except AssertionError:
            print("Invalid person value: ", val)

        return ret

    def _validate_weather_value(self, val: str) -> Optional[str]:
        """ Validates circumstance values for weather """
        master_dict = {}
        master_dict.update(TANG_WEATHER)
        master_dict.update(TANG_MASTER)
        master_dict.update(ACRS_WEATHER)

        ret = None
        try:
            ret = self._validate_value(val, master_dict)
        except AssertionError:
            print("Invalid weather value: {}", val)

        return ret

    def _validate_road_value(self, val: str) -> Optional[str]:
        """ Validates circumstance values for road """
        master_dict = {}
        master_dict.update(TANG_ROAD)
        master_dict.update(TANG_MASTER)
        master_dict.update(ACRS_ROAD)

        ret = None
        try:
            ret = self._validate_value(val, master_dict)
        except AssertionError:
            print("Invalid road value: {}", val)

        return ret

    @staticmethod
    def _validate_value(val: str, master_dict: Dict) -> str:
        if val is None:
            return None

        val = str(val)
        if val not in master_dict.keys():
            raise AssertionError("Unable to validate {}. Expected values {}".format(val, master_dict.keys()))
        return val

    @staticmethod
    def _lookup_sex(val: str) -> Optional[str]:
        master_dict = {}
        master_dict.update(TANG_MASTER)
        master_dict.update(SEX)

        return master_dict.get(val)

    @staticmethod
    def _lookup_direction(val: str) -> Optional[str]:
        master_dict = {}
        master_dict.update(TANG_MASTER)
        master_dict.update(DIRECTION)

        return master_dict.get(val)

    def _create_worksheet(self, sql_cmd: str, worksheet_name: str) -> None:
        """
        Writes the first line of headers as strings
        :param sql_cmd: SQL statement to execute
        :param worksheet_name: Name of the sheet to add
        :return: None
        """
        self.cursor.execute(sql_cmd)
        worksheet = self.workbook.add_worksheet(worksheet_name)
        header_list = [i[0] for i in self.cursor.description]

        for col_num, _ in enumerate(header_list):
            worksheet.write(0, col_num, header_list[col_num])

        date_fmt = self.workbook.add_format({'num_format': 'mm/dd/yy'})

        row_no = 1
        for row in self.cursor.fetchall():
            for element_no, _ in enumerate(row):
                if isinstance(row[element_no], datetime.datetime):
                    worksheet.write(row_no, element_no, row[element_no], date_fmt)
                elif isinstance(row[element_no], str) and row[element_no].isdigit():
                    worksheet.write(row_no, element_no, int(row[element_no]))
                else:
                    worksheet.write(row_no, element_no, row[element_no])
            row_no += 1

    def _get_person_uuid(self, person_id: str) -> str:
        """ Safe lookup of the person uuid """
        if self.vehicle_id_dict.get(person_id) is None:
            self.vehicle_id_dict[person_id] = str(uuid.uuid4())
        return self.vehicle_id_dict[person_id]

    def _get_vehicle_uuid(self, vehicle_id: str) -> str:
        """ Safe lookup of the vehicle uuid """
        if self.vehicle_id_dict.get(vehicle_id) is None:
            self.vehicle_id_dict[vehicle_id] = str(uuid.uuid4())
        return self.vehicle_id_dict[vehicle_id]
