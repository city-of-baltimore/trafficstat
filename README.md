# trafficstat
Deals with traffic and crash data

backfill_census_tracts.py - populates the 'sanitized' tables with census tract data. This only need to be run after a
yearly dump of ACRS data is ingested into the _sanitized databases. The census tract information is used by the PowerBI
dashboards to generate maps of hotspots


## To import data from an aacdb file:
This applies to the sanitized data that the State Highway Administration

1. Open the aacdb file in Access and save the file as an mdb file.
2. Open Sql Server Management server, and right click the database that the data will be inserted into
3. Select Microsoft Access as the data source and select the file
4. Select Microsoft OLE DB Driver for Sql Server as the destination and click properties
* Server name: balt-sql311-prd
* Authentication: Windows Authentication
* Select the database: <database to use>

Table names:
[dbo].[acrs_crash_sanitized]
[dbo].[acrs_citation_codes_sanitized]
[dbo].[acrs_circumstances_sanitized]
[dbo].[acrs_ems_sanitized]
[dbo].[acrs_person_sanitized]
[dbo].[acrs_roadway_sanitized]
[dbo].[acrs_trailer_sanitized]
[dbo].[acrs_vehicles_sanitized]

Add three columns that are needed:

ALTER TABLE acrs_roadway_sanitized
ADD CENSUS_TRACT nvarchar(25);

ALTER TABLE acrs_roadway_sanitized
ADD ROAD_NAME_CLEAN nvarchar(50);

ALTER TABLE acrs_roadway_sanitized
ADD REFERENCE_ROAD_NAME_CLEAN nvarchar(50);

Then run the data enricher with `main.py -e`

# Unsanitized data table creation

To create the tables used in `crash_data_ingestor.py`, use the create table statements in test_crash_data_ingestor.py
