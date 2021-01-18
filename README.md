# trafficstat
Library that handles the parsing, cleaning and exporting of ACRS crash data. This library is able to process raw ACRS XML files and put them into most any kind of database. It also can generate CSV files from that data, which can be ingested by MS2 for better visualization. 

## Setup ##
To setup your environment:

1. Check out the code. Either download it from the Github repository, or clone it with Git
2. Create a virtual environment. `python -m venv .venv`
3. Activate the virtual environment. `.venv\Scripts\activate`
4. Download all required python libraries. `python -m pip install -r requirements.txt`
5. Install the trafficstat library. `python setup.py install`

## Parse XML Files
To parse ACRS XML files, run 

`python main.py parse --directory <path>`

By default, this will process all files with an `.xml` extension, create the required database structure, parse the data into a database, and move the processed files into a `.processed` directory in the same folder that they were originally stored in. By default, it will put the data into a SQLite database file `crash.db`

To use a different database, pass the connection string with the `--conn_str` argument. For example, to use a different SQLite database:

`python main.py parse --directory <path> --conn_str sqlite://c:\Program Files\acrsdb.db`

To use the Baltimore City SQL Server:

`python main.py parse --directory <path> --conn_str "mssql+pyodbc://balt-sql311-prd/DOT_DATA?driver=SQL Server"`

## Data Enrichment
The State Highway Administration also releases sanitized crash data, which comes without latitude and longitude. After the data is imported from the AACDB files, the enrichment script will add geocoding information.  

**To import data from an aacdb file:**

This applies to the sanitized data that the State Highway Administration

1. Open the aacdb file in Access and save the file as an mdb file.
2. Open Sql Server Management server, and right click the database that the data will be inserted into
3. Select Microsoft Access as the data source and select the file
4. Select Microsoft OLE DB Driver for Sql Server as the destination and click properties
* Server name: balt-sql311-prd
* Authentication: Windows Authentication
* Select the database: DOT_DATA

Table names:
* [dbo].[acrs_crash_sanitized]
* [dbo].[acrs_citation_codes_sanitized]
* [dbo].[acrs_circumstances_sanitized]
* [dbo].[acrs_ems_sanitized]
* [dbo].[acrs_person_sanitized]
* [dbo].[acrs_roadway_sanitized]
* [dbo].[acrs_trailer_sanitized]
* [dbo].[acrs_vehicles_sanitized]

Add three columns that are needed:

```
ALTER TABLE acrs_roadway_sanitized
ADD CENSUS_TRACT nvarchar(25);

ALTER TABLE acrs_roadway_sanitized
ADD ROAD_NAME_CLEAN nvarchar(50);

ALTER TABLE acrs_roadway_sanitized
ADD REFERENCE_ROAD_NAME_CLEAN nvarchar(50);
```

Then run the data enricher. The enricher populates the 'sanitized' tables with census tract data. This only need to be run after a
yearly dump of ACRS data is ingested into the _sanitized databases. The census tract information is used by the PowerBI
dashboards to generate maps of hotspots.

`python main.py enrich`

## Export to MS2
MS2 is a tool that the department uses to visualize crash data. To create a spreadsheet that MS2 can ingest, run `python main.py ms2export`. This will create a spreadsheet called `BaltimoreCrash.xlsx` in the same directory.
