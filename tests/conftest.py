"""Pytest directory-specific hook implementations"""
import tempfile
import pytest

from sqlalchemy import create_engine   # type: ignore

from trafficstat.crash_data_ingestor import CrashDataReader
from trafficstat.ms2generator import WorksheetMaker
from trafficstat.ms2generator_schema import Base


@pytest.fixture(name='crash_data_reader')
def crash_data_reader_fixture():
    """Fixture for the CrashDataReader class"""
    with tempfile.TemporaryFile() as tmpfile:
        yield CrashDataReader(conn_str='sqlite:///{}.db'.format(tmpfile.name))


@pytest.fixture(name='worksheet_maker')
def crash_worksheet_maker_fixture():
    """Fixture for the WorksheetMaker class"""
    with tempfile.TemporaryFile() as tmpfile:
        conn_str = 'sqlite:///{}.db'.format(tmpfile.name)
        """
        # Make the database
        engine = create_engine(conn_str, echo=True, future=True)

        with engine.begin() as connection:
            Base.metadata.create_all(connection)
        """
        # Make the WorksheetMaker fixture
        ws_maker = WorksheetMaker(conn_str="mssql+pyodbc://balt-sql311-prd/DOT_DATA?driver=ODBC Driver 17 for SQL Server")
        with ws_maker:
            yield ws_maker
