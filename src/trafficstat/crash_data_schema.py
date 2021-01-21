"""Schema information used for SQL Alchemy"""
# pylint:disable=line-too-long
# pylint:disable=too-few-public-methods
import uuid

from sqlalchemy import Column, ForeignKey  # type: ignore
from sqlalchemy.dialects.postgresql import UUID  # type: ignore
from sqlalchemy.ext.declarative import DeclarativeMeta  # type: ignore
from sqlalchemy.ext.declarative import declarative_base  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore
from sqlalchemy.types import Boolean, CHAR, Date, DateTime, Float, Integer, String, Time, TypeDecorator  # type: ignore

Base: DeclarativeMeta = declarative_base()
REPORTNUMBER_LEN = 14


class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(32), storing as stringified hex values.
    Copy/paste from https://docs.sqlalchemy.org/en/14/core/custom_types.html#backend-agnostic-guid-type
    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value

        if dialect.name == 'postgresql':
            return str(value)

        if not isinstance(value, uuid.UUID):
            return "%.32x" % uuid.UUID(value).int

        # hexstring
        return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value

        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(value)
        return value

    @property
    def python_type(self):
        return uuid.UUID

    def process_literal_param(self, value, dialect):
        return str(value)


########################
#     acrs_crash       #
########################
class Crash(Base):
    """Sqlalchemy: Data for table acrs_crash"""
    __tablename__ = "acrs_crash"

    ACRSREPORTTIMESTAMP = Column(DateTime)  # <xs:element type="xs:dateTime" name="ACRSREPORTTIMESTAMP"/>
    AGENCYIDENTIFIER = Column(String)  # <xs:element type="xs:string" name="AGENCYIDENTIFIER"/>
    AGENCYNAME = Column(String)  # <xs:element type="xs:string" name="AGENCYNAME"/>
    APPROVAL = relationship('Approval', uselist=False,
                            back_populates='CRASHES')  # one:one <xs:element type="cras:APPROVALDATAType" name="APPROVALDATA" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    AREA = Column(String)  # <xs:element type="xs:string" name="AREA"/>
    CIRCUMSTANCES = relationship(
        'Circumstance')  # one:many <xs:element type="cras:CIRCUMSTANCESType" name="CIRCUMSTANCES" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    COLLISIONTYPE = Column(Integer)  # <xs:element type="xs:byte" name="COLLISIONTYPE"/>
    CONMAINCLOSURE = Column(
        String)  # <xs:element name="CONMAINCLOSURE" nillable="true"> (restricted to values 00, 01, 02, 03, 04, 88, 99, and ''
    CONMAINLOCATION = Column(
        String)  # <xs:element name="CONMAINLOCATION" nillable="true"> (restricted to values 00, 01, 02, 03, 04, 05, 88, 99, and '')
    CONMAINWORKERSPRESENT = Column(
        Boolean, nullable=True)  # <xs:element name="CONMAINWORKERSPRESENT" nillable="true"> (restricted to Y, N, U, '')
    CONMAINZONE = Column(Boolean, nullable=True)  # <xs:element name="CONMAINWORKERSPRESENT" nillable="true">
    CRASHDATE = Column(Date)  # <xs:element type="xs:dateTime" name="CRASHDATE"/>
    CRASHTIME = Column(Time)  # <xs:element type="xs:dateTime" name="CRASHTIME"/>
    CURRENTASSIGNMENT = Column(String)  # <xs:element name="CURRENTASSIGNMENT"> (restricted to values 999, BCPD, and '')
    CURRENTGROUP = Column(String)  # <xs:element type="xs:string" name="CURRENTGROUP"/>
    DEFAULTASSIGNMENT = Column(String)  # <xs:element name="DEFAULTASSIGNMENT"> (restricted to values 999, BCPD, and '')
    DEFAULTGROUP = Column(String)  # <xs:element type="xs:string" name="DEFAULTGROUP"/>
    DIAGRAM = relationship('CrashDiagram', uselist=False,
                           back_populates='CRASHES')  # one:one <xs:element type="cras:DIAGRAMType" name="DIAGRAM" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    DOCTYPE = Column(String)  # <xs:element type="xs:string" name="DOCTYPE"/>
    EMSes = relationship(
        'Ems')  # one:many <xs:element type="cras:EMSType" name="EMS" maxOccurs="unbounded" minOccurs="0" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    FIXEDOBJECTSTRUCK = Column(Float)  # <xs:element type="xs:float" name="FIXEDOBJECTSTRUCK"/>
    HARMFULEVENTONE = Column(Float)  # <xs:element type="xs:float" name="HARMFULEVENTONE"/>
    HARMFULEVENTTWO = Column(Float)  # <xs:element type="xs:float" name="HARMFULEVENTTWO"/>
    HITANDRUN = Column(Boolean, nullable=True)  # <xs:element name="HITANDRUN"> nillable to handle the Unknown option
    INSERTDATE = Column(DateTime)  # <xs:element type="xs:dateTime" name="INSERTDATE"/>
    INTERCHANGEAREA = Column(
        String)  # <xs:element name="INTERCHANGEAREA"> (restricted to 00, 01, 02, 03, 04, 05, 06, 88, 99, and '')
    INTERCHANGEIDENTIFICATION = Column(String,
                                       nullable=True)  # <xs:element type="xs:string" name="INTERCHANGEIDENTIFICATION" nillable="true"/>
    INTERSECTIONTYPE = Column(String)  # <xs:element name="INTERSECTIONTYPE">
    INVESTIGATINGOFFICERUSERNAME = Column(String)  # <xs:element type="xs:string" name="INVESTIGATINGOFFICERUSERNAME"/>
    INVESTIGATOR = Column(String)  # <xs:element type="xs:string" name="INVESTIGATOR" nillable="true"/>
    JUNCTION = Column(String)  # <xs:element type="xs:string" name="JUNCTION"/>
    LANEDIRECTION = Column(String)  # <xs:element name="LANEDIRECTION"> (restricted to N, S, E, W, U and '')
    LANENUMBER = Column(String)  # <xs:element name="LANENUMBER"> (restricted to 1, 2, 3, 4, 5, 6 or '')
    LANETYPE = Column(String, nullable=True)  # <xs:element type="xs:string" name="LANETYPE" nillable="true"/>
    LATITUDE = Column(Float)  # <xs:element type="xs:float" name="LATITUDE"/>
    LIGHT = Column(Float)  # <xs:element name="LIGHT">
    LOCALCASENUMBER = Column(String)  # <xs:element type="xs:string" name="LOCALCASENUMBER"/>
    LOCALCODES = Column(String)  # <xs:element type="xs:string" name="LOCALCODES" nillable="true"/>
    LONGITUDE = Column(Float)  # <xs:element type="xs:float" name="LONGITUDE"/>
    MILEPOINTDIRECTION = Column(String)  # <xs:element name="MILEPOINTDIRECTION"> (restrcted to N, S, E, W, U, and '')
    MILEPOINTDISTANCE = Column(String)  # <xs:element type="xs:string" name="MILEPOINTDISTANCE"/>
    MILEPOINTDISTANCEUNITS = Column(
        String)  # <xs:element name="MILEPOINTDISTANCEUNITS"> (restricted to M, F, U, and '')
    NARRATIVE = Column(String)  # <xs:element type="xs:string" name="NARRATIVE"/>
    NONMOTORIST = relationship(
        'PersonInfo')  # one:many <xs:element type="cras:NONMOTORISTType" name="NONMOTORIST" maxOccurs="unbounded" minOccurs="0" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    NONTRAFFIC = Column(Boolean, nullable=True)  # <xs:element name="NONTRAFFIC"> nillable to handle the Unknown option
    NUMBEROFLANES = Column(String)  # <xs:element type="xs:string" name="NUMBEROFLANES"/>
    OFFROADDESCRIPTION = Column(String,
                                nullable=True)  # <xs:element type="xs:string" name="OFFROADDESCRIPTION" nillable="true"/>
    PDFREPORTs = relationship('PdfReport', uselist=False,
                              back_populates='CRASHES')  # one:one <xs:element type="cras:PDFREPORTsType" name="PDFREPORTs" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    PHOTOSTAKEN = Column(Boolean,
                         nullable=True)  # <xs:element name="PHOTOSTAKEN"> nillable to handle the Unknown option
    PEOPLE = relationship(
        'Person')  # one:many <xs:element type="cras:PeopleType" name="People" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    RAMP = Column(String)  # <xs:element type="xs:string" name="RAMP" nillable="true"/>
    REPORTCOUNTYLOCATION = Column(
        Integer)  # <xs:element name="REPORTCOUNTYLOCATION"> (restricted to 03, 23, 24, and 88)
    REPORTDOCUMENTs = relationship(
        'ReportDocument')  # one:many: ReportDocumentsType  # <xs:element type="xs:string" name="REPORTDOCUMENTs" nillable="true"/>
    REPORTNUMBER = Column(String(length=REPORTNUMBER_LEN),
                          primary_key=True)  # <xs:element type="xs:string" name="REPORTNUMBER"/>
    REPORTPHOTOes = relationship(
        'ReportPhoto')  # one:many <xs:element type="xs:string" name="REPORTPHOTOes" nillable="true"/>
    REPORTTYPE = Column(
        String)  # <xs:element name="REPORTTYPE"> (restricted to 'Property Damage Crash', 'Injury Crash', and 'Fatal Crash')
    ROADALIGNMENT = Column(String)  # <xs:element name="ROADALIGNMENT"> (restricted to 00, 01, 02, 03, 88, 99 and '')
    ROADCONDITION = Column(String)  # <xs:element type="xs:string" name="ROADCONDITION"/>
    ROADDIVISION = Column(
        String)  # <xs:element name="ROADDIVISION"> (restricted to 00, 01, 02, 03, 04, 05.01, 88, 99 and '')
    ROADGRADE = Column(
        String)  # <xs:element name="ROADGRADE"> (restricted to 00, 01, 02, 03, 04, 05, 06, 88, 99 and '')
    ROADID = Column(String(length=36), ForeignKey('acrs_roadway.ROADID'))  # <xs:element type="xs:string" name="ROADID"/> (this is a six digit number or a UUID)
    ROADWAY = relationship('Roadway', uselist=False,
                           back_populates='CRASHES')  # one:one <xs:element type="cras:ROADWAYType" name="ROADWAY" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    SCHOOLBUSINVOLVEMENT = Column(
        Integer)  # <xs:element name="SCHOOLBUSINVOLVEMENT"> (restricted to 00, 01, 02, 03, and 99)
    STATEGOVERNMENTPROPERTYNAME = Column(String,
                                         nullable=True)  # <xs:element type="xs:string" name="STATEGOVERNMENTPROPERTYNAME" nillable="true"/>
    SUPERVISOR = Column(String)  # <xs:element type="xs:string" name="SUPERVISOR" nillable="true"/>
    SUPERVISORUSERNAME = Column(String)  # <xs:element type="xs:string" name="SUPERVISORUSERNAME"/>
    SUPERVISORYDATE = Column(DateTime)  # <xs:element type="xs:dateTime" name="SUPERVISORYDATE"/>
    SURFACECONDITION = Column(String)  # <xs:element type="xs:string" name="SURFACECONDITION"/>
    TRAFFICCONTROL = Column(Integer)  # <xs:element type="xs:byte" name="TRAFFICCONTROL"/>
    TRAFFICCONTROLFUNCTIONING = Column(
        Boolean, nullable=True)  # <xs:element name="TRAFFICCONTROLFUNCTIONING"> (restricted to Y, N, U, and '')
    UPDATEDATE = Column(DateTime)  # <xs:element type="xs:string" name="UPDATEDATE"/>
    UPLOADVERSION = Column(String)  # <xs:element type="xs:string" name="UPLOADVERSION"/>
    VEHICLEs = relationship(
        'Vehicle')  # one:many <xs:element type="cras:VEHICLEsType" name="VEHICLEs" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    VERSIONNUMBER = Column(Integer)  # <xs:element name="VERSIONNUMBER">
    WEATHER = Column(Float)  # <xs:element type="xs:float" name="WEATHER"/>
    WITNESSes = relationship('Witness')  # one:many


