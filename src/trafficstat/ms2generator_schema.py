"""Schema information used for SQL Alchemy"""
# pylint:disable=too-few-public-methods
from sqlalchemy import Column, ForeignKey  # type: ignore
from sqlalchemy.ext.declarative import declarative_base  # type: ignore
from sqlalchemy.ext.declarative import DeclarativeMeta  # type: ignore
from sqlalchemy.types import DateTime, Float, Numeric, String  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore

Base: DeclarativeMeta = declarative_base()


##########################################
#     acrs_circumstance_sanitized       #
##########################################
class CircumstanceSanitized(Base):
    """Sqlalchemy: Data for table acrs_circumstance_sanitized"""
    __tablename__ = 'acrs_circumstance_sanitized'

    REPORT_NO = Column(String(length=10), ForeignKey('acrs_crash_sanitized.REPORT_NO'))
    CONTRIB_CODE1 = Column(String(length=5), nullable=True)
    CONTRIB_CODE2 = Column(String(length=5), nullable=True)
    CONTRIB_CODE3 = Column(String(length=5), nullable=True)
    CONTRIB_CODE4 = Column(String(length=5), nullable=True)
    PERSON_ID = Column(Float, ForeignKey('acrs_person_sanitized.PERSON_ID'))
    VEHICLE_ID = Column(Float, ForeignKey('acrs_vehicle_sanitized.VEHICLE_ID'))
    CIRCUMSTANCE_ID = Column(Float, primary_key=True)
    ACC_DATE = Column(DateTime, nullable=True)
    CONTRIB_FLAG = Column(String(length=1), nullable=True)
    DS_KEY = Column(String(length=20), nullable=True)


##########################################
#     acrs_citation_code_sanitized       #
##########################################
class CitationCodeSanitized(Base):
    """Sqlalchemy: Data for table acrs_citation_code_sanitized"""
    __tablename__ = 'acrs_citation_code_sanitized'

    CITATION = Column(String(length=25), nullable=True)
    PERSON_ID = Column(Float, ForeignKey('acrs_person_sanitized.PERSON_ID'))
    REPORT_NO = Column(String(length=10), ForeignKey('acrs_crash_sanitized.REPORT_NO'))
    ACC_DATE = Column(DateTime, nullable=True)
    CITATION_ID = Column(Float, primary_key=True)
    DS_KEY = Column(String(length=20), nullable=True)


