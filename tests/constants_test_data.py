"""Constants used in test_crash_data_ingestor"""
from collections import OrderedDict

# CRASH
crash_test_input_data = OrderedDict([
    ('@xmlns:i', 'http://www.w3.org/2001/XMLSchema-instance'),
    ('@xmlns', 'http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201'),
    ('ACRSREPORTTIMESTAMP', '2020-11-28T21:59:32.009631'),
    ('AGENCYIDENTIFIER', 'BALTIMORE'),
    ('AGENCYNAME', 'Baltimore City Police Department'),
    ('APPROVALDATA', None),  # tested in test_read_approval_data
    ('AREA', 'UNK'),
    ('CIRCUMSTANCES', None),  # tested in test_read_circumstance_data
    ('COLLISIONTYPE', '03'),
    ('CONMAINCLOSURE', OrderedDict([('@i:nil', 'true')])),
    ('CONMAINLOCATION', OrderedDict([('@i:nil', 'true')])),
    ('CONMAINWORKERSPRESENT', 'N'),
    ('CONMAINZONE', 'N'),
    ('CRASHDATE', '2020-11-28T00:00:00'),
    ('CRASHTIME', '2020-11-28T19:45:00'),
    ('CURRENTASSIGNMENT', '999'),
    ('CURRENTGROUP', '2519'),
    ('DEFAULTASSIGNMENT', '999'),
    ('DEFAULTGROUP', '2514'),
    ('DIAGRAM', None),  # tested in test_read_crash_diagrams_data
    ('DOCTYPE', 'ACRS'),
    ('EMSes', None),
    ('FIXEDOBJECTSTRUCK', '00'),
    ('HARMFULEVENTONE', '01'),
    ('HARMFULEVENTTWO', '01'),
    ('HITANDRUN', 'N'),
    ('INSERTDATE', '2020-11-28T21:59:53'),
    ('INTERCHANGEAREA', '03'),
    ('INTERCHANGEIDENTIFICATION', OrderedDict([('@i:nil', 'true')])),
    ('INTERSECTIONTYPE', '02'),
    ('INVESTIGATINGOFFICERUSERNAME', 'BALTIMORED934'),
    ('INVESTIGATOR', OrderedDict([('@i:nil', 'true')])),
    ('JUNCTION', '03'),
    ('LANEDIRECTION', 'W'),
    ('LANENUMBER', '1'),
    ('LANETYPE', OrderedDict([('@i:nil', 'true')])),
    ('LATITUDE', '39.25760123456789'),
    ('LIGHT', '03'),
    ('LOCALCASENUMBER', '9201107985'),
    ('LOCALCODES', '3502'),
    ('LONGITUDE', '-76.63280123456789'),
    ('MILEPOINTDIRECTION', 'W'),
    ('MILEPOINTDISTANCE', '80'),
    ('MILEPOINTDISTANCEUNITS', 'F'),
    ('NARRATIVE', 'Test narrative'),
    ('NONMOTORISTs', None),  # tested in test_read_person_info_data_nonmotorist
    ('NONTRAFFIC', 'N'),
    ('NUMBEROFLANES', '4'),
    ('OFFROADDESCRIPTION', OrderedDict([('@i:nil', 'true')])),
    ('PDFREPORTs', None),  # tested in test_read_pdf_data
    ('PHOTOSTAKEN', 'N'),
    ('People', None),  # tested in test_read_acrs_person_data
    ('RAMP', OrderedDict([('@i:nil', 'true')])),
    ('REPORTCOUNTYLOCATION', '24'),
    ('REPORTDOCUMENTs', OrderedDict([('@i:nil', 'true')])),  # Not tested. We need example data or schema
    ('REPORTNUMBER', 'ADD9340058'),
    ('REPORTPHOTOes', OrderedDict([('@i:nil', 'true')])),  # Not tested. We need example data or schema
    ('REPORTTYPE', 'Injury Crash'),
    ('ROADALIGNMENT', '01'),
    ('ROADCONDITION', '01'),
    ('ROADDIVISION', '03'),
    ('ROADGRADE', '01'),
    ('ROADID', '9316ed0c-cddf-481c-94ee-4662e0b77384'),
    ('ROADWAY', None),  # tested in test_read_roadway_data
    ('SCHOOLBUSINVOLVEMENT', '01'),
    ('STATEGOVERNMENTPROPERTYNAME', OrderedDict([('@i:nil', 'true')])),
    ('SUPERVISOR', OrderedDict([('@i:nil', 'true')])),
    ('SUPERVISORUSERNAME', 'BALTIMOREH923'),
    ('SUPERVISORYDATE', '2020-12-03T02:27:08.755331'),
    ('SURFACECONDITION', '02'),
    ('TRAFFICCONTROL', '03'),
    ('TRAFFICCONTROLFUNCTIONING', 'Y'),
    ('UPDATEDATE', '2020-11-28T21:58:35'),
    ('UPLOADVERSION', '20.17.02.01'),
    ('VEHICLEs', None),  # tested in test_read_acrs_vehicle_data
    ('VERSIONNUMBER', '1'),
    ('WEATHER', '06.01'),
    ('WITNESSes', None),
])

