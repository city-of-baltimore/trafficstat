"""Pytest suite for src/crash_data_ingestor"""
from collections import OrderedDict

import pytest

from . import constants_test_data


def test_read_crash_data(crash_data_reader, acrs_crashes_table, cursor):  # pylint:disable=unused-argument
    """Testing the elements in the REPORTS tag"""
    assert crash_data_reader._read_main_crash_data(  # pylint:disable=protected-access
        crash_dict=constants_test_data.crash_test_input_data)

    cursor.execute('SELECT * FROM acrs_test_crashes')
    records = cursor.fetchall()
    assert len(records) == len(constants_test_data.crash_test_exp_data)

    for i, _ in enumerate(records[0]):
        assert constants_test_data.crash_test_exp_data[0][i] == records[0][i]


def test_read_approval_data(crash_data_reader, acrs_approval_table, cursor):  # pylint:disable=unused-argument
    """Testing the elements in the APPROVALDATA tag"""
    assert crash_data_reader._read_approval_data(  # pylint:disable=protected-access
        approval_dict=constants_test_data.approval_input_data)

    cursor.execute('SELECT * FROM acrs_test_approval')
    records = cursor.fetchall()
    assert len(records) == len(constants_test_data.approval_exp_data)

    for i, _ in enumerate(records[0]):
        assert constants_test_data.approval_exp_data[0][i] == records[0][i]


def test_read_circumstance_data(crash_data_reader, acrs_circumstances_table, cursor):  # pylint:disable=unused-argument
    """Testing the elements in the CIRCUMSTANCES tag"""
    assert crash_data_reader._read_circumstance_data(  # pylint:disable=protected-access
        circumstance_dict=constants_test_data.circum_input_data)

    cursor.execute('SELECT * FROM acrs_test_circumstances')
    records = cursor.fetchall()
    assert len(records) == len(constants_test_data.circum_exp_data)

    for i, _ in enumerate(records):
        for j, _ in enumerate(records[i]):
            assert constants_test_data.circum_exp_data[i][j] == records[i][j]


def test_read_citation_data(crash_data_reader, acrs_citation_codes_table, cursor):  # pylint:disable=unused-argument
    """Testing the elements in the CITATIONCODES tag"""
    assert crash_data_reader._read_citation_data(  # pylint:disable=protected-access
        citation_dict=constants_test_data.citation_input_data.get('CITATIONCODEs'))

    cursor.execute('SELECT * FROM acrs_test_citation_codes')
    records = cursor.fetchall()
    assert len(records) == len(constants_test_data.citation_exp_data)

    for i, _ in enumerate(records[0]):
        assert constants_test_data.citation_exp_data[0][i] == records[0][i]


def test_read_crash_diagrams_data(crash_data_reader, acrs_crash_diagrams_table, cursor):  # pylint:disable=unused-argument
    """Testing the elements in the DIAGRAM tag"""
    assert crash_data_reader._read_crash_diagrams_data(  # pylint:disable=protected-access
        crash_diagram_dict=constants_test_data.crash_input_data)

    cursor.execute('SELECT * FROM acrs_test_crash_diagrams')
    records = cursor.fetchall()
    assert len(records) == len(constants_test_data.crash_exp_data)

    for i, _ in enumerate(records[0]):
        assert constants_test_data.crash_exp_data[0][i] == records[0][i]


def test_read_commercial_vehicle_data(crash_data_reader, acrs_commercial_vehicle_table, cursor):  # pylint:disable=unused-argument
    """Testing the OrderedDict from the COMMERCIALVEHICLE tag"""
    assert crash_data_reader._read_commercial_vehicle_data(  # pylint:disable=protected-access
        commvehicle_dict=constants_test_data.commveh_input_data)

    cursor.execute('SELECT * FROM acrs_test_commercial_vehicles')
    records = cursor.fetchall()
    assert len(records) == len(constants_test_data.commveh_exp_data)

    for i, _ in enumerate(records[0]):
        assert constants_test_data.commveh_exp_data[0][i] == records[0][i]


