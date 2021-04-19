"""Pytest suite for src/crash_data_ingestor"""
# pylint:disable=protected-access
# pylint:disable=R0801 ; copied code
import os
import shutil
import tempfile
from collections import OrderedDict
from typing import Dict, List, Tuple, Union

import decorator
import pytest
from sqlalchemy import engine as enginetype, inspect  # type: ignore
from sqlalchemy.ext.declarative import DeclarativeMeta  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from trafficstat.crash_data_ingester import CrashDataReader
from trafficstat.crash_data_schema import Approval, Base, Crash, Circumstance, CitationCode, CommercialVehicle, \
    CrashDiagram, DamagedArea, Ems, Event, PdfReport, Person, PersonInfo, Roadway, TowedUnit, Vehicle, VehicleUse, \
    Witness
from . import constants_test_data


def check_database_rows(session, model: DeclarativeMeta, expected_rows: int):
    """Does a simple check that the number of rows in the table is what we expect"""
    qry = session.query(model).filter_by()
    assert qry.count() == expected_rows, "Expected database {} to have {} rows. Actual: {}".format(
        model.__tablename__, expected_rows, qry.count()
    )


def clean(model: Union[DeclarativeMeta, Tuple[DeclarativeMeta]]):
    """Decorator that deletes all rows in the table referenced in the model. Expects the first arg of the function to
    be decorated is a CrashDataReader pytest fixture"""

    def _clean(func):
        def wrapper(_func, *args, **kwargs):
            engine = args[0].engine
            _model = (model,) if not isinstance(model, tuple) else model

            with Session(engine) as session:
                for mod in _model:
                    session.query(mod).delete()
                session.commit()
            return _func(*args, **kwargs)

        return decorator.decorator(wrapper, func)

    return _clean


def verify_results(model: Base, engine: enginetype, expected: List[Dict]) -> None:
    """
    Does verification on the values in the database after a test inserts data
    :param model: The ORM model to query
    :param engine: Sqlalchemy engine to use
    :param expected: The data that was inserted into the database
    """
    with Session(engine) as session:
        primary_keys = [x.key for x in inspect(model).primary_key]
        actual = session.query(model).filter_by()

        # Verify the number of results
        assert actual.count() == len(expected)

        # Verify that all of the expected columns are in the results
        exp_cols = [x for x in expected[0].keys() if not isinstance(x, OrderedDict) and
                    not CrashDataReader.is_element_nil(x)]
        act_cols = actual.column_descriptions[0]['type'].__table__.columns.keys()
        assert all(x in act_cols for x in exp_cols), \
            "All expected columns were not in the results.\nExpected: {}\nActual: {}\n".format(exp_cols, act_cols)

        for exp in expected:
            args = {}
            for primary_key in primary_keys:
                args[primary_key] = exp[primary_key]

            act = actual.filter_by(**args)
            assert act.count() == 1  # if its a primary key, there should be exactly one result
            for col in exp_cols:
                exp_val = exp[col]
                assert act[0].__dict__[col] == exp_val, "Failed on column {}\nExpected: {}\nActual: {}".format(
                    col, exp_val, act[0].__dict__[col])


def check_single_entries(_session, i, checks=None):
    """Helper for the test_read_crash_data_* tests to check the tables that should all have i entries per XML"""
    if checks is None:
        checks = [Approval, CrashDiagram, Crash, PdfReport, Roadway]
    for model in checks:
        check_database_rows(_session, model, i)


@clean((Approval, Crash, Circumstance, CitationCode, CommercialVehicle, CrashDiagram, DamagedArea, Ems, Event,
        PdfReport, Person, PersonInfo, Roadway, TowedUnit, Vehicle, VehicleUse, Witness))