# APPROVAL
approval_input_data = OrderedDict([
    ('AGENCY', 'BALTIMORE'),
    ('APPROVALDATE', '2020-08-05T15:30:01'),
    ('CADSENT', OrderedDict([('@i:nil', 'true')])),
    ('CADSENT_DATE', OrderedDict([('@i:nil', 'true')])),
    ('CC_NUMBER', '9200708732'),
    ('DATE_INITIATED2', '2020-07-29T15:53:20'),
    ('GROUP_NUMBER', '2519'),
    ('HISTORICALAPPROVALDATAs', OrderedDict([('@i:nil', 'true')])),
    ('INCIDENT_DATE', '2020-07-28T00:00:00'),
    ('INVESTIGATOR', OrderedDict([('@i:nil', 'true')])),
    ('REPORT_TYPE', 'ACRS'),
    ('SEQ_GUID', 'ADD934004Q'),
    ('STATUS_CHANGE_DATE', '2020-08-05T11:29:43'),
    ('STATUS_ID', '3'),
    ('STEP_NUMBER', '1'),
    ('TR_USERNAME', 'BALTIMORED934'),
    ('UNIT_CODE', '999')])

# CIRCUMSTANCE
circum_input_data = [
    OrderedDict(
        [('CIRCUMSTANCECODE', '00'),
         ('CIRCUMSTANCEID', '10360030'),
         ('CIRCUMSTANCETYPE', 'Weather'),
         ('PERSONID', OrderedDict([('@i:nil', 'true')])),
         ('REPORTNUMBER', 'ADD934004Q'),
         ('VEHICLEID', OrderedDict([('@i:nil', 'true')]))]),
    OrderedDict(
        [('CIRCUMSTANCECODE', '00'),
         ('CIRCUMSTANCEID', '10360031'),
         ('CIRCUMSTANCETYPE', 'Road'),
         ('PERSONID', OrderedDict([('@i:nil', 'true')])),
         ('REPORTNUMBER', 'ADD934004Q'),
         ('VEHICLEID', OrderedDict([('@i:nil', 'true')]))]),
    OrderedDict(
        [('CIRCUMSTANCECODE', '60.88'),
         ('CIRCUMSTANCEID', '10360032'),
         ('CIRCUMSTANCETYPE', 'Person'),
         ('PERSONID', '6239e4e7-65b8-452a-ba1e-6bc26b8c5cc4'),
         ('REPORTNUMBER', 'ADD934004Q'),
         ('VEHICLEID', OrderedDict([('@i:nil', 'true')]))]),
    OrderedDict(
        [('CIRCUMSTANCECODE', '00'),
         ('CIRCUMSTANCEID', '10360033'),
         ('CIRCUMSTANCETYPE', 'Vehicle'),
         ('PERSONID', OrderedDict([('@i:nil', 'true')])),
         ('REPORTNUMBER', 'ADD934004Q'),
         ('VEHICLEID', '65cd4028-82ab-401e-a7fa-d392dfb98e03')]),
    OrderedDict(
        [('CIRCUMSTANCECODE', '00'),
         ('CIRCUMSTANCEID', '10360034'),
         ('CIRCUMSTANCETYPE', 'Person'),
         ('PERSONID', 'c3e96bdd-5049-426f-b27d-c3bf43b1eeca'),
         ('REPORTNUMBER', 'ADD934004Q'),
         ('VEHICLEID', OrderedDict([('@i:nil', 'true')]))]),
    OrderedDict(
        [('CIRCUMSTANCECODE', '00'),
         ('CIRCUMSTANCEID', '10360035'),
         ('CIRCUMSTANCETYPE', 'Vehicle'),
         ('PERSONID', OrderedDict([('@i:nil', 'true')])),
         ('REPORTNUMBER', 'ADD934004Q'),
         ('VEHICLEID', 'ddd4ed36-cca5-4634-8209-01e38cc13ced')])]

# CITATION
citation_input_data = [OrderedDict([
    ('CITATIONNUMBER', 'KK15676'),
    ('PERSONID', '6fffe61c-6bec-476a-8a6e-47c52544fb3c'),
    ('REPORTNUMBER', 'ADD9340058')])]

citation_exp_data = [('KK15676', '6FFFE61C-6BEC-476A-8A6E-47C52544FB3C', 'ADD9340058')]

# CRASH
DUMMY_DATA_LEN = 10
crash_input_data = OrderedDict([
    ('CRASHDIAGRAM', 'X' * DUMMY_DATA_LEN),
    ('CRASHDIAGRAMNATIVE', 'X' * DUMMY_DATA_LEN),
    ('REPORTNUMBER', 'ADD9340058')])