def test_read_damaged_areas_data(crash_data_reader, acrs_damaged_areas_table, cursor):  # pylint:disable=unused-argument
    """Testing the OrderedDict from the DAMAGEDAREAs tag"""
    assert crash_data_reader._read_damaged_areas_data(  # pylint:disable=protected-access
        damaged_dict=constants_test_data.damaged_input_data)

    cursor.execute('SELECT * FROM acrs_test_damaged_areas')
    records = cursor.fetchall()
    assert len(records) == len(constants_test_data.damaged_exp_data)

    for i, _ in enumerate(records[0]):
        assert constants_test_data.damaged_exp_data[0][i] == records[0][i]


def test_read_ems_data(crash_data_reader, acrs_ems_table, cursor):  # pylint:disable=unused-argument
    """Testing the ordereddict from the EMSes tag"""
    assert crash_data_reader._read_ems_data(  # pylint:disable=protected-access
        ems_dict=constants_test_data.ems_input_data.get('EMSes'))

    cursor.execute('SELECT * FROM acrs_test_ems')
    records = cursor.fetchall()
    assert len(records) == len(constants_test_data.ems_exp_data)

    for i, _ in enumerate(records[0]):
        assert constants_test_data.ems_exp_data[0][i] == records[0][i]


def test_read_event_data(crash_data_reader, acrs_events_table, cursor):  # pylint:disable=unused-argument
    """Testing the ordereddict from the EVENTS tag"""
    assert crash_data_reader._read_event_data(  # pylint:disable=protected-access
        event_dict=constants_test_data.event_input_data)

    cursor.execute('SELECT * FROM acrs_test_events')
    records = cursor.fetchall()
    assert len(records) == len(constants_test_data.event_exp_data)

    for i, _ in enumerate(records[0]):
        assert constants_test_data.event_exp_data[0][i] == records[0][i]


def test_read_pdf_data(crash_data_reader, acrs_pdf_report_table, cursor):  # pylint:disable=unused-argument
    """Testing the ordereddict from the PDFREPORTs tag"""
    assert crash_data_reader._read_pdf_data(  # pylint:disable=protected-access
        pdfreport_dict=constants_test_data.pdf_input_data.get('PDFREPORTs'))

    cursor.execute('SELECT * FROM acrs_test_pdf_report')
    records = cursor.fetchall()
    assert len(records) == len(constants_test_data.pdf_exp_data)

    for i, _ in enumerate(records[0]):
        assert constants_test_data.pdf_exp_data[0][i] == records[0][i]


def test_read_acrs_person_data(crash_data_reader, acrs_person_table, acrs_citation_codes_table, cursor):  # pylint:disable=unused-argument
    """Tests the ordereddict from the PERSON/OWNER tag"""
    for person in constants_test_data.person_input_data.get('ACRSPERSON'):
        assert crash_data_reader._read_acrs_person_data(person_dict=person)  # pylint:disable=protected-access

    cursor.execute('SELECT * FROM acrs_test_person')
    person_records = cursor.fetchall()

    cursor.execute('SELECT * FROM acrs_test_citation_codes')
    citation_records = cursor.fetchall()

    assert len(person_records) == len(constants_test_data.person_exp_data)
    assert len(citation_records) == len(constants_test_data.person_citation_exp_data)

    for i, _ in enumerate(person_records):
        assert len(constants_test_data.person_exp_data[i]) == len(person_records[i])
        for j, _ in enumerate(person_records[i]):
            assert constants_test_data.person_exp_data[i][j] == person_records[i][j]

    for i, _ in enumerate(citation_records[0]):
        assert constants_test_data.person_citation_exp_data[0][i] == citation_records[0][i]


