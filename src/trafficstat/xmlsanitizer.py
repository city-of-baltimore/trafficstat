"""Cleans up personally identifiable information in ACRS files"""
import glob
import os
import re
from loguru import logger


def sanitize_xml(path: str, output_dir: str = 'sanitized') -> None:
    """
    Sanitizes the personally identifiable information in an ACRS file
    :param path: path to sanitize, either a file or a path (where all .xml files will be sanitized)
    :param output_dir: directory to write the sanitized file
    :return: none
    """
    if os.path.isdir(path):
        for file in glob.glob(os.path.join(path, '*.xml')):
            _sanitize_xml_file(file, output_dir)
    else:
        _sanitize_xml_file(path, output_dir)


def _sanitize_xml_file(filename: str, output_dir: str = '.sanitized') -> None:
    """
    Sanitizes the personally identifiable information in an ACRS file
    :param filename: file to sanitize
    :param output_dir: directory to write the sanitized file
    :return: None
    """
    with open(filename, 'r') as xml_file:
        xml_contents = xml_file.read()

    narrative = re.findall('<NARRATIVE>(.*?)</NARRATIVE>', xml_contents)
    if not narrative:
        logger.error("Unable to find NARRATIVE tag in {}".format(filename))
        return

    for person_type in ['OWNER', 'DRIVER', 'PASSENGER', 'NONMOTORIST']:
        last_names = re.findall('<{pt}>.*<LASTNAME>(.*?)</LASTNAME>.*</{pt}>'.format(pt=person_type), xml_contents)
        for last_name in last_names:
            narrative = narrative[0].replace(' {} '.format(last_name), ' **{}** '.format(person_type))

        xml_contents = re.sub('<FIRSTNAME>.*?</FIRSTNAME>', '<FIRSTNAME></FIRSTNAME>', xml_contents)
        xml_contents = re.sub('<LASTNAME>.*?</LASTNAME>', '<LASTNAME></LASTNAME>', xml_contents)

    xml_contents = re.sub('<NARRATIVE>.*?</NARRATIVE>', '<NARRATIVE>{nar}</NARRATIVE>'.format(nar=narrative),
                          xml_contents)

    if os.path.isfile(output_dir):
        raise RuntimeError("The output dir is already a file")

    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    with open(os.path.join(output_dir, os.path.basename(filename)), 'w') as output_file:
        output_file.write(xml_contents)
