/*********************
** ACRS_CRASHES
*********************/
DROP TABLE [dbo].[acrs_crashes];
CREATE TABLE [dbo].[acrs_crashes](
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
    [CRASHTIME] datetime2 NOT NULL,
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
    [INTERSECTIONTYPE] int NOT NULL,
    [INVESTIGATINGOFFICERUSERNAME] nvarchar(100),
    [JUNCTION] varchar(10) NOT NULL,
    [LANEDIRECTION] varchar(5),
    [LANENUMBER] int NOT NULL,
    [LANETYPE] int,
    [LATITUDE] float,
    [LIGHT] varchar(10) NOT NULL,
    [LOCALCASENUMBER] varchar(50) NOT NULL,
    [LOCALCODES] varchar(20),
    [LONGITUDE] float,
    [MILEPOINTDIRECTION] char(2),
    [MILEPOINTDISTANCE] float NOT NULL,
    [MILEPOINTDISTANCEUNITS] varchar(5),
    [NARRATIVE] VARCHAR(MAX),
    [NONTRAFFIC] bit NOT NULL,
    [NUMBEROFLANES] int NOT NULL,
    [OFFROADDESCRIPTION] varchar(max),
    [PHOTOSTAKEN] bit,
    [REPORTCOUNTYLOCATION] int NOT NULL,
    [REPORTNUMBER] NCHAR(12) NOT NULL PRIMARY KEY, /* Report number, used as master primary key across all tables */
    [REPORTTYPE] varchar(max),
    [ROADALIGNMENT] int NOT NULL,
    [ROADCONDITION] int NOT NULL,
    [ROADDIVISION] varchar(10) NOT NULL,
    [ROADGRADE] int NOT NULL,
    [ROADID] varchar(50), /* Refers to primary key in acrs_road_id database */
    [SCHOOLBUSINVOLVEMENT] int NOT NULL,
    [STATEGOVERNMENTPROPERTYNAME] varchar(max),
    [SUPERVISORUSERNAME] varchar(50),
    [SUPERVISORYDATE] datetime2 NOT NULL,
    [SURFACECONDITION] int NOT NULL,
    [TRAFFICCONTROL] int,
    [TRAFFICCONTROLFUNCTIONING] bit,
    [UPDATEDATE] datetime2 NOT NULL,
    [UPLOADVERSION] varchar(50),
    [VERSIONNUMBER] int NOT NULL,
    [WEATHER] varchar(20)
);

/*********************
** Approval
*********************/
DROP TABLE [dbo].[acrs_approval];
CREATE TABLE [dbo].[acrs_approval] (
    [AGENCY] varchar(20),
    [DATE] datetime2 NOT NULL,
    [CADSENT] varchar(50),
    [CADSENT_DATE] datetime,
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
);

/*********************
** Circumstances
*********************/
DROP TABLE [dbo].[acrs_circumstances];
CREATE TABLE [dbo].[acrs_circumstances] (
    [CIRCUMSTANCECODE] varchar(10) NOT NULL,
    [CIRCUMSTANCEID] int NOT NULL PRIMARY KEY,
    [CIRCUMSTANCETYPE] varchar(20),
    [PERSONID] uniqueidentifier, /* Refers to PERSONID in ACRSPERSON */
    [REPORTNUMBER] NCHAR(12) NOT NULL,  /* Refers to primary key in main ACRS table */
    [VEHICLEID] uniqueidentifier
);

/*********************
** CITATIONCODES
*********************/
DROP TABLE [dbo].[acrs_citation_codes];
CREATE TABLE [dbo].[acrs_citation_codes] (
    [CITATIONNUMBER] varchar(50) NOT NULL,
    [PERSONID] uniqueidentifier NOT NULL, /* Refers to PERSONID in acrs_person */
    [REPORTNUMBER] NCHAR(12) NOT NULL /* Report number, used as master primary key across all tables */
);

/*********************
** CRASH DIAGRAM
*********************/
DROP TABLE [dbo].[acrs_crash_diagrams];
CREATE TABLE [dbo].[acrs_crash_diagrams] (
    [CRASHDIAGRAM] VARCHAR(MAX),
    [CRASHDIAGRAMNATIVE] VARCHAR(MAX),
    [REPORTNUMBER] NCHAR(12) NOT NULL  /* Refers to primary key in main ACRS table */
);

/*********************
** COMMERCIAL VEHICLES
*********************/
DROP TABLE [dbo].[acrs_commercial_vehicles];
CREATE TABLE [dbo].[acrs_commercial_vehicles] (
    [BODYTYPE] int,
    [BUSUSE] int,
    [CARRIERCLASSIFICATION] int,
    [CITY] varchar(50),
    [CONFIGURATION] int,
    [COUNTRY] varchar(50),
    [DOTNUMBER] bigint,
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
)

/*********************
** DAMAGEDAREAs
*********************/
DROP TABLE [dbo].[acrs_damaged_areas];
CREATE TABLE [dbo].[acrs_damaged_areas] (
    [DAMAGEID] int NOT NULL PRIMARY KEY,
    [IMPACTTYPE] int NOT NULL,
    [VEHICLEID] uniqueidentifier NOT NULL /* Refers to vehicleid in acrsvehicle table */
);

/*********************
** EMSes
*********************/
DROP TABLE [dbo].[acrs_ems];
CREATE TABLE [dbo].[acrs_ems] (
    [EMSTRANSPORTATIONTYPE] char(5),
    [EMSUNITNUMBER] char(5),
    [INJUREDTAKENBY] VARCHAR(MAX),
    [INJUREDTAKENTO] VARCHAR(MAX),
    [REPORTNUMBER] NCHAR(12) NOT NULL
);