def test_read_person_info_data_driver(crash_data_reader, cursor,
                                      acrs_person_info_table, acrs_person_table, acrs_citation_codes_table):  # pylint:disable=unused-argument
    """Tests the ordereddict from the DRIVERs tag"""
    assert crash_data_reader._read_person_info_data(  # pylint:disable=protected-access
        person_dict=constants_test_data.person_info_driver_input_data.get('DRIVERs'),
        tag='DRIVER')

    cursor.execute('SELECT * FROM acrs_test_person_info')
    records = cursor.fetchall()

    cursor.execute('SELECT * FROM acrs_test_person')
    person_records = cursor.fetchall()

    cursor.execute('SELECT * FROM acrs_test_citation_codes')
    citation_records = cursor.fetchall()

    assert len(records) == len(constants_test_data.person_info_driver_exp_data)
    assert len(person_records) == len(constants_test_data.person_info_driver_person_exp_data)
    assert len(citation_records) == len(constants_test_data.person_info_driver_citations_exp_data)

    for i, _ in enumerate(records[0]):
        assert constants_test_data.person_info_driver_exp_data[0][i] == records[0][i]

    for i, _ in enumerate(person_records):
        assert len(constants_test_data.person_info_driver_person_exp_data[i]) == len(person_records[i])
        for j, _ in enumerate(person_records[i]):
            assert constants_test_data.person_info_driver_person_exp_data[i][j] == person_records[i][j]

    for i, _ in enumerate(citation_records[0]):
        assert constants_test_data.person_info_driver_citations_exp_data[0][i] == citation_records[0][i]


def test_read_person_info_data_passenger(crash_data_reader, acrs_person_info_table, acrs_person_table, cursor):  # pylint:disable=unused-argument
    """Tests the ordereddict from the PASSENGERs tag"""
    assert crash_data_reader._read_person_info_data(  # pylint:disable=protected-access
        person_dict=constants_test_data.person_info_pass_input_data.get('PASSENGERs'), tag='PASSENGER')

    cursor.execute('SELECT * FROM acrs_test_person_info')
    records = cursor.fetchall()

    cursor.execute('SELECT * FROM acrs_test_person')
    person_records = cursor.fetchall()

    assert len(records) == len(constants_test_data.person_info_pass_exp_data)
    assert len(person_records) == len(constants_test_data.person_info_person_pass_exp_data)

    for i, _ in enumerate(records[0]):
        assert constants_test_data.person_info_pass_exp_data[0][i] == records[0][i]

    for i, _ in enumerate(person_records):
        assert len(constants_test_data.person_info_person_pass_exp_data[i]) == len(person_records[i])
        for j, _ in enumerate(person_records[i]):
            assert constants_test_data.person_info_person_pass_exp_data[i][j] == person_records[i][j]


def test_read_person_info_data_passenger_multiple(crash_data_reader, acrs_person_info_table, acrs_person_table,  # pylint:disable=unused-argument
                                                  cursor):
    """Tests the OrderedDict that comes from the PASSENGERs tag. This tests the multiple """
    assert crash_data_reader._read_person_info_data(  # pylint:disable=protected-access
        person_dict=constants_test_data.person_info_pass_mult_input_data.get('PASSENGERs'), tag='PASSENGER')

    cursor.execute('SELECT * FROM acrs_test_person_info')
    records = cursor.fetchall()

    cursor.execute('SELECT * FROM acrs_test_person')
    person_records = cursor.fetchall()

    assert len(records) == len(constants_test_data.person_info_pass_mult_exp_data)
    assert len(person_records) == len(constants_test_data.person_info_person_mult_pass_exp_data)

    for i, _ in enumerate(records[0]):
        assert constants_test_data.person_info_pass_mult_exp_data[0][i] == records[0][i]

    for i, _ in enumerate(person_records):
        assert len(constants_test_data.person_info_person_mult_pass_exp_data[i]) == len(person_records[i])
        for j, _ in enumerate(person_records[i]):
            assert constants_test_data.person_info_person_mult_pass_exp_data[i][j] == person_records[i][j]