def test_read_crash_data_files_by_dir(crash_data_reader, tmpdir):
    """Reads in all files in the testfiles dir to make sure they are properly processed"""
    expected_vals_accumulator = {
        'Singles': 13,
        'Circumstance': 40,
        'CitationCode': 6,
        'CommercialVehicle': 3,
        'DamagedArea': 47,
        'Ems': 6,
        'Event': 15,
        'Person': 51,
        'PersonInfo': 30,
        'TowedUnit': 3,
        'Vehicle': 22,
        'VehicleUse': 22,
        'Witness': 3,
    }

    def check():
        check_single_entries(session, expected_vals_accumulator['Singles'])
        check_database_rows(session, Circumstance, expected_vals_accumulator['Circumstance'])
        check_database_rows(session, CitationCode, expected_vals_accumulator['CitationCode'])
        check_database_rows(session, CommercialVehicle, expected_vals_accumulator['CommercialVehicle'])
        check_database_rows(session, DamagedArea, expected_vals_accumulator['DamagedArea'])
        check_database_rows(session, Ems, expected_vals_accumulator['Ems'])
        check_database_rows(session, Event, expected_vals_accumulator['Event'])
        check_database_rows(session, Person, expected_vals_accumulator['Person'])
        check_database_rows(session, PersonInfo, expected_vals_accumulator['PersonInfo'])
        check_database_rows(session, TowedUnit, expected_vals_accumulator['TowedUnit'])
        check_database_rows(session, Vehicle, expected_vals_accumulator['Vehicle'])
        check_database_rows(session, VehicleUse, expected_vals_accumulator['VehicleUse'])
        check_database_rows(session, Witness, expected_vals_accumulator['Witness'])

    with Session(crash_data_reader.engine) as session:
        test_dir = os.path.join(tmpdir, 'testfiles')
        shutil.copytree(os.path.join('tests', 'testfiles'), test_dir)

        # test that the non-copy works
        crash_data_reader.read_crash_data(dir_name=test_dir, copy=False)
        assert not os.path.exists(os.path.join(test_dir, '.processed'))
        check()

        # we should be able to do it all over with the same results, and with the files copied
        crash_data_reader.read_crash_data(dir_name=test_dir)
        assert os.path.exists(os.path.join(test_dir, '.processed'))
        check()


@clean((Approval, Crash, Circumstance, CitationCode, CommercialVehicle, CrashDiagram, DamagedArea, Ems, Event,
        PdfReport, Person, PersonInfo, Roadway, TowedUnit, Vehicle, VehicleUse, Witness))
def test_read_crash_data_files_by_file(crash_data_reader, tmpdir):  # pylint:disable=too-many-statements
    """Rudamentary check that there are the right number of records after a few xml files are read in"""
    expected_vals_accumulator = {
        'Singles': 0,
        'Circumstance': 0,
        'CitationCode': 0,
        'CommercialVehicle': 0,
        'DamagedArea': 0,
        'Ems': 0,
        'Event': 0,
        'Person': 0,
        'PersonInfo': 0,
        'TowedUnit': 0,
        'Vehicle': 0,
        'VehicleUse': 0,
        'Witness': 0,
    }

    def check_all_database_rows(src_file_name, expected_vals: dict, accumulate=True):
        tmp_file_name = os.path.join(tmpdir, os.path.basename(src_file_name))
        shutil.copyfile(src_file_name, tmp_file_name)

        crash_data_reader.read_crash_data(file_name=tmp_file_name, copy=True)
        assert os.path.exists(os.path.join(tmpdir, '.processed', os.path.basename(src_file_name)))

        if accumulate:
            expected_vals_accumulator['Singles'] += 1
            expected_vals_accumulator['Circumstance'] += expected_vals['Circumstance']
            expected_vals_accumulator['CitationCode'] += expected_vals['CitationCode']
            expected_vals_accumulator['CommercialVehicle'] += expected_vals['CommercialVehicle']
            expected_vals_accumulator['DamagedArea'] += expected_vals['DamagedArea']
            expected_vals_accumulator['Ems'] += expected_vals['Ems']
            expected_vals_accumulator['Event'] += expected_vals['Event']
            expected_vals_accumulator['Person'] += expected_vals['Person']
            expected_vals_accumulator['PersonInfo'] += expected_vals['PersonInfo']
            expected_vals_accumulator['TowedUnit'] += expected_vals['TowedUnit']
            expected_vals_accumulator['Vehicle'] += expected_vals['Vehicle']
            expected_vals_accumulator['VehicleUse'] += expected_vals['VehicleUse']
            expected_vals_accumulator['Witness'] += expected_vals['Witness']

        check_single_entries(session, expected_vals_accumulator['Singles'])
        check_database_rows(session, Circumstance, expected_vals_accumulator['Circumstance'])
        check_database_rows(session, CitationCode, expected_vals_accumulator['CitationCode'])
        check_database_rows(session, CommercialVehicle, expected_vals_accumulator['CommercialVehicle'])
        check_database_rows(session, DamagedArea, expected_vals_accumulator['DamagedArea'])
        check_database_rows(session, Ems, expected_vals_accumulator['Ems'])
        check_database_rows(session, Event, expected_vals_accumulator['Event'])
        check_database_rows(session, Person, expected_vals_accumulator['Person'])
        check_database_rows(session, PersonInfo, expected_vals_accumulator['PersonInfo'])
        check_database_rows(session, TowedUnit, expected_vals_accumulator['TowedUnit'])
        check_database_rows(session, Vehicle, expected_vals_accumulator['Vehicle'])
        check_database_rows(session, VehicleUse, expected_vals_accumulator['VehicleUse'])
        check_database_rows(session, Witness, expected_vals_accumulator['Witness'])

    with Session(crash_data_reader.engine) as session:

        first = True
        for file_name, exp_vals in constants_test_data.TEST_READ_CRASH_DATA_CONST.items():
            check_all_database_rows(file_name, exp_vals)

            if first:
                # Insert values twice to make sure primary keys work properly on a single run
                check_all_database_rows(file_name, exp_vals, False)
                first = False


