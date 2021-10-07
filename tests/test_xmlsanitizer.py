"""Test suite for xmlsanitizer.py"""
# pylint:disable=protected-access
import glob
import os
import re
import shutil

import pytest

from trafficstat import xmlsanitizer


def test_sanitize_xml(tmpdir):
    """tests sanitize_xml"""
    testfiles = os.path.join(tmpdir, 'testfiles')
    os.mkdir(testfiles)
    for file in glob.glob(os.path.join('tests', 'testfiles', '*.xml')):
        shutil.copy(file, testfiles)

    # create a file and pass it as the output folder... this should fail
    empty_file = os.path.join(tmpdir, 'filenotfolder')
    with open(empty_file, 'w', encoding='utf8'):
        pass
    with pytest.raises(RuntimeError):
        xmlsanitizer.sanitize_xml_path(testfiles, empty_file)

    # now do it right
    sanitized_files = os.path.join(tmpdir, '.sanitized')
    xmlsanitizer.sanitize_xml_path(testfiles, sanitized_files)

    files = glob.glob(os.path.join(sanitized_files, '*.xml'))
    assert len(files) - 1 == 13  # remove one because of the duplicate version test
    for file in files:
        with open(file, 'r', encoding='utf8') as xml_file:
            xml_contents = xml_file.read()

        assert set(re.findall('<FIRSTNAME>(.*?)</FIRSTNAME>', xml_contents)) == {''}
        assert set(re.findall('<LASTNAME>(.*?)</LASTNAME>', xml_contents)) == {''}
        narrative = re.findall('<NARRATIVE>(.*?)</NARRATIVE>', xml_contents, re.DOTALL)[0]
        assert 'LASTNAME' not in narrative
        assert len(narrative) > 1


def test_sanitize_xml_file(tmpdir):
    """tests sanitize_xml_file()"""
    original_file = os.path.join(tmpdir, 'BALTIMORE_acrs_ADJ5220059-witness-nonmotorist.xml')
    sanitized_files = os.path.join(tmpdir, '.sanitized')
    shutil.copyfile(os.path.join('tests', 'testfiles', 'BALTIMORE_acrs_ADJ5220059-witness-nonmotorist.xml'),
                    original_file)
    xmlsanitizer.sanitize_xml_path(original_file, sanitized_files)

    with open(os.path.join(sanitized_files, os.path.basename(original_file)), 'r', encoding='utf8') as xml_file:
        xml_contents = xml_file.read()

    assert set(re.findall('<FIRSTNAME>(.*?)</FIRSTNAME>', xml_contents)) == {''}
    assert set(re.findall('<LASTNAME>(.*?)</LASTNAME>', xml_contents)) == {''}
    narrative = re.findall('<NARRATIVE>(.*?)</NARRATIVE>', xml_contents, re.DOTALL)[0]
    assert 'LASTNAME' not in narrative
    assert len(narrative) > 1
