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
        'pandas~=1.2.4',
        'decorator~=5.0.7',
        'pyodbc~=4.0.30',
        'tqdm~=4.60.0',
        'XlsxWriter~=1.4.0',
        'xmltodict~=0.12.0',
        'loguru~=0.5.3',
        'sqlalchemy~=1.4.11',
        'openpyxl~=3.0.7',
        'numpy~=1.20.2',
        'pyvin@git+https://github.com/cylussec/pyvin@added_testing#egg=pyvin',
        'balt-geocoder@git+https://github.com/city-of-baltimore/Geocoder@v1.0.4#egg=balt-geocoder',
    ]
)
