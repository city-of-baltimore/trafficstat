"""Test suite for enrich_data"""


def test_geocode_acrs_sanitized(enrich):
    """Test for geocode_acrs_sanitized"""
    enrich.geocode_acrs_sanitized()


def test_clean_road_names(enrich):
    """Test for clean_road_names"""
    assert enrich.clean_road_names('295 NORTHBOUND', 'DUMMYTEXT') == '2700 Waterview'
    assert enrich.clean_road_names('ENT TO FT MCHENRY', 'DUMMYTEXT') == '1200 Frankfurst'
    assert enrich.clean_road_names('1100 NORTH AVE', 'NORTH AVE') == '1100 NORTH AVE'
    assert enrich.clean_road_names('300 S. GILMORE ST', '1600 BLK W PRATT ST') == 'GILMORE', 'PRATT'


def test_get_cleaned_location(enrich):
    """Test for get_cleaned_location"""
    enrich.get_cleaned_location()
