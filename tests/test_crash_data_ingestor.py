"""Pytest suite for src/crash_data_ingestor"""
from collections import OrderedDict

import pytest

from . import constants_test_data


def check_database_rows(cursor, table_name: str, expected_rows: int):
    """Does a simple check that the number of rows in the table is what we expect"""
    cursor.execute('SELECT * FROM {}'.format(table_name))
    records = cursor.fetchall()
    assert len(records) == expected_rows


def test_read_crash_data_file(crash_data_reader, acrs_crashes_table, acrs_approval_table, acrs_circumstances_table,
                              acrs_citation_codes_table, acrs_crash_diagrams_table, acrs_commercial_vehicle_table,
                              acrs_damaged_areas_table, acrs_ems_table, acrs_events_table, acrs_pdf_report_table,
                              acrs_person_table, acrs_person_info_table, acrs_report_docs_table,
                              acrs_report_photos_table, acrs_roadway_table, acrs_towed_unit_table, acrs_vehicles_table,
                              acrs_vehicle_use_table, acrs_witnesses_table, cursor):
    crash_data_reader.read_crash_data('C:/Users/brian.seel/Desktop/tmp/testfiles/BALTIMORE_acrs_ADJ5220059-witness-nonmotorist.xml', '')
    check_database_rows(cursor, 'acrs_test_approval', 1)
    check_database_rows(cursor, 'acrs_test_circumstances', 3)
    check_database_rows(cursor, 'acrs_test_citation_codes', 0)
    check_database_rows(cursor, 'acrs_test_crash_diagrams', 1)
    check_database_rows(cursor, 'acrs_test_crashes', 1)
    check_database_rows(cursor, 'acrs_test_commercial_vehicles', 1)
    check_database_rows(cursor, 'acrs_test_damaged_areas', 1)
    check_database_rows(cursor, 'acrs_test_ems', 1)
    check_database_rows(cursor, 'acrs_test_events', 1)
    check_database_rows(cursor, 'acrs_test_pdf_report', 1)
    check_database_rows(cursor, 'acrs_test_person', 5)
    check_database_rows(cursor, 'acrs_test_person_info', 2)
    check_database_rows(cursor, 'acrs_test_roadway', 1)
    check_database_rows(cursor, 'acrs_test_towed_unit', 1)
    check_database_rows(cursor, 'acrs_test_vehicles', 1)
    check_database_rows(cursor, 'acrs_test_vehicle_uses', 1)
    check_database_rows(cursor, 'acrs_test_witnesses', 1)

    # crash_data_reader.read_crash_data('C:/Users/brian.seel/Desktop/tmp/testfiles/BALTIMORE_acrs_ADK378000C.xml', '')


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
        citation_dict=constants_test_data.citation_input_data)

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
    """Testing the OrderedDict from the EMSes tag"""
    assert crash_data_reader._read_ems_data(  # pylint:disable=protected-access
        ems_dict=constants_test_data.ems_input_data)

    cursor.execute('SELECT * FROM acrs_test_ems')
    records = cursor.fetchall()
    assert len(records) == len(constants_test_data.ems_exp_data)

    for i, _ in enumerate(records[0]):
        assert constants_test_data.ems_exp_data[0][i] == records[0][i]


def test_read_event_data(crash_data_reader, acrs_events_table, cursor):  # pylint:disable=unused-argument
    """Testing the OrderedDict from the EVENTS tag"""
    assert crash_data_reader._read_event_data(  # pylint:disable=protected-access
        event_dict=constants_test_data.event_input_data)

    cursor.execute('SELECT * FROM acrs_test_events')
    records = cursor.fetchall()
    assert len(records) == len(constants_test_data.event_exp_data)

    for i, _ in enumerate(records[0]):
        assert constants_test_data.event_exp_data[0][i] == records[0][i]


def test_read_pdf_data(crash_data_reader, acrs_pdf_report_table, cursor):  # pylint:disable=unused-argument
    """Testing the OrderedDict from the PDFREPORTs tag"""
    assert crash_data_reader._read_pdf_data(  # pylint:disable=protected-access
        pdfreport_dict=constants_test_data.pdf_input_data)

    cursor.execute('SELECT * FROM acrs_test_pdf_report')
    records = cursor.fetchall()
    assert len(records) == len(constants_test_data.pdf_exp_data)

    for i, _ in enumerate(records[0]):
        assert constants_test_data.pdf_exp_data[0][i] == records[0][i]