crash_exp_data = [('X' * DUMMY_DATA_LEN, 'X' * DUMMY_DATA_LEN, 'ADD9340058')]

# COMMERCIAL VEHICLE
commveh_input_data = OrderedDict([
    ('BODYTYPE', '03'),
    ('BUSUSE', '00'),
    ('CARRIERCLASSIFICATION', '99'),
    ('CITY', 'BALTIMORE'),
    ('CONFIGURATION', '03'),
    ('COUNTRY', OrderedDict([('@i:nil', 'true')])),
    ('DOTNUMBER', '3430518'),
    ('GVW', '99'),
    ('HAZMATCLASS', '10'),
    ('HAZMATNAME', OrderedDict([('@i:nil', 'true')])),
    ('HAZMATNUMBER', OrderedDict([('@i:nil', 'true')])),
    ('HAZMATSPILL', 'N'),
    ('MCNUMBER', '111139'),
    ('NAME', 'COMPANY LLC'),
    ('NUMBEROFAXLES', '3'),
    ('PLACARDVISIBLE', 'U'),
    ('POSTALCODE', '21207'),
    ('STATE', 'MD'),
    ('STREET', '34839 PRATT ST'),
    ('VEHICLEID', 'edeaa7cd-06f1-4dde-b318-66a28ec604e0'),
    ('WEIGHT', OrderedDict([('@i:nil', 'true')])),
    ('WEIGHTUNIT', OrderedDict([('@i:nil', 'true')]))])

# DAMAGED
damaged_input_data = [
    OrderedDict([
        ('DAMAGEID', '6783466'),
        ('IMPACTTYPE', '06'),
        ('VEHICLEID', '5ce12003-c7aa-43e1-b5e8-4c0e79160a02')]),
    OrderedDict([
        ('DAMAGEID', '6783467'),
        ('IMPACTTYPE', '12'),
        ('VEHICLEID', '5ce12003-c7aa-43e1-b5e8-4c0e79160a02')])]

damaged_exp_data = [(6783466, 6, '5CE12003-C7AA-43E1-B5E8-4C0E79160A02'),
                    (6783467, 12, '5CE12003-C7AA-43E1-B5E8-4C0E79160A02')]

# EMS
ems_input_data = [
    OrderedDict([
        ('EMSTRANSPORTATIONTYPE', 'G'),
        ('EMSUNITNUMBER', 'A'),
        ('INJUREDTAKENBY', 'MEDIC 1'),
        ('INJUREDTAKENTO', 'UNIVERSITY OF MARYLAND'),
        ('REPORTNUMBER', 'ADJ063005D')]),
    OrderedDict([
        ('EMSTRANSPORTATIONTYPE', 'G'),
        ('EMSUNITNUMBER', 'B'),
        ('INJUREDTAKENBY', 'MEDIC 1'),
        ('INJUREDTAKENTO', 'UNIVERSITY OF MARYLAND'),
        ('REPORTNUMBER', 'ADJ063005D')])
]

# EVENT
event_input_data = [
    OrderedDict([
        ('EVENTID', '2685835'),
        ('EVENTSEQUENCE', '0'),
        ('EVENTTYPE', '35'),
        ('VEHICLEID', '5ce12003-c7aa-43e1-b5e8-4c0e79160a02')])]

# PDF
pdf_input_data = [
    OrderedDict([
        ('CHANGEDBY', 'BALTIMOREH923'),
        ('DATESTATUSCHANGED', '2020-12-02T21:27:08'),
        ('PDFREPORT1', 'testdata'),
        ('PDF_ID', '774946'),
        ('REPORTNUMBER', 'ADD9340058'),
        ('STATUS', 'Active')])]

