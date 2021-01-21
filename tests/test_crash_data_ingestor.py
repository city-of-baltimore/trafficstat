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

from trafficstat.crash_data_ingestor import CrashDataReader
from trafficstat.crash_data_schema import Approval, Base, Crash, Circumstance, CitationCode, CommercialVehicle, \
    CrashDiagram, DamagedArea, Ems, Event, PdfReport, Person, PersonInfo, Roadway, TowedUnit, Vehicle, VehicleUse, \
    Witness
from . import constants_test_data


def check_database_rows(session, model: DeclarativeMeta, expected_rows: int):
    """Does a simple check that the number of rows in the table is what we expect"""
    qry = session.query(model).filter_by()
    assert qry.count() == expected_rows


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
def test_read_crash_data_file(crash_data_reader):  # pylint:disable=too-many-statements
    """Rudamentary check that there are the right number of records after a few xml files are read in"""
    with Session(crash_data_reader.engine) as session:
        # test with witness and a nonmotorist, which also moves the file to a processed dir
        if os.path.exists('.processed'):
            shutil.rmtree('.processed')
        shutil.copyfile(os.path.join('tests', 'testfiles', 'BALTIMORE_acrs_ADJ5220059-witness-nonmotorist.xml'),
                        os.path.join('tests', 'testfiles', 'BALTIMORE_acrs_ADJ5220059-witness-nonmotorist-copy.xml'))

        crash_data_reader.read_crash_data(
            file_name=os.path.join('tests', 'testfiles', 'BALTIMORE_acrs_ADJ5220059-witness-nonmotorist-copy.xml'),
            copy=True)

        assert os.path.exists('.processed/BALTIMORE_acrs_ADJ5220059-witness-nonmotorist-copy.xml')

        check_single_entries(session, 1)
        check_database_rows(session, Circumstance, 3)
        check_database_rows(session, CitationCode, 0)
        check_database_rows(session, CommercialVehicle, 1)
        check_database_rows(session, DamagedArea, 1)
        check_database_rows(session, Ems, 1)
        check_database_rows(session, Event, 1)
        check_database_rows(session, Person, 5)
        check_database_rows(session, PersonInfo, 2)
        check_database_rows(session, TowedUnit, 1)
        check_database_rows(session, Vehicle, 1)
        check_database_rows(session, VehicleUse, 1)
        check_database_rows(session, Witness, 1)

        # do the same test to make sure primary keys are handled properly
        shutil.copyfile(os.path.join('tests', 'testfiles', 'BALTIMORE_acrs_ADJ5220059-witness-nonmotorist.xml'),
                        os.path.join('tests', 'testfiles', 'BALTIMORE_acrs_ADJ5220059-witness-nonmotorist-copy.xml'))
        crash_data_reader.read_crash_data(
            file_name=os.path.join('tests', 'testfiles', 'BALTIMORE_acrs_ADJ5220059-witness-nonmotorist-copy.xml'),
            copy=True)
        assert os.path.exists('.processed/BALTIMORE_acrs_ADJ5220059-witness-nonmotorist-copy.xml_1')

        check_single_entries(session, 1)
        check_database_rows(session, Circumstance, 3)
        check_database_rows(session, CitationCode, 0)
        check_database_rows(session, CommercialVehicle, 1)
        check_database_rows(session, DamagedArea, 1)
        check_database_rows(session, Ems, 1)
        check_database_rows(session, Event, 1)
        check_database_rows(session, Person, 5)
        check_database_rows(session, PersonInfo, 2)
        check_database_rows(session, TowedUnit, 1)
        check_database_rows(session, Vehicle, 1)
        check_database_rows(session, VehicleUse, 1)
        check_database_rows(session, Witness, 1)

        # File with citation codes
        crash_data_reader.read_crash_data(
            file_name=os.path.join('tests', 'testfiles', 'BALTIMORE_acrs_ADJ47600BL-citationcodes.xml'),
            copy=False)
        check_single_entries(session, 2)
        check_database_rows(session, Circumstance, 5)
        check_database_rows(session, CitationCode, 1)
        check_database_rows(session, CommercialVehicle, 1)
        check_database_rows(session, DamagedArea, 5)
        check_database_rows(session, Ems, 1)
        check_database_rows(session, Event, 1)
        check_database_rows(session, Person, 10)
        check_database_rows(session, PersonInfo, 5)
        check_database_rows(session, TowedUnit, 1)
        check_database_rows(session, Vehicle, 3)
        check_database_rows(session, VehicleUse, 3)
        check_database_rows(session, Witness, 1)

        # File with passenger information
        crash_data_reader.read_crash_data(
            file_name=os.path.join('tests', 'testfiles', 'BALTIMORE_acrs_ADJ2200021-passenger.xml'),
            copy=False)
        check_single_entries(session, 3)
        check_database_rows(session, Circumstance, 7)
        check_database_rows(session, CitationCode, 1)
        check_database_rows(session, CommercialVehicle, 1)
        check_database_rows(session, DamagedArea, 9)
        check_database_rows(session, Ems, 1)
        check_database_rows(session, Event, 1)
        check_database_rows(session, Person, 18)
        check_database_rows(session, PersonInfo, 12)
        check_database_rows(session, TowedUnit, 1)
        check_database_rows(session, Vehicle, 5)
        check_database_rows(session, VehicleUse, 5)
        check_database_rows(session, Witness, 1)

        # File with multiple vehicles
        crash_data_reader.read_crash_data(
            file_name=os.path.join('tests', 'testfiles', 'BALTIMORE_acrs_ADJ8750031-multiplevehicles.xml'),
            copy=False)
        check_single_entries(session, 4)
        check_database_rows(session, Circumstance, 13)
        check_database_rows(session, CitationCode, 1)
        check_database_rows(session, CommercialVehicle, 1)
        check_database_rows(session, DamagedArea, 13)
        check_database_rows(session, Ems, 1)
        check_database_rows(session, Event, 3)
        check_database_rows(session, Person, 21)
        check_database_rows(session, PersonInfo, 14)
        check_database_rows(session, TowedUnit, 1)
        check_database_rows(session, Vehicle, 7)
        check_database_rows(session, VehicleUse, 7)
        check_database_rows(session, Witness, 1)

        # File with witnesses
        crash_data_reader.read_crash_data(
            file_name=os.path.join('tests', 'testfiles', 'BALTIMORE_acrs_ADK378000C-witnesses.xml'),
            copy=False)
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
def test_read_crash_data_dir(crash_data_reader):  # pylint:disable=too-many-statements
    """Rudamentary check that there are the right number of records after a few xml files are read in"""
    with tempfile.TemporaryDirectory() as tmpdirname:
        shutil.copyfile(os.path.join('tests', 'testfiles', 'BALTIMORE_acrs_ADJ5220059-witness-nonmotorist.xml'),
                        os.path.join(tmpdirname, 'BALTIMORE_acrs_ADJ5220059-witness-nonmotorist.xml'))
        shutil.copyfile(os.path.join('tests', 'testfiles', 'BALTIMORE_acrs_ADJ2200021-passenger.xml'),
                        os.path.join(tmpdirname, 'BALTIMORE_acrs_ADJ2200021-passenger.xml'))
        shutil.copyfile(os.path.join('tests', 'testfiles', 'BALTIMORE_acrs_ADJ47600BL-citationcodes.xml'),
                        os.path.join(tmpdirname, 'BALTIMORE_acrs_ADJ47600BL-citationcodes.xml'))
        shutil.copyfile(os.path.join('tests', 'testfiles', 'BALTIMORE_acrs_ADJ8750031-multiplevehicles.xml'),
                        os.path.join(tmpdirname, 'BALTIMORE_acrs_ADJ8750031-multiplevehicles.xml'))
        shutil.copyfile(os.path.join('tests', 'testfiles', 'BALTIMORE_acrs_ADK378000C-witnesses.xml'),
                        os.path.join(tmpdirname, 'BALTIMORE_acrs_ADK378000C-witnesses.xml'))

        if os.path.exists('.processed'):
            shutil.rmtree('.processed')

        with Session(crash_data_reader.engine) as session:
            crash_data_reader.read_crash_data(dir_name=tmpdirname, copy=False)
            assert not os.path.exists(
                os.path.join(tmpdirname, '.processed', 'BALTIMORE_acrs_ADJ5220059-witness-nonmotorist.xml'))
            assert not os.path.exists(
                os.path.join(tmpdirname, '.processed', 'BALTIMORE_acrs_ADJ2200021-passenger.xml'))
            assert not os.path.exists(
                os.path.join(tmpdirname, '.processed', 'BALTIMORE_acrs_ADJ47600BL-citationcodes.xml'))
            assert not os.path.exists(
                os.path.join(tmpdirname, '.processed', 'BALTIMORE_acrs_ADJ8750031-multiplevehicles.xml'))
            assert not os.path.exists(
                os.path.join(tmpdirname, '.processed', 'BALTIMORE_acrs_ADK378000C-witnesses.xml'))

            crash_data_reader.read_crash_data(dir_name=tmpdirname, copy=True)

            assert os.path.exists(
                os.path.join(tmpdirname, '.processed', 'BALTIMORE_acrs_ADJ5220059-witness-nonmotorist.xml'))
            assert os.path.exists(
                os.path.join(tmpdirname, '.processed', 'BALTIMORE_acrs_ADJ2200021-passenger.xml'))
            assert os.path.exists(
                os.path.join(tmpdirname, '.processed', 'BALTIMORE_acrs_ADJ47600BL-citationcodes.xml'))
            assert os.path.exists(
                os.path.join(tmpdirname, '.processed', 'BALTIMORE_acrs_ADJ8750031-multiplevehicles.xml'))
            assert os.path.exists(
                os.path.join(tmpdirname, '.processed', 'BALTIMORE_acrs_ADK378000C-witnesses.xml'))

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
def test_read_crash_data(crash_data_reader):
    """Testing the elements in the REPORTS tag"""
    crash_data_reader._read_main_crash_data(crash_dict=constants_test_data.crash_test_input_data)
    verify_results(Crash, crash_data_reader.engine, constants_test_data.crash_test_output_data)