#########################
#     acrs_approval     #
#########################
class Approval(Base):
    """Sqlalchemy: Data for table acrs_crash"""
    __tablename__ = "acrs_approval"

    AGENCY = Column(String)  # <xs:element type="xs:string" name="AGENCY"/>
    APPROVALDATE = Column(DateTime)  # <xs:element type="xs:dateTime" name="APPROVALDATE"/>
    CADSENT = Column(String, nullable=True)  # <xs:element type="xs:string" name="CADSENT" nillable="true"/>
    CADSENT_DATE = Column(DateTime, nullable=True)  # <xs:element type="xs:string" name="CADSENT_DATE" nillable="true"/>
    CC_NUMBER = Column(String)  # <xs:element type="xs:string" name="CC_NUMBER"/>
    CRASHES = relationship('Crash', back_populates='APPROVAL')
    DATE_INITIATED2 = Column(DateTime)  # <xs:element type="xs:dateTime" name="DATE_INITIATED2"/>
    GROUP_NUMBER = Column(String)  # <xs:element type="xs:string" name="GROUP_NUMBER"/>
    HISTORICALAPPROVALDATAs = Column(String,
                                     nullable=True)  # <xs:element type="xs:string" name="HISTORICALAPPROVALDATAs" nillable="true"/>
    INCIDENT_DATE = Column(DateTime)  # <xs:element type="xs:dateTime" name="INCIDENT_DATE"/>
    INVESTIGATOR = Column(String, nullable=True)  # <xs:element type="xs:string" name="INVESTIGATOR" nillable="true"/>
    REPORT_TYPE = Column(String)  # <xs:element type="xs:string" name="REPORT_TYPE"/>
    SEQ_GUID = Column(String(length=REPORTNUMBER_LEN), ForeignKey('acrs_crash.REPORTNUMBER'),
                      primary_key=True)  # <xs:element type="xs:string" name="SEQ_GUID"/>
    STATUS_CHANGE_DATE = Column(DateTime)  # <xs:element type="xs:dateTime" name="STATUS_CHANGE_DATE"/>
    STATUS_ID = Column(Integer)  # <xs:element type="xs:byte" name="STATUS_ID"/>
    STEP_NUMBER = Column(Integer)  # <xs:element name="STEP_NUMBER"> (restricted to values 1 and 2)
    TR_USERNAME = Column(String)  # <xs:element type="xs:string" name="TR_USERNAME"/>
    UNIT_CODE = Column(String)  # <xs:element name="UNIT_CODE"> (only values 999 and BCPD)


