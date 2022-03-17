"""This is just for Tox support"""
from setuptools import setup, find_packages

setup(
    name='trafficstat',
    version='0.1',
    author="Brian Seel",
    author_email="brian.seel@baltimorecity.gov",
    description="Interface with the Ridesystems website",
    packages=find_packages('src'),
    package_data={'trafficstat': ['py.typed'], },
    python_requires='>=3.0',
    package_dir={'': 'src'},
    install_requires=[
        'pandas~=1.4.1',
        'decorator~=5.1.0',
        'pyodbc~=4.0.32',
        'tqdm~=4.63.0',
        'XlsxWriter~=3.0.2',
        'xmltodict~=0.12.0',
        'loguru~=0.6.0',
        'sqlalchemy~=1.4.27',
        'openpyxl~=3.0.9',
        'numpy~=1.22.3',
        'arcgis~=2.0.0',
        'git+https://github.com/arpuffer/pyvin@f96b8cf50ed7c8427537fb7d6fbe7d06496db485#egg=pyvin',
    ]
)