@clean(Approval)
def test_read_approval_data(crash_data_reader):
    """Testing the elements in the APPROVALDATA tag"""
    crash_data_reader._read_approval_data(approval_dict=constants_test_data.approval_input_data)
    verify_results(Approval, crash_data_reader.engine, constants_test_data.approval_output_data)


@clean(Circumstance)
def test_read_circumstance_data(crash_data_reader):
    """Testing the elements in the CIRCUMSTANCES tag"""
    crash_data_reader._read_circumstance_data(circumstance_dict=constants_test_data.circum_input_data)
    verify_results(Circumstance, crash_data_reader.engine, constants_test_data.circum_output_data)


@clean(CitationCode)
def test_read_citation_data(crash_data_reader):
    """Testing the elements in the CITATIONCODES tag"""
    crash_data_reader._read_citation_data(citation_dict=constants_test_data.citation_input_data)
    verify_results(CitationCode, crash_data_reader.engine, constants_test_data.citation_output_data)


@clean(CrashDiagram)
def test_read_crash_diagrams_data(crash_data_reader):
    """Testing the elements in the DIAGRAM tag"""
    crash_data_reader._read_crash_diagrams_data(crash_diagram_dict=constants_test_data.crash_input_data)
    verify_results(CrashDiagram, crash_data_reader.engine, constants_test_data.crash_output_data)