##############################
#     acrs_circumstance      #
##############################
# Inside the CIRCUMSTANCEs tag
class Circumstance(Base):
    """Sqlalchemy: Data for table acrs_circumstance"""
    __tablename__ = "acrs_circumstance"

    CIRCUMSTANCECODE = Column(Float)  # <xs:element type="xs:float" name="CIRCUMSTANCECODE"/>
    CIRCUMSTANCEID = Column(Integer, primary_key=True)  # <xs:element type="xs:int" name="CIRCUMSTANCEID"/>
    CIRCUMSTANCETYPE = Column(
        String)  # <xs:element name="CIRCUMSTANCETYPE"> (restricted to values 'weather', 'road', 'person', and 'vehicle')
    PERSONID = Column(GUID, ForeignKey('acrs_person.PERSONID'))  # <xs:element type="xs:string" name="PERSONID" nillable="true"/>
    REPORTNUMBER = Column(String(length=REPORTNUMBER_LEN),
                          ForeignKey('acrs_crash.REPORTNUMBER'))  # <xs:element type="xs:string" name="REPORTNUMBER"/>
    VEHICLEID = Column(GUID, ForeignKey('acrs_vehicle.VEHICLEID'))  # <xs:element type="xs:string" name="VEHICLEID" nillable="true"/>


###############################
#     acrs_crash_diagram      #
###############################
# Inside the DIAGRAM tag
class CrashDiagram(Base):
    """Sqlalchemy: Data for table acrs_crash_diagrams """
    __tablename__ = "acrs_crash_diagram"

    CRASHDIAGRAM = Column(String)  # <xs:element type="xs:string" name="CRASHDIAGRAM"/>
    CRASHDIAGRAMNATIVE = Column(String)  # <xs:element type="xs:string" name="CRASHDIAGRAMNATIVE"/>
    CRASHES = relationship('Crash', back_populates='DIAGRAM')
    REPORTNUMBER = Column(String(length=REPORTNUMBER_LEN), ForeignKey('acrs_crash.REPORTNUMBER'),
                          primary_key=True)  # <xs:element type="xs:string" name="REPORTNUMBER"/>