@clean((Approval, Crash, Circumstance, CitationCode, CommercialVehicle, CrashDiagram,
        DamagedArea, Ems, Event,
        PdfReport, Person, PersonInfo, Roadway, TowedUnit, Vehicle, VehicleUse, Witness))
def test_read_crash_data_dir(crash_data_reader, tmpdir):  # pylint:disable=too-many-statements
    """Rudamentary check that there are the right number of records after a few xml files are read in"""
    xml_files = [
        'BALTIMORE_acrs_ADJ5220059-witness-nonmotorist.xml',
        'BALTIMORE_acrs_ADJ2200021-passenger.xml',
        'BALTIMORE_acrs_ADJ47600BL-citationcodes.xml',
        'BALTIMORE_acrs_ADJ8750031-multiplevehicles.xml',
        'BALTIMORE_acrs_ADK378000C-witnesses.xml',
        'BALTIMORE_acrs_ADK378000C-witnesses.xml',
        'BALTIMORE_emptyxml.xml'
    ]

    for file in xml_files:
        shutil.copyfile(os.path.join('tests', 'testfiles', file),
                        os.path.join(tmpdir, file))

    with Session(crash_data_reader.engine) as session:
        crash_data_reader.read_crash_data(dir_name=tmpdir, copy=False)
        for file in xml_files:
            assert not os.path.exists(
                os.path.join(tmpdir, '.processed', file))

        crash_data_reader.read_crash_data(dir_name=tmpdir, copy=True)

        for file in xml_files:
            assert os.path.exists(
                os.path.join(tmpdir, '.processed', file))

        check_single_entries(session, 5)
        check_database_rows(session, Circumstance, 15)
        check_database_rows(session, CitationCode, 1)
        check_database_rows(session, CommercialVehicle, 2)
        check_database_rows(session, DamagedArea, 14)
        check_database_rows(session, Ems, 2)
        check_database_rows(session, Event, 4)
        check_database_rows(session, Person, 27)
        check_database_rows(session, PersonInfo, 16)
        check_database_rows(session, TowedUnit, 2)
        check_database_rows(session, Vehicle, 8)
        check_database_rows(session, VehicleUse, 8)
        check_database_rows(session, Witness, 3)