##################################
#     acrs_crash_sanitized       #
##################################
class CrashSanitized(Base):
    """Sqlalchemy: Data for table acrs_crash_sanitized"""
    __tablename__ = 'acrs_crash_sanitized'

    CIRCUMSTANCE = relationship('CircumstanceSanitized')
    CITATION = relationship('CitationCodeSanitized')
    EMS = relationship('EmsSanitized')
    PERSON = relationship('PersonSanitized')
    ROADWAY = relationship('RoadwaySanitized', back_populates="CRASH")
    TRAILER = relationship('TrailerSanitized')
    VEHICLE = relationship('VehicleSanitized')

    RAMP_MOVEMENT_CODE = Column(String(length=5), nullable=True)
    LIGHT_CODE = Column(String(length=5), nullable=True)
    COUNTY_NO = Column(Numeric(precision=2, scale=0), nullable=True)
    MUNI_CODE = Column(String(length=3), nullable=True)
    JUNCTION_CODE = Column(String(length=5), nullable=True)
    COLLISION_TYPE_CODE = Column(String(length=5), nullable=True)
    SURF_COND_CODE = Column(String(length=5), nullable=True)
    LANE_CODE = Column(String(length=5), nullable=True)
    RD_COND_CODE = Column(String(length=5), nullable=True)
    FIX_OBJ_CODE = Column(String(length=5), nullable=True)
    REPORT_NO = Column(String(length=10), primary_key=True)
    WEATHER_CODE = Column(String(length=5), nullable=True)
    ACC_DATE = Column(DateTime, nullable=True)
    ACC_TIME = Column(String(length=4), nullable=True)
    LOC_CODE = Column(String(length=8), nullable=True)
    RAMP_FLAG = Column(String(length=1), nullable=True)
    SIGNAL_FLAG = Column(String(length=1), nullable=True)
    C_M_ZONE_FLAG = Column(String(length=1), nullable=True)
    INTER_NUM = Column(String(length=20), nullable=True)
    OFFICER_INFO = Column(String(length=20), nullable=True)
    AGENCY_CODE = Column(String(length=3), nullable=True)
    AREA_CODE = Column(String(length=3), nullable=True)
    HARM_EVENT_CODE1 = Column(String(length=5), nullable=True)
    HARM_EVENT_CODE2 = Column(String(length=5), nullable=True)
    LOC_CASE_NO = Column(String(length=20), nullable=True)
    ACRS_REPORT_NO = Column(String(length=20), nullable=True)
    REPORT_TYPE_CODE = Column(String(length=5), nullable=True)
    OFFICER_ID = Column(String(length=20), nullable=True)
    OFFICER_NAME = Column(String(length=80), nullable=True)
    DS_KEY = Column(String(length=20), nullable=True)
    PHOTOS_FLAG = Column(String(length=1), nullable=True)
    LANE_NUMBER = Column(Numeric(precision=2, scale=0), nullable=True)
    LANE_DIRECTION_CODE = Column(String(length=5), nullable=True)
    LANE_TYPE_CODE = Column(String(length=5), nullable=True)
    INTERSECTION_TYPE_CODE = Column(String(length=5), nullable=True)
    TRAFFIC_CONTROL_CODE = Column(String(length=5), nullable=True)
    TRAFFIC_CONTROL_FUNCTION_FLAG = Column(String(length=1), nullable=True)
    NUM_LANES = Column(Numeric(precision=2, scale=0), nullable=True)
    INTER_AREA_CODE = Column(String(length=5), nullable=True)
    SCHOOL_BUS_INVOLVED_CODE = Column(String(length=5), nullable=True)
    C_M_LOCATION_CODE = Column(String(length=5), nullable=True)
    REVIEW_DATE = Column(DateTime, nullable=True)
    REVIEW_OFFICER_ID = Column(String(length=20), nullable=True)
    REVIEW_OFFICER_NAME = Column(String(length=40), nullable=True)
    SUPER_DATE = Column(DateTime, nullable=True)
    SUPER_OFFICER_ID = Column(String(length=20), nullable=True)
    SUPER_OFFICER_NAME = Column(String(length=40), nullable=True)
    C_M_CLOSURE_CODE = Column(String(length=5), nullable=True)
    C_M_WORKERS_PRESENT_FLAG = Column(String(length=1), nullable=True)
    NARRATIVE = Column(String, nullable=True)
    GOV_PROPERTY_TXT = Column(String, nullable=True)


################################
#     acrs_ems_sanitized       #
################################
class EmsSanitized(Base):
    """Sqlalchemy: Data for table acrs_ems_sanitized"""
    __tablename__ = 'acrs_ems_sanitized'

    EMS_ID = Column(Float, primary_key=True)
    REPORT_NO = Column(String(length=10), ForeignKey('acrs_crash_sanitized.REPORT_NO'))
    RUN_REP_NO = Column(String(length=10), nullable=True)
    EMS_UNIT_TAKEN_BY = Column(String(length=40), nullable=True)
    EMS_UNIT_LABEL = Column(String(length=3), nullable=True)
    EMS_UNIT_TAKEN_TO = Column(String(length=40), nullable=True)
    EMS_SNO = Column(Numeric(precision=4, scale=0), nullable=True)
    ACC_DATE = Column(DateTime, nullable=True)
    EMS_TRANSPORT_TYPE_FLAG = Column(String(length=1), nullable=True)
    DS_KEY = Column(String(length=20), nullable=True)


