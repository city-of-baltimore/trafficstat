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
        'loguru~=0.5.3',
        'pandas~=1.2.2',
        'pyodbc~=4.0.30',
        'tqdm~=4.57.0',
        'balt-geocoder @ git+https://github.com/city-of-baltimore/Geocoder@main#egg=balt-geocoder',
        'xlsxwriter~=1.3.7',
    ]
)