####################
#     acrs_ems     #
####################
# Inside EMSes tag
class Ems(Base):
    """Sqlalchemy: Data for table acrs_ems"""
    __tablename__ = "acrs_ems"

    EMSTRANSPORTATIONTYPE = Column(
        String(length=1))  # <xs:element name="EMSTRANSPORTATIONTYPE"> (restricted to G, U and A)
    EMSUNITNUMBER = Column(String(length=1), primary_key=True)  # <xs:element name="EMSUNITNUMBER"> (restricted to A-F)
    INJUREDTAKENBY = Column(String)  # <xs:element type="xs:string" name="INJUREDTAKENBY"/> (IE: Medic # 20)
    INJUREDTAKENTO = Column(String)  # <xs:element type="xs:string" name="INJUREDTAKENTO"/>
    REPORTNUMBER = Column(String(length=REPORTNUMBER_LEN), ForeignKey('acrs_crash.REPORTNUMBER'),
                          primary_key=True)  # <xs:element type="xs:string" name="REPORTNUMBER"/>


####################################
#     acrs_person_info: driver     #
####################################
class PersonInfo(Base):
    """Sqlalchemy: Data for table acrs_person_info"""
    __tablename__ = "acrs_person_info"

    AIRBAGDEPLOYED = Column(
        Integer)  # <xs:element name="AIRBAGDEPLOYED"> (restricted to values 00, 01, 02, 03, 04, 88 and 99)
    ALCOHOLTESTINDICATOR = Column(
        Integer)  # <xs:element name="ALCOHOLTESTINDICATOR"> (restricted to 00, 01, 02, 03, 88 and 99)
    ALCOHOLTESTTYPE = Column(String,
                             nullable=True)  # <xs:element name="ALCOHOLTESTTYPE" nillable="true"> (restricted to 00, 01, 02, 88, 99 and '')
    ATFAULT = Column(Boolean, nullable=True)  # <xs:element name="ATFAULT"> (restricted to values Y, N, and U)
    BAC = Column(String, nullable=True)  # <xs:element type="xs:string" name="BAC" nillable="true"/>
    CONDITION = Column(String)  # <xs:element type="xs:float" name="CONDITION"/> (Nonmotorist type is str)
    CONTINUEDIRECTION = Column(String, nullable=True)
    DRIVERDISTRACTEDBY = Column(Integer)  # <xs:element type="xs:byte" name="DRIVERDISTRACTEDBY"/>
    DRUGTESTINDICATOR = Column(
        Integer)  # <xs:element name="DRUGTESTINDICATOR"> (restricted to 00, 01, 02, 03, 88 and 99)
    DRUGTESTRESULT = Column(String(length=1),
                            nullable=True)  # <xs:element name="DRUGTESTRESULT" nillable="true"> (restricted to P, N, U, A, and '')
    EJECTION = Column(Integer)  # <xs:element name="EJECTION"> (restricted to 00, 01, 02, 03, 04, 88, and 99)
    EMSRUNREPORTNUMBER = Column(String,
                                nullable=True)  # <xs:element type="xs:string" name="EMSRUNREPORTNUMBER" nillable="true"/>
    EMSUNITNUMBER = Column(String(length=1),
                           nullable=True)  # <xs:element name="EMSUNITNUMBER" nillable="true"> (restricted to A, B, C, D, E, J, K, L and '')
    EQUIPMENTPROBLEM = Column(
        Integer)  # <xs:element name="EQUIPMENTPROBLEM"> (restricted to 00, 01, 11, 13, 31, 44, 45, 47, 88 and 99)
    GOINGDIRECTION = Column(String,
                            nullable=True)  # <xs:element type="xs:string" name="GOINGDIRECTION" nillable="true"/>
    HASCDL = Column(Boolean, nullable=True)  # <xs:element name="HASCDL">
    INJURYSEVERITY = Column(Integer)  # <xs:element name="INJURYSEVERITY"> (restricted to 01, 02, 03, 04, and 05)
    PERSON = relationship(
        "Person")  # one:many <xs:element type="cras:PERSONType" name="PERSON"
    # xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    PEDESTRIANACTIONS = Column(Integer)  # <xs:element type="xs:byte" name="PEDESTRIANACTIONS"/>
    PEDESTRIANLOCATION = Column(Float)  # <xs:element type="xs:float" name="PEDESTRIANLOCATION"/>
    PEDESTRIANMOVEMENT = Column(Float)  # <xs:element type="xs:float" name="PEDESTRIANMOVEMENT"/>
    PEDESTRIANOBEYTRAFFICSIGNAL = Column(
        Integer)  # <xs:element name="PEDESTRIANOBEYTRAFFICSIGNAL"> (restricted to 00, 01, 02, 03, 04, 88, and 99)
    PEDESTRIANTYPE = Column(
        Integer)  # <xs:element name="PEDESTRIANTYPE"> (restricted to 01, 02, 03, 05, 06, 07, 88, and 99)
    PEDESTRIANVISIBILITY = Column(
        Integer)  # <xs:element name="PEDESTRIANVISIBILITY"> (restricted to 00, 01, 02, 03, 04, 06, 07, 88 and 99)
    PERSONID = Column(GUID, ForeignKey('acrs_person.PERSONID'), primary_key=True)  # <xs:element type="xs:string" name="PERSONID"/>
    REPORTNUMBER = Column(String(length=REPORTNUMBER_LEN),
                          ForeignKey('acrs_crash.REPORTNUMBER'))  # <xs:element type="xs:string" name="REPORTNUMBER"/>
    SAFETYEQUIPMENT = Column(Float)  # <xs:element type="xs:float" name="SAFETYEQUIPMENT"/>
    SEAT = Column(Integer)  # <xs:element name="SEAT"> (restricted to 00, 01, 02, 03, 88, and 99)
    SEATINGLOCATION = Column(Float)  # <xs:element type="xs:float" name="SEATINGLOCATION"/>
    SEATINGROW = Column(Integer)  # <xs:element type="xs:byte" name="SEATINGROW"/>
    SUBSTANCEUSE = Column(Integer, nullable=True)  # <xs:element type="xs:byte" name="SUBSTANCEUSE"/>
    UNITNUMBERFIRSTSTRIKE = Column(String)  # <xs:element name="UNITNUMBERFIRSTSTRIKE"> (restricted to 1, 2 and '')
    VEHICLEID = Column(GUID, ForeignKey('acrs_vehicle.VEHICLEID'))  # <xs:element type="xs:string" name="VEHICLEID"/>


