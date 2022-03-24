"""Test suite for enrich_data"""
import os
import shutil

from sqlalchemy.orm import Session  # type: ignore

from trafficstat.ms2generator_schema import CrashSanitized, RoadwaySanitized


def test_clean_road_names(enrich):
    """Test for clean_road_names"""
    assert enrich.clean_road_names('1100 NORTH AVE', 'HOWARD ST') == ('NORTH AVE', 'HOWARD ST')
    assert enrich.clean_road_names('300 S. GILMORE ST', '1600 BLK W PRATT ST') == ('GILMORE ST', 'PRATT ST')
    assert enrich.clean_road_names('3100 WILKINS') == ('3100 WILKINS', None)


def test_get_cleaned_location(enrich):
    """Test for get_cleaned_location"""
    with Session(bind=enrich.engine) as session:
        session.add_all([
            CrashSanitized(REPORT_NO='A1'),
            CrashSanitized(REPORT_NO='A2'),
            CrashSanitized(REPORT_NO='A3'),
            CrashSanitized(REPORT_NO='A4'),
            CrashSanitized(REPORT_NO='A5'),
            CrashSanitized(REPORT_NO='A6'),
            CrashSanitized(REPORT_NO='A7'),
            CrashSanitized(REPORT_NO='A8'),
            RoadwaySanitized(REPORT_NO='A1', ROAD_NAME='295 NORTHBOUND', REFERENCE_ROAD_NAME='DUMMYTEXT'),
            RoadwaySanitized(REPORT_NO='A2', ROAD_NAME='ENT TO FT MCHENRY', REFERENCE_ROAD_NAME='DUMMYTEXT'),
            RoadwaySanitized(REPORT_NO='A3', ROAD_NAME='1100 NORTH AVE', REFERENCE_ROAD_NAME='NORTH AVE'),
            RoadwaySanitized(REPORT_NO='A4', ROAD_NAME='1600 BLK W PRATT ST', REFERENCE_ROAD_NAME='300 S. GILMORE ST'),
            RoadwaySanitized(REPORT_NO='A5', ROAD_NAME='RAMP 4 I-895 NB', REFERENCE_ROAD_NAME='HARBOR TUNNEL THRUWAY'),
            RoadwaySanitized(REPORT_NO='A6', ROAD_NAME='WILKINS', REFERENCE_ROAD_NAME=''),
            RoadwaySanitized(REPORT_NO='A7', ROAD_NAME='3100 WILKINS', REFERENCE_ROAD_NAME=''),
            RoadwaySanitized(REPORT_NO='A8', ROAD_NAME='ACRS MARKED OFF ROAD', REFERENCE_ROAD_NAME=''),
        ])
        session.commit()

    enrich.get_cleaned_location()

    expected = {'A1': (None, None, None, 'NA'),
                'A2': (None, None, None, 'NA'),
                'A3': ('1100 NORTH AVE', '1100 NORTH AVE', None, '130300'),
                'A4': ('GILMORE ST & PRATT ST', 'PRATT ST', 'GILMORE ST', '190300'),
                'A5': (None, None, None, 'NA'),
                'A6': ('WILKINS', 'WILKINS', None, 'NA'),
                'A7': ('3100 WILKINS', '3100 WILKINS', None, 'NA'),
                'A8': ('ACRS MARKED OFF ROAD', 'ACRS MARKED OFF ROAD', None, 'NA'),
                }

    with Session(enrich.engine) as session:
        for report_no, cleaned in expected.items():

            qry = session.query(RoadwaySanitized.CRASH_LOCATION,
                                RoadwaySanitized.ROAD_NAME_CLEAN,
                                RoadwaySanitized.REFERENCE_ROAD_NAME_CLEAN,
                                RoadwaySanitized.CENSUS_TRACT).\
                filter(RoadwaySanitized.REPORT_NO.is_(report_no))
            assert qry.first()[0] == cleaned[0]
            assert qry.first()[1] == cleaned[1]
            assert qry.first()[2] == cleaned[2]
            assert qry.first()[3] == cleaned[3]


def test_add_cleaned_names(enrich, tmpdir):
    """Test for add_cleaned_names"""
    test_dir = os.path.join(tmpdir, 'testfiles')
    shutil.copytree(os.path.join('tests', 'testfiles'), test_dir)

    with Session(bind=enrich.engine) as session:
        session.add_all([
            CrashSanitized(REPORT_NO='A1'),
            CrashSanitized(REPORT_NO='A2'),
            CrashSanitized(REPORT_NO='A3'),
            RoadwaySanitized(REPORT_NO='A1', ROAD_NAME='1100 NORTH AVE', REFERENCE_ROAD_NAME='NORTH AVE'),
            RoadwaySanitized(REPORT_NO='A2', ROAD_NAME='1100 NORTH AVE', REFERENCE_ROAD_NAME='NORTH AVE'),
            RoadwaySanitized(REPORT_NO='A3', ROAD_NAME='1100 NORTH AVE', REFERENCE_ROAD_NAME='NORTH AVE'),
        ])
        session.commit()

        enrich.get_cleaned_location()
        enrich.add_cleaned_names(os.path.join(test_dir, 'cleanednames.csv'))

        qry = session.query(RoadwaySanitized).order_by(RoadwaySanitized.REPORT_NO)
        ret = qry.all()
        assert ret[0].REPORT_NO == 'A1'
        assert ret[0].CRASH_LOCATION == '1100 NORTH AVE'
        assert ret[1].REPORT_NO == 'A2'
        assert ret[1].CRASH_LOCATION == 'INTERSECTION2'
        assert ret[2].REPORT_NO == 'A3'
        assert ret[2].CRASH_LOCATION == 'INTERSECTION3'
