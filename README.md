# trafficstat
Deals with traffic and crash data

backfill_census_tracts.py - populates the 'sanitized' tables with census tract data. This only need to be run after a 
yearly dump of ACRS data is ingested into the _sanitized databases. The census tract information is used by the PowerBI
dashboards to generate maps of hotspots