@clean((Approval, Crash, Circumstance, CitationCode, CommercialVehicle, CrashDiagram, DamagedArea, Ems, Event,
        PdfReport, Person, PersonInfo, Roadway, TowedUnit, Vehicle, VehicleUse, Witness))
def test_read_crash_data_file_dne(crash_data_reader):  # pylint:disable=too-many-statements
    """Rudamentary check that there are the right number of records after a few xml files are read in"""
    with Session(crash_data_reader.engine) as session:
        crash_data_reader.read_crash_data(file_name='NONEXISTANT', copy=False)
        check_single_entries(session, 0, [Approval, Crash, Circumstance, CitationCode, CommercialVehicle,
                                          CrashDiagram, DamagedArea, Ems, Event, PdfReport, Person, PersonInfo, Roadway,
                                          TowedUnit, Vehicle, VehicleUse, Witness])


@clean(Crash)
def test_read_crash_data_single(crash_data_reader):
    """Testing the elements in the REPORTS tag"""
    # Dealing with the foreign key requirement
    with Session(crash_data_reader.engine) as session:
        session.add(Roadway(ROADID='9316ed0c-cddf-481c-94ee-4662e0b77384'))
        session.commit()
    crash_data_reader._read_main_crash_data(crash_dict=constants_test_data.crash_test_input_data)
    verify_results(Crash, crash_data_reader.engine, constants_test_data.crash_test_output_data)


@clean(Approval)
def test_read_approval_data(crash_data_reader):
    """Testing the elements in the APPROVALDATA tag"""
    # Dealing with the foreign key requirement
    with Session(crash_data_reader.engine) as session:
        session.add(Crash(REPORTNUMBER='ADD934004Q'))
        session.commit()
    crash_data_reader._read_approval_data(approval_dict=constants_test_data.approval_input_data)
    verify_results(Approval, crash_data_reader.engine, constants_test_data.approval_output_data)


@clean(Circumstance)
def test_read_circumstance_data(crash_data_reader):
    """Testing the elements in the CIRCUMSTANCES tag"""
    # Dealing with the foreign key requirement
    with Session(crash_data_reader.engine) as session:
        session.add_all([
            Crash(REPORTNUMBER='ADD934004Q'),
            Person(PERSONID='6239e4e7-65b8-452a-ba1e-6bc26b8c5cc4'),
            Person(PERSONID='c3e96bdd-5049-426f-b27d-c3bf43b1eeca'),
            Vehicle(VEHICLEID='65cd4028-82ab-401e-a7fa-d392dfb98e03'),
            Vehicle(VEHICLEID='ddd4ed36-cca5-4634-8209-01e38cc13ced')
        ])
        session.commit()
    crash_data_reader._read_circumstance_data(circumstance_dict=constants_test_data.circum_input_data)
    verify_results(Circumstance, crash_data_reader.engine, constants_test_data.circum_output_data)


@clean(CitationCode)
def test_read_citation_data(crash_data_reader):
    """Testing the elements in the CITATIONCODES tag"""
    with Session(crash_data_reader.engine) as session:
        session.add_all([
            Crash(REPORTNUMBER='ADD9340058'),
            Person(PERSONID='6fffe61c-6bec-476a-8a6e-47c52544fb3c')
        ])
        session.commit()
    crash_data_reader._read_citation_data(citation_dict=constants_test_data.citation_input_data)
    verify_results(CitationCode, crash_data_reader.engine, constants_test_data.citation_output_data)


@clean(CrashDiagram)
def test_read_crash_diagrams_data(crash_data_reader):
    """Testing the elements in the DIAGRAM tag"""
    # Dealing with the foreign key requirement
    with Session(crash_data_reader.engine) as session:
        session.add(Crash(REPORTNUMBER='ADD9340058'))
        session.commit()
    crash_data_reader._read_crash_diagrams_data(crash_diagram_dict=constants_test_data.crash_input_data)
    verify_results(CrashDiagram, crash_data_reader.engine, constants_test_data.crash_output_data)


