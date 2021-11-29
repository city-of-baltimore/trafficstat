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
        'pandas~=1.3.4',
        'decorator~=5.1.0',
        'pyodbc~=4.0.32',
        'tqdm~=4.62.3',
        'XlsxWriter~=3.0.2',
        'xmltodict~=0.12.0',
        'loguru~=0.5.3',
        'sqlalchemy~=1.4.27',
        'openpyxl~=3.0.9',
        'numpy~=1.21.4',
        'arcgis~=1.9.1',
        'pyvin@git+https://github.com/cylussec/pyvin@added_testing#egg=pyvin',
    ]
)
