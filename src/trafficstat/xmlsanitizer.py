"""Cleans up personally identifiable information in ACRS files"""
import argparse
import glob
import os
import re
from typing import Optional

from loguru import logger


def sanitize_xml_path(path: str, output_dir: str = 'sanitized') -> None:
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
    with open(filename, 'r', encoding='utf8') as xml_file:
        xml_contents = sanitize_xml_str(xml_file.read())

    if xml_contents is None:
        return

    if os.path.isfile(output_dir):
        raise RuntimeError("The output dir is already a file")

    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    with open(os.path.join(output_dir, os.path.basename(filename)), 'w', encoding='utf8') as output_file:
        output_file.write(xml_contents)


def sanitize_xml_str(xml_str) -> Optional[str]:
    """
    Sanitizes the personally identifiable information in an ACRS file from a string
    :param xml_str: string (containing XML) to sanitize
    :return: none
    """
    narratives = re.findall('<NARRATIVE>(.*?)</NARRATIVE>', xml_str, re.DOTALL)
    if not narratives:
        logger.error("Unable to find NARRATIVE")
        return None

    narrative = narratives[0]

    for person_type in ['OWNER', 'DRIVER', 'PASSENGER', 'NONMOTORIST']:
        last_names = re.findall('<{pt}>.*<LASTNAME>(.*?)</LASTNAME>.*</{pt}>'.format(pt=person_type), xml_str)
        for last_name in last_names:
            if last_name:
                narrative = narrative.replace(f' {last_name} ', f' **{person_type}** ')

    xml_str = re.sub('<FIRSTNAME>.*?</FIRSTNAME>', '<FIRSTNAME></FIRSTNAME>', xml_str)
    xml_str = re.sub('<LASTNAME>.*?</LASTNAME>', '<LASTNAME></LASTNAME>', xml_str)
    xml_str = re.sub('<MIDDLENAME>.*?</MIDDLENAME>', '<MIDDLENAME></MIDDLENAME>', xml_str)

    narrative = re.sub(r"(\\)", r"\\\\", narrative)
    return re.sub('<NARRATIVE>.*?</NARRATIVE>', f'<NARRATIVE>{narrative}</NARRATIVE>', xml_str,
                  flags=re.DOTALL)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sanitizes PII out of ACRS XML files.')
    parser.add_argument('-i', '--input_dir', required=True, help='Directory with XML files to sanitize')
    parser.add_argument('-o', '--output_dir', required=True, help='Directory to write sanitized XML files to')

    args = parser.parse_args()

    sanitize_xml_path(path=args.input_dir, output_dir=args.output_dir)