###################################
#     acrs_person_sanitized       #
###################################
class PersonSanitized(Base):
    """Sqlalchemy: Data for table acrs_person_sanitized"""
    __tablename__ = 'acrs_person_sanitized'

    CIRCUMSTANCE = relationship('CircumstanceSanitized')
    CITATION = relationship('CitationCodeSanitized')

    SEX = Column(String(length=5), nullable=True)
    CONDITION_CODE = Column(String(length=5), nullable=True)
    DR_UNIT = Column(String(length=2), nullable=True)
    INJ_SEVER_CODE = Column(String(length=5), nullable=True)
    PED_UNIT = Column(String(length=2), nullable=True)
    OCC_UNIT = Column(String(length=2), nullable=True)
    OCC_NUM = Column(String(length=4), nullable=True)
    REPORT_NO = Column(String(length=10), ForeignKey('acrs_crash_sanitized.REPORT_NO'))
    OCC_SEAT_POS_CODE = Column(String(length=5), nullable=True)
    PED_VISIBLE_CODE = Column(String(length=5), nullable=True)
    PED_LOCATION_CODE = Column(String(length=5), nullable=True)
    PED_OBEY_CODE = Column(String(length=5), nullable=True)
    PED_TYPE_CODE = Column(String(length=5), nullable=True)
    MOVEMENT_CODE = Column(String(length=5), nullable=True)
    PERSON_TYPE = Column(String(length=1), nullable=True)
    DEATH_NUM = Column(String(length=4), nullable=True)
    AGE = Column(Numeric(precision=3, scale=0), nullable=True)
    SUBST_TEST_CODE = Column(String(length=5), nullable=True)
    SUBST_USE_CODE = Column(String(length=5), nullable=True)
    BAC = Column(String(length=2), nullable=True)
    FAULT_FLAG = Column(String(length=1), nullable=True)
    EQUIP_PROB_CODE = Column(String(length=5), nullable=True)
    SAF_EQUIP_CODE = Column(String(length=5), nullable=True)
    WOULD_HAVE_LIVED_FLAG = Column(String(length=1), nullable=True)
    EJECT_CODE = Column(String(length=5), nullable=True)
    DRIVER_DOB = Column(DateTime, nullable=True)
    PERSON_ID = Column(Float, primary_key=True)
    STATE_CODE = Column(String(length=2), nullable=True)
    CLASS = Column(String(length=2), nullable=True)
    CDL_FLAG = Column(String(length=1), nullable=True)
    ALCO_DRUG_IMPAIRED_FLAG = Column(String(length=1), nullable=True)
    ACC_DATE = Column(DateTime, nullable=True)
    VEHICLE_ID = Column(Float, ForeignKey('acrs_vehicle_sanitized.VEHICLE_ID'), nullable=True)
    DEATH_SUFFIX = Column(String(length=1), nullable=True)
    EMS_UNIT_LABEL = Column(String(length=3), nullable=True)
    EMS_ID = Column(Float, nullable=True)
    PERSON_PHONE_NUMBER = Column(String(length=10), nullable=True)
    PERSON_OTHER_PHONE = Column(String(length=10), nullable=True)
    PERSON_STREET_ADDRESS = Column(String(length=40), nullable=True)
    PERSON_CITY = Column(String(length=40), nullable=True)
    PERSON_STATE_CODE = Column(String(length=2), nullable=True)
    PERSON_ZIPCODE = Column(String(length=10), nullable=True)
    NONMOTOR_ACTION_TIME_CODE1 = Column(String(length=5), nullable=True)
    NONMOTOR_ACTION_TIME_CODE2 = Column(String(length=5), nullable=True)
    NONMOTOR_PRIOR_CODE = Column(String(length=5), nullable=True)
    UNIT_FIRST_STRIKE = Column(String(length=4), nullable=True)
    AIR_BAG_CODE = Column(String(length=5), nullable=True)
    DISTRACTED_BY_CODE = Column(String(length=5), nullable=True)
    ALCO_TEST_CODE = Column(String(length=5), nullable=True)
    ALCO_TEST_TYPE_CODE = Column(String(length=5), nullable=True)
    DRUG_TEST_CODE = Column(String(length=5), nullable=True)
    DRUG_TEST_RESULT_FLAG = Column(String(length=1), nullable=True)
    OCC_SEAT_LOCATION = Column(String(length=5), nullable=True)
    OCC_SEAT_ROW = Column(Numeric(precision=2, scale=0), nullable=True)
    OCC_POS_INROW_CODE = Column(String(length=5), nullable=True)
    LIC_STATUS_FLAG = Column(String(length=1), nullable=True)
    CITATION_ISSUED_FLAG = Column(String(length=1), nullable=True)
    DS_KEY = Column(String(length=20), nullable=True)