# PERSON
person_input_data = [
    OrderedDict([
        ('ADDRESS', '8848848 CHARLES ST'),
        ('CITATIONCODES', None),
        ('CITY', 'BALTIMORE'),
        ('COMPANY', OrderedDict([('@i:nil', 'true')])),
        ('COUNTRY', OrderedDict([('@i:nil', 'true')])),
        ('COUNTY', OrderedDict([('@i:nil', 'true')])),
        ('DLCLASS', OrderedDict([('@i:nil', 'true')])),
        ('DLNUMBER', 'B650589744192'),
        ('DLSTATE', 'MD'),
        ('DOB', '1997-03-13T00:00:00'),
        ('FIRSTNAME', 'FIRSTNAME'),
        ('HOMEPHONE', OrderedDict([('@i:nil', 'true')])),
        ('LASTNAME', 'LASTNAME'),
        ('MIDDLENAME', OrderedDict([('@i:nil', 'true')])),
        ('OTHERPHONE', OrderedDict([('@i:nil', 'true')])),
        ('PERSONID', '0bd82e1d-8c96-40c5-b1e4-b4dfc82cb971'),
        ('RACE', OrderedDict([('@i:nil', 'true')])),
        ('REPORTNUMBER', 'ADD9340058'),
        ('SEX', 'M'),
        ('STATE', 'MD'),
        ('ZIP', '21769')]),
    OrderedDict([
        ('ADDRESS', '0000 PATTERSON PARK ST'),
        ('CITATIONCODES', OrderedDict([
            ('CITATIONCODE', [OrderedDict([
                ('CITATIONNUMBER', 'KK15680'),
                ('PERSONID', 'fcd8309c-250a-4fa4-9fdf-d6dafe2c6946'),
                ('REPORTNUMBER', 'ADD9340058')])])])),
        ('CITY', 'BALTIMORE'),
        ('COMPANY', OrderedDict([('@i:nil', 'true')])),
        ('COUNTRY', OrderedDict([('@i:nil', 'true')])),
        ('COUNTY', OrderedDict([('@i:nil', 'true')])),
        ('DLCLASS', OrderedDict([('@i:nil', 'true')])),
        ('DLNUMBER', 'C636762792077'),
        ('DLSTATE', 'MD'),
        ('DOB', '1980-01-29T00:00:00'),
        ('FIRSTNAME', 'FIRSTNAME'),
        ('HOMEPHONE', OrderedDict([('@i:nil', 'true')])),
        ('LASTNAME', 'LASTNAME'),
        ('MIDDLENAME', OrderedDict([('@i:nil', 'true')])),
        ('OTHERPHONE', OrderedDict([('@i:nil', 'true')])),
        ('PERSONID', 'fcd8309c-250a-4fa4-9fdf-d6dafe2c6946'),
        ('RACE', OrderedDict([('@i:nil', 'true')])),
        ('REPORTNUMBER', 'ADD9340058'),
        ('SEX', 'M'),
        ('STATE', 'MD'),
        ('ZIP', '21218')])]

# PERSON INFO (DRIVER)
person_info_driver_input_data = [
    OrderedDict([
        ('AIRBAGDEPLOYED', '02'),
        ('ALCOHOLTESTINDICATOR', '00'),
        ('ALCOHOLTESTTYPE', OrderedDict([('@i:nil', 'true')])),
        ('ATFAULT', 'Y'),
        ('BAC', OrderedDict([('@i:nil', 'true')])),
        ('CONDITION', '01'),
        ('DRIVERDISTRACTEDBY', '88'),
        ('DRUGTESTINDICATOR', '00'),
        ('DRUGTESTRESULT', OrderedDict([('@i:nil', 'true')])),
        ('EJECTION', '01'),
        ('EMSRUNREPORTNUMBER', OrderedDict([('@i:nil', 'true')])),
        ('EMSUNITNUMBER', OrderedDict([('@i:nil', 'true')])),
        ('EQUIPMENTPROBLEM', '99'),
        ('HASCDL', 'N'),
        ('INJURYSEVERITY', '01'),
        ('PERSON', OrderedDict(
            [('ADDRESS', '34838 ROAD ST'),
             ('CITATIONCODES', OrderedDict([
                 ('CITATIONCODE', [
                     OrderedDict(
                         [('CITATIONNUMBER', 'KK15680'),
                          ('PERSONID', 'fcd8309c-250a-4fa4-9fdf-d6dafe2c6946'),
                          ('REPORTNUMBER', 'ADD9340058')])])])),
             ('CITY', 'BALTIMORE'),
             ('COMPANY', OrderedDict([('@i:nil', 'true')])),
             ('COUNTRY', OrderedDict([('@i:nil', 'true')])),
             ('COUNTY', OrderedDict([('@i:nil', 'true')])),
             ('DLCLASS', OrderedDict([('@i:nil', 'true')])),
             ('DLNUMBER', 'C636762792077'),
             ('DLSTATE', 'MD'),
             ('DOB', '1984-01-29T00:00:00'),
             ('FIRSTNAME', 'FIRSTNAME'),
             ('HOMEPHONE', OrderedDict([('@i:nil', 'true')])),
             ('LASTNAME', 'LASTNAME'),
             ('MIDDLENAME', OrderedDict([('@i:nil', 'true')])),
             ('OTHERPHONE', OrderedDict([('@i:nil', 'true')])),
             ('PERSONID', 'fcd8309c-250a-4fa4-9fdf-d6dafe2c6946'),
             ('RACE', OrderedDict([('@i:nil', 'true')])),
             ('REPORTNUMBER', 'ADD9340058'),
             ('SEX', 'M'),
             ('STATE', 'MD'),
             ('ZIP', '21218')])),
        ('PERSONID', 'fcd8309c-250a-4fa4-9fdf-d6dafe2c6946'),
        ('SAFETYEQUIPMENT', '99'),
        ('SUBSTANCEUSE', '00'),
        ('VEHICLEID', '5f19b3c5-4e3b-4010-9959-506a84632cdb')])]

