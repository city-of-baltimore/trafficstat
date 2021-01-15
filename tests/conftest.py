"""Pytest directory-specific hook implementations"""
import tempfile
import pytest

from trafficstat.crash_data_ingestor import CrashDataReader


@pytest.fixture(name='crash_data_reader')
def crash_data_reader_fixture():
    """Fixture for the CrashDataReader class"""
    with tempfile.TemporaryFile() as tmpfile:
        yield CrashDataReader(conn_str='sqlite:///{}.db'.format(tmpfile.name))
