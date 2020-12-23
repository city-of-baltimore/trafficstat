"""Pytest directory-specific hook implementations"""
import sys
from pathlib import PurePath, Path

import pyodbc
import pytest

sys.path.append(str(PurePath(Path.cwd().parent, 'src')))

from src.crash_data_ingestor import CrashDataReader  # pylint:disable=wrong-import-position  # noqa: E402


@pytest.fixture(name='crash_data_reader')
def crash_data_reader_fixture():
    """Fixture for the CrashDataReader class"""
    cdr = CrashDataReader()
    cdr.approval_table = 'acrs_test_approval'
    cdr.circumstance_table = 'acrs_test_circumstances'
    cdr.citation_codes_table = 'acrs_test_citation_codes'
    cdr.crash_diagrams_table = 'acrs_test_crash_diagrams'
    cdr.crashes_table = 'acrs_test_crashes'
    cdr.commercial_vehicles_table = 'acrs_test_commercial_vehicles'
    cdr.damaged_areas_table = 'acrs_test_damaged_areas'
    cdr.ems_table = 'acrs_test_ems'
    cdr.events_table = 'acrs_test_events'
    cdr.pdf_table = 'acrs_test_pdf_report'
    cdr.person_table = 'acrs_test_person'
    cdr.person_info_table = 'acrs_test_person_info'
    cdr.roadway_table = 'acrs_test_roadway'
    cdr.towed_unit_table = 'acrs_test_towed_unit'
    cdr.vehicle_table = 'acrs_test_vehicles'
    cdr.vehicle_users_table = 'acrs_test_vehicle_uses'
    cdr.witnesses_table = 'acrs_test_witnesses'

    return cdr


@pytest.fixture(name='conn', scope='module')
def conn_fixture():
    """Fixture providing a connection to the DOT_DATA database table"""
    conn = pyodbc.connect(
        r'Driver={SQL Server};Server=balt-sql311-prd;Database=DOT_DATA;Trusted_Connection=yes;')
    yield conn
    conn.close()


@pytest.fixture(name='cursor')
def cursor_fixture(conn):
    """Fixture providing the cursor to the DOT_DATA database table"""
    cursor = conn.cursor()
    return cursor