####################################
#     acrs_roadway_sanitized       #
####################################
class RoadwaySanitized(Base):
    """Sqlalchemy: Data for table acrs_roadway_sanitized"""
    __tablename__ = 'acrs_roadway_sanitized'

    CRASH = relationship(CrashSanitized)

    REPORT_NO = Column(String(length=10), ForeignKey('acrs_crash_sanitized.REPORT_NO'), primary_key=True)
    ROUTE_NUMBER = Column(Numeric(precision=5, scale=0), nullable=True)
    ROUTE_TYPE_CODE = Column(String(length=2), nullable=True)
    ROUTE_SUFFIX = Column(String(length=2), nullable=True)
    LOG_MILE = Column(Numeric(precision=6, scale=3), nullable=True)
    RD_CHAR_CODE = Column(String(length=5), nullable=True)
    RD_DIV_CODE = Column(String(length=5), nullable=True)
    LOGMILE_DIR_FLAG = Column(String(length=1), nullable=True)
    ROAD_NAME = Column(String(length=50), nullable=True)
    FUNCTIONAL_CLASS_NO = Column(Numeric(precision=2, scale=0), nullable=True)
    TC_CODE = Column(String(length=3), nullable=True)
    DISTANCE = Column(Numeric(precision=6, scale=3), nullable=True)
    FEET_MILES_FLAG = Column(String(length=1), nullable=True)
    DISTANCE_DIR_FLAG = Column(String(length=1), nullable=True)
    FINAL_LOG_MILE = Column(Numeric(precision=6, scale=3), nullable=True)
    REFERENCE_NUMBER = Column(Numeric(precision=5, scale=0), nullable=True)
    REFERENCE_TYPE_CODE = Column(String(length=2), nullable=True)
    REFERENCE_SUFFIX = Column(String(length=2), nullable=True)
    REFERENCE_ROAD_NAME = Column(String(length=50), nullable=True)
    ACC_DATE = Column(DateTime, nullable=True)
    X_COORDINATES = Column(Float, nullable=True)
    Y_COORDINATES = Column(Float, nullable=True)
    RD_ALIGNMENT_CODE = Column(String(length=5), nullable=True)
    RD_GRADE_CODE = Column(String(length=5), nullable=True)
    OFF_ROAD_TXT = Column(String, nullable=True)
    FINAL_X_COORDINATES = Column(Float, nullable=True)
    FINAL_Y_COORDINATES = Column(Float, nullable=True)
    DS_KEY = Column(String(length=20), nullable=True)
    CENSUS_TRACT = Column(String(length=25), nullable=True)
    ROAD_NAME_CLEAN = Column(String(length=50), nullable=True)
    REFERENCE_ROAD_NAME_CLEAN = Column(String(length=50), nullable=True)
    CRASH_LOCATION = Column(String, nullable=True)


####################################
#     acrs_trailer_sanitized       #
####################################
class TrailerSanitized(Base):
    """Sqlalchemy: Data for table acrs_trailer_sanitized"""
    __tablename__ = 'acrs_trailer_sanitized'

    TRAILER_RECORD_ID = Column(Float, primary_key=True)
    REPORT_NO = Column(String(length=10), ForeignKey('acrs_crash_sanitized.REPORT_NO'))
    ACC_DATE = Column(DateTime, nullable=True)
    VEHICLE_ID = Column(Float, nullable=True)
    REFERENCE_UNIT_NO = Column(String(length=4), nullable=True)
    TOWED_VEHICLE_UNIT_NO = Column(String(length=4), nullable=True)
    VEH_YEAR = Column(String(length=4), nullable=True)
    VEH_MAKE = Column(String(length=20), nullable=True)
    VEH_MODEL = Column(String(length=40), nullable=True)
    BODY_TYPE_CODE = Column(String(length=5), nullable=True)
    PLATE_STATE = Column(String(length=2), nullable=True)
    PLATE_YEAR = Column(String(length=4), nullable=True)
    DS_KEY = Column(String(length=20), nullable=True)


