"""Pytest suite for src/ms2generator"""
# pylint:disable=protected-access
import os

import pandas as pd  # type: ignore
import pytest
from numpy import nan

from trafficstat.ms2generator import WorksheetMaker


def test_add_crash_worksheet(tmpdir, conn_str_sanitized, conn_str_unsanitized):  # pylint:disable=unused-argument
    """test for the add_crash_worksheet method"""
    worksheet_maker = WorksheetMaker(conn_str=conn_str_sanitized, workbook_name=os.path.join(tmpdir, 'sheet.xlsx'))
    with worksheet_maker:
        worksheet_maker.add_crash_worksheet()

    dfs = pd.read_excel(worksheet_maker.workbook_name, sheet_name='CRASH')
    assert dfs.columns.to_list() == ['LIGHT_CODE', 'COUNTY_NO', 'MUNI_CODE', 'JUNCTION_CODE', 'COLLISION_TYPE_CODE',
                                     'SURF_COND_CODE', 'LANE_CODE', 'RD_COND_CODE', 'RD_DIV_CODE', 'FIX_OBJ_CODE',
                                     'REPORT_NO', 'REPORT_TYPE', 'WEATHER_CODE', 'ACC_DATE', 'ACC_TIME', 'LOC_CODE',
                                     'SIGNAL_FLAG', 'C_M_ZONE_FLAG', 'AGENCY_CODE', 'AREA_CODE', 'HARM_EVENT_CODE1',
                                     'HARM_EVENT_CODE2', 'RTE_NO', 'ROUTE_TYPE_CODE', 'RTE_SUFFIX', 'LOG_MILE',
                                     'LOGMILE_DIR_FLAG', 'MAINROAD_NAME', 'DISTANCE', 'FEET_MILES_FLAG',
                                     'DISTANCE_DIR_FLAG', 'REFERENCE_NO', 'REFERENCE_TYPE_CODE', 'REFERENCE_SUFFIX',
                                     'REFERENCE_ROAD_NAME', 'LATITUDE', 'LONGITUDE']
    assert len(dfs) == 10


def test_add_person_worksheet(tmpdir, conn_str_sanitized):
    """test for the add_person_worksheet method"""
    worksheet_maker = WorksheetMaker(conn_str=conn_str_sanitized, workbook_name=os.path.join(tmpdir, 'sheet.xlsx'))
    with worksheet_maker:
        worksheet_maker.add_person_worksheet()

    dfs = pd.read_excel(worksheet_maker.workbook_name, sheet_name='PERSON')
    assert dfs.columns.to_list() == ['SEX_CODE', 'CONDITION_CODE', 'INJ_SEVER_CODE', 'REPORT_NO', 'OCC_SEAT_POS_CODE',
                                     'PED_VISIBLE_CODE', 'PED_LOCATION_CODE', 'PED_OBEY_CODE', 'PED_TYPE_CODE',
                                     'MOVEMENT_CODE', 'PERSON_TYPE', 'ALCOHOL_TEST_CODE', 'ALCOHOL_TESTTYPE_CODE',
                                     'DRUG_TEST_CODE', 'DRUG_TESTRESULT_CODE', 'BAC_CODE', 'FAULT_FLAG',
                                     'EQUIP_PROB_CODE', 'SAF_EQUIP_CODE', 'EJECT_CODE', 'AIRBAG_DEPLOYED',
                                     'DATE_OF_BIRTH', 'PERSON_ID', 'LICENSE_STATE_CODE', 'CLASS', 'CDL_FLAG',
                                     'VEHICLE_ID', 'EMS_UNIT_LABEL']
    assert len(dfs) == 10


def test_add_ems_worksheet(tmpdir, conn_str_sanitized):
    """test for the add_ems_worksheet method"""
    worksheet_maker = WorksheetMaker(conn_str=conn_str_sanitized, workbook_name=os.path.join(tmpdir, 'sheet.xlsx'))
    with worksheet_maker:
        worksheet_maker.add_ems_worksheet()

    dfs = pd.read_excel(worksheet_maker.workbook_name, sheet_name='EMS')
    assert dfs.columns.to_list() == ['REPORT_NO', 'EMS_UNIT_TAKEN_BY', 'EMS_UNIT_TAKEN_TO', 'EMS_UNIT_LABEL',
                                     'EMS_TRANSPORT_TYPE']
    assert len(dfs) == 10


def test_add_vehicle_worksheet(tmpdir, conn_str_sanitized):
    """test for the add_vehicle_worksheet method"""
    worksheet_maker = WorksheetMaker(conn_str=conn_str_sanitized, workbook_name=os.path.join(tmpdir, 'sheet.xlsx'))
    with worksheet_maker:
        worksheet_maker.add_vehicle_worksheet()

    dfs = pd.read_excel(worksheet_maker.workbook_name, sheet_name='VEHICLE')
    assert dfs.columns.to_list() == ['HARM_EVENT_CODE', 'CONTI_DIRECTION_CODE', 'DAMAGE_CODE', 'MOVEMENT_CODE',
                                     'VIN_NO', 'REPORT_NO', 'CV_BODY_TYPE_CODE', 'VEH_YEAR', 'VEH_MAKE',
                                     'COMMERCIAL_FLAG', 'VEH_MODEL', 'HZM_NUM', 'TOWED_AWAY_FLAG', 'NUM_AXLES',
                                     'GVW_CODE', 'GOING_DIRECTION_CODE', 'BODY_TYPE_CODE', 'DRIVERLESS_FLAG',
                                     'FIRE_FLAG', 'PARKED_FLAG', 'SPEED_LIMIT', 'HIT_AND_RUN_FLAG', 'HAZMAT_SPILL_FLAG',
                                     'VEHICLE_ID', 'TOWED_VEHICLE_CONFIG_CODE', 'AREA_DAMAGED_CODE_IMP1',
                                     'AREA_DAMAGED_CODE1', 'AREA_DAMAGED_CODE2', 'AREA_DAMAGED_CODE3',
                                     'AREA_DAMAGED_CODE_MAIN']
    assert len(dfs) == 10

    # verify that vehicle_circum was populated
    dfs = pd.read_excel(worksheet_maker.workbook_name, sheet_name='VEHICLE_CIRCUM')
    assert len(dfs) == 4