def test_read_person_info_data_nonmotorist(crash_data_reader, acrs_person_info_table, acrs_person_table, cursor):  # pylint:disable=unused-argument
    """Tests the ordereddict that comes from the NONMOTORSTs tag"""
    assert crash_data_reader._read_person_info_data(  # pylint:disable=protected-access
        person_dict=constants_test_data.person_info_nonmotorist_input_data.get('NONMOTORISTs'), tag='NONMOTORIST')

    cursor.execute('SELECT * FROM acrs_test_person_info')
    records = cursor.fetchall()

    cursor.execute('SELECT * FROM acrs_test_person')
    person_records = cursor.fetchall()

    assert len(records) == len(constants_test_data.person_info_nonmotorist_exp_data)
    assert len(person_records) == len(constants_test_data.person_info_records_nonmotorist_input_data)

    for i, _ in enumerate(records[0]):
        assert constants_test_data.person_info_nonmotorist_exp_data[0][i] == records[0][i]

    for i, _ in enumerate(person_records):
        assert len(constants_test_data.person_info_records_nonmotorist_input_data[i]) == len(person_records[i])
        for j, _ in enumerate(person_records[i]):
            assert constants_test_data.person_info_records_nonmotorist_input_data[i][j] == person_records[i][j]


def test_read_roadway_data(crash_data_reader, acrs_roadway_table, cursor):  # pylint:disable=unused-argument
    """Tests the ordereddict from ROADWAY tag"""
    assert crash_data_reader._read_roadway_data(  # pylint:disable=protected-access
        roadway_dict=constants_test_data.roadway_input_data)

    cursor.execute('SELECT * FROM acrs_test_roadway')
    records = cursor.fetchall()
    assert len(records) == len(constants_test_data.roadway_exp_data)

    for i, _ in enumerate(records[0]):
        assert constants_test_data.roadway_exp_data[0][i] == records[0][i]


def test_read_towed_vehicle_data(crash_data_reader, acrs_towed_unit_table, cursor):  # pylint:disable=unused-argument
    """Tests the ordereddict from TOWEDUNITs tag"""
    assert crash_data_reader._read_towed_vehicle_data(  # pylint:disable=protected-access
        towed_dict=constants_test_data.towed_input_data.get('TOWEDUNITs'))

    cursor.execute('SELECT * FROM acrs_test_towed_unit')
    records = cursor.fetchall()
    assert len(records) == len(constants_test_data.towed_exp_data)

    for i, _ in enumerate(records[0]):
        assert constants_test_data.towed_exp_data[0][i] == records[0][i]


def test_read_acrs_vehicle_data(crash_data_reader, acrs_vehicles_table, cursor):  # pylint:disable=unused-argument
    """Tests the ordereddict from ACRSVEHICLE"""
    assert crash_data_reader._read_acrs_vehicle_data(  # pylint:disable=protected-access
        vehicle_dict=constants_test_data.vehicle_input_data.get('VEHICLEs'))

    cursor.execute('SELECT * FROM acrs_test_vehicles')
    records = cursor.fetchall()
    assert len(records) == len(constants_test_data.vehicle_exp_data)

    for i, _ in enumerate(records):
        for j, _ in enumerate(records[i]):
            print(constants_test_data.vehicle_exp_data[i][j], records[i][j])
            assert constants_test_data.vehicle_exp_data[i][j] == records[i][j]


def test_read_acrs_vehicle_use_data(crash_data_reader, acrs_vehicle_use_table, cursor):  # pylint:disable=unused-argument
    """Testing the ordereddict contained in VEHICLEUSEs"""
    assert crash_data_reader._read_acrs_vehicle_use_data(  # pylint:disable=protected-access
        vehicleuse_dict=constants_test_data.vehicle_use_input_data.get(
            'VEHICLEUSEs'))

    cursor.execute('SELECT * FROM acrs_test_vehicle_uses')
    records = cursor.fetchall()
    assert len(records) == len(constants_test_data.vehicle_use_exp_data)

    for i, _ in enumerate(records[0]):
        assert constants_test_data.vehicle_use_exp_data[0][i] == records[0][i]