@pytest.fixture
def acrs_crashes_table(cursor):
    """Fixture providing a clean version of the acrs_crashes table"""
    try:
        cursor.execute("DROP TABLE [dbo].[acrs_test_crashes];")
        cursor.commit()
    except pyodbc.ProgrammingError:
        pass  # The table doesn't exist

    cursor.execute("""
        CREATE TABLE [dbo].[acrs_test_crashes](
            [ACRSREPORTTIMESTAMP] datetime2 NOT NULL,
            [AGENCYIDENTIFIER] varchar(20),
            [AGENCYNAME] varchar(50),
            [AREA] varchar(10),
            [COLLISIONTYPE] int NOT NULL,
            [CONMAINCLOSURE] int,
            [CONMAINLOCATION] int,
            [CONMAINWORKERSPRESENT] bit,
            [CONMAINZONE] char(1),
            [CRASHDATE] date NOT NULL,
            [CRASHTIME] time NOT NULL,
            [CURRENTASSIGNMENT] varchar(20) NOT NULL,
            [CURRENTGROUP] int NOT NULL,
            [DEFAULTASSIGNMENT] varchar(20) NOT NULL,
            [DEFAULTGROUP] int NOT NULL,
            [DOCTYPE] varchar(5),
            [FIXEDOBJECTSTRUCK] varchar(10) NOT NULL,
            [HARMFULEVENTONE] varchar(10) NOT NULL,
            [HARMFULEVENTTWO] varchar(10) NOT NULL,
            [HITANDRUN] bit NOT NULL,
            [INSERTDATE] datetime2 NOT NULL,
            [INTERCHANGEAREA] int NOT NULL,
            [INTERCHANGEIDENTIFICATION] varchar(max),
            [INTERSECTIONTYPE] int NOT NULL,
            [INVESTIGATINGOFFICERUSERNAME] nvarchar(100),
            [INVESTIGATOR] varchar(max),
            [JUNCTION] varchar(10) NOT NULL,
            [LANEDIRECTION] varchar(5),
            [LANENUMBER] int NOT NULL,
            [LANETYPE] int,
            [LATITUDE] float,
            [LIGHT] varchar(10) NOT NULL,
            [LOCALCASENUMBER] varchar(50) NOT NULL,
            [LOCALCODES] varchar(20),
            [LONGITUDE] float,
            [MILEPOINTDIRECTION] varchar(2),
            [MILEPOINTDISTANCE] float NOT NULL,
            [MILEPOINTDISTANCEUNITS] varchar(5),
            [NARRATIVE] VARCHAR(MAX),
            [NONTRAFFIC] bit NOT NULL,
            [NUMBEROFLANES] int NOT NULL,
            [OFFROADDESCRIPTION] varchar(max),
            [PHOTOSTAKEN] bit,
            [RAMP] varchar(max),
            [REPORTCOUNTYLOCATION] int NOT NULL,
            [REPORTNUMBER] NVARCHAR(12) NOT NULL PRIMARY KEY, /* Report number, used as master primary key across all tables */
            [REPORTTYPE] varchar(max),
            [ROADALIGNMENT] int NOT NULL,
            [ROADCONDITION] int NOT NULL,
            [ROADDIVISION] varchar(10) NOT NULL,
            [ROADGRADE] int NOT NULL,
            [ROADID] varchar(50), /* Refers to primary key in acrs_road_id database */
            [SCHOOLBUSINVOLVEMENT] int NOT NULL,
            [STATEGOVERNMENTPROPERTYNAME] varchar(max),
            [SUPERVISOR] varchar(max),
            [SUPERVISORUSERNAME] varchar(50),
            [SUPERVISORYDATE] datetime2 NOT NULL,
            [SURFACECONDITION] varchar(10) NOT NULL,
            [TRAFFICCONTROL] int,
            [TRAFFICCONTROLFUNCTIONING] bit,
            [UPDATEDATE] datetime2 NOT NULL,
            [UPLOADVERSION] varchar(50),
            [VERSIONNUMBER] int NOT NULL,
            [WEATHER] varchar(20)
        );""")
    cursor.commit()

    return cursor


@pytest.fixture
def acrs_approval_table(cursor):
    """Fixture providing a clean version of the acrs_approval table"""
    try:
        cursor.execute("DROP TABLE [dbo].[acrs_test_approval];")
        cursor.commit()
    except pyodbc.ProgrammingError:
        pass  # The table doesn't exist

    cursor.execute("""
        CREATE TABLE [dbo].[acrs_test_approval] (
            [AGENCY] varchar(20),
            [DATE] datetime2 NOT NULL,
            [CADSENT] varchar(50),
            [CADSENT_DATE] datetime2,
            [CC_NUMBER] varchar(50) NOT NULL,
            [DATE_INITIATED2] datetime2 NOT NULL,
            [GROUP_NUMBER] int NOT NULL,
            [HISTORICALAPPROVALDATA] varchar(50),
            [INCIDENT_DATE] datetime2 NOT NULL,
            [INVESTIGATOR] varchar(20),
            [REPORT_TYPE] varchar(10),
            [SEQ_GUID] varchar(12), /* Refers to the report number in this table */
            [STATUS_CHANGE_DATE] datetime2 NOT NULL,
            [STATUS_ID] int NOT NULL,
            [STEP_NUMBER] int,
            [TR_USERNAME] varchar(20),
            [UNIT_CODE] varchar(20) NOT NULL
        );""")
    cursor.commit()

    return cursor