@clean(CommercialVehicle)
def test_read_commercial_vehicle_data(crash_data_reader):
    """Testing the OrderedDict from the COMMERCIALVEHICLE tag"""
    # Dealing with the foreign key requirement
    with Session(crash_data_reader.engine) as session:
        session.add(Vehicle(VEHICLEID='edeaa7cd-06f1-4dde-b318-66a28ec604e0'))
        session.commit()
    crash_data_reader._read_commercial_vehicle_data(commvehicle_dict=constants_test_data.commveh_input_data)
    verify_results(CommercialVehicle, crash_data_reader.engine, constants_test_data.commveh_output_data)


@clean(DamagedArea)
def test_read_damaged_areas_data(crash_data_reader):
    """Testing the OrderedDict from the DAMAGEDAREAs tag"""
    # Dealing with the foreign key requirement
    with Session(crash_data_reader.engine) as session:
        session.add(Vehicle(VEHICLEID='5ce12003-c7aa-43e1-b5e8-4c0e79160a02'))
        session.commit()
    crash_data_reader._read_damaged_areas_data(damaged_dict=constants_test_data.damaged_input_data)
    verify_results(DamagedArea, crash_data_reader.engine, constants_test_data.damaged_output_data)


@clean(Ems)
def test_read_ems_data(crash_data_reader):
    """Testing the OrderedDict from the EMSes tag"""
    # Dealing with the foreign key requirement
    with Session(crash_data_reader.engine) as session:
        session.add(Crash(REPORTNUMBER='ADJ063005D'))
        session.commit()
    crash_data_reader._read_ems_data(ems_dict=constants_test_data.ems_input_data)
    verify_results(Ems, crash_data_reader.engine, constants_test_data.ems_output_data)


@clean(Event)
def test_read_event_data(crash_data_reader):
    """Testing the OrderedDict from the EVENTS tag"""
    # Dealing with the foreign key requirement
    with Session(crash_data_reader.engine) as session:
        session.add(Vehicle(VEHICLEID='5ce12003-c7aa-43e1-b5e8-4c0e79160a02'))
        session.commit()
    crash_data_reader._read_event_data(event_dict=constants_test_data.event_input_data)
    verify_results(Event, crash_data_reader.engine, constants_test_data.event_output_data)


@clean(PdfReport)
def test_read_pdf_data(crash_data_reader):
    """Testing the OrderedDict from the PDFREPORTs tag"""
    # Dealing with the foreign key requirement
    with Session(crash_data_reader.engine) as session:
        session.add(Crash(REPORTNUMBER='ADD9340058'))
        session.commit()
    crash_data_reader._read_pdf_data(pdfreport_dict=constants_test_data.pdf_input_data)
    verify_results(PdfReport, crash_data_reader.engine, constants_test_data.pdf_output_data)


@clean(Person)
def test_read_acrs_person_data(crash_data_reader):
    """Tests the OrderedDict from the PERSON/OWNER tag"""
    # Dealing with the foreign key requirement
    with Session(crash_data_reader.engine) as session:
        session.add(Crash(REPORTNUMBER='ADD9340058'))
        session.commit()
    crash_data_reader._read_acrs_person_data(person_dict=constants_test_data.person_input_data)
    verify_results(Person, crash_data_reader.engine, constants_test_data.person_output_data)


@clean(PersonInfo)
def test_read_person_info_data_driver(crash_data_reader):
    """Tests the OrderedDict from the DRIVERs tag"""
    # Dealing with the foreign key requirement
    with Session(crash_data_reader.engine) as session:
        session.add_all([
            Crash(REPORTNUMBER='ADD9340058'),
            Person(PERSONID='fcd8309c-250a-4fa4-9fdf-d6dafe2c6946'),
            Vehicle(VEHICLEID='5f19b3c5-4e3b-4010-9959-506a84632cdb')
        ])
        session.commit()
    crash_data_reader._read_person_info_data(person_dict=constants_test_data.person_info_driver_input_data)
    verify_results(PersonInfo, crash_data_reader.engine, constants_test_data.person_info_driver_output_data)


