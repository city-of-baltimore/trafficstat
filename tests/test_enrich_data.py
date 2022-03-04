"""Test suite for enrich_data"""
from sqlalchemy.orm import Session  # type: ignore

from trafficstat.ms2generator_schema import CrashSanitized, RoadwaySanitized


def test_geocode_acrs_sanitized(enrich):
    """Test for geocode_acrs_sanitized"""
    with Session(bind=enrich.engine) as session:
        session.add_all([
            CrashSanitized(REPORT_NO=11), CrashSanitized(REPORT_NO=12),
            CrashSanitized(REPORT_NO=13), CrashSanitized(REPORT_NO=14),
            RoadwaySanitized(REPORT_NO=11, X_COORDINATES=-76.6147012764419, Y_COORDINATES=39.2662592254051),
            RoadwaySanitized(REPORT_NO=12, X_COORDINATES=-76.6145704472065, Y_COORDINATES=39.3054704684803),
            RoadwaySanitized(REPORT_NO=13, X_COORDINATES=-76.6316923284531, Y_COORDINATES=39.3069128837032),
            RoadwaySanitized(REPORT_NO=14, X_COORDINATES=-76.6728773204327, Y_COORDINATES=39.2810172044491)])
        session.commit()

    enrich.geocode_acrs_sanitized()

    expected = {11: None,
                12: '110100',
                13: '140200',
                14: '200800'}

    with Session(enrich.engine) as session:
        for report_no, census_tract in expected.items():
            qry = session.query(RoadwaySanitized.CENSUS_TRACT). \
                filter(RoadwaySanitized.REPORT_NO.is_(report_no))
            assert qry.first()[0] == census_tract


def test_clean_road_names(enrich):
    """Test for clean_road_names"""
    assert enrich.clean_road_names('1100 NORTH AVE', 'HOWARD ST') == ('NORTH AVE', 'HOWARD ST')
    assert enrich.clean_road_names('300 S. GILMORE ST', '1600 BLK W PRATT ST') == ('GILMORE ST', 'PRATT ST')


def test_get_cleaned_location(enrich):
    """Test for get_cleaned_location"""
    with Session(bind=enrich.engine) as session:
        session.add_all([
            CrashSanitized(REPORT_NO=1),
            CrashSanitized(REPORT_NO=2),
            CrashSanitized(REPORT_NO=3),
            CrashSanitized(REPORT_NO=4),
            CrashSanitized(REPORT_NO=5),
            CrashSanitized(REPORT_NO=6),
            RoadwaySanitized(REPORT_NO=1, ROAD_NAME='295 NORTHBOUND', REFERENCE_ROAD_NAME='DUMMYTEXT'),
            RoadwaySanitized(REPORT_NO=2, ROAD_NAME='ENT TO FT MCHENRY', REFERENCE_ROAD_NAME='DUMMYTEXT'),
            RoadwaySanitized(REPORT_NO=3, ROAD_NAME='1100 NORTH AVE', REFERENCE_ROAD_NAME='NORTH AVE'),
            RoadwaySanitized(REPORT_NO=4, ROAD_NAME='300 S. GILMORE ST', REFERENCE_ROAD_NAME='1600 BLK W PRATT ST'),
            RoadwaySanitized(REPORT_NO=5, ROAD_NAME='RAMP 4 FR IS 895 NB', REFERENCE_ROAD_NAME='HARBOR TUNNEL THRUWAY'),
        ])
        session.commit()

    enrich.get_cleaned_location()

    expected = {1: ('2700 WATERVIEW AVE', '2700 WATERVIEW AVE', None),
                2: ('1200 FRANKFURST AVE', '1200 FRANKFURST AVE', None),
                3: ('1100 NORTH AVE', '1100 NORTH AVE', None),
                4: ('GILMORE ST & PRATT ST', 'GILMORE ST', 'PRATT ST'),
                5: ('1200 FRANKFURST AVE', '1200 FRANKFURST AVE', None),
                }

    with Session(enrich.engine) as session:
        for report_no, cleaned in expected.items():

            qry = session.query(RoadwaySanitized.CRASH_LOCATION,
                                RoadwaySanitized.ROAD_NAME_CLEAN,
                                RoadwaySanitized.REFERENCE_ROAD_NAME_CLEAN).\
                filter(RoadwaySanitized.REPORT_NO.is_(report_no))
            assert qry.first()[0] == cleaned[0]
            assert qry.first()[1] == cleaned[1]
            assert qry.first()[2] == cleaned[2]
