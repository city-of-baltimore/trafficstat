"""Creates data files that MS2 can use to import data"""
import datetime
import uuid
from typing import Dict, Optional

import xlsxwriter  # type: ignore
from loguru import logger
from sqlalchemy import and_, create_engine, select  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from trafficstat.crash_data_schema import Crash, Roadway
from trafficstat.ms2generator_schema import Base, CircumstanceSanitized, CrashSanitized, EmsSanitized, \
    PersonSanitized, RoadwaySanitized, VehicleSanitized

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
    '0': 'NOT APPLICABLE',
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
    '1': 'Under Influence of Drugs',
    '01': 'Under Influence of Drugs',
    '2': 'Under Influence of Alcohol',
    '02': 'Under Influence of Alcohol',
    '3': 'Under Influence of Medication',
    '03': 'Under Influence of Medication',
    '4': 'Under Combined Influence',
    '04': 'Under Combined Influence',
    '5': 'Physical/Mental Difficulty',
    '05': 'Physical/Mental Difficulty',
    '6': 'Fell Asleep, Fainted, Etc.',
    '06': 'Fell Asleep, Fainted, Etc.',
    '7': 'Failed to Give Full Time and Attention',
    '07': 'Failed to Give Full Time and Attention',
    '8': 'Did Not Comply with License Restrictions',
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

        self.workbook_name = workbook_name

        self.vehicle_id_dict: dict = {}
        self.person_id_dict: dict = {}

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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.workbook.close()

    def add_crash_worksheet(self) -> None:  # pylint:disable=too-many-branches
        """Generates the worksheet for the acrs_crash_sanitized table"""
        with Session(self.engine) as session:
            qry_sanitized = session.query(CrashSanitized.LIGHT_CODE,
                                          CrashSanitized.COUNTY_NO,
                                          CrashSanitized.MUNI_CODE,
                                          CrashSanitized.JUNCTION_CODE,
                                          CrashSanitized.COLLISION_TYPE_CODE,
                                          CrashSanitized.SURF_COND_CODE,
                                          CrashSanitized.LANE_CODE,
                                          CrashSanitized.RD_COND_CODE,
                                          RoadwaySanitized.RD_DIV_CODE,
                                          CrashSanitized.FIX_OBJ_CODE,
                                          CrashSanitized.REPORT_NO,
                                          CrashSanitized.REPORT_TYPE_CODE,  # REPORT_TYPE_CODE as REPORT_TYPE,
                                          CrashSanitized.WEATHER_CODE,
                                          CrashSanitized.ACC_DATE,
                                          CrashSanitized.ACC_TIME,
                                          CrashSanitized.LOC_CODE,
                                          CrashSanitized.SIGNAL_FLAG,
                                          CrashSanitized.C_M_ZONE_FLAG,
                                          CrashSanitized.AGENCY_CODE,
                                          CrashSanitized.AREA_CODE,
                                          CrashSanitized.HARM_EVENT_CODE1,
                                          CrashSanitized.HARM_EVENT_CODE2,
                                          RoadwaySanitized.ROUTE_NUMBER,  # ROUTE_NUMBER as RTE_NO,
                                          RoadwaySanitized.ROUTE_TYPE_CODE,
                                          RoadwaySanitized.ROUTE_SUFFIX,  # ROUTE_SUFFIX as RTE_SUFFIX,
                                          RoadwaySanitized.LOG_MILE,
                                          RoadwaySanitized.LOGMILE_DIR_FLAG,
                                          RoadwaySanitized.ROAD_NAME,  # ROAD_NAME as MAINROAD_NAME,
                                          RoadwaySanitized.DISTANCE,
                                          RoadwaySanitized.FEET_MILES_FLAG,
                                          RoadwaySanitized.DISTANCE_DIR_FLAG,
                                          RoadwaySanitized.REFERENCE_NUMBER,  # REFERENCE_NUMBER as REFERENCE_NO,
                                          RoadwaySanitized.REFERENCE_TYPE_CODE,
                                          RoadwaySanitized.REFERENCE_SUFFIX,
                                          RoadwaySanitized.REFERENCE_ROAD_NAME,
                                          RoadwaySanitized.X_COORDINATES,  # X_COORDINATES as LATITUDE,
                                          RoadwaySanitized.Y_COORDINATES  # Y_COORDINATES as LONGITUDE
                                          ).join(CrashSanitized.ROADWAY)

            qry_unsanitized = session.query(Crash.LIGHT,
                                            Crash.REPORTCOUNTYLOCATION,
                                            Roadway.MUNICIPAL,
                                            Crash.JUNCTION,
                                            Crash.COLLISIONTYPE,
                                            Crash.SURFACECONDITION,
                                            Crash.LANEDIRECTION + Crash.LANENUMBER,
                                            Crash.ROADCONDITION,
                                            Crash.ROADDIVISION,
                                            Crash.FIXEDOBJECTSTRUCK,
                                            Crash.REPORTNUMBER,
                                            Crash.REPORTTYPE,
                                            Crash.WEATHER,
                                            Crash.CRASHDATE,
                                            Crash.CRASHTIME,
                                            Crash.LOCALCODES,
                                            Crash.TRAFFICCONTROL,
                                            Crash.CONMAINZONE,
                                            Crash.AGENCYNAME,
                                            Crash.AREA,
                                            Crash.HARMFULEVENTONE,
                                            Crash.HARMFULEVENTTWO,
                                            Roadway.ROUTE_NUMBER,
                                            Roadway.ROUTE_TYPE,
                                            Roadway.ROUTE_SUFFIX,
                                            Roadway.MILEPOINT,  # RoadwaySanitized.LOG_MILE,
                                            Roadway.LOGMILE_DIR,  # RoadwaySanitized.LOGMILE_DIR_FLAG,
                                            Roadway.ROAD_NAME,
                                            Crash.MILEPOINTDISTANCE,  # distance
                                            Crash.MILEPOINTDISTANCEUNITS,
                                            Crash.MILEPOINTDIRECTION,  # distance dir flag
                                            Roadway.REFERENCE_ROUTE_NUMBER,
                                            Roadway.REFERENCE_ROUTE_TYPE,
                                            Roadway.REFERENCE_ROUTE_SUFFIX,
                                            Roadway.REFERENCE_ROADNAME,
                                            Crash.LATITUDE,
                                            Crash.LONGITUDE
                                            ).join(Crash.ROADWAY).where(Crash.CRASHDATE > '2020-01-01')

            worksheet = self.workbook.add_worksheet("CRASH")
            key_subs = {
                'REPORT_TYPE_CODE': 'REPORT_TYPE',
                'ROUTE_NUMBER': 'RTE_NO',
                'ROUTE_SUFFIX': 'RTE_SUFFIX',
                'ROAD_NAME': 'MAINROAD_NAME',
                'REFERENCE_NUMBER': 'REFERENCE_NO',
                'X_COORDINATES': 'LATITUDE',
                'Y_COORDINATES': 'LONGITUDE',
            }

            row_no = 0
            for row in qry_sanitized.all() + qry_unsanitized.all():
                if row_no == 0:
                    # Build header row
                    header_list = list(row.keys())
                    for orig, repl in key_subs.items():
                        header_list[header_list.index(orig)] = repl
                    worksheet.write_row(0, 0, header_list)

                    # These columns need to be zero padded, to make them a two digit number
                    padded_ints = [header_list.index('LIGHT_CODE'), header_list.index('COLLISION_TYPE_CODE'),
                                   header_list.index('FIX_OBJ_CODE'), header_list.index('WEATHER_CODE'),
                                   header_list.index('HARM_EVENT_CODE1'), header_list.index('HARM_EVENT_CODE2')]

                    row_no += 1

                for element_no, _ in enumerate(row):

                    # Deal with the special cases
                    if element_no == header_list.index('ACC_DATE'):
                        worksheet.write(row_no, element_no, row[element_no].strftime('%m/%d/%Y'))
                    elif element_no == header_list.index('REPORT_TYPE'):
                        worksheet.write(row_no, element_no, REPORT_TYPE.get(row[element_no]))
                    elif element_no == header_list.index('ACC_TIME'):
                        if isinstance(row[element_no], datetime.time):
                            worksheet.write(row_no, element_no, row[element_no].strftime('%H%M'))
                        else:
                            # needs to be a four digit number, left zero padded
                            worksheet.write(row_no, element_no, str(row[element_no]).zfill(4))
                    elif element_no == header_list.index('MUNI_CODE'):
                        # needs to be a three digit number, left zero padded
                        worksheet.write(row_no, element_no, str(row[element_no]).zfill(3))
                    elif element_no in padded_ints:
                        val = int(row[element_no]) if isinstance(row[element_no], float) else row[element_no]

                        # needs to be a two digit number, left zero padded
                        worksheet.write(row_no, element_no, str(val).zfill(2))
                    elif element_no == header_list.index('C_M_ZONE_FLAG') and isinstance(row[element_no], bool):
                        worksheet.write(row_no, element_no, 'Y' if row[element_no] else 'N')

                    # Other cases
                    elif isinstance(row[element_no], datetime.datetime):
                        worksheet.write(row_no, element_no, row[element_no], self.date_fmt)
                    else:
                        worksheet.write(row_no, element_no, row[element_no])
                row_no += 1

    def add_person_worksheet(self) -> None:
        """Generates the worksheet for the acrs_person_sanitized table"""
        with Session(self.engine) as session:
            qry = session.execute(select(PersonSanitized.SEX,
                                         PersonSanitized.CONDITION_CODE,
                                         PersonSanitized.INJ_SEVER_CODE,
                                         PersonSanitized.REPORT_NO,
                                         PersonSanitized.OCC_SEAT_POS_CODE,
                                         PersonSanitized.PED_VISIBLE_CODE,
                                         PersonSanitized.PED_LOCATION_CODE,
                                         PersonSanitized.PED_OBEY_CODE,
                                         PersonSanitized.PED_TYPE_CODE,
                                         PersonSanitized.MOVEMENT_CODE,
                                         PersonSanitized.PERSON_TYPE,
                                         PersonSanitized.ALCO_TEST_CODE,  # ALCO_TEST_CODE as ALCOHOL_TEST_CODE,
                                         PersonSanitized.ALCO_TEST_TYPE_CODE,
                                         # ALCO_TEST_TYPE_CODE as ALCOHOL_TESTTYPE_CODE,
                                         PersonSanitized.DRUG_TEST_CODE,
                                         PersonSanitized.DRUG_TEST_RESULT_FLAG,
                                         # DRUG_TEST_RESULT_FLAG as DRUG_TESTRESULT_CODE,
                                         PersonSanitized.BAC,  # BAC as BAC_CODE,
                                         PersonSanitized.FAULT_FLAG,
                                         PersonSanitized.EQUIP_PROB_CODE,
                                         PersonSanitized.SAF_EQUIP_CODE,
                                         PersonSanitized.EJECT_CODE,
                                         PersonSanitized.AIR_BAG_CODE,  # AIR_BAG_CODE as AIRBAG_DEPLOYED,
                                         PersonSanitized.DRIVER_DOB,  # DRIVER_DOB as DATE_OF_BIRTH,
                                         PersonSanitized.PERSON_ID,
                                         PersonSanitized.STATE_CODE,  # STATE_CODE as LICENSE_STATE_CODE,
                                         PersonSanitized.CLASS,
                                         PersonSanitized.CDL_FLAG,
                                         PersonSanitized.VEHICLE_ID,
                                         PersonSanitized.EMS_UNIT_LABEL))

            # headers that need to be renamed
            key_subs = {
                'ALCO_TEST_CODE': 'ALCOHOL_TEST_CODE',
                'ALCO_TEST_TYPE_CODE': 'ALCOHOL_TESTTYPE_CODE',
                'DRUG_TEST_RESULT_FLAG': 'DRUG_TESTRESULT_CODE',
                'BAC': 'BAC_CODE',
                'AIR_BAG_CODE': 'AIRBAG_DEPLOYED',
                'DRIVER_DOB': 'DATE_OF_BIRTH',
                'STATE_CODE': 'LICENSE_STATE_CODE'
            }

            worksheet = self.workbook.add_worksheet("PERSON")

            row_no = 0
            for row in qry.fetchall():
                if row_no == 0:
                    # Build header row
                    header_list = list(row.keys())
                    for orig, repl in key_subs.items():
                        header_list[header_list.index(orig)] = repl

                    worksheet.write_row(0, 0, header_list)

                    row_no += 1

                for element_no, _ in enumerate(row):
                    # Deal with the special cases
                    if element_no == header_list.index('PERSON_ID'):
                        worksheet.write(row_no, element_no, self._get_person_uuid(row[element_no]))
                    elif element_no == header_list.index('VEHICLE_ID'):
                        worksheet.write(row_no, element_no, self._get_vehicle_uuid(row[element_no]))
                    elif element_no == header_list.index('SEX'):
                        worksheet.write(row_no, element_no, self._lookup_sex(row[element_no]))

                    # Other cases
                    elif isinstance(row[element_no], datetime.datetime):
                        worksheet.write(row_no, element_no, row[element_no], self.date_fmt)
                    else:
                        worksheet.write(row_no, element_no, row[element_no])

                row_no += 1

    def add_ems_worksheet(self) -> None:
        """Generates the worksheet for the acrs_ems_sanitized table"""
        with Session(self.engine) as session:
            qry = session.execute(select(EmsSanitized.REPORT_NO,
                                         EmsSanitized.EMS_UNIT_TAKEN_BY,
                                         EmsSanitized.EMS_UNIT_TAKEN_TO,
                                         EmsSanitized.EMS_UNIT_LABEL,
                                         EmsSanitized.EMS_TRANSPORT_TYPE_FLAG))

            worksheet = self.workbook.add_worksheet("EMS")
            date_fmt = self.workbook.add_format({'num_format': 'mm/dd/yy'})
            key_subs = {'EMS_TRANSPORT_TYPE_FLAG': 'EMS_TRANSPORT_TYPE'}

            row_no = 0
            for row in qry.fetchall():
                if row_no == 0:
                    header_list = list(row.keys())
                    for orig, repl in key_subs.items():
                        header_list[header_list.index(orig)] = repl

                    for col_num, _ in enumerate(header_list):
                        worksheet.write(0, col_num, header_list[col_num])
                    row_no += 1

                for element_no, _ in enumerate(row):
                    if isinstance(row[element_no], datetime.datetime):
                        worksheet.write(row_no, element_no, row[element_no], date_fmt)
                    elif isinstance(row[element_no], str) and row[element_no].isdigit():
                        worksheet.write(row_no, element_no, int(row[element_no]))
                    else:
                        worksheet.write(row_no, element_no, row[element_no])
                row_no += 1

    def add_vehicle_worksheet(self) -> None:
        """Generates the worksheet for the acrs_vehicle_sanitized table"""
        with Session(self.engine) as session:
            qry = session.execute(select(VehicleSanitized.HARM_EVENT_CODE,
                                         VehicleSanitized.CONTI_DIRECTION_CODE,
                                         VehicleSanitized.DAMAGE_CODE,
                                         VehicleSanitized.MOVEMENT_CODE,
                                         VehicleSanitized.VIN_NO,  # VEHICLE_ID as VIN_NO,
                                         VehicleSanitized.REPORT_NO,
                                         VehicleSanitized.CV_BODY_TYPE_CODE,
                                         VehicleSanitized.VEH_YEAR,
                                         VehicleSanitized.VEH_MAKE,
                                         VehicleSanitized.COMMERCIAL_FLAG,
                                         VehicleSanitized.VEH_MODEL,
                                         VehicleSanitized.HZM_NUM,  # HZM_NAME as HZM_NUM,
                                         VehicleSanitized.TOWED_AWAY_FLAG,
                                         VehicleSanitized.NUM_AXLES,
                                         VehicleSanitized.GVW_CODE,  # GVW as GVW_CODE,
                                         VehicleSanitized.GOING_DIRECTION_CODE,
                                         VehicleSanitized.BODY_TYPE_CODE,
                                         VehicleSanitized.DRIVERLESS_FLAG,
                                         VehicleSanitized.FIRE_FLAG,
                                         VehicleSanitized.PARKED_FLAG,
                                         VehicleSanitized.SPEED_LIMIT,
                                         VehicleSanitized.HIT_AND_RUN_FLAG,
                                         VehicleSanitized.HAZMAT_SPILL_FLAG,
                                         VehicleSanitized.VIN_NO,  # duplicate to be renamed VEHICLE_ID
                                         VehicleSanitized.TOWED_VEHICLE_CONFIG_CODE,
                                         # TOWED_VEHICLE_CODE1 as TOWED_VEHICLE_CONFIG_CODE,
                                         VehicleSanitized.AREA_DAMAGED_CODE_IMP1,
                                         VehicleSanitized.AREA_DAMAGED_CODE1,
                                         VehicleSanitized.AREA_DAMAGED_CODE2,
                                         VehicleSanitized.AREA_DAMAGED_CODE3,
                                         VehicleSanitized.AREA_DAMAGED_CODE_MAIN))

            worksheet = self.workbook.add_worksheet("VEHICLE")

            row_no = 0
            for row in qry.fetchall():

                if row_no == 0:
                    # Replace the last instane of VIN_NO with VEHICLE_ID, per the spec
                    header_list = list(row.keys())
                    header_list[header_list.index('VEHICLE_ID_1')] = 'VEHICLE_ID'
                    worksheet.write_row(0, 0, header_list)

                    # Find the indexes of the special cases we need to deal with
                    report_no_index = header_list.index('REPORT_NO')
                    vehicle_id_index = header_list.index('VEHICLE_ID')
                    cont_dir_index = header_list.index('CONTI_DIRECTION_CODE')
                    going_dir_index = header_list.index('GOING_DIRECTION_CODE')

                    row_no += 1

                self.add_vehicle_circum(row[report_no_index],
                                        row[vehicle_id_index])

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

    def add_vehicle_circum(self, report_no: str, vehicle_id: str) -> None:
        """ Creates the vehicle_circum sheet"""
        with Session(self.engine) as session:
            qry = session.execute(select(CircumstanceSanitized.REPORT_NO, CircumstanceSanitized.CONTRIB_CODE1,
                                         CircumstanceSanitized.CONTRIB_CODE2, CircumstanceSanitized.CONTRIB_CODE3,
                                         CircumstanceSanitized.CONTRIB_CODE4).
                                  where(and_(CircumstanceSanitized.CONTRIB_FLAG == 'V',
                                             CircumstanceSanitized.REPORT_NO == report_no,
                                             CircumstanceSanitized.VEHICLE_ID == vehicle_id)))

            for row in qry.fetchall():
                report_no = row[0]
                for contrib_code in row[1:]:
                    try:
                        val = self._validate_vehicle_value(contrib_code)
                    except ValueError as err:
                        logger.error(err)
                        continue

                    if val is not None:
                        self.vehicle_circum_ws.write_row(self.road_circum_ws_row, 0,
                                                         (report_no,
                                                          'Vehicle',
                                                          contrib_code,
                                                          None,
                                                          self._get_vehicle_uuid(vehicle_id) if vehicle_id else None))
                        self.road_circum_ws_row += 1

    def add_road_circum(self) -> None:
        """ Populates the road sheet"""
        with Session(self.engine) as session:
            qry = session.execute(select(CircumstanceSanitized.REPORT_NO, CircumstanceSanitized.CONTRIB_CODE1,
                                         CircumstanceSanitized.CONTRIB_CODE2, CircumstanceSanitized.CONTRIB_CODE3,
                                         CircumstanceSanitized.CONTRIB_CODE4).
                                  where(CircumstanceSanitized.CONTRIB_FLAG == 'R'))
            for row in qry.fetchall():
                report_no = row[0]
                for contrib_code in row[1:]:
                    try:
                        val = self._validate_road_value(contrib_code)
                    except ValueError as err:
                        logger.error(err)
                        continue

                    if val is not None:
                        self.road_circum_ws.write_row(self.road_circum_ws_row, 0,
                                                      (report_no,
                                                       'Road',
                                                       contrib_code,
                                                       None,
                                                       None))
                        self.road_circum_ws_row += 1

    def _validate_vehicle_value(self, val: str) -> Optional[str]:
        """ Validates circumstance values for vehicles """
        master_dict = {}
        master_dict.update(TANG_VEHICLE)
        master_dict.update(TANG_MASTER)
        master_dict.update(ACRS_VEHICLE)

        ret = self._validate_value(val, master_dict)

        return ret

    def _validate_person_value(self, val: str) -> str:
        """ Validates circumstance values for persons. Will raise ValueError if val is not a valid person code. """
        master_dict = {}
        master_dict.update(TANG_PERSON)
        master_dict.update(TANG_MASTER)
        master_dict.update(ACRS_PERSON)

        ret = self._validate_value(val, master_dict)

        return ret

    def _validate_weather_value(self, val: str) -> str:
        """ Validates circumstance values for weather. Will raise ValueError if val is not a valid weather code. """
        master_dict = {}
        master_dict.update(TANG_WEATHER)
        master_dict.update(TANG_MASTER)
        master_dict.update(ACRS_WEATHER)

        ret = self._validate_value(val, master_dict)

        return ret

    def _validate_road_value(self, val: str) -> str:
        """ Validates circumstance values for road. Will raise ValueError if val is not a valid road code. """
        master_dict = {}
        master_dict.update(TANG_ROAD)
        master_dict.update(TANG_MASTER)
        master_dict.update(ACRS_ROAD)

        ret = self._validate_value(val, master_dict)

        return ret

    @staticmethod
    def _validate_value(val: str, master_dict: Dict) -> str:
        if val is None:
            return None

        val = str(val)
        if val not in master_dict.keys():
            raise ValueError("Unable to validate {}. Expected values {}".format(val, master_dict.keys()))
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


if __name__ == '__main__':
    ws_maker = WorksheetMaker(
        conn_str="mssql+pyodbc://balt-sql311-prd/DOT_DATA?driver=ODBC Driver 17 for SQL Server")
    with ws_maker:
        ws_maker.add_crash_worksheet()
        ws_maker.add_person_worksheet()
        ws_maker.add_ems_worksheet()
        ws_maker.add_vehicle_worksheet()
        ws_maker.add_road_circum()
