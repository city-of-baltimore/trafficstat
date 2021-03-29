"""Test suite for trafficstat.viewer"""
import os

from trafficstat.viewer import get_crash_diagram


def test_get_crash_diagram(tmpdir, conn_str_unsanitized):
    """Tests get_crash_diagram"""
    get_crash_diagram('A0000001', conn_str_unsanitized, tmpdir)

    assert os.path.exists(os.path.join(tmpdir, 'A0000001.jpg'))
    assert os.path.exists(os.path.join(tmpdir, 'A0000001.pdf'))

    get_crash_diagram('A0000002', conn_str_unsanitized, tmpdir)

    assert not os.path.exists(os.path.join(tmpdir, 'A0000002.jpg'))
    assert not os.path.exists(os.path.join(tmpdir, 'A0000002.pdf'))

    get_crash_diagram('A0000003', conn_str_unsanitized, tmpdir)