# PERSON INFO PASSENGER
person_info_pass_input_data = [
    OrderedDict([
        ('AIRBAGDEPLOYED', '01'),
        ('EJECTION', '01'),
        ('EMSRUNREPORTNUMBER', 'UNK'),
        ('EMSUNITNUMBER', 'A'),
        ('EQUIPMENTPROBLEM', '01'),
        ('INJURYSEVERITY', '02'),
        ('PERSON', OrderedDict([
            ('ADDRESS', '3600 W FRANKLIN STREET'),
            ('CITATIONCODES', None),
            ('CITY', 'BALTIMORE'),
            ('COMPANY', OrderedDict([('@i:nil', 'true')])),
            ('COUNTRY', OrderedDict([('@i:nil', 'true')])),
            ('COUNTY', OrderedDict([('@i:nil', 'true')])),
            ('DLCLASS', OrderedDict([('@i:nil', 'true')])),
            ('DLNUMBER', OrderedDict([('@i:nil', 'true')])),
            ('DLSTATE', OrderedDict([('@i:nil', 'true')])),
            ('DOB', '1987-06-24T00:00:00'),
            ('FIRSTNAME', 'FIRSTNAME'),
            ('HOMEPHONE', OrderedDict([('@i:nil', 'true')])),
            ('LASTNAME', 'LASTNAME'),
            ('MIDDLENAME', OrderedDict([('@i:nil', 'true')])),
            ('OTHERPHONE', '4439432045'),
            ('PERSONID', 'fd3dffba-c1c6-41df-9fc5-a45ae4379db1'),
            ('RACE', OrderedDict([('@i:nil', 'true')])),
            ('REPORTNUMBER', 'ADJ063005D'),
            ('SEX', 'M'),
            ('STATE', 'MD'),
            ('ZIP', '21229')])),
        ('PERSONID', 'fd3dffba-c1c6-41df-9fc5-a45ae4379db1'),
        ('SAFETYEQUIPMENT', '13'),
        ('SEAT', '03'),
        ('SEATINGLOCATION', '06'),
        ('SEATINGROW', '2'),
        ('VEHICLEID', '6dde66e1-433b-4839-9df8-ffb969d35d68')])]

# PERSON INFO (PASSENGER) - MULTIPLE
person_info_pass_mult_input_data = [
    OrderedDict([
        ('AIRBAGDEPLOYED', '01'),
        ('EJECTION', '01'),
        ('EMSRUNREPORTNUMBER', OrderedDict([('@i:nil', 'true')])),
        ('EMSUNITNUMBER', OrderedDict([('@i:nil', 'true')])),
        ('EQUIPMENTPROBLEM', '01'),
        ('INJURYSEVERITY', '01'),
        ('PERSON', OrderedDict([
            ('ADDRESS', '34983 SOMESTREET ST'),
            ('CITATIONCODES', None),
            ('CITY', 'BALTIMORE'),
            ('COMPANY', OrderedDict([('@i:nil', 'true')])),
            ('COUNTRY', OrderedDict([('@i:nil', 'true')])),
            ('COUNTY', OrderedDict([('@i:nil', 'true')])),
            ('DLCLASS', OrderedDict([('@i:nil', 'true')])),
            ('DLNUMBER', OrderedDict([('@i:nil', 'true')])),
            ('DLSTATE', OrderedDict([('@i:nil', 'true')])),
            ('DOB', '2002-08-18T00:00:00'),
            ('FIRSTNAME', 'FIRSTNAMER'),
            ('HOMEPHONE', OrderedDict([('@i:nil', 'true')])),
            ('LASTNAME', 'LASTNAMER'),
            ('MIDDLENAME', OrderedDict([('@i:nil', 'true')])),
            ('OTHERPHONE', '6677861336'),
            ('PERSONID', '3c348c05-c3c1-44fb-840c-dd5c23cd9811'),
            ('RACE', OrderedDict([('@i:nil', 'true')])),
            ('REPORTNUMBER', 'ADD90500BB'),
            ('SEX', 'M'),
            ('STATE', 'MD'),
            ('ZIP', '21042')])),
        ('PERSONID', '3c348c05-c3c1-44fb-840c-dd5c23cd9811'),
        ('SAFETYEQUIPMENT', '13'),
        ('SEAT', '01'),
        ('SEATINGLOCATION', '04'),
        ('SEATINGROW', '2'),
        ('VEHICLEID', 'c783f85b-ac08-4ad4-8493-e211e5d8ec6e')]),
    OrderedDict([
        ('AIRBAGDEPLOYED', '01'),
        ('EJECTION', '01'),
        ('EMSRUNREPORTNUMBER', OrderedDict([('@i:nil', 'true')])),
        ('EMSUNITNUMBER', OrderedDict([('@i:nil', 'true')])),
        ('EQUIPMENTPROBLEM', '01'),
        ('INJURYSEVERITY', '01'),
        ('PERSON',
         OrderedDict([
             ('ADDRESS', '100 W PRATT ST'),
             ('CITATIONCODES', None),
             ('CITY', 'ELLICOTT CITY'),
             ('COMPANY', OrderedDict([('@i:nil', 'true')])),
             ('COUNTRY', OrderedDict([('@i:nil', 'true')])),
             ('COUNTY', OrderedDict([('@i:nil', 'true')])),
             ('DLCLASS', OrderedDict([('@i:nil', 'true')])),
             ('DLNUMBER', OrderedDict([('@i:nil', 'true')])),
             ('DLSTATE', OrderedDict([('@i:nil', 'true')])),
             ('DOB', '2002-06-01T00:00:00'),
             ('FIRSTNAME', 'SOME'),
             ('HOMEPHONE', OrderedDict([('@i:nil', 'true')])),
             ('LASTNAME', 'ONE'),
             ('MIDDLENAME', OrderedDict([('@i:nil', 'true')])),
             ('OTHERPHONE', '4437453018'),
             ('PERSONID', '64f9cda0-1477-4cb9-8891-67087d4163bc'),
             ('RACE', OrderedDict([('@i:nil', 'true')])),
             ('REPORTNUMBER', 'ADD90500BB'),
             ('SEX', 'F'),
             ('STATE', 'MD'),
             ('ZIP', '21043')])),
        ('PERSONID', '64f9cda0-1477-4cb9-8891-67087d4163bc'),
        ('SAFETYEQUIPMENT', '13'),
        ('SEAT', '03'),
        ('SEATINGLOCATION', '03'),
        ('SEATINGROW', '1'),
        ('VEHICLEID', 'c783f85b-ac08-4ad4-8493-e211e5d8ec6e')])]