@clean(PersonInfo)
def test_read_person_info_data_passenger_single(crash_data_reader):
    """Tests the OrderedDict from the PASSENGERs tag"""
    # Dealing with the foreign key requirement
    with Session(crash_data_reader.engine) as session:
        session.add_all([Crash(REPORTNUMBER='ADD9340058'),
                         Person(PERSONID='fd3dffba-c1c6-41df-9fc5-a45ae4379db1'),
                         Vehicle(VEHICLEID='6dde66e1-433b-4839-9df8-ffb969d35d68')])
        session.commit()

    crash_data_reader._read_person_info_data(person_dict=constants_test_data.person_info_pass_input_data)
    verify_results(PersonInfo, crash_data_reader.engine, constants_test_data.person_info_pass_output_data)


@clean(PersonInfo)
def test_read_person_info_data_passenger_multiple(crash_data_reader):
    """Tests the OrderedDict that comes from the PASSENGERs tag. This tests the multiple """
    # Dealing with the foreign key requirement
    with Session(crash_data_reader.engine) as session:
        session.add_all([
            Crash(REPORTNUMBER='ADD90500BB'),
            Person(PERSONID='3c348c05-c3c1-44fb-840c-dd5c23cd9811'),
            Person(PERSONID='64f9cda0-1477-4cb9-8891-67087d4163bc'),
            Vehicle(VEHICLEID='c783f85b-ac08-4ad4-8493-e211e5d8ec6e')
        ])
        session.commit()
    crash_data_reader._read_person_info_data(person_dict=constants_test_data.person_info_pass_mult_input_data)
    verify_results(PersonInfo, crash_data_reader.engine, constants_test_data.person_info_pass_mult_output_data)


@clean(PersonInfo)
def test_read_person_info_data_nonmotorist(crash_data_reader):
    """Tests the OrderedDict that comes from the NONMOTORSTs tag"""
    # Dealing with the foreign key requirement
    with Session(crash_data_reader.engine) as session:
        session.add_all([
            Crash(REPORTNUMBER='ADD905004N'),
            Person(PERSONID='d18f27b0-d7e3-40de-b778-89f7a88ccd4f')
        ])
        session.commit()
    crash_data_reader._read_person_info_data(person_dict=constants_test_data.person_info_nonmotorist_input_data)
    verify_results(PersonInfo, crash_data_reader.engine, constants_test_data.person_info_nonmotorist_output_data)


@clean(Roadway)
def test_read_roadway_data(crash_data_reader):
    """Tests the OrderedDict from ROADWAY tag"""
    crash_data_reader._read_roadway_data(roadway_dict=constants_test_data.roadway_input_data)
    verify_results(Roadway, crash_data_reader.engine, constants_test_data.roadway_output_data)


@clean(TowedUnit)
def test_read_towed_vehicle_data(crash_data_reader):
    """Tests the OrderedDict from TOWEDUNITs tag"""
    # Dealing with the foreign key requirement
    with Session(crash_data_reader.engine) as session:
        session.add_all([
            Person(PERSONID='0eea2c7f-3f2c-4fd6-abc2-4927605d237a'),
            Vehicle(VEHICLEID='642f511d-fd4b-4daf-a6b8-5418546be524')
        ])
        session.commit()
    crash_data_reader._read_towed_vehicle_data(towed_dict=constants_test_data.towed_input_data)
    verify_results(TowedUnit, crash_data_reader.engine, constants_test_data.towed_output_data)


@clean(Vehicle)
def test_read_acrs_vehicle_data(crash_data_reader):
    """Tests the OrderedDict from ACRSVEHICLE"""
    # Dealing with the foreign key requirement
    with Session(crash_data_reader.engine) as session:
        session.add_all([
            Crash(REPORTNUMBER='ADJ063005D'),
            Person(PERSONID='21732e90-2796-497f-a5c2-5d7877510d4c'),
            Person(PERSONID='d978be20-08c7-4ff3-b2e9-a251047ac3a7')
        ])
        session.commit()
    crash_data_reader._read_acrs_vehicle_data(vehicle_dict=constants_test_data.vehicle_input_data)
    verify_results(Vehicle, crash_data_reader.engine, constants_test_data.vehicle_output_data)