@pytest.fixture
def acrs_circumstances_table(cursor):
    """Fixture providing a clean version of the acrs_circumstances table"""
    try:
        cursor.execute("DROP TABLE [dbo].[acrs_test_circumstances];")
        cursor.commit()
    except pyodbc.ProgrammingError:
        pass  # The table doesn't exist

    cursor.execute("""
        CREATE TABLE [dbo].[acrs_test_circumstances] (
            [CIRCUMSTANCECODE] varchar(10) NOT NULL,
            [CIRCUMSTANCEID] int NOT NULL PRIMARY KEY,
            [CIRCUMSTANCETYPE] varchar(20),
            [PERSONID] uniqueidentifier, /* Refers to PERSONID in ACRSPERSON */
            [REPORTNUMBER] NVARCHAR(12) NOT NULL,  /* Refers to primary key in main ACRS table */
            [VEHICLEID] uniqueidentifier
        );""")
    cursor.commit()

    return cursor


@pytest.fixture
def acrs_citation_codes_table(cursor):
    """Fixture providing a clean version of the acrs_citation_codes table"""
    try:
        cursor.execute("DROP TABLE [dbo].[acrs_test_citation_codes];")
        cursor.commit()
    except pyodbc.ProgrammingError:
        pass  # The table doesn't exist

    cursor.execute("""
        CREATE TABLE [dbo].[acrs_test_citation_codes] (
            [CITATIONNUMBER] varchar(50) NOT NULL,
            [PERSONID] uniqueidentifier NOT NULL, /* Refers to PERSONID in acrs_person */
            [REPORTNUMBER] nvarchar(12) NOT NULL /* Report number, used as master primary key across all tables */
        );""")
    cursor.commit()

    return cursor


@pytest.fixture
def acrs_crash_diagrams_table(cursor):
    """Fixture providing a clean version of the acrs_crash_diagrams table"""
    try:
        cursor.execute("DROP TABLE [dbo].[acrs_test_crash_diagrams];")
        cursor.commit()
    except pyodbc.ProgrammingError:
        pass  # The table doesn't exist

    cursor.execute("""
        CREATE TABLE [dbo].[acrs_test_crash_diagrams] (
            [CRASHDIAGRAM] VARCHAR(MAX),
            [CRASHDIAGRAMNATIVE] VARCHAR(MAX),
            [REPORTNUMBER] NVARCHAR(12) NOT NULL  /* Refers to primary key in main ACRS table */
        );""")
    cursor.commit()

    return cursor


@pytest.fixture
def acrs_commercial_vehicle_table(cursor):
    """Fixture providing a clean version of the acrs_commercial_vehicles table"""
    try:
        cursor.execute("DROP TABLE [dbo].[acrs_test_commercial_vehicles];")
        cursor.commit()
    except pyodbc.ProgrammingError:
        pass  # The table doesn't exist

    cursor.execute("""
        CREATE TABLE [dbo].[acrs_test_commercial_vehicles] (
            [BODYTYPE] varchar(10),
            [BUSUSE] int,
            [CARRIERCLASSIFICATION] int,
            [CITY] varchar(50),
            [CONFIGURATION] int,
            [COUNTRY] varchar(50),
            [DOTNUMBER] varchar(20),
            [GVW] int,
            [HAZMATCLASS] varchar(50),
            [HAZMATNAME] varchar(50),
            [HAZMATNUMBER] varchar(50),
            [HAZMATSPILL] varchar(50),
            [MCNUMBER] varchar(50),
            [NAME] varchar(max),
            [NUMBEROFAXLES] int,
            [PLACARDVISIBLE] varchar(50),
            [POSTALCODE] varchar(5),
            [STATE] varchar(2),
            [STREET] varchar(50),
            [VEHICLEID] uniqueidentifier NOT NULL, /* Refers to vehicleid in acrsvehicle table */
            [WEIGHT] varchar(50),
            [WEIGHTUNIT] varchar(50)
        );""")
    cursor.commit()

    return cursor