def test_read_acrs_person_data(crash_data_reader, acrs_person_table, acrs_citation_codes_table, cursor):  # pylint:disable=unused-argument
    """Tests the OrderedDict from the PERSON/OWNER tag"""
    assert crash_data_reader._read_acrs_person_data(person_dict=constants_test_data.person_input_data)  # pylint:disable=protected-access

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
    """Tests the OrderedDict from the DRIVERs tag"""
    assert crash_data_reader._read_person_info_data(person_dict=constants_test_data.person_info_driver_input_data)  # pylint:disable=protected-access

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
    """Tests the OrderedDict from the PASSENGERs tag"""
    assert crash_data_reader._read_person_info_data(person_dict=constants_test_data.person_info_pass_input_data)  # pylint:disable=protected-access

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
    assert crash_data_reader._read_person_info_data(person_dict=constants_test_data.person_info_pass_mult_input_data)  # pylint:disable=protected-access

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
    """Tests the OrderedDict that comes from the NONMOTORSTs tag"""
    assert crash_data_reader._read_person_info_data(person_dict=constants_test_data.person_info_nonmotorist_input_data)  # pylint:disable=protected-access

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
    """Tests the OrderedDict from ROADWAY tag"""
    assert crash_data_reader._read_roadway_data(  # pylint:disable=protected-access
        roadway_dict=constants_test_data.roadway_input_data)

    cursor.execute('SELECT * FROM acrs_test_roadway')
    records = cursor.fetchall()
    assert len(records) == len(constants_test_data.roadway_exp_data)

    for i, _ in enumerate(records[0]):
        assert constants_test_data.roadway_exp_data[0][i] == records[0][i]


def test_read_towed_vehicle_data(crash_data_reader, acrs_towed_unit_table, cursor):  # pylint:disable=unused-argument
    """Tests the OrderedDict from TOWEDUNITs tag"""
    assert crash_data_reader._read_towed_vehicle_data(  # pylint:disable=protected-access
        towed_dict=constants_test_data.towed_input_data)

    cursor.execute('SELECT * FROM acrs_test_towed_unit')
    records = cursor.fetchall()
    assert len(records) == len(constants_test_data.towed_exp_data)

    for i, _ in enumerate(records[0]):
        assert constants_test_data.towed_exp_data[0][i] == records[0][i]


def test_read_acrs_vehicle_data(crash_data_reader, acrs_vehicles_table, cursor):  # pylint:disable=unused-argument
    """Tests the OrderedDict from ACRSVEHICLE"""
    assert crash_data_reader._read_acrs_vehicle_data(  # pylint:disable=protected-access
        vehicle_dict=constants_test_data.vehicle_input_data)

    cursor.execute('SELECT * FROM acrs_test_vehicles')
    records = cursor.fetchall()
    assert len(records) == len(constants_test_data.vehicle_exp_data)

    for i, _ in enumerate(records):
        for j, _ in enumerate(records[i]):
            print(constants_test_data.vehicle_exp_data[i][j], records[i][j])
            assert constants_test_data.vehicle_exp_data[i][j] == records[i][j]


def test_read_acrs_vehicle_use_data(crash_data_reader, acrs_vehicle_use_table, cursor):  # pylint:disable=unused-argument
    """Testing the OrderedDict contained in VEHICLEUSEs"""
    assert crash_data_reader._read_acrs_vehicle_use_data(  # pylint:disable=protected-access
        vehicleuse_dict=constants_test_data.vehicle_use_input_data)

    cursor.execute('SELECT * FROM acrs_test_vehicle_uses')
    records = cursor.fetchall()
    assert len(records) == len(constants_test_data.vehicle_use_exp_data)

    for i, _ in enumerate(records[0]):
        assert constants_test_data.vehicle_use_exp_data[0][i] == records[0][i]


def test_read_witness_data(crash_data_reader, acrs_witnesses_table, acrs_person_table, cursor):  # pylint:disable=unused-argument
    """Testing the OrderedDict contained in WITNESSes"""
    assert crash_data_reader._read_witness_data(  # pylint:disable=protected-access
        witness_dict=constants_test_data.witness_input_data)

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
