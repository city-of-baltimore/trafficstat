# trafficstat
Library that handles the parsing, cleaning and exporting of ACRS crash data. This library is able to process raw ACRS XML files and put them into most any kind of database. It also can generate CSV files from that data, which can be ingested by MS2 for better visualization. 

## Setup ##
To setup your environment:

1. Check out the code. Either download it from the Github repository, or clone it with Git
2. Create a virtual environment. `python -m venv .venv`
3. Activate the virtual environment. `.venv\Scripts\activate`
4. Download all required python libraries. `python -m pip install -r requirements.txt`
5. Install the trafficstat library. `python setup.py install`

## Parse XML Files
To parse ACRS XML files, run 

`python main.py parse --directory <path>`

By default, this will process all files with an `.xml` extension, create the required database structure, parse the data into a database, and move the processed files into a `.processed` directory in the same folder that they were originally stored in. By default, it will put the data into a SQLite database file `crash.db`

To use a different database, pass the connection string with the `--conn_str` argument. For example, to use a different SQLite database:

`python main.py parse --directory <path> --conn_str sqlite://c:\Program Files\acrsdb.db`

To use the Baltimore City SQL Server:

`python main.py parse --directory <path> --conn_str "mssql+pyodbc://balt-sql311-prd/DOT_DATA?driver=ODBC Driver 17 for SQL Server"`

## Data Enrichment
The State Highway Administration also releases sanitized crash data, which comes without latitude and longitude. After the data is imported from the AACDB files, the enrichment script will add geocoding information.  

**To import data from an aacdb file:**

This applies to the sanitized data that the State Highway Administration

1. Open the aacdb file in Access and save the file as an mdb file.
2. Open Sql Server Management server, and right click the database that the data will be inserted into
3. Select tasks->import data. Click next.
4. Select Microsoft Access as the data source and select the file. Click next.
5. Select Microsoft OLE DB Driver for Sql Server as the destination and click properties
* Server name: balt-sql311-prd
* Authentication: Windows Authentication
* Select the database: DOT_DATA
6. Test connection. If it succeeds, then click ok. 
7. Select 'Copy data from one or more tables or views'
8. There should be eight tables in the list to be copied. Click the check box for each of the eight tables.
9. They will have different names in different years, but there should basicaly be a table each for crashes, citations, circumstances, EMS, persons, roadways, trailers, and vehicles. Enter the following table names in the second column that correlates with the source name in the left column.
    ```
    Table names:
    * acrs_crash_sanitized
    * acrs_citation_code_sanitized
    * acrs_circumstance_sanitized
    * acrs_ems_sanitized
    * acrs_person_sanitized
    * acrs_roadway_sanitized
    * acrs_trailer_sanitized
    * acrs_vehicle_sanitized
    ```

10. Click the crash table entry, and click Edit Mappings. Then click Edit SQL, and paste in the following.
    ```
    CREATE TABLE [acrs_crash_sanitized] 
    (
        [RAMP_MOVEMENT_CODE] nvarchar(5),
        [LIGHT_CODE] nvarchar(5),
        [COUNTY_NO] decimal(2,0),
        [MUNI_CODE] nvarchar(3),
        [JUNCTION_CODE] nvarchar(5),
        [COLLISION_TYPE_CODE] nvarchar(5),
        [SURF_COND_CODE] nvarchar(5),
        [LANE_CODE] nvarchar(5),
        [RD_COND_CODE] nvarchar(5),
        [FIX_OBJ_CODE] nvarchar(5),
        [REPORT_NO] nvarchar(10) NOT NULL,
        [WEATHER_CODE] nvarchar(5),
        [ACC_DATE] datetime,
        [ACC_TIME] nvarchar(4),
        [LOC_CODE] nvarchar(8),
        [RAMP_FLAG] nvarchar(1),
        [SIGNAL_FLAG] nvarchar(1),
        [C_M_ZONE_FLAG] nvarchar(1),
        [INTER_NUM] nvarchar(20),
        [OFFICER_INFO] nvarchar(20),
        [AGENCY_CODE] nvarchar(3),
        [AREA_CODE] nvarchar(3),
        [HARM_EVENT_CODE1] nvarchar(5),
        [HARM_EVENT_CODE2] nvarchar(5),
        [LOC_CASE_NO] nvarchar(20),
        [ACRS_REPORT_NO] nvarchar(20),
        [OFFICER_ID] nvarchar(20),
        [OFFICER_NAME] nvarchar(80),
        [DS_KEY] nvarchar(20),
        [REPORT_TYPE_CODE] nvarchar(5),
        [PHOTOS_FLAG] nvarchar(1),
        [LANE_NUMBER] decimal(2,0),
        [LANE_DIRECTION_CODE] nvarchar(5),
        [LANE_TYPE_CODE] nvarchar(5),
        [INTERSECTION_TYPE_CODE] nvarchar(5),
        [TRAFFIC_CONTROL_CODE] nvarchar(5),
        [TRAFFIC_CONTROL_FUNCTION_FLAG] nvarchar(1),
        [NUM_LANES] decimal(2,0),
        [INTER_AREA_CODE] nvarchar(5),
        [SCHOOL_BUS_INVOLVED_CODE] nvarchar(5),
        [C_M_LOCATION_CODE] nvarchar(5),
        [REVIEW_DATE] [datetime],
        [REVIEW_OFFICER_ID] nvarchar(20),
        [REVIEW_OFFICER_NAME] nvarchar(40),
        [SUPER_DATE] [datetime],
        [SUPER_OFFICER_ID] nvarchar(20),
        [SUPER_OFFICER_NAME] nvarchar(40),
        [C_M_CLOSURE_CODE] nvarchar(5),
        [C_M_WORKERS_PRESENT_FLAG] nvarchar(1),
        [NARRATIVE] nvarchar(max),
        [GOV_PROPERTY_TXT] nvarchar(max),
        CONSTRAINT PK_acrs_crash_sanitized_REPORT_NO PRIMARY KEY NONCLUSTERED (REPORT_NO)
    )
    ```
    