####################################
#     acrs_vehicle_sanitized       #
####################################
class VehicleSanitized(Base):
    """Sqlalchemy: Data for table acrs_vehicle_sanitized"""
    __tablename__ = 'acrs_vehicle_sanitized'

    CIRCUMSTANCE = relationship('CircumstanceSanitized')

    HARM_EVENT_CODE = Column(String(length=5), nullable=True)
    PERSON_ID = Column(String(length=38), nullable=True)
    CONTI_DIRECTION_CODE = Column(String(length=5), nullable=True)
    DAMAGE_CODE = Column(String(length=5), nullable=True)
    MOVEMENT_CODE = Column(String(length=5), nullable=True)
    REPORT_NO = Column(String(length=10), ForeignKey('acrs_crash_sanitized.REPORT_NO'))
    CV_BODY_TYPE_CODE = Column(String(length=5), nullable=True)
    VEH_YEAR = Column(String(length=4), nullable=True)
    VEH_MAKE = Column(String(length=30), nullable=True)
    COMMERCIAL_FLAG = Column(String(length=1), nullable=True)
    VEH_MODEL = Column(String(length=30), nullable=True)
    TOWED_AWAY_FLAG = Column(String(length=1), nullable=True)
    NUM_AXLES = Column(String(length=2), nullable=True)
    GVW_CODE = Column('GVW', String(length=6), nullable=True)
    GOING_DIRECTION_CODE = Column(String(length=5), nullable=True)
    BODY_TYPE_CODE = Column(String(length=5), nullable=True)
    DRIVERLESS_FLAG = Column(String(length=1), nullable=True)
    FIRE_FLAG = Column(String(length=1), nullable=True)
    NUM_OCC = Column(Numeric(precision=3, scale=0), nullable=True)
    PARKED_FLAG = Column(String(length=1), nullable=True)
    SPEED_LIMIT = Column(String(length=2), nullable=True)
    HIT_AND_RUN_FLAG = Column(String(length=1), nullable=True)
    HAZMAT_SPILL_FLAG = Column(String(length=1), nullable=True)
    VIN_NO = Column('VEHICLE_ID', Float, primary_key=True)
    # VEHICLE_ID = Column(Float, primary_key=True)  # this is a duplicate, but thats required
    TOWED_VEHICLE_CONFIG_CODE = Column('TOWED_VEHICLE_CODE1', String(length=5), nullable=True)
    TOWED_VEHICLE_CODE2 = Column(String(length=5), nullable=True)
    TOWED_VEHICLE_CODE3 = Column(String(length=5), nullable=True)
    PLATE_STATE = Column(String(length=2), nullable=True)
    PLATE_YEAR = Column(String(length=4), nullable=True)
    AREA_DAMAGED_CODE1 = Column(String(length=5), nullable=True)
    AREA_DAMAGED_CODE2 = Column(String(length=5), nullable=True)
    AREA_DAMAGED_CODE3 = Column(String(length=5), nullable=True)
    AREA_DAMAGED_CODE_IMP1 = Column(String(length=5), nullable=True)
    AREA_DAMAGED_CODE_MAIN = Column(String(length=5), nullable=True)
    ACC_DATE = Column(DateTime, nullable=True)
    SEQ_EVENT_CODE1 = Column(String(length=5), nullable=True)
    SEQ_EVENT_CODE2 = Column(String(length=5), nullable=True)
    SEQ_EVENT_CODE3 = Column(String(length=5), nullable=True)
    SEQ_EVENT_CODE4 = Column(String(length=5), nullable=True)
    REMOVED_BY = Column(String(length=40), nullable=True)
    REMOVED_TO = Column(String(length=40), nullable=True)
    VEH_SPECIAL_FUNCTION_CODE = Column(String(length=5), nullable=True)
    EMERGENCY_USE_FLAG = Column(String(length=1), nullable=True)
    CV_CONFIG_CODE = Column(String(length=5), nullable=True)
    BUS_USE_CODE = Column(String(length=5), nullable=True)
    HZM_NUM = Column('HZM_NAME', String(length=40), nullable=True)
    PLACARD_VISIBLE_FLAG = Column(String(length=1), nullable=True)
    VEHICLE_WEIGHT_CODE = Column(String(length=5), nullable=True)
    OWNER_STATE_CODE = Column(String(length=2), nullable=True)
    DS_KEY = Column(String(length=20), nullable=True)
