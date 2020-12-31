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
    ('WITNESSes', None)])

crash_test_exp_data = [
    ('2020-11-28 21:59:32.0096310', 'BALTIMORE', 'Baltimore City Police Department', 'UNK', 3, None, None, False, 'N',
     '2020-11-28', '19:45:00.0000000', '999', 2519, '999', 2514, 'ACRS', '00', '01', '01', False,
     '2020-11-28 21:59:53.0000000', 3, None, 2, 'BALTIMORED934', None, '03', 'W', 1, None, 39.25760123456789, '03',
     '9201107985', '3502', -76.63280123456789, 'W', 80.0, 'F', 'Test narrative', False, 4, None, False, None, 24,
     'ADD9340058', 'Injury Crash', 1, 1, '03', 1, '9316ed0c-cddf-481c-94ee-4662e0b77384', 1, None, None,
     'BALTIMOREH923', '2020-12-03 02:27:08.7553310', '02', 3, True, '2020-11-28 21:58:35.0000000', '20.17.02.01', 1,
     '06.01')]

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

approval_exp_data = [
    ('BALTIMORE', '2020-08-05 15:30:01.0000000', None, None, '9200708732', '2020-07-29 15:53:20.0000000', 2519, None,
     '2020-07-28 00:00:00.0000000', None, 'ACRS', 'ADD934004Q', '2020-08-05 11:29:43.0000000', 3, 1, 'BALTIMORED934',
     '999')]

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

circum_exp_data = [
    ('00', 10360030, 'Weather', None, 'ADD934004Q', None),
    ('00', 10360031, 'Road', None, 'ADD934004Q', None),
    ('60.88', 10360032, 'Person', '6239E4E7-65B8-452A-BA1E-6BC26B8C5CC4', 'ADD934004Q', None),
    ('00', 10360033, 'Vehicle', None, 'ADD934004Q', '65CD4028-82AB-401E-A7FA-D392DFB98E03'),
    ('00', 10360034, 'Person', 'C3E96BDD-5049-426F-B27D-C3BF43B1EECA', 'ADD934004Q', None),
    ('00', 10360035, 'Vehicle', None, 'ADD934004Q', 'DDD4ED36-CCA5-4634-8209-01E38CC13CED')
]

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

commveh_exp_data = [(
    '03', 0, 99, 'BALTIMORE', 3, None, '3430518', 99, '10', None, None, 'N', '111139', 'COMPANY LLC',
    3, 'U', '21207', 'MD', '34839 PRATT ST', 'EDEAA7CD-06F1-4DDE-B318-66A28EC604E0', None,
    None)]

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
        ('REPORTNUMBER', 'ADJ063005D')])]

ems_exp_data = [('G', 'A', 'MEDIC 1', 'UNIVERSITY OF MARYLAND', 'ADJ063005D')]

# EVENT
event_input_data = [
    OrderedDict([
        ('EVENTID', '2685835'),
        ('EVENTSEQUENCE', '0'),
        ('EVENTTYPE', '35'),
        ('VEHICLEID', '5ce12003-c7aa-43e1-b5e8-4c0e79160a02')])]

event_exp_data = [(2685835, 0, 35, '5CE12003-C7AA-43E1-B5E8-4C0E79160A02')]

# PDF
pdf_input_data = [
    OrderedDict([
        ('CHANGEDBY', 'BALTIMOREH923'),
        ('DATESTATUSCHANGED', '2020-12-02T21:27:08'),
        ('PDFREPORT1', 'testdata'),
        ('PDF_ID', '774946'),
        ('REPORTNUMBER', 'ADD9340058'),
        ('STATUS', 'Active')])]

pdf_exp_data = [('BALTIMOREH923', '2020-12-02 21:27:08.0000000', 'testdata', 774946, 'ADD9340058', 'Active')]

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

