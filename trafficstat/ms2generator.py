"""Creates data files that MS2 can use to import data"""
import datetime
import xlsxwriter

import pyodbc


class WorksheetMaker:
    """Creates XLSX files with crash data from the DOT_DATA table for MS2"""

    def __init__(self):
        conn = pyodbc.connect(r'Driver={SQL Server};Server=balt-sql311-prd;Database=DOT_DATA;Trusted_Connection=yes;')
        self.cursor = conn.cursor()
        self.workbook = None

    def __enter__(self):
        self.workbook = xlsxwriter.Workbook('BaltimoreCrash.xlsx')

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.workbook.close()

    def add_crash_worksheet(self):
        """Generates the worksheet for the acrs_crash_sanitized table"""
        self._create_worksheet("""
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
        """, "CRASH")

    def add_person_worksheet(self):
        """Generates the worksheet for the acrs_person_sanitized table"""
        self._create_worksheet("""
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
            FROM acrs_person_sanitized
        """, "PERSON")

    def add_ems_worksheet(self):
        """Generates the worksheet for the acrs_ems_sanitized table"""
        self._create_worksheet("""
            SELECT REPORT_NO,
                   EMS_UNIT_TAKEN_BY,
                   EMS_UNIT_TAKEN_TO,
                   EMS_UNIT_LABEL,
                   EMS_TRANSPORT_TYPE_FLAG as EMS_TRANSPORT_TYPE
            FROM acrs_ems_sanitized
        """, "EMS")

    def add_vehicle_worksheet(self):
        """Generates the worksheet for the acrs_vehicle_sanitized table"""
        self._create_worksheet("""
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
                   TOWED_VEHICLE_CODE1 as TOWED_VEHICLE_CONFIG_CODE1,
                   TOWED_VEHICLE_CODE2 as TOWED_VEHICLE_CONFIG_CODE2,
                   TOWED_VEHICLE_CODE3 as TOWED_VEHICLE_CONFIG_CODE3,
                   AREA_DAMAGED_CODE1,
                   AREA_DAMAGED_CODE2,
                   AREA_DAMAGED_CODE3,
                   AREA_DAMAGED_CODE_MAIN
            FROM acrs_vehicles_sanitized
        """, "VEHICLE")

    def _create_worksheet(self, sql_cmd, worksheet_name):
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