@pytest.fixture
def acrs_damaged_areas_table(cursor):
    """Fixture providing a clean version of the acrs_damaged_areas table"""
    try:
        cursor.execute("DROP TABLE [dbo].[acrs_test_damaged_areas];")
        cursor.commit()
    except pyodbc.ProgrammingError:
        pass  # The table doesn't exist

    cursor.execute("""
        CREATE TABLE [dbo].[acrs_test_damaged_areas] (
            [DAMAGEID] int NOT NULL PRIMARY KEY,
            [IMPACTTYPE] int NOT NULL,
            [VEHICLEID] uniqueidentifier NOT NULL /* Refers to vehicleid in acrsvehicle table */
        );""")
    cursor.commit()

    return cursor


@pytest.fixture
def acrs_ems_table(cursor):
    """Fixture providing a clean verison of the acrs_ems table"""
    try:
        cursor.execute("DROP TABLE [dbo].[acrs_test_ems];")
        cursor.commit()
    except pyodbc.ProgrammingError:
        pass  # The table doesn't exist

    cursor.execute("""
        CREATE TABLE [dbo].[acrs_test_ems] (
            [EMSTRANSPORTATIONTYPE] varchar(5),
            [EMSUNITNUMBER] varchar(5),
            [INJUREDTAKENBY] VARCHAR(MAX),
            [INJUREDTAKENTO] VARCHAR(MAX),
            [REPORTNUMBER] NVARCHAR(12) NOT NULL /* Refers to primary key in main ACRS table */
        );""")
    cursor.commit()

    return cursor


@pytest.fixture
def acrs_events_table(cursor):
    """Fixture providing a clean version of the acrs_events table"""
    try:
        cursor.execute("DROP TABLE [dbo].[acrs_test_events];")
        cursor.commit()
    except pyodbc.ProgrammingError:
        pass  # The table doesn't exist

    cursor.execute("""
        CREATE TABLE [dbo].[acrs_test_events] (
            [EVENTID] int NOT NULL,
            [EVENTSEQUENCE] int,
            [EVENTTYPE] int,
            [VEHICLEID] uniqueidentifier /* Refers to VEHICLEID in ACRSVEHICLE */
        );""")
    cursor.commit()

    return cursor


@pytest.fixture
def acrs_pdf_report_table(cursor):
    """Fixture providing a clean verison of the acrs_pdf_report table"""
    try:
        cursor.execute("DROP TABLE [dbo].[acrs_test_pdf_report];")
        cursor.commit()
    except pyodbc.ProgrammingError:
        pass  # The table doesn't exist

    cursor.execute("""
        CREATE TABLE [dbo].[acrs_test_pdf_report] (
            [CHANGEDBY] varchar(50),
            [DATESTATUSCHANGED] datetime2 NOT NULL,
            [PDFREPORT1] VARCHAR(MAX),
            [PDF_ID] int NOT NULL PRIMARY KEY,
            [REPORTNUMBER] NVARCHAR(12) NOT NULL,  /* Refers to primary key in main ACRS table */
            [STATUS] varchar(20)
        );""")
    cursor.commit()

    return cursor