#######################
#     acrs_person     #
#######################
class Person(Base):
    """Sqlalchemy: Data for table acrs_person"""
    __tablename__ = "acrs_person"

    ADDRESS = Column(String)  # <xs:element type="xs:string" name="ADDRESS"/>
    CITATIONCODES = relationship(
        'CitationCode')  # one:many <xs:element type="cras:CITATIONCODEType" name="CITATIONCODE" maxOccurs="unbounded"
    # minOccurs="0" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    CITY = Column(String)  # <xs:element type="xs:string" name="CITY"/>
    COMPANY = Column(String, nullable=True)  # <xs:element type="xs:string" name="COMPANY" nillable="true"/>
    COUNTRY = Column(String, nullable=True)  # <xs:element type="xs:string" name="COUNTRY" nillable="true"/>
    COUNTY = Column(String, nullable=True)  # <xs:element type="xs:string" name="COUNTY" nillable="true"/>
    DLCLASS = Column(String, nullable=True)  # <xs:element type="xs:string" name="DLCLASS" nillable="true"/>
    DLNUMBER = Column(String)  # <xs:element type="xs:string" name="DLNUMBER"/>
    DLSTATE = Column(String)  # <xs:element type="xs:string" name="DLSTATE"/>
    DOB = Column(Date)  # <xs:element type="xs:string" name="DOB"/>
    FIRSTNAME = Column(String)  # <xs:element type="xs:string" name="FIRSTNAME"/>
    HOMEPHONE = Column(String, nullable=True)  # <xs:element type="xs:string" name="HOMEPHONE" nillable="true"/>
    LASTNAME = Column(String)  # <xs:element type="xs:string" name="LASTNAME"/>
    MIDDLENAME = Column(String, nullable=True)  # <xs:element type="xs:string" name="MIDDLENAME" nillable="true"/>
    OTHERPHONE = Column(String)  # <xs:element type="xs:string" name="OTHERPHONE"/>
    PERSONID = Column(GUID, primary_key=True)  # <xs:element type="xs:string" name="PERSONID"/>
    RACE = Column(String, nullable=True)  # <xs:element type="xs:string" name="RACE" nillable="true"/>
    REPORTNUMBER = Column(String(length=REPORTNUMBER_LEN),
                          ForeignKey('acrs_crash.REPORTNUMBER'))  # <xs:element type="xs:string" name="REPORTNUMBER"/>
    SEX = Column(String)  # <xs:element name="SEX"> (restricted to 'F', 'M', 'U', and '')
    STATE = Column(String)  # <xs:element type="xs:string" name="STATE"/>
    VEHICLE = relationship('Vehicle')
    ZIP = Column(String)  # <xs:element type="xs:string" name="ZIP"/>


###############################
#     acrs_citation_code      #
###############################
# Inside the CITATIONCODES tag
class CitationCode(Base):
    """Sqlalchemy: Data for table acrs_citation_code"""
    __tablename__ = "acrs_citation_code"

    CITATIONNUMBER = Column(String(length=15), primary_key=True)  # <xs:element type="xs:string" name="CITATIONNUMBER"/>
    PERSONID = Column(GUID, ForeignKey('acrs_person.PERSONID'))  # <xs:element type="xs:string" name="PERSONID"/>
    REPORTNUMBER = Column(String(length=REPORTNUMBER_LEN),
                          ForeignKey('acrs_crash.REPORTNUMBER'))  # <xs:element type="xs:string" name="REPORTNUMBER"/>


###########################
#     acrs_pdf_report     #
###########################
# Inside the PDFREPORTs tag
class PdfReport(Base):
    """Sqlalchemy: Data for table acrs_pdf_report"""
    __tablename__ = "acrs_pdf_report"

    CHANGEDBY = Column(String)  # <xs:element type="xs:string" name="CHANGEDBY"/>
    CRASHES = relationship('Crash', back_populates='PDFREPORTs')
    DATESTATUSCHANGED = Column(DateTime)  # <xs:element type="xs:dateTime" name="DATESTATUSCHANGED"/>
    PDFREPORT1 = Column(String)  # <xs:element type="xs:string" name="PDFREPORT1"/>
    PDF_ID = Column(Integer, primary_key=True)  # <xs:element type="xs:int" name="PDF_ID"/>
    REPORTNUMBER = Column(String(length=REPORTNUMBER_LEN),
                          ForeignKey('acrs_crash.REPORTNUMBER'))  # <xs:element type="xs:string" name="REPORTNUMBER"/>
    STATUS = Column(String)  # <xs:element type="xs:string" name="STATUS"/>


###########################
#     acrs_report_doc     #
###########################
class ReportDocument(Base):
    """Sqlalchemy: Data for table acrs_report_doc"""
    __tablename__ = "acrs_report_doc"
    NULLCOLUMN = Column(Integer, primary_key=True)
    REPORTNUMBER = Column(String(length=REPORTNUMBER_LEN),
                          ForeignKey('acrs_crash.REPORTNUMBER'))  # <xs:element type="xs:string" name="REPORTNUMBER"/>