11. Repeat the steps for the Citation table.
    ```
    CREATE TABLE [acrs_citation_code_sanitized] 
    (
        [CITATION] nvarchar(25),
        [PERSON_ID] float NOT NULL,
        [REPORT_NO] nvarchar(10) NOT NULL,
        [ACC_DATE] datetime,
        [CITATION_ID] float,
        [DS_KEY] nvarchar(20),
        CONSTRAINT PK_acrs_citation_code_sanitized_CITATION_ID PRIMARY KEY NONCLUSTERED (CITATION_ID)
    )
    ```
    
12. Repeat the steps for the Circumstance table.
    ```
    CREATE TABLE [dbo].[acrs_circumstance_sanitized] 
    (
        [REPORT_NO] nvarchar(10) NOT NULL,
        [CONTRIB_CODE1] nvarchar(5),
        [CONTRIB_CODE2] nvarchar(5),
        [CONTRIB_CODE3] nvarchar(5),
        [CONTRIB_CODE4] nvarchar(5),
        [PERSON_ID] float,
        [VEHICLE_ID] float,
        [CIRCUMSTANCE_ID] float,
        [ACC_DATE] datetime,
        [CONTRIB_FLAG] nvarchar(1),
        [DS_KEY] nvarchar(20),
        CONSTRAINT PK_acrs_circumstance_sanitized_CIRCUMSTANCE_ID PRIMARY KEY NONCLUSTERED (CIRCUMSTANCE_ID)
    )
    ```
    
13. Repeat the steps for the EMS table.
    ```
    CREATE TABLE [dbo].[acrs_ems_sanitized] 
    (
        [EMS_ID] float,
        [REPORT_NO] nvarchar(10) NOT NULL,
        [RUN_REP_NO] nvarchar(10),
        [EMS_UNIT_TAKEN_BY] nvarchar(40),
        [EMS_UNIT_LABEL] nvarchar(3),
        [EMS_UNIT_TAKEN_TO] nvarchar(40),
        [EMS_SNO] decimal(4,0),
        [ACC_DATE] datetime,
        [EMS_TRANSPORT_TYPE_FLAG] nvarchar(1),
        [DS_KEY] nvarchar(20),
        CONSTRAINT PK_acrs_ems_sanitized_EMS_ID PRIMARY KEY NONCLUSTERED (EMS_ID)
    )
    ```
    