def test_read_witness_data(crash_data_reader, acrs_witnesses_table, acrs_person_table, cursor):  # pylint:disable=unused-argument
    """Testing the ordereddict contained in WITNESSes"""
    assert crash_data_reader._read_witness_data(  # pylint:disable=protected-access
        witness_dict=constants_test_data.witness_input_data.get('WITNESSes'))

    cursor.execute('SELECT * FROM acrs_test_witnesses')
    records = cursor.fetchall()

    cursor.execute('SELECT * FROM acrs_test_person')
    person_records = cursor.fetchall()

    assert len(records) == len(constants_test_data.witness_exp_data)
    assert len(person_records) == len(constants_test_data.witness_records_expt_data)

    for i, _ in enumerate(records[0]):
        assert constants_test_data.witness_exp_data[0][i] == records[0][i]

    for i, _ in enumerate(person_records):
        for j, _ in enumerate(person_records[i]):
            assert constants_test_data.witness_records_expt_data[i][j] == person_records[i][j]


def test_is_nil(crash_data_reader):
    """Testing the results of is_dict_nil"""
    assert crash_data_reader.is_element_nil(OrderedDict([('@i:nil', 'true')]))
    assert crash_data_reader.is_element_nil(None)


def test_convert_to_date(crash_data_reader):
    """Testing the results of _convert_to_date"""
    assert crash_data_reader._convert_to_date(  # pylint:disable=protected-access
        '2020-11-28T21:59:53.0000000') == '2020-11-28'


def test_convert_to_bool(crash_data_reader):
    """Testing the results of _convert_to_bool"""
    assert not crash_data_reader._convert_to_bool('N')  # pylint:disable=protected-access
    assert crash_data_reader._convert_to_bool('Y')  # pylint:disable=protected-access
    assert crash_data_reader._convert_to_bool('U') is None  # pylint:disable=protected-access

    with pytest.raises(AssertionError):
        crash_data_reader._convert_to_bool('X')  # pylint:disable=protected-access


def test_validate_uniqueidentifier(crash_data_reader):
    """Testing the results of _validate_uniqueidentifier"""
    uid = '9316ed0c-cddf-481c-94ee-4662e0b77384'
    assert crash_data_reader._validate_uniqueidentifier(uid) == uid  # pylint:disable=protected-access
    assert crash_data_reader._validate_uniqueidentifier('') is None  # pylint:disable=protected-access


def test_get_single_attr(crash_data_reader):
    """Testing the results of get_single_attr"""
    assert crash_data_reader.get_single_attr('STRNODE', constants_test_data.single_attr_input_data) == 'STRDATA'
    assert crash_data_reader.get_single_attr('NONENODE', constants_test_data.single_attr_input_data) is None
    assert crash_data_reader.get_single_attr('NILNODE', constants_test_data.single_attr_input_data) is None

    with pytest.raises(AssertionError):
        crash_data_reader.get_single_attr('MULTIPLENODE', constants_test_data.single_attr_input_data)


def test_get_multiple_attr_single(crash_data_reader):
    """Testing the results of get_multiple_attr with a single element in the source"""
    actual = crash_data_reader.get_multiple_attr('TOPELEMENT',
                                                 constants_test_data.multi_attr_single_input_data.get(
                                                     'TOPELEMENTs'))
    assert len(actual) == len(constants_test_data.multi_attr_single_exp_data)
    assert len(actual[0]) == len(constants_test_data.multi_attr_single_exp_data[0])

    assert actual[0].pop('ELEMENT1') == '01'
    assert actual[0].pop('ELEMENT2') == '02'

    # make sure its empty
    assert not actual[0]


def test_get_multiple_attr_mulitple(crash_data_reader):
    """Testing the results of get_multiple_attr with multiple elements in the source"""

    actual = crash_data_reader.get_multiple_attr('TOPELEMENT', constants_test_data.multi_attr_multi_input_data.get(
        'TOPELEMENTs'))
    assert len(actual) == len(constants_test_data.multi_attr_multi_exp_data)

    assert len(actual[0]) == len(constants_test_data.multi_attr_multi_exp_data[0])
    assert actual[0].pop('ELEMENT1') == '01'
    assert actual[0].pop('ELEMENT2') == '02'

    assert len(actual[1]) == len(constants_test_data.multi_attr_multi_exp_data[1])
    assert actual[1].pop('ELEMENT1') == '03'
    assert actual[1].pop('ELEMENT2') == '04'

    # make sure they are empty
    assert not actual[0]
    assert not actual[1]