# PERSON INFO (NONMOTORIST)
person_info_nonmotorist_input_data = [
    OrderedDict([
        ('ALCOHOLTESTINDICATOR', '00'),
        ('ALCOHOLTESTTYPE', OrderedDict([('@i:nil', 'true')])),
        ('ATFAULT', 'N'),
        ('BAC', OrderedDict([('@i:nil', 'true')])),
        ('CONDITION', '01'),
        ('CONTINUEDIRECTION', OrderedDict([('@i:nil', 'true')])),
        ('DRUGTESTINDICATOR', '00'),
        ('DRUGTESTRESULT', OrderedDict([('@i:nil', 'true')])),
        ('EMSRUNREPORTNUMBER', '0000000000'),
        ('EMSUNITNUMBER', 'C'),
        ('GOINGDIRECTION', OrderedDict([('@i:nil', 'true')])),
        ('INJURYSEVERITY', '03'),
        ('PEDESTRIANACTIONS', '01'),
        ('PEDESTRIANLOCATION', '88'),
        ('PEDESTRIANMOVEMENT', '88'),
        ('PEDESTRIANOBEYTRAFFICSIGNAL', '00'),
        ('PEDESTRIANTYPE', '06'),
        ('PEDESTRIANVISIBILITY', '00'),
        ('PERSON', OrderedDict([
            ('ADDRESS', '100 NEWHAM ST'),
            ('CITATIONCODES', None),
            ('CITY', 'BALTIMORE'),
            ('COMPANY', OrderedDict([('@i:nil', 'true')])),
            ('COUNTRY', OrderedDict([('@i:nil', 'true')])),
            ('COUNTY', OrderedDict([('@i:nil', 'true')])),
            ('DLCLASS', OrderedDict([('@i:nil', 'true')])),
            ('DLNUMBER', OrderedDict([('@i:nil', 'true')])),
            ('DLSTATE', OrderedDict([('@i:nil', 'true')])),
            ('DOB', '1962-12-01T00:00:00'),
            ('FIRSTNAME', 'JAN'),
            ('HOMEPHONE', OrderedDict([('@i:nil', 'true')])),
            ('LASTNAME', 'UARY'),
            ('MIDDLENAME', OrderedDict([('@i:nil', 'true')])),
            ('OTHERPHONE', '4435226285'),
            ('PERSONID', 'd18f27b0-d7e3-40de-b778-89f7a88ccd4f'),
            ('RACE', OrderedDict([('@i:nil', 'true')])),
            ('REPORTNUMBER', 'ADD905004N'),
            ('SEX', 'F'),
            ('STATE', 'MD'),
            ('ZIP', '21224')])),
        ('PERSONID', 'd18f27b0-d7e3-40de-b778-89f7a88ccd4f'),
        ('REPORTNUMBER', 'ADD905004N'),
        ('SAFETYEQUIPMENT', '01'),
        ('SUBSTANCEUSE', '01'),
        ('UNITNUMBERFIRSTSTRIKE', '1')])]