#############################
#     acrs_report_photo     #
#############################
class ReportPhoto(Base):
    """Sqlalchemy: Data for table acrs_report_photo"""
    __tablename__ = "acrs_report_photo"
    NULLCOLUMN = Column(Integer, primary_key=True)
    REPORTNUMBER = Column(String(length=REPORTNUMBER_LEN),
                          ForeignKey('acrs_crash.REPORTNUMBER'))  # <xs:element type="xs:string" name="REPORTNUMBER"/>


########################
#     acrs_roadway     #
########################
class Roadway(Base):
    """Sqlalchemy: Data for table acrs_roadway"""
    __tablename__ = "acrs_roadway"

    COUNTY = Column(Integer)  # <xs:element name="COUNTY" minOccurs="0"> (restricted to 3, 23, and 24)
    CRASHES = relationship('Crash', back_populates='ROADWAY')
    LOGMILE_DIR = Column(String,
                         nullable=True)  # <xs:element name="LOGMILE_DIR" minOccurs="0"> (restricted to N, S, E, W, U, and '')
    MILEPOINT = Column(Float, nullable=True)  # <xs:element type="xs:float" name="MILEPOINT" minOccurs="0"/>
    MUNICIPAL = Column(Integer,
                       nullable=True)  # <xs:element name="MUNICIPAL" minOccurs="0"> (restricted to 999 and 000)
    MUNICIPAL_AREA_CODE = Column(Integer,
                                 nullable=True)  # <xs:element name="MUNICIPAL_AREA_CODE" minOccurs="0"> (restricted to 999 and 000)
    REFERENCE_MUNI = Column(Integer,
                            nullable=True)  # <xs:element name="REFERENCE_MUNI" minOccurs="0"> (restricted to 999 and 000)
    REFERENCE_ROADNAME = Column(String,
                                nullable=True)  # <xs:element type="xs:string" name="REFERENCE_ROADNAME" minOccurs="0"/>
    REFERENCE_ROUTE_NUMBER = Column(String,
                                    nullable=True)  # <xs:element type="xs:string" name="REFERENCE_ROUTE_NUMBER" minOccurs="0"/>
    REFERENCE_ROUTE_SUFFIX = Column(String,
                                    nullable=True)  # <xs:element name="REFERENCE_ROUTE_SUFFIX" minOccurs="0" nillable="true"> (restricted to E, B, AL, AV, 6, IR, and '')
    REFERENCE_ROUTE_TYPE = Column(String,
                                  nullable=True)  # <xs:element type="xs:string" name="REFERENCE_ROUTE_TYPE" minOccurs="0"/>
    ROADID = Column(String(length=36),
                    primary_key=True)  # <xs:element type="xs:string" name="ROADID" minOccurs="0"/> This is a six digit number, or a UUID
    ROAD_NAME = Column(String, nullable=True)  # <xs:element type="xs:string" name="ROAD_NAME" minOccurs="0"/>
    ROUTE_NUMBER = Column(String, nullable=True)  # <xs:element type="xs:string" name="ROUTE_NUMBER" minOccurs="0"/>
    ROUTE_SUFFIX = Column(String,
                          nullable=True)  # <xs:element name="ROUTE_SUFFIX" minOccurs="0" nillable="true"> (restricted to E, AL, B, A and '')
    ROUTE_TYPE = Column(String, nullable=True)  # <xs:element name="ROUTE_TYPE" minOccurs="0">


