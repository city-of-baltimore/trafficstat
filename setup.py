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
        'pandas',
        'decorator',
        'pyodbc',
        'tqdm',
        'XlsxWriter',
        'xmltodict',
        'loguru',
        'sqlalchemy',
        'openpyxl',
        'numpy',
        'arcgis',
        'pyvin@git+https://github.com/cylussec/pyvin@added_testing#egg=pyvin',
    ]
)