person_exp_data = [
    (
        '8848848 CHARLES ST', 'BALTIMORE', None, None, None, None, 'B650589744192', 'MD', '1997-03-13', 'FIRSTNAME',
        None, 'LASTNAME', None, None, '0BD82E1D-8C96-40C5-B1E4-B4DFC82CB971', None, 'ADD9340058', 'M', 'MD', '21769'),
    ('0000 PATTERSON PARK ST', 'BALTIMORE', None, None, None, None, 'C636762792077', 'MD', '1980-01-29', 'FIRSTNAME',
     None, 'LASTNAME', None, None, 'FCD8309C-250A-4FA4-9FDF-D6DAFE2C6946', None, 'ADD9340058', 'M', 'MD', '21218')]

person_citation_exp_data = [('KK15680', 'FCD8309C-250A-4FA4-9FDF-D6DAFE2C6946', 'ADD9340058')]

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

person_info_driver_exp_data = [
    (2, 0, None, True, None, '01', None, 88, 0, None, 1, None, None, 99, None, False, 1, None, None, None, None, None,
     None, 'FCD8309C-250A-4FA4-9FDF-D6DAFE2C6946', 'ADD9340058', '99', None, None, None, 0, None,
     '5F19B3C5-4E3B-4010-9959-506A84632CDB')]

person_info_driver_person_exp_data = [
    ('34838 ROAD ST', 'BALTIMORE', None, None, None, None, 'C636762792077', 'MD', '1984-01-29', 'FIRSTNAME', None,
     'LASTNAME', None, None, 'FCD8309C-250A-4FA4-9FDF-D6DAFE2C6946', None, 'ADD9340058', 'M', 'MD', '21218')]

person_info_driver_citations_exp_data = [
    ('KK15680', 'FCD8309C-250A-4FA4-9FDF-D6DAFE2C6946', 'ADD9340058')]

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

person_info_pass_exp_data = [
    (1, None, None, None, None, None, None, None, None, None, 1, 'UNK', 'A', 1, None, None, 2, None, None, None, None,
     None, None, 'FD3DFFBA-C1C6-41DF-9FC5-A45AE4379DB1', 'ADJ063005D', '13', 3, 6, 2, None, None,
     '6DDE66E1-433B-4839-9DF8-FFB969D35D68')]

person_info_person_pass_exp_data = [
    ('3600 W FRANKLIN STREET', 'BALTIMORE', None, None, None, None, None, None, '1987-06-24', 'FIRSTNAME', None,
     'LASTNAME', None, '4439432045', 'FD3DFFBA-C1C6-41DF-9FC5-A45AE4379DB1', None, 'ADJ063005D', 'M', 'MD', '21229')]

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

person_info_pass_mult_exp_data = [
    (1, None, None, None, None, None, None, None, None, None, 1, None, None, 1, None, None, 1, None, None, None, None,
     None, None, '3C348C05-C3C1-44FB-840C-DD5C23CD9811', 'ADD90500BB', '13', 1, 4, 2, None, None,
     'C783F85B-AC08-4AD4-8493-E211E5D8EC6E'),
    (1, None, None, None, None, None, None, None, None, None, 1, None, None, 1, None, None, 1, None, None, None, None,
     None, None, '64f9cda0-1477-4cb9-8891-67087d4163bc', 'ADD90500BB', '13', 3, 3, 1, None, None,
     'C783F85B-AC08-4AD4-8493-E211E5D8EC6E')]

person_info_person_mult_pass_exp_data = [
    ('100 W PRATT ST', 'ELLICOTT CITY', None, None, None, None, None, None, '2002-06-01', 'SOME', None, 'ONE',
     None, '4437453018', '64F9CDA0-1477-4CB9-8891-67087D4163BC', None, 'ADD90500BB', 'F', 'MD', '21043'),
    ('34983 SOMESTREET ST', 'BALTIMORE', None, None, None, None, None, None, '2002-08-18', 'FIRSTNAMER', None,
     'LASTNAMER', None, '6677861336', '3C348C05-C3C1-44FB-840C-DD5C23CD9811', None, 'ADD90500BB', 'M', 'MD', '21042')
]

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