@clean(CommercialVehicle)
def test_read_commercial_vehicle_data(crash_data_reader):
    """Testing the OrderedDict from the COMMERCIALVEHICLE tag"""
    crash_data_reader._read_commercial_vehicle_data(commvehicle_dict=constants_test_data.commveh_input_data)
    verify_results(CommercialVehicle, crash_data_reader.engine, constants_test_data.commveh_output_data)


@clean(DamagedArea)
def test_read_damaged_areas_data(crash_data_reader):
    """Testing the OrderedDict from the DAMAGEDAREAs tag"""
    crash_data_reader._read_damaged_areas_data(damaged_dict=constants_test_data.damaged_input_data)
    verify_results(DamagedArea, crash_data_reader.engine, constants_test_data.damaged_output_data)


@clean(Ems)
def test_read_ems_data(crash_data_reader):
    """Testing the OrderedDict from the EMSes tag"""
    crash_data_reader._read_ems_data(ems_dict=constants_test_data.ems_input_data)
    verify_results(Ems, crash_data_reader.engine, constants_test_data.ems_output_data)


@clean(Event)
def test_read_event_data(crash_data_reader):
    """Testing the OrderedDict from the EVENTS tag"""
    crash_data_reader._read_event_data(event_dict=constants_test_data.event_input_data)
    verify_results(Event, crash_data_reader.engine, constants_test_data.event_output_data)