/*********************
** EVENTS
*********************/
DROP TABLE [dbo].[acrs_events];
CREATE TABLE [dbo].[acrs_events] (
    [EVENTID] int NOT NULL,
    [EVENTSEQUENCE] int,
    [EVENTTYPE] int,
    [VEHICLEID] uniqueidentifier /* Refers to VEHICLEID in ACRSVEHICLE */
);

/*********************
** PDF report
*********************/
DROP TABLE [dbo].[acrs_pdf_report];
CREATE TABLE [dbo].[acrs_pdf_report] (
    [CHANGEDBY] varchar(50),
    [DATESTATUSCHANGED] datetime2 NOT NULL,
    [PDFREPORT1] VARCHAR(MAX),
    [PDF_ID] int NOT NULL PRIMARY KEY,
    [REPORTNUMBER] NCHAR(12) NOT NULL,  /* Refers to primary key in main ACRS table */
    [STATUS] varchar(20)
);

/*********************
** ACRSPERSON
*********************/
DROP TABLE [dbo].[acrs_person];
CREATE TABLE [dbo].[acrs_person] (
    [ADDRESS] nvarchar(max),
    [CITY] nvarchar(max),
    [COMPANY] nvarchar(max),
    [COUNTRY] nvarchar(max),
    [COUNTY] nvarchar(max),
    [DLCLASS] nvarchar(max),
    [DLNUMBER] nvarchar(max),
    [DLSTATE] nvarchar(2),
    [DOB] date NOT NULL,
    [FIRSTNAME] nvarchar(max),
    [HOMEPHONE] nvarchar(max),
    [LASTNAME] nvarchar(max),
    [MIDDLENAME] nvarchar(max),
    [OTHERPHONE] nvarchar(max),
    [PERSONID] uniqueidentifier NOT NULL PRIMARY KEY,
    [RACE] nvarchar(max),
    [REPORTNUMBER] NCHAR(12) NOT NULL,  /* Refers to primary key in main ACRS table */
    [SEX] varchar(5),
    [STATE] char(2),
    [ZIP] varchar(5)
);

/*********************
** PERSONINFORMATION
** Driver, Passenger or Nonmotorist
*********************/
DROP TABLE [dbo].[acrs_person_info];
CREATE TABLE [dbo].[acrs_person_info](
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
    [EMSRUNREPORTNUMBER] varchar(max) NOT NULL,
    [EMSUNITNUMBER] varchar(max) NOT NULL,
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
    [REPORTNUMBER] NCHAR(12) NOT NULL,            /* Refers to primary key in main ACRS table */
    [SAFETYEQUIPMENT] varchar(10) NOT NULL,
    [SEAT] char(2),                               /* 00 if driver, otherwise a number if passenger; null for nonmotorist */
    [SEATINGLOCATION] char(10),                   /* 00 if driver, otherwise a number if passenger; null for nonmotorist */
    [SEATINGROW] char(2),                         /* 00 if driver, otherwise a number if passenger; null for nonmotorist */
    [SUBSTANCEUSE] int,                           /* Only applicable to driver and nonmotorist */
    [UNITNUMBERFIRSTSTRIKE] int,                  /* Only applicable to nonmotorist */
    [VEHICLEID] uniqueidentifier                  /* Refers to VEHICLEID in ACRSVEHICLE, only applies to driver and passenger */
);

/*********************
** ROADWAY
*********************/
DROP TABLE [dbo].[acrs_roadway];
CREATE TABLE [dbo].[acrs_roadway] (
    [COUNTY] int,
    [LOGMILE_DIR] char,
    [MILEPOINT] float,
    [MUNICIPAL] int,
    [MUNICIPAL_AREA_CODE] int,
    [REFERENCE_MUNI] int,
    [REFERENCE_ROADNAME] varchar(50),
    [REFERENCE_ROUTE_NUMBER] char(10),
    [REFERENCE_ROUTE_SUFFIX] char(5),
    [REFERENCE_ROUTE_TYPE] char(2),
    [ROADID] varchar(50) NOT NULL PRIMARY KEY,
    [ROAD_NAME] varchar(max),
    [ROUTE_NUMBER] char(10),
    [ROUTE_SUFFIX] char(10),
    [ROUTE_TYPE] char(10)
);

/*********************
** TOWED UNIT
*********************/
DROP TABLE [dbo].[acrs_towed_unit];
CREATE TABLE [dbo].[acrs_towed_unit] (
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
    [VIN] char(17)
);

/*********************
** ACRSVEHICLE
*********************/
DROP TABLE [dbo].[acrs_vehicles];
CREATE TABLE [dbo].[acrs_vehicles] (
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
    [REPORTNUMBER] NCHAR(12) NOT NULL,  /* Refers to primary key in main ACRS table */
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
);

/*********************
** VEHICLEUSES
*********************/
DROP TABLE [dbo].[acrs_vehicle_uses];
CREATE TABLE [dbo].[acrs_vehicle_uses] (
    [ID] bigint NOT NULL,
    [VEHICLEID] uniqueidentifier NOT NULL, /* Refers to primary key in ACRSVEHICLE */
    [VEHICLEUSECODE] int
);

/*********************
** WITNESSes
*********************/
DROP TABLE [dbo].[acrs_witnesses];
CREATE TABLE [dbo].[acrs_witnesses](
    [PERSONID] uniqueidentifier NOT NULL,
    [REPORTNUMBER] NCHAR(12) NOT NULL /* Report number, used as master primary key across all tables */
);