@pytest.fixture
def acrs_person_table(cursor):
    """Fixture providing a clean version of the acrs_person table"""
    try:
        cursor.execute("DROP TABLE [dbo].[acrs_test_person];")
        cursor.commit()
    except pyodbc.ProgrammingError:
        pass  # The table doesn't exist

    cursor.execute("""
        CREATE TABLE [dbo].[acrs_test_person] (
            [ADDRESS] nvarchar(max),
            [CITY] nvarchar(max),
            [COMPANY] nvarchar(max),
            [COUNTRY] nvarchar(max),
            [COUNTY] nvarchar(max),
            [DLCLASS] nvarchar(max),
            [DLNUMBER] nvarchar(max),
            [DLSTATE] nvarchar(2),
            [DOB] date,
            [FIRSTNAME] nvarchar(max),
            [HOMEPHONE] nvarchar(max),
            [LASTNAME] nvarchar(max),
            [MIDDLENAME] nvarchar(max),
            [OTHERPHONE] nvarchar(max),
            [PERSONID] uniqueidentifier NOT NULL PRIMARY KEY,
            [RACE] nvarchar(max),
            [REPORTNUMBER] NVARCHAR(12) NOT NULL,  /* Refers to primary key in main ACRS table */
            [SEX] varchar(5),
            [STATE] char(2),
            [ZIP] varchar(max)
        );""")
    cursor.commit()

    return cursor


@pytest.fixture
def acrs_person_info_table(cursor):
    """Fixture providing a clean version of the acrs_person_info table"""
    try:
        cursor.execute("DROP TABLE [dbo].[acrs_test_person_info];")
        cursor.commit()
    except pyodbc.ProgrammingError:
        pass  # The table doesn't exist

    cursor.execute("""
        CREATE TABLE [dbo].[acrs_test_person_info](
            [AIRBAGDEPLOYED] int,                         /* Only applicable to driver and passenger */
            [ALCOHOLTESTINDICATOR] int,                   /* Only applicable to driver and nonmotorist */
            [ALCOHOLTESTTYPE] varchar(max),               /* Only applicable to driver and nonmotorist */
            [ATFAULT] bit,                                /* Only applicable to driver and nonmotorist */
            [BAC] varchar(max),                           /* Only applicable to driver and nonmotorist */
            [CONDITION] varchar(10),                      /* Only applicable to driver and nonmotorist */
            [CONTINUEDIRECTION] varchar(5),               /* Only applicable for nonmotorist */
            [DRIVERDISTRACTEDBY] int,                     /* Only applicable for driver */
            [DRUGTESTINDICATOR] int,                      /* Only applicable to driver and nonmotorist */
            [DRUGTESTRESULT] varchar(max),                /* Only applicable to driver and nonmotorist */
            [EJECTION] int,                               /* Only applicable to driver and passenger */
            [EMSRUNREPORTNUMBER] varchar(max),
            [EMSUNITNUMBER] varchar(max),
            [EQUIPMENTPROBLEM] int,                       /* Only applicable to driver and passenger */
            [GOINGDIRECTION] varchar(max),                /* Only applicable to nonmotorist */
            [HASCDL] bit,                                 /* Only applicable for driver */
            [INJURYSEVERITY] int NOT NULL,
            [PEDESTRIANACTIONS] int,                      /* Only applicable to nonmotorist */
            [PEDESTRIANLOCATION] float,                   /* Only applicable to nonmotorist */
            [PEDESTRIANMOVEMENT] varchar(10),             /* Only applicable to nonmotorist */
            [PEDESTRIANOBEYTRAFFICSIGNAL] int,            /* Only applicable to nonmotorist */
            [PEDESTRIANTYPE] int,                         /* Only applicable to nonmotorist */
            [PEDESTRIANVISIBILITY] int,                   /* Only applicable to nonmotorist */
            [PERSONID] uniqueidentifier NOT NULL,         /* Refers to PERSONID in ACRSPERSON */
            [REPORTNUMBER] NVARCHAR(12) NOT NULL,         /* Refers to primary key in main ACRS table */
            [SAFETYEQUIPMENT] varchar(10) NOT NULL,
            [SEAT] int,                                   /* 00 if driver, otherwise a number if passenger; null for nonmotorist */
            [SEATINGLOCATION] int,                        /* 00 if driver, otherwise a number if passenger; null for nonmotorist */
            [SEATINGROW] int,                             /* 00 if driver, otherwise a number if passenger; null for nonmotorist */
            [SUBSTANCEUSE] int,                           /* Only applicable to driver and nonmotorist */
            [UNITNUMBERFIRSTSTRIKE] int,                  /* Only applicable to nonmotorist */
            [VEHICLEID] uniqueidentifier                  /* Refers to VEHICLEID in ACRSVEHICLE, only applies to driver and passenger */
        );""")
    cursor.commit()

    return cursor