14. Repeat the steps for the Person table.
    ```
    CREATE TABLE [dbo].[acrs_person_sanitized] (
        [SEX] nvarchar(5),
        [CONDITION_CODE] nvarchar(5),
        [DR_UNIT] nvarchar(2),
        [INJ_SEVER_CODE] nvarchar(5),
        [PED_UNIT] nvarchar(2),
        [OCC_UNIT] nvarchar(2),
        [OCC_NUM] nvarchar(4),
        [REPORT_NO] nvarchar(10) NOT NULL,
        [OCC_SEAT_POS_CODE] nvarchar(5),
        [PED_VISIBLE_CODE] nvarchar(5),
        [PED_LOCATION_CODE] nvarchar(5),
        [PED_OBEY_CODE] nvarchar(5),
        [PED_TYPE_CODE] nvarchar(5),
        [MOVEMENT_CODE] nvarchar(5),
        [PERSON_TYPE] nvarchar(1),
        [DEATH_NUM] nvarchar(4),
        [AGE] decimal(3,0),
        [SUBST_TEST_CODE] nvarchar(5),
        [SUBST_USE_CODE] nvarchar(5),
        [BAC] nvarchar(2),
        [FAULT_FLAG] nvarchar(1),
        [EQUIP_PROB_CODE] nvarchar(5),
        [SAF_EQUIP_CODE] nvarchar(5),
        [WOULD_HAVE_LIVED_FLAG] nvarchar(1),
        [EJECT_CODE] nvarchar(5),
        [DRIVER_DOB] datetime,
        [PERSON_ID] float,
        [STATE_CODE] nvarchar(2),
        [CLASS] nvarchar(2),
        [CDL_FLAG] nvarchar(1),
        [ALCO_DRUG_IMPAIRED_FLAG] nvarchar(1),
        [ACC_DATE] datetime,
        [VEHICLE_ID] float,
        [DEATH_SUFFIX] nvarchar(1),
        [EMS_UNIT_LABEL] nvarchar(3),
        [EMS_ID] float,
        [PERSON_PHONE_NUMBER] nvarchar(10),
        [PERSON_OTHER_PHONE] nvarchar(10),
        [PERSON_STREET_ADDRESS] nvarchar(40),
        [PERSON_CITY] nvarchar(40),
        [PERSON_STATE_CODE] nvarchar(2),
        [PERSON_ZIPCODE] nvarchar(10),
        [NONMOTOR_ACTION_TIME_CODE1] nvarchar(5),
        [NONMOTOR_ACTION_TIME_CODE2] nvarchar(5),
        [NONMOTOR_PRIOR_CODE] nvarchar(5),
        [UNIT_FIRST_STRIKE] nvarchar(4),
        [AIR_BAG_CODE] nvarchar(5),
        [DISTRACTED_BY_CODE] nvarchar(5),
        [ALCO_TEST_CODE] nvarchar(5),
        [ALCO_TEST_TYPE_CODE] nvarchar(5),
        [DRUG_TEST_CODE] nvarchar(5),
        [DRUG_TEST_RESULT_FLAG] nvarchar(1),
        [OCC_SEAT_LOCATION] nvarchar(5),
        [OCC_SEAT_ROW] decimal(2,0),
        [OCC_POS_INROW_CODE] nvarchar(5),
        [LIC_STATUS_FLAG] nvarchar(1),
        [CITATION_ISSUED_FLAG] nvarchar(1),
        [DS_KEY] nvarchar(20),
        CONSTRAINT PK_acrs_person_sanitized_PERSON_ID PRIMARY KEY NONCLUSTERED (PERSON_ID)
    )
    ```

15. Repeat the steps for the roadway table.
    ```
    CREATE TABLE [dbo].[acrs_roadway_sanitized] (
        [REPORT_NO] nvarchar(10) NOT NULL,
        [ROUTE_NUMBER] decimal(5,0),
        [ROUTE_TYPE_CODE] nvarchar(2),
        [ROUTE_SUFFIX] nvarchar(2),
        [LOG_MILE] decimal(6,3),
        [RD_CHAR_CODE] nvarchar(5),
        [RD_DIV_CODE] nvarchar(5),
        [LOGMILE_DIR_FLAG] nvarchar(1),
        [ROAD_NAME] nvarchar(50),
        [DISTANCE] decimal(6,3),
        [FEET_MILES_FLAG] nvarchar(1),
        [DISTANCE_DIR_FLAG] nvarchar(1),
        [FINAL_LOG_MILE] decimal(6,3),
        [REFERENCE_NUMBER] decimal(5,0),
        [REFERENCE_TYPE_CODE] nvarchar(2),
        [REFERENCE_SUFFIX] nvarchar(2),
        [REFERENCE_ROAD_NAME] nvarchar(50),
        [ACC_DATE] datetime,
        [X_COORDINATES] float,
        [Y_COORDINATES] float,
        [RD_ALIGNMENT_CODE] nvarchar(5),
        [RD_GRADE_CODE] nvarchar(5),
        [OFF_ROAD_TXT] nvarchar(max),
        [FINAL_X_COORDINATES] float,
        [FINAL_Y_COORDINATES] float,
        [DS_KEY] nvarchar(20),
        [CENSUS_TRACT] nvarchar(25),
        [ROAD_NAME_CLEAN] nvarchar(50),
        [REFERENCE_ROAD_NAME_CLEAN] nvarchar(50)
    )
    ```