@clean(VehicleUse)
def test_read_acrs_vehicle_use_data(crash_data_reader):
    """Testing the OrderedDict contained in VEHICLEUSEs"""
    # Dealing with the foreign key requirement
    with Session(crash_data_reader.engine) as session:
        session.add(Vehicle(VEHICLEID='5f19b3c5-4e3b-4010-9959-506a84632cdb'))
        session.commit()
    crash_data_reader._read_acrs_vehicle_use_data(vehicleuse_dict=constants_test_data.vehicle_use_input_data)
    verify_results(VehicleUse, crash_data_reader.engine, constants_test_data.vehicle_use_output_data)


@clean(Witness)
def test_read_witness_data(crash_data_reader):
    """Testing the OrderedDict contained in WITNESSes"""
    # Dealing with the foreign key requirement
    with Session(crash_data_reader.engine) as session:
        session.add(Crash(REPORTNUMBER='ADJ956004Z'))
        session.commit()
    crash_data_reader._read_witness_data(witness_dict=constants_test_data.witness_input_data)
    verify_results(Witness, crash_data_reader.engine, constants_test_data.witness_output_data)


def test_is_nil(crash_data_reader):
    """Testing the results of is_dict_nil"""
    assert crash_data_reader.is_element_nil(OrderedDict([('@i:nil', 'true')]))
    assert crash_data_reader.is_element_nil(None)


def test_convert_to_bool(crash_data_reader):
    """Testing the results of _convert_to_bool"""
    assert not crash_data_reader.convert_to_bool('N')
    assert crash_data_reader.convert_to_bool('Y')
    assert crash_data_reader.convert_to_bool('U') is None

    with pytest.raises(AssertionError):
        crash_data_reader.convert_to_bool('X')


def test_validate_uniqueidentifier(crash_data_reader):
    """Testing the results of _validate_uniqueidentifier"""
    uid = '9316ed0c-cddf-481c-94ee-4662e0b77384'
    assert crash_data_reader._validate_uniqueidentifier(uid) == uid
    assert crash_data_reader._validate_uniqueidentifier('') is None


def test_get_single_attr(crash_data_reader):
    """Testing the results of get_single_attr"""
    assert crash_data_reader.get_single_attr('STRNODE', constants_test_data.single_attr_input_data) == 'STRDATA'
    assert crash_data_reader.get_single_attr('NONENODE', constants_test_data.single_attr_input_data) is None
    assert crash_data_reader.get_single_attr('NILNODE', constants_test_data.single_attr_input_data) is None

    with pytest.raises(AssertionError):
        crash_data_reader.get_single_attr('MULTIPLENODE', constants_test_data.single_attr_input_data)


def test_file_move(crash_data_reader, tmpdir):
    """Test _file_move"""
    file = tempfile.NamedTemporaryFile(delete=False)
    file.close()
    tmp_file_name = "{}X".format(file.name)  # temp filename so we can copy the original for each iteration

    for _ in range(6):
        shutil.copyfile(file.name, tmp_file_name)
        assert crash_data_reader._file_move(tmp_file_name, tmpdir)

    shutil.copyfile(file.name, tmp_file_name)
    assert not crash_data_reader._file_move(tmp_file_name, tmpdir)

    assert os.path.exists(os.path.join(tmpdir, os.path.basename(tmp_file_name)))
    assert os.path.exists(os.path.join(tmpdir, '{}_1'.format(os.path.basename(tmp_file_name))))
    assert os.path.exists(os.path.join(tmpdir, '{}_2'.format(os.path.basename(tmp_file_name))))
    assert os.path.exists(os.path.join(tmpdir, '{}_3'.format(os.path.basename(tmp_file_name))))
    assert os.path.exists(os.path.join(tmpdir, '{}_4'.format(os.path.basename(tmp_file_name))))
    assert os.path.exists(os.path.join(tmpdir, '{}_5'.format(os.path.basename(tmp_file_name))))
    assert not os.path.exists(os.path.join(tmpdir, '{}_6'.format(os.path.basename(tmp_file_name))))