#########################
#     acrs_vehicle      #
#########################
# Inside the VEHICLEs.ACRSVEHICLE tag
class Vehicle(Base):
    """Sqlalchemy: Data for table acrs_vehicle"""
    __tablename__ = "acrs_vehicle"

    COMMERCIALVEHICLE = relationship(
        'CommercialVehicle')  # one:many <xs:element name="COMMERCIALVEHICLE" nillable="true">
    CONTINUEDIRECTION = Column(String)  # <xs:element name="CONTINUEDIRECTION">
    DAMAGEDAREAs = relationship('DamagedArea')  # one:many <xs:element type="cras:DAMAGEDAREAsType" name="DAMAGEDAREAs" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    DAMAGEEXTENT = Column(Integer)  # <xs:element name="DAMAGEEXTENT"> (restricted to 00, 01, 02, 03, 04, 05, 88 and 99)
    DRIVERLESSVEHICLE = Column(Boolean, nullable=True)  # <xs:element name="DRIVERLESSVEHICLE"> (restricted to 'Y', 'N', and 'U')
    DRIVERs = relationship(
        'PersonInfo')  # one:many <xs:element type="cras:DRIVERsType" name="DRIVERs" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    EMERGENCYMOTORVEHICLEUSE = Column(
        Boolean, nullable=True)  # <xs:element name="EMERGENCYMOTORVEHICLEUSE"> (restricted to 'Y', 'N', and 'U')
    EVENTS = relationship('Event')  # one:many <xs:element type="cras:EVENTType" name="EVENT" maxOccurs="unbounded" minOccurs="0" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    FIRE = Column(Boolean, nullable=True)  # <xs:element name="FIRE"> (restricted to 'Y', 'N', and 'U')
    FIRSTIMPACT = Column(String)  # <xs:element type="xs:string" name="FIRSTIMPACT"/>
    GOINGDIRECTION = Column(String)  # <xs:element name="GOINGDIRECTION"> (restricted to N, S, E, W, U, and '')
    HITANDRUN = Column(Boolean, nullable=True)  # <xs:element name="HITANDRUN"> (restricted to 'Y', 'N', and 'U')
    INSURANCEPOLICYNUMBER = Column(String)  # <xs:element type="xs:string" name="INSURANCEPOLICYNUMBER"/>
    INSURER = Column(String)  # <xs:element type="xs:string" name="INSURER"/>
    LICENSEPLATENUMBER = Column(String)  # <xs:element type="xs:string" name="LICENSEPLATENUMBER"/>
    LICENSEPLATESTATE = Column(String)  # <xs:element type="xs:string" name="LICENSEPLATESTATE"/>
    MAINIMPACT = Column(Integer, nullable=True)  # <xs:element type="xs:string" name="MAINIMPACT"/>
    MOSTHARMFULEVENT = Column(Float)  # <xs:element type="xs:float" name="MOSTHARMFULEVENT"/>
    OWNER = relationship(
        'Person', back_populates='VEHICLE')  # one:one <xs:element type="cras:OWNERType" name="OWNER" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    OWNERID = Column(GUID, ForeignKey('acrs_person.PERSONID'))  # <xs:element type="xs:string" name="OWNERID"/>
    PARKEDVEHICLE = Column(Boolean, nullable=True)  # <xs:element name="PARKEDVEHICLE">
    PASSENGERs = relationship(
        'PersonInfo')  # one:many <xs:element name="PASSENGERs">
    REGISTRATIONEXPIRATIONYEAR = Column(
        String, nullable=True)  # <xs:element type="xs:string" name="REGISTRATIONEXPIRATIONYEAR" nillable="true"/>
    REPORTNUMBER = Column(String(length=REPORTNUMBER_LEN), ForeignKey('acrs_crash.REPORTNUMBER'))  # <xs:element type="xs:string" name="REPORTNUMBER"/>
    SFVEHICLEINTRANSPORT = Column(Integer)  # <xs:element type="xs:byte" name="SFVEHICLEINTRANSPORT"/>
    SPEEDLIMIT = Column(Integer)  # <xs:element type="xs:byte" name="SPEEDLIMIT"/>
    TOWEDUNITTYPE = Column(Integer)  # <xs:element name="TOWEDUNITTYPE"> (restricted to 00, 01, 03, 06, 07, 88 and 99)
    TOWEDUNITs = relationship('TowedUnit')  # one:many <xs:element name="TOWEDUNITs">
    UNITNUMBER = Column(Integer)  # <xs:element name="UNITNUMBER"> (restricted to values 1-10)
    VEHICLEBODYTYPE = Column(String)  # <xs:element type="xs:string" name="VEHICLEBODYTYPE"/>
    VEHICLEID = Column(GUID, primary_key=True)  # <xs:element type="xs:string" name="VEHICLEID"/>
    VEHICLEMAKE = Column(String)  # <xs:element type="xs:string" name="VEHICLEMAKE"/>
    VEHICLEMODEL = Column(String)  # <xs:element type="xs:string" name="VEHICLEMODEL"/>
    VEHICLEMOVEMENT = Column(Float, nullable=True)  # <xs:element type="xs:float" name="VEHICLEMOVEMENT"/>
    VEHICLEREMOVEDBY = Column(String,
                              nullable=True)  # <xs:element type="xs:string" name="VEHICLEREMOVEDBY" nillable="true"/>
    VEHICLEREMOVEDTO = Column(String,
                              nullable=True)  # <xs:element type="xs:string" name="VEHICLEREMOVEDTO" nillable="true"/>
    VEHICLETOWEDAWAY = Column(String(length=1),
                              nullable=True)  # <xs:element name="VEHICLETOWEDAWAY"> (restricted to Y, N, U and '')
    VEHICLEUSEs = relationship('VehicleUse')  # one:many <xs:element type="cras:VEHICLEUSEsType" name="VEHICLEUSEs" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    VEHICLEYEAR = Column(String)  # <xs:element type="xs:string" name="VEHICLEYEAR"/>
    VIN = Column(String)  # <xs:element type="xs:string" name="VIN"/>


##########################
#     acrs_witnesses     #
##########################
class Witness(Base):
    """Sqlalchemy: Data for table acrs_witness"""
    __tablename__ = "acrs_witness"

    # PERSON: PersonType  # <xs:element type="cras:PERSONType" name="PERSON" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    PERSONID = Column(GUID, ForeignKey('acrs_person.PERSONID'), primary_key=True)  # <xs:element type="xs:string" name="PERSONID"/>
    REPORTNUMBER = Column(String(length=REPORTNUMBER_LEN), ForeignKey('acrs_crash.REPORTNUMBER'), primary_key=True)  # <xs:element type="xs:string" name="REPORTNUMBER"/>