# ROADWAY
roadway_input_data = OrderedDict([
    ('COUNTY', '24'),
    ('LOGMILE_DIR', OrderedDict([('@i:nil', 'true')])),
    ('MILEPOINT', '0'),
    ('MUNICIPAL', '000'),
    ('MUNICIPAL_AREA_CODE', OrderedDict([('@i:nil', 'true')])),
    ('REFERENCE_MUNI', OrderedDict([('@i:nil', 'true')])),
    ('REFERENCE_ROADNAME', 'WATERVIEW AVE'),
    ('REFERENCE_ROUTE_NUMBER', OrderedDict([('@i:nil', 'true')])),
    ('REFERENCE_ROUTE_SUFFIX', OrderedDict([('@i:nil', 'true')])),
    ('REFERENCE_ROUTE_TYPE', OrderedDict([('@i:nil', 'true')])),
    ('ROADID', '9316ed0c-cddf-481c-94ee-4662e0b77384'),
    ('ROAD_NAME', 'CHERRY HILL RD'),
    ('ROUTE_NUMBER', OrderedDict([('@i:nil', 'true')])),
    ('ROUTE_SUFFIX', OrderedDict([('@i:nil', 'true')])),
    ('ROUTE_TYPE', OrderedDict([('@i:nil', 'true')]))])

# TOWED
towed_input_data = [
    OrderedDict([
        ('INSURANCEPOLICYNUMBER', '0923954101'),
        ('INSURER', 'GEICO'),
        ('LICENSEPLATENUMBER', 'ARS'),
        ('LICENSEPLATESTATE', 'MD'),
        ('OWNER', None),  # tested in test_read_acrs_person_data
        ('OWNERID', '0eea2c7f-3f2c-4fd6-abc2-4927605d237a'),
        ('TOWEDID', '6671f8b9-b7d0-469d-8766-f1d153f72986'),
        ('UNITNUMBER', OrderedDict([('@i:nil', 'true')])),
        ('VEHICLEID', '642f511d-fd4b-4daf-a6b8-5418546be524'),
        ('VEHICLEMAKE', 'CADILLAC'),
        ('VEHICLEMODEL', 'ESCALADE'),
        ('VEHICLEYEAR', '2097'),
        ('VIN', '10123456789ABCDEF')])]

# VEHICLE DATA
vehicle_input_data = [
    OrderedDict([
        ('COMMERCIALVEHICLE', OrderedDict([('@i:nil', 'true')])),
        ('CONTINUEDIRECTION', 'W'),
        ('DAMAGEDAREAs', None),  # tested in test_read_damaged_areas_data
        ('DAMAGEEXTENT', '02'),
        ('DRIVERLESSVEHICLE', 'N'),
        ('DRIVERs', None),  # tested in test_read_person_info_data
        ('EMERGENCYMOTORVEHICLEUSE', 'N'),
        ('EVENTS', None),  # tested in test_read_event_data
        ('FIRE', OrderedDict([('@i:nil', 'true')])),
        ('FIRSTIMPACT', '01'),
        ('GOINGDIRECTION', 'W'),
        ('HITANDRUN', 'N'),
        ('INSURANCEPOLICYNUMBER', '0123456789AGF'),
        ('INSURER', 'USAA'),
        ('LICENSEPLATENUMBER', '1ACDEF'),
        ('LICENSEPLATESTATE', 'MD'),
        ('MAINIMPACT', '01'),
        ('MOSTHARMFULEVENT', '01'),
        ('OWNER', None),  # tested in test_read_acrs_person_data
        ('OWNERID', '21732e90-2796-497f-a5c2-5d7877510d4c'),
        ('PARKEDVEHICLE', 'N'),
        ('PASSENGERs', None),  # tested in test_read_person_info_data_passenger
        ('REGISTRATIONEXPIRATIONYEAR', OrderedDict([('@i:nil', 'true')])),
        ('REPORTNUMBER', 'ADJ063005D'),
        ('SFVEHICLEINTRANSPORT', '00'),
        ('SPEEDLIMIT', '25'),
        ('TOWEDUNITTYPE', '00'),
        ('TOWEDUNITs', None),  # tested in test_read_towed_vehicle_data
        ('UNITNUMBER', '1'),
        ('VEHICLEBODYTYPE', '23.08'),
        ('VEHICLEID', '01a1ac19-5c24-4fbe-a001-173574c5cbed'),
        ('VEHICLEMAKE', 'GMC'),
        ('VEHICLEMODEL', 'ENVOY'),
        ('VEHICLEMOVEMENT', '13'),
        ('VEHICLEREMOVEDBY', OrderedDict([('@i:nil', 'true')])),
        ('VEHICLEREMOVEDTO', OrderedDict([('@i:nil', 'true')])),
        ('VEHICLETOWEDAWAY', OrderedDict([('@i:nil', 'true')])),
        ('VEHICLEUSEs', None),  # tested in test_read_acrs_vehicle_use_data
        ('VEHICLEYEAR', '2017'),
        ('VIN', '1234567890123456')]),
    OrderedDict([
        ('COMMERCIALVEHICLE', OrderedDict([('@i:nil', 'true')])),
        ('CONTINUEDIRECTION', 'W'),
        ('DAMAGEDAREAs', None),  # tested in test_read_damaged_areas_data
        ('DAMAGEEXTENT', '03'),
        ('DRIVERLESSVEHICLE', 'N'),
        ('DRIVERs', None),  # tested in test_read_person_info_data_driver
        ('EMERGENCYMOTORVEHICLEUSE', 'N'),
        ('EVENTS', None),  # tested in test_read_event_data
        ('FIRE', OrderedDict([('@i:nil', 'true')])),
        ('FIRSTIMPACT', '11'),
        ('GOINGDIRECTION', 'W'),
        ('HITANDRUN', 'N'),
        ('INSURANCEPOLICYNUMBER', 'G00999263900'),
        ('INSURER', 'BRISTOL WEST'),
        ('LICENSEPLATENUMBER', 'QWERTY'),
        ('LICENSEPLATESTATE', 'PA'),
        ('MAINIMPACT', '11'),
        ('MOSTHARMFULEVENT', '00'),
        ('OWNER', None),  # tested in test_read_acrs_person_data
        ('OWNERID', 'd978be20-08c7-4ff3-b2e9-a251047ac3a7'),
        ('PARKEDVEHICLE', 'N'),
        ('PASSENGERs', None),  # tested in test_read_person_info_data_passenger
        ('REGISTRATIONEXPIRATIONYEAR', OrderedDict([('@i:nil', 'true')])),
        ('REPORTNUMBER', 'ADJ063005D'),
        ('SFVEHICLEINTRANSPORT', '00'),
        ('SPEEDLIMIT', '0'),
        ('TOWEDUNITTYPE', '00'),
        ('TOWEDUNITs', None),  # tested in test_read_towed_vehicle_data
        ('UNITNUMBER', '2'),
        ('VEHICLEBODYTYPE', '23.08'),
        ('VEHICLEID', '6dde66e1-433b-4839-9df8-ffb969d35d68'),
        ('VEHICLEMAKE', 'BUICK'),
        ('VEHICLEMODEL', 'ENCLAVE'),
        ('VEHICLEMOVEMENT', '06'),
        ('VEHICLEREMOVEDBY', OrderedDict([('@i:nil', 'true')])),
        ('VEHICLEREMOVEDTO', OrderedDict([('@i:nil', 'true')])),
        ('VEHICLETOWEDAWAY', OrderedDict([('@i:nil', 'true')])),
        ('VEHICLEUSEs', None),  # tested in test_read_acrs_vehicle_use_data
        ('VEHICLEYEAR', '2013'),
        ('VIN', '1ASDFGHJKLZXCVBNM')])]