@pytest.fixture
def acrs_report_docs_table(cursor):
    """Fixture providinga clean version of the acrs_test_report_docs table. Currently a stub until we get example data
    or schema for this data"""
    try:
        cursor.execute("DROP TABLE [dbo].[acrs_test_report_docs];")
        cursor.commit()
    except pyodbc.ProgrammingError:
        pass  # The table doesn't exist

    cursor.execute("""
        CREATE TABLE [dbo].[acrs_test_report_docs] (
            [REPORTNUMBER] NVARCHAR(12) NOT NULL         /* Refers to primary key in main ACRS table */
        );""")
    cursor.commit()

    return cursor


@pytest.fixture
def acrs_report_photos_table(cursor):
    """Fixture providing a clean version of the acrs_report_photos table"""
    # Currently a stub until we get example data or schema for this data
    try:
        cursor.execute("DROP TABLE [dbo].[acrs_test_report_photos];")
        cursor.commit()
    except pyodbc.ProgrammingError:
        pass  # The table doesn't exist

    cursor.execute("""
        CREATE TABLE [dbo].[acrs_test_report_photos] (
            [REPORTNUMBER] NVARCHAR(12) NOT NULL         /* Refers to primary key in main ACRS table */
        );""")
    cursor.commit()

    return cursor


@pytest.fixture
def acrs_roadway_table(cursor):
    """Fixture providing a clean version of the acrs_roadway table"""
    try:
        cursor.execute("DROP TABLE [dbo].[acrs_test_roadway];")
        cursor.commit()
    except pyodbc.ProgrammingError:
        pass  # The table doesn't exist

    cursor.execute("""
        CREATE TABLE [dbo].[acrs_test_roadway] (
            [COUNTY] int,
            [LOGMILE_DIR] varchar,
            [MILEPOINT] float,
            [MUNICIPAL] int,
            [MUNICIPAL_AREA_CODE] int,
            [REFERENCE_MUNI] int,
            [REFERENCE_ROADNAME] varchar(50),
            [REFERENCE_ROUTE_NUMBER] varchar(10),
            [REFERENCE_ROUTE_SUFFIX] varchar(5),
            [REFERENCE_ROUTE_TYPE] varchar(2),
            [ROADID] varchar(50) NOT NULL PRIMARY KEY,
            [ROAD_NAME] varchar(max),
            [ROUTE_NUMBER] varchar(10),
            [ROUTE_SUFFIX] varchar(10),
            [ROUTE_TYPE] varchar(10),
            [CENSUS_TRACT] varchar(20)
        );""")
    cursor.commit()

    return cursor


@pytest.fixture
def acrs_towed_unit_table(cursor):
    """Fixture providing a clean version of the acrs_towed_unit table"""
    try:
        cursor.execute("DROP TABLE [dbo].[acrs_test_towed_unit];")
        cursor.commit()
    except pyodbc.ProgrammingError:
        pass  # The table doesn't exist

    cursor.execute("""
        CREATE TABLE [dbo].[acrs_test_towed_unit] (
            [INSURANCEPOLICYNUMBER] varchar(50),
            [INSURER] varchar(50),
            [LICENSEPLATENUMBER] varchar(15),
            [LICENSEPLATESTATE] char(2),
            [OWNERID] uniqueidentifier NOT NULL, /* Refers to primary key in acrs_person_info */
            [TOWEDID] uniqueidentifier NOT NULL PRIMARY KEY,
            [UNITNUMBER] varchar(50),
            [VEHICLEID] uniqueidentifier NOT NULL, /* Refers to primary key in ACRSVEHICLE */
            [VEHICLEMAKE] varchar(20),
            [VEHICLEMODEL] varchar(30),
            [VEHICLEYEAR] int,
            [VIN] varchar(17)
        );""")
    cursor.commit()

    return cursor


