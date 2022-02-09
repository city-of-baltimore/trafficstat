"""Test suite for enrich_data"""
from sqlalchemy.orm import Session  # type: ignore

from trafficstat.ms2generator_schema import CrashSanitized, RoadwaySanitized


def test_geocode_acrs_sanitized(enrich):
    """Test for geocode_acrs_sanitized"""
    enrich.geocode_acrs_sanitized()


def test_clean_road_names(enrich):
    """Test for clean_road_names"""
    assert enrich.clean_road_names('1100 NORTH AVE', 'HOWARD ST') == ('NORTH AVE', 'HOWARD ST')
    assert enrich.clean_road_names('300 S. GILMORE ST', '1600 BLK W PRATT ST') == ('GILMORE ST', 'PRATT ST')


def test_get_cleaned_location(enrich):
    """Test for get_cleaned_location"""
    with Session(bind=enrich.engine) as session:
        session.add_all([
            CrashSanitized(REPORT_NO=1), CrashSanitized(REPORT_NO=2),
            CrashSanitized(REPORT_NO=3), CrashSanitized(REPORT_NO=4),
            RoadwaySanitized(REPORT_NO=1, ROAD_NAME='295 NORTHBOUND', REFERENCE_ROAD_NAME='DUMMYTEXT'),
            RoadwaySanitized(REPORT_NO=2, ROAD_NAME='ENT TO FT MCHENRY', REFERENCE_ROAD_NAME='DUMMYTEXT'),
            RoadwaySanitized(REPORT_NO=3, ROAD_NAME='1100 NORTH AVE', REFERENCE_ROAD_NAME='NORTH AVE'),
            RoadwaySanitized(REPORT_NO=4, ROAD_NAME='300 S. GILMORE ST', REFERENCE_ROAD_NAME='1600 BLK W PRATT ST')])
        session.commit()

    enrich.get_cleaned_location()

    expected = {1: ('2700 Waterview Ave', None),
                2: ('1200 Frankfurst Ave', None),
                3: ('1100 NORTH AVE', None),
                4: ('GILMORE ST', 'PRATT ST')}

    with Session(enrich.engine) as session:
        for report_no, cleaned in expected.items():

            qry = session.query(RoadwaySanitized.ROAD_NAME_CLEAN,
                                RoadwaySanitized.REFERENCE_ROAD_NAME_CLEAN).\
                filter(RoadwaySanitized.REPORT_NO.is_(report_no))
            assert qry.first()[0] == cleaned[0]
            assert qry.first()[1] == cleaned[1]