@clean(PdfReport)
def test_read_pdf_data(crash_data_reader):
    """Testing the OrderedDict from the PDFREPORTs tag"""
    crash_data_reader._read_pdf_data(pdfreport_dict=constants_test_data.pdf_input_data)
    verify_results(PdfReport, crash_data_reader.engine, constants_test_data.pdf_output_data)


@clean(Person)
def test_read_acrs_person_data(crash_data_reader):
    """Tests the OrderedDict from the PERSON/OWNER tag"""
    crash_data_reader._read_acrs_person_data(person_dict=constants_test_data.person_input_data)
    verify_results(Person, crash_data_reader.engine, constants_test_data.person_output_data)


@clean(PersonInfo)
def test_read_person_info_data_driver(crash_data_reader):
    """Tests the OrderedDict from the DRIVERs tag"""
    crash_data_reader._read_person_info_data(person_dict=constants_test_data.person_info_driver_input_data)
    verify_results(PersonInfo, crash_data_reader.engine, constants_test_data.person_info_driver_output_data)


@clean(PersonInfo)
def test_read_person_info_data_passenger(crash_data_reader):
    """Tests the OrderedDict from the PASSENGERs tag"""
    crash_data_reader._read_person_info_data(person_dict=constants_test_data.person_info_pass_input_data)
    verify_results(PersonInfo, crash_data_reader.engine, constants_test_data.person_info_pass_output_data)


@clean(PersonInfo)
def test_read_person_info_data_passenger_multiple(crash_data_reader):
    """Tests the OrderedDict that comes from the PASSENGERs tag. This tests the multiple """
    crash_data_reader._read_person_info_data(person_dict=constants_test_data.person_info_pass_mult_input_data)
    verify_results(PersonInfo, crash_data_reader.engine, constants_test_data.person_info_pass_mult_output_data)


@clean(PersonInfo)
def test_read_person_info_data_nonmotorist(crash_data_reader):
    """Tests the OrderedDict that comes from the NONMOTORSTs tag"""
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
    crash_data_reader._read_towed_vehicle_data(towed_dict=constants_test_data.towed_input_data)
    verify_results(TowedUnit, crash_data_reader.engine, constants_test_data.towed_output_data)


@clean(Vehicle)
def test_read_acrs_vehicle_data(crash_data_reader):
    """Tests the OrderedDict from ACRSVEHICLE"""
    crash_data_reader._read_acrs_vehicle_data(vehicle_dict=constants_test_data.vehicle_input_data)
    verify_results(Vehicle, crash_data_reader.engine, constants_test_data.vehicle_output_data)


@clean(VehicleUse)
def test_read_acrs_vehicle_use_data(crash_data_reader):
    """Testing the OrderedDict contained in VEHICLEUSEs"""
    crash_data_reader._read_acrs_vehicle_use_data(vehicleuse_dict=constants_test_data.vehicle_use_input_data)
    verify_results(VehicleUse, crash_data_reader.engine, constants_test_data.vehicle_use_output_data)


@clean(Witness)
def test_read_witness_data(crash_data_reader):
    """Testing the OrderedDict contained in WITNESSes"""
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


def test_file_move(crash_data_reader):
    """Test _file_move"""
    file = tempfile.NamedTemporaryFile(delete=False)
    file.close()
    tmp_file_name = "{}X".format(file.name)  # temp filename so we can copy the original for each iteration
    with tempfile.TemporaryDirectory() as temp_dir:
        for _ in range(6):
            shutil.copyfile(file.name, tmp_file_name)
            assert crash_data_reader._file_move(tmp_file_name, temp_dir)

        shutil.copyfile(file.name, tmp_file_name)
        assert not crash_data_reader._file_move(tmp_file_name, temp_dir)

        assert os.path.exists(os.path.join(temp_dir, os.path.basename(tmp_file_name)))
        assert os.path.exists(os.path.join(temp_dir, '{}_1'.format(os.path.basename(tmp_file_name))))
        assert os.path.exists(os.path.join(temp_dir, '{}_2'.format(os.path.basename(tmp_file_name))))
        assert os.path.exists(os.path.join(temp_dir, '{}_3'.format(os.path.basename(tmp_file_name))))
        assert os.path.exists(os.path.join(temp_dir, '{}_4'.format(os.path.basename(tmp_file_name))))
        assert os.path.exists(os.path.join(temp_dir, '{}_5'.format(os.path.basename(tmp_file_name))))
        assert not os.path.exists(os.path.join(temp_dir, '{}_6'.format(os.path.basename(tmp_file_name))))