person_info_nonmotorist_exp_data = [
    (
        None, 0, None, False, None, '01', None, None, 0, None, None, '0000000000', 'C', None, None, None, 3, 1, 88,
        '88', 0,
        6, 0, 'D18F27B0-D7E3-40DE-B778-89F7A88CCD4F', 'ADD905004N', '01', None, None, None, 1, 1, None)]

person_info_records_nonmotorist_input_data = [('100 NEWHAM ST', 'BALTIMORE', None, None, None, None, None, None,
                                               '1962-12-01', 'JAN', None, 'UARY', None, '4435226285',
                                               'D18F27B0-D7E3-40DE-B778-89F7A88CCD4F', None, 'ADD905004N', 'F', 'MD',
                                               '21224')]

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

roadway_exp_data = [
    (24, None, 0.0, 0, None, None, 'WATERVIEW AVE', None, None, None, '9316ed0c-cddf-481c-94ee-4662e0b77384',
     'CHERRY HILL RD', None, None, None, None)]

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

towed_exp_data = [
    ('0923954101', 'GEICO', 'ARS', 'MD', '0EEA2C7F-3F2C-4FD6-ABC2-4927605D237A', '6671F8B9-B7D0-469D-8766-F1D153F72986',
     None, '642F511D-FD4B-4DAF-A6B8-5418546BE524', 'CADILLAC', 'ESCALADE', 2097, '10123456789ABCDEF')]

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

vehicle_exp_data = [
    (None, 'W', 2, False, False, None, 1, 'W', False, '0123456789AGF', 'USAA', '1ACDEF', 'MD', 1, '01',
     '21732E90-2796-497F-A5C2-5D7877510D4C', False, None, 'ADJ063005D', 0, 25, 0, '1', '23.08',
     '01A1AC19-5C24-4FBE-A001-173574C5CBED', 'GMC', 'ENVOY', 13.0, None, None, None, 2017, '1234567890123456'),
    (None, 'W', 3, False, False, None, 11, 'W', False, 'G00999263900', 'BRISTOL WEST', 'QWERTY', 'PA', 11, '00',
     'D978BE20-08C7-4FF3-B2E9-A251047AC3A7', False, None, 'ADJ063005D', 0, 0, 0, '2', '23.08',
     '6DDE66E1-433B-4839-9DF8-FFB969D35D68', 'BUICK', 'ENCLAVE', 6.0, None, None, None, 2013, '1ASDFGHJKLZXCVBNM')]

# VEHICLE USE
vehicle_use_input_data = [
    OrderedDict([
        ('ID', '3696806'),
        ('VEHICLEID', '5f19b3c5-4e3b-4010-9959-506a84632cdb'),
        ('VEHICLEUSECODE', '00')])]

vehicle_use_exp_data = [(3696806, '5F19B3C5-4E3B-4010-9959-506A84632CDB', 0)]

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

witness_exp_data = [('6B76FBC7-56E8-4CF5-9D35-DFEB33A4E60D', 'ADJ956004Z'), ]
witness_records_expt_data = [
    ('3498 SDFJKD RD', 'BALTIMORE', None, None, None, None, None, None, None, 'TONY', '4109037977', 'TONY',
     'TONY', None, '6B76FBC7-56E8-4CF5-9D35-DFEB33A4E60D', None, 'ADJ956004Z', None, 'MD', '21218'), ]

# SINGLE ATTR
single_attr_input_data = OrderedDict([
    ('MULTIPLENODE', OrderedDict([
        ('NODE', 'TESTDATA')])),
    ('STRNODE', 'STRDATA'),
    ('NONENODE', None),
    ('NILNODE', OrderedDict([('@i:nil', 'true')]))
])