def test_add_circum(tmpdir, conn_str_sanitized):
    """test for the add_vehicle_circum and add_road_circum method"""
    worksheet_maker = WorksheetMaker(conn_str=conn_str_sanitized, workbook_name=os.path.join(tmpdir, 'sheet.xlsx'))
    with worksheet_maker:
        worksheet_maker.add_vehicle_circum('A0000001', '8849671')
        worksheet_maker.add_vehicle_circum('A0000002', '8849672')
        worksheet_maker.add_road_circum()

    dfs = pd.read_excel(worksheet_maker.workbook_name, sheet_name='VEHICLE_CIRCUM')
    expected = pd.DataFrame(data={'REPORT_NO': ['A0000001', 'A0000001', 'A0000001', 'A0000002'],
                                  'CONTRIB_TYPE': ['Vehicle', 'Vehicle', 'Vehicle', 'Vehicle'],
                                  'CONTRIB_CODE': [99.00, 53.00, 76.88, 88.00], 'PERSON_ID': [nan, nan, nan, nan],
                                  'VEHICLE_ID': [dfs['VEHICLE_ID'][0],
                                                 dfs['VEHICLE_ID'][0],
                                                 dfs['VEHICLE_ID'][0],
                                                 dfs['VEHICLE_ID'][3]]})
    assert len(dfs) == 4
    assert dfs.equals(expected)

    dfs = pd.read_excel(worksheet_maker.workbook_name, sheet_name='ROAD_CIRCUM')
    expected = pd.DataFrame(data={'REPORT_NO': ['A0000004', 'A0000004', 'A0000004', 'A0000009', 'A0000009'],
                                  'CONTRIB_TYPE': ['Road', 'Road', 'Road', 'Road', 'Road'],
                                  'CONTRIB_CODE': [88.00, 78.00, 69.88, 99.00, 83.88],
                                  'PERSON_ID': [nan, nan, nan, nan, nan],
                                  'VEHICLE_ID': [nan, nan, nan, nan, nan]})
    assert len(dfs) == 5
    assert dfs.equals(expected)


def test_validate_vehicle_value():
    """test for the _validate_vehicle_value method"""
    worksheet_maker = WorksheetMaker(conn_str='sqlite://')
    assert worksheet_maker._validate_vehicle_value('48.88') == '48.88'
    assert worksheet_maker._validate_vehicle_value('A9.99') is None
    assert worksheet_maker._validate_vehicle_value('00') == '00'
    assert worksheet_maker._validate_vehicle_value(None) is None

    with pytest.raises(ValueError):
        worksheet_maker._validate_vehicle_value('01')


def test_validate_person_value():
    """test for the _validate_person_value method"""
    worksheet_maker = WorksheetMaker(conn_str='sqlite://')
    assert worksheet_maker._validate_person_value('39.88') == '39.88'
    assert worksheet_maker._validate_person_value('A9.99') is None
    assert worksheet_maker._validate_person_value('01') == '01'
    assert worksheet_maker._validate_person_value(None) is None

    with pytest.raises(ValueError):
        worksheet_maker._validate_person_value('30')


def test_validate_weather_value():
    """test for the _validate_weather_value method"""
    worksheet_maker = WorksheetMaker(conn_str='sqlite://')
    assert worksheet_maker._validate_weather_value('82.88') == '82.88'
    assert worksheet_maker._validate_weather_value('A9.99') is None
    assert worksheet_maker._validate_weather_value('45') == '45'
    assert worksheet_maker._validate_weather_value(None) is None

    with pytest.raises(ValueError):
        worksheet_maker._validate_weather_value('40')


def test_validate_road_value():
    """test for the _validate_road_value method"""
    worksheet_maker = WorksheetMaker(conn_str='sqlite://')
    assert worksheet_maker._validate_road_value('69.88') == '69.88'
    assert worksheet_maker._validate_road_value('A9.99') is None
    assert worksheet_maker._validate_road_value('61') == '61'
    assert worksheet_maker._validate_road_value(None) is None

    with pytest.raises(ValueError):
        worksheet_maker._validate_road_value('60')


def test_lookup_sex():
    """test for the _lookup_sex method"""


def test_lookup_direction():
    """test for the _lookup_direction method"""


def test_create_worksheet():
    """test for the _create_worksheet method"""


def test_get_person_uuid():
    """test for the _get_person_uuid method"""


def test_get_vehicle_uuid():
    """test for the _get_vehicle_uuid method"""