# VEHICLE USE
vehicle_use_input_data = [
    OrderedDict([
        ('ID', '3696806'),
        ('VEHICLEID', '5f19b3c5-4e3b-4010-9959-506a84632cdb'),
        ('VEHICLEUSECODE', '00')])]

# WITNESS
witness_input_data = [
    OrderedDict([
        ('PERSON', OrderedDict([
            ('ADDRESS', '3498 SDFJKD RD'),
            ('CITATIONCODES', None),
            ('CITY', 'BALTIMORE'),
            ('COMPANY', OrderedDict([('@i:nil', 'true')])),
            ('COUNTRY', OrderedDict([('@i:nil', 'true')])),
            ('COUNTY', OrderedDict([('@i:nil', 'true')])),
            ('DLCLASS', OrderedDict([('@i:nil', 'true')])),
            ('DLNUMBER', OrderedDict([('@i:nil', 'true')])),
            ('DLSTATE', OrderedDict([('@i:nil', 'true')])),
            ('DOB', OrderedDict([('@i:nil', 'true')])),
            ('FIRSTNAME', 'TONY'),
            ('MIDDLENAME', 'TONY'),
            ('LASTNAME', 'TONY'),
            ('HOMEPHONE', '4109037977'),
            ('OTHERPHONE', OrderedDict([('@i:nil', 'true')])),
            ('PERSONID', '6b76fbc7-56e8-4cf5-9d35-dfeb33a4e60d'),
            ('RACE', OrderedDict([('@i:nil', 'true')])),
            ('REPORTNUMBER', 'ADJ956004Z'),
            ('SEX', OrderedDict([('@i:nil', 'true')])),
            ('STATE', 'MD'),
            ('ZIP', '21218')])),
        ('PERSONID', '6b76fbc7-56e8-4cf5-9d35-dfeb33a4e60d'),
        ('REPORTNUMBER', 'ADJ956004Z')])]

# SINGLE ATTR
single_attr_input_data = OrderedDict([
    ('MULTIPLENODE', OrderedDict([
        ('NODE', 'TESTDATA')])),
    ('STRNODE', 'STRDATA'),
    ('NONENODE', None),
    ('NILNODE', OrderedDict([('@i:nil', 'true')]))
])