####################################
#     acrs_commercial_vehicle      #
####################################
class CommercialVehicle(Base):
    """Sqlalchemy: Data for table acrs_commercial_vehicle"""
    __tablename__ = "acrs_commercial_vehicle"

    BODYTYPE = Column(String)  # <xs:element type="xs:float" name="BODYTYPE" minOccurs="0"/>
    BUSUSE = Column(
        String)  # <xs:element name="BUSUSE" minOccurs="0"> (restricted to 00, 01, 02, 03, 04, 05, 07, 88, 99 and '')
    CARRIERCLASSIFICATION = Column(
        Integer)  # <xs:element name="CARRIERCLASSIFICATION" minOccurs="0"> (restricted to 00, 01, 02, 03, 04, 88 and 99)
    CITY = Column(String)  # <xs:element type="xs:string" name="CITY" minOccurs="0"/>
    CONFIGURATION = Column(Integer)  # <xs:element type="xs:byte" name="CONFIGURATION" minOccurs="0"/>
    COUNTRY = Column(String,
                     nullable=True)  # <xs:element type="xs:string" name="COUNTRY" minOccurs="0" nillable="true"/>
    DOTNUMBER = Column(String)  # <xs:element type="xs:string" name="DOTNUMBER" minOccurs="0"/>
    GVW = Column(Integer)  # <xs:element name="GVW" minOccurs="0"> (restricted to 00, 01, 02, 03, 88 and 99)
    HAZMATCLASS = Column(String)  # <xs:element name="HAZMATCLASS" minOccurs="0"> (restricted to 01, 02, 03, 10, and "")
    HAZMATNAME = Column(String,
                        nullable=True)  # <xs:element type="xs:string" name="HAZMATNAME" minOccurs="0" nillable="true"/>
    HAZMATNUMBER = Column(String,
                          nullable=True)  # <xs:element type="xs:string" name="HAZMATNUMBER" minOccurs="0" nillable="true"/>
    HAZMATSPILL = Column(String)  # <xs:element name="HAZMATSPILL" minOccurs="0"> (restricted to Y, N, U, and '')
    MCNUMBER = Column(String)  # <xs:element type="xs:string" name="MCNUMBER" minOccurs="0"/>
    NAME = Column(String)  # <xs:element type="xs:string" name="NAME" minOccurs="0"/>
    NUMBEROFAXLES = Column(String)  # <xs:element type="xs:string" name="NUMBEROFAXLES" minOccurs="0"/>
    PLACARDVISIBLE = Column(String)  # <xs:element name="PLACARDVISIBLE" minOccurs="0"> (restricted to Y, N, U, '')
    POSTALCODE = Column(String)  # <xs:element type="xs:string" name="POSTALCODE" minOccurs="0"/>
    STATE = Column(String)  # <xs:element type="xs:string" name="STATE" minOccurs="0"/>
    STREET = Column(String)  # <xs:element type="xs:string" name="STREET" minOccurs="0"/>
    VEHICLEID = Column(GUID, ForeignKey('acrs_vehicle.VEHICLEID'),
                       primary_key=True)  # <xs:element type="xs:string" name="VEHICLEID" minOccurs="0"/>
    WEIGHT = Column(String, nullable=True)  # <xs:element type="xs:string" name="WEIGHT" minOccurs="0" nillable="true"/>
    WEIGHTUNIT = Column(String,
                        nullable=True)  # <xs:element type="xs:string" name="WEIGHTUNIT" minOccurs="0" nillable="true"/>


##############################
#     acrs_damaged_areas     #
##############################
# Inside DAMAGEDAREAs tag
class DamagedArea(Base):
    """Sqlalchemy: Data for table acrs_damaged_areas"""
    __tablename__ = "acrs_damaged_area"

    DAMAGEID = Column(Integer, primary_key=True)  # <xs:element type="xs:int" name="DAMAGEID"/>
    IMPACTTYPE = Column(Integer)  # <xs:element type="xs:byte" name="IMPACTTYPE"/>
    VEHICLEID = Column(GUID, ForeignKey('acrs_vehicle.VEHICLEID'))  # <xs:element type="xs:string" name="VEHICLEID"/>


#######################
#     acrs_events     #
#######################
# Inside EVENTS tag
class Event(Base):
    """Sqlalchemy: Data for table acrs_events"""
    __tablename__ = "acrs_event"

    EVENTID = Column(Integer, primary_key=True)  # <xs:element type="xs:int" name="EVENTID"/>
    EVENTSEQUENCE = Column(Integer)  # <xs:element type="xs:byte" name="EVENTSEQUENCE"/>
    EVENTTYPE = Column(Integer)  # <xs:element type="xs:byte" name="EVENTTYPE"/>
    VEHICLEID = Column(GUID, ForeignKey('acrs_vehicle.VEHICLEID'))  # <xs:element type="xs:string" name="VEHICLEID"/>


###########################
#     acrs_towed_unit     #
###########################
# Inside the TOWEDUNITs tag
class TowedUnit(Base):
    """Sqlalchemy: Data for table acrs_towed_unit"""
    __tablename__ = "acrs_towed_unit"

    INSURANCEPOLICYNUMBER = Column(String)  # <xs:element type="xs:string" name="INSURANCEPOLICYNUMBER"/>
    INSURER = Column(String)  # <xs:element type="xs:string" name="INSURER"/>
    LICENSEPLATENUMBER = Column(String)  # <xs:element type="xs:string" name="LICENSEPLATENUMBER"/>
    LICENSEPLATESTATE = Column(String)  # <xs:element type="xs:string" name="LICENSEPLATESTATE"/>
    OWNER = relationship('Person')  # <xs:element type="cras:OWNERType" name="OWNER" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    OWNERID = Column(GUID, ForeignKey('acrs_person.PERSONID'))  # <xs:element type="xs:string" name="OWNERID"/>
    TOWEDID = Column(GUID, primary_key=True)  # <xs:element type="xs:string" name="TOWEDID"/>
    UNITNUMBER = Column(String)  # <xs:element type="xs:string" name="UNITNUMBER" nillable="true"/>
    VEHICLEID = Column(GUID, ForeignKey('acrs_vehicle.VEHICLEID'))  # <xs:element type="xs:string" name="VEHICLEID"/>
    VEHICLEMAKE = Column(String)  # <xs:element type="xs:string" name="VEHICLEMAKE"/>
    VEHICLEMODEL = Column(String)  # <xs:element type="xs:string" name="VEHICLEMODEL"/>
    VEHICLEYEAR = Column(Integer)  # <xs:element type="xs:short" name="VEHICLEYEAR"/>
    VIN = Column(String)  # <xs:element type="xs:string" name="VIN"/>


#############################
#     acrs_vehicle_uses     #
#############################
# Inside VEHICLEUSEs tag
class VehicleUse(Base):
    """Sqlalchemy: Data for table acrs_vehicle_use"""
    __tablename__ = "acrs_vehicle_use"

    ID = Column(Integer, primary_key=True)  # <xs:element type="xs:int" name="ID"/>
    VEHICLEID = Column(GUID, ForeignKey('acrs_vehicle.VEHICLEID'))  # <xs:element type="xs:string" name="VEHICLEID"/>
    VEHICLEUSECODE = Column(Integer)  # <xs:element name="VEHICLEUSECODE"> (restricted to 00, 01, 02, and 03)