16. Repeat the steps for the trailer
    ```
    CREATE TABLE [dbo].[acrs_trailer_sanitized] 
    (
        [TRAILER_RECORD_ID] float,
        [REPORT_NO] nvarchar(10) NOT NULL,
        [ACC_DATE] datetime,
        [VEHICLE_ID] float,
        [TOWED_VEHICLE_UNIT_NO] nvarchar(4),
        [VEH_YEAR] nvarchar(4),
        [VEH_MAKE] nvarchar(20),
        [VEH_MODEL] nvarchar(40),
        [BODY_TYPE_CODE] nvarchar(5),
        [PLATE_STATE] nvarchar(2),
        [PLATE_YEAR] nvarchar(4),
        [DS_KEY] nvarchar(20),
        CONSTRAINT PK_acrs_trailer_sanitized_TRAILER_RECORD_ID PRIMARY KEY NONCLUSTERED (TRAILER_RECORD_ID)
    )
    ```

17. Repeat the steps for the vehicles table
    ```
    CREATE TABLE [dbo].[acrs_vehicle_sanitized] (
        [HARM_EVENT_CODE] nvarchar(5),
        [PERSON_ID] nvarchar(38),
        [CONTI_DIRECTION_CODE] nvarchar(5),
        [DAMAGE_CODE] nvarchar(5),
        [MOVEMENT_CODE] nvarchar(5),
        [VIN] nvarchar(18),
        [REPORT_NO] nvarchar(10) NOT NULL,
        [CV_BODY_TYPE_CODE] nvarchar(5),
        [VEH_YEAR] nvarchar(4),
        [VEH_MAKE] nvarchar(30),
        [COMMERCIAL_FLAG] nvarchar(1),
        [VEH_MODEL] nvarchar(30),
        [TOWED_AWAY_FLAG] nvarchar(1),
        [NUM_AXLES] nvarchar(2),
        [GVW] nvarchar(6),
        [GOING_DIRECTION_CODE] nvarchar(5),
        [BODY_TYPE_CODE] nvarchar(5),
        [DRIVERLESS_FLAG] nvarchar(1),
        [FIRE_FLAG] nvarchar(1),
        [NUM_OCC] decimal(3,0),
        [PARKED_FLAG] nvarchar(1),
        [SPEED_LIMIT] nvarchar(2),
        [HIT_AND_RUN_FLAG] nvarchar(1),
        [HAZMAT_SPILL_FLAG] nvarchar(1),
        [VEHICLE_ID] float,
        [TOWED_VEHICLE_CODE1] nvarchar(5),
        [TOWED_VEHICLE_CODE2] nvarchar(5),
        [TOWED_VEHICLE_CODE3] nvarchar(5),
        [PLATE_STATE] nvarchar(2),
        [PLATE_YEAR] nvarchar(4),
        [AREA_DAMAGED_CODE1] nvarchar(5),
        [AREA_DAMAGED_CODE2] nvarchar(5),
        [AREA_DAMAGED_CODE3] nvarchar(5),
        [AREA_DAMAGED_CODE_IMP1] nvarchar(5),
        [AREA_DAMAGED_CODE_MAIN] nvarchar(5),
        [ACC_DATE] datetime,
        [SEQ_EVENT_CODE1] nvarchar(5),
        [SEQ_EVENT_CODE2] nvarchar(5),
        [SEQ_EVENT_CODE3] nvarchar(5),
        [SEQ_EVENT_CODE4] nvarchar(5),
        [REMOVED_BY] nvarchar(40),
        [REMOVED_TO] nvarchar(40),
        [VEH_SPECIAL_FUNCTION_CODE] nvarchar(5),
        [EMERGENCY_USE_FLAG] nvarchar(1),
        [CV_CONFIG_CODE] nvarchar(5),
        [BUS_USE_CODE] nvarchar(5),
        [HZM_NAME] nvarchar(40),
        [PLACARD_VISIBLE_FLAG] nvarchar(1),
        [VEHICLE_WEIGHT_CODE] nvarchar(5),
        [OWNER_STATE_CODE] nvarchar(2),
        [DS_KEY] nvarchar(20),
        CONSTRAINT PK_acrs_vehicle_sanitized_VEHICLE_ID PRIMARY KEY NONCLUSTERED (VEHICLE_ID)
    )
    ```

18. Hit Finish and complete the injest. 

Then run the data enricher. The enricher populates the 'sanitized' tables with census tract data. This only need to be run after a
yearly dump of ACRS data is ingested into the _sanitized databases. The census tract information is used by the PowerBI
dashboards to generate maps of hotspots.

`python main.py enrich`

## Export to MS2
MS2 is a tool that the department uses to visualize crash data. To create a spreadsheet that MS2 can ingest, run `python main.py ms2export`. This will create a spreadsheet called `BaltimoreCrash.xlsx` in the same directory.
