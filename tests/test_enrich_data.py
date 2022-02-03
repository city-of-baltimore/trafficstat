"""Test suite for enrich_data"""


def test_geocode_acrs_sanitized(enrich):
    """Test for geocode_acrs_sanitized"""
    enrich.geocode_acrs_sanitized()


def test_clean_road_names(enrich):
    """Test for clean_road_names"""
    enrich.clean_road_names()