@pytest.fixture
def acrs_vehicles_table(cursor):
    """Fixture providing a clean version of the acrs_vehicles table"""
    try:
        cursor.execute("DROP TABLE [dbo].[acrs_test_vehicles];")
        cursor.commit()
    except pyodbc.ProgrammingError:
        pass  # The table doesn't exist

    cursor.execute("""
        CREATE TABLE [dbo].[acrs_test_vehicles] (
            [COMMERCIALVEHICLE] varchar(max),
            [CONTINUEDIRECTION] varchar(1) NOT NULL,
            [DAMAGEEXTENT] int,
            [DRIVERLESSVEHICLE] bit,
            [EMERGENCYMOTORVEHICLEUSE] bit,
            [FIRE] bit,
            [FIRSTIMPACT] int,
            [GOINGDIRECTION] varchar(5),
            [HITANDRUN] bit,
            [INSURANCEPOLICYNUMBER] varchar(50),
            [INSURER] nvarchar(50),
            [LICENSEPLATENUMBER] varchar(20),
            [LICENSEPLATESTATE] char(2),
            [MAINIMPACT] int,
            [MOSTHARMFULEVENT] varchar(10),
            [OWNERID] uniqueidentifier, /* Refers to the ACRSPERSON table */
            [PARKEDVEHICLE] bit,
            [REGISTRATIONEXPIRATIONYEAR] int,
            [REPORTNUMBER] NVARCHAR(12) NOT NULL,  /* Refers to primary key in main ACRS table */
            [SFVEHICLEINTRANSPORT] int,
            [SPEEDLIMIT] int,
            [TOWEDUNITTYPE] int,
            [UNITNUMBER] varchar(max),
            [VEHICLEBODYTYPE] varchar(max),
            [VEHICLEID] uniqueidentifier NOT NULL PRIMARY KEY,
            [VEHICLEMAKE] varchar(50),
            [VEHICLEMODEL] varchar(50),
            [VEHICLEMOVEMENT] float,
            [VEHICLEREMOVEDBY] varchar(max),
            [VEHICLEREMOVEDTO] varchar(max),
            [VEHICLETOWEDAWAY] varchar(max),
            [VEHICLEYEAR] int,
            [VIN] varchar(17)
        );""")
    cursor.commit()

    return cursor


@pytest.fixture
def acrs_vehicle_use_table(cursor):
    """Fixture providing a clean version of the acrs_vehicle_uses table"""
    try:
        cursor.execute("DROP TABLE [dbo].[acrs_test_vehicle_uses];")
        cursor.commit()
    except pyodbc.ProgrammingError:
        pass  # The table doesn't exist

    cursor.execute("""
        CREATE TABLE [dbo].[acrs_test_vehicle_uses] (
            [ID] bigint NOT NULL,
            [VEHICLEID] uniqueidentifier NOT NULL, /* Refers to primary key in ACRSVEHICLE */
            [VEHICLEUSECODE] int
        );""")
    cursor.commit()

    return cursor


@pytest.fixture
def acrs_witnesses_table(cursor):
    """Fixture providing a clean version of the acrs_witnesses table"""
    try:
        cursor.execute("DROP TABLE [dbo].[acrs_test_witnesses];")
        cursor.commit()
    except pyodbc.ProgrammingError:
        pass  # The table doesn't exist

    cursor.execute("""
        CREATE TABLE [dbo].[acrs_test_witnesses](
            [PERSONID] uniqueidentifier NOT NULL,
            [REPORTNUMBER] NVARCHAR(12) NOT NULL /* Report number, used as master primary key across all tables */
        );""")
    cursor.commit()

    return cursor
