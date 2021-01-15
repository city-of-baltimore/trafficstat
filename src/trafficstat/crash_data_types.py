"""Types used in src/crash_data_ingestor.py"""
# pylint:disable=line-too-long
# pylint:disable=too-few-public-methods
# pylint:disable=inherit-non-class ; Inheriting 'TypedDict', which is not a class. https://bugs.python.org/issue41973
from collections import OrderedDict
from typing import Any, List, Optional, Sequence, Tuple, TypedDict, Union
from datetime import date, datetime
import uuid

from sqlalchemy import Column  # type: ignore
from sqlalchemy.ext.declarative import declarative_base  # type: ignore
from sqlalchemy.types import Boolean, CHAR, Date, DateTime, Float, Integer, String, TypeDecorator  # type: ignore
from sqlalchemy.dialects.postgresql import UUID  # type: ignore
from sqlalchemy.ext.declarative import DeclarativeMeta  # type: ignore


Base: DeclarativeMeta = declarative_base()

# definitions for typing
SingleAttrElement = OrderedDict[str, Optional[str]]
MultipleAttrElement = List[SingleAttrElement]
SqlExecuteType = Sequence[Union[Tuple[Any], Any]]


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


#########################
#     acrs_approval     #
#########################
class Approval(Base):
    """Sqlalchemy: Data for table acrs_crashes"""
    __tablename__ = "acrs_approval"

    AGENCY = Column(String)  # <xs:element type="xs:string" name="AGENCY"/>
    APPROVALDATE = Column(DateTime)  # <xs:element type="xs:dateTime" name="APPROVALDATE"/>
    CADSENT = Column(String, nullable=True)  # <xs:element type="xs:string" name="CADSENT" nillable="true"/>
    CADSENT_DATE = Column(DateTime, nullable=True)  # <xs:element type="xs:string" name="CADSENT_DATE" nillable="true"/>
    CC_NUMBER = Column(String)  # <xs:element type="xs:string" name="CC_NUMBER"/>
    DATE_INITIATED2 = Column(DateTime)  # <xs:element type="xs:dateTime" name="DATE_INITIATED2"/>
    GROUP_NUMBER = Column(String)  # <xs:element type="xs:string" name="GROUP_NUMBER"/>
    HISTORICALAPPROVALDATAs = Column(String, nullable=True)  # <xs:element type="xs:string" name="HISTORICALAPPROVALDATAs" nillable="true"/>
    INCIDENT_DATE = Column(DateTime)  # <xs:element type="xs:dateTime" name="INCIDENT_DATE"/>
    INVESTIGATOR = Column(String, nullable=True)  # <xs:element type="xs:string" name="INVESTIGATOR" nillable="true"/>
    REPORT_TYPE = Column(String)  # <xs:element type="xs:string" name="REPORT_TYPE"/>
    SEQ_GUID = Column(String, primary_key=True)  # <xs:element type="xs:string" name="SEQ_GUID"/>
    STATUS_CHANGE_DATE = Column(DateTime)  # <xs:element type="xs:dateTime" name="STATUS_CHANGE_DATE"/>
    STATUS_ID = Column(Integer)  # <xs:element type="xs:byte" name="STATUS_ID"/>
    STEP_NUMBER = Column(Integer)  # <xs:element name="STEP_NUMBER"> (restricted to values 1 and 2)
    TR_USERNAME = Column(String)  # <xs:element type="xs:string" name="TR_USERNAME"/>
    UNIT_CODE = Column(String)  # <xs:element name="UNIT_CODE"> (only values 999 and BCPD)


class ApprovalDataType(TypedDict):
    """Data for table acrs_approval"""
    AGENCY: str  # <xs:element type="xs:string" name="AGENCY"/>
    APPROVALDATE: datetime  # <xs:element type="xs:dateTime" name="APPROVALDATE"/>
    CADSENT: Optional[str]  # <xs:element type="xs:string" name="CADSENT" nillable="true"/>
    CADSENT_DATE: Optional[datetime]  # <xs:element type="xs:string" name="CADSENT_DATE" nillable="true"/>
    CC_NUMBER: str  # <xs:element type="xs:string" name="CC_NUMBER"/>
    DATE_INITIATED2: datetime  # <xs:element type="xs:dateTime" name="DATE_INITIATED2"/>
    GROUP_NUMBER: str  # <xs:element type="xs:string" name="GROUP_NUMBER"/>
    HISTORICALAPPROVALDATAs: Optional[List[str]]  # <xs:element type="xs:string" name="HISTORICALAPPROVALDATAs" nillable="true"/>
    INCIDENT_DATE: datetime  # <xs:element type="xs:dateTime" name="INCIDENT_DATE"/>
    INVESTIGATOR: Optional[str]  # <xs:element type="xs:string" name="INVESTIGATOR" nillable="true"/>
    REPORT_TYPE: str  # <xs:element type="xs:string" name="REPORT_TYPE"/>
    SEQ_GUID: str  # <xs:element type="xs:string" name="SEQ_GUID"/>
    STATUS_CHANGE_DATE: datetime  # <xs:element type="xs:dateTime" name="STATUS_CHANGE_DATE"/>
    STATUS_ID: int  # <xs:element type="xs:byte" name="STATUS_ID"/>
    STEP_NUMBER: int  # <xs:element name="STEP_NUMBER"> (restricted to values 1 and 2)
    TR_USERNAME: str  # <xs:element type="xs:string" name="TR_USERNAME"/>
    UNIT_CODE: str  # <xs:element name="UNIT_CODE"> (only values 999 and BCPD)


##############################
#     acrs_circumstances     #
##############################
# Inside the CIRCUMSTANCEs tag
class Circumstance(Base):
    """Sqlalchemy: Data for table acrs_circumstances"""
    __tablename__ = "acrs_circumstances"

    CIRCUMSTANCECODE = Column(Float)  # <xs:element type="xs:float" name="CIRCUMSTANCECODE"/>
    CIRCUMSTANCEID = Column(Integer, primary_key=True)  # <xs:element type="xs:int" name="CIRCUMSTANCEID"/>
    CIRCUMSTANCETYPE = Column(String)  # <xs:element name="CIRCUMSTANCETYPE"> (restricted to values 'weather', 'road', 'person', and 'vehicle')
    PERSONID = Column(GUID)  # <xs:element type="xs:string" name="PERSONID" nillable="true"/>
    REPORTNUMBER = Column(String)  # <xs:element type="xs:string" name="REPORTNUMBER"/>
    VEHICLEID = Column(GUID)  # <xs:element type="xs:string" name="VEHICLEID" nillable="true"/>


class CircumstanceType(TypedDict):
    """Data for table acrs_circumstances"""
    CIRCUMSTANCECODE: float  # <xs:element type="xs:float" name="CIRCUMSTANCECODE"/>
    CIRCUMSTANCEID: int  # <xs:element type="xs:int" name="CIRCUMSTANCEID"/>
    CIRCUMSTANCETYPE: str  # <xs:element name="CIRCUMSTANCETYPE"> (restricted to values 'weather', 'road', 'person', and 'vehicle')
    PERSONID: Optional[uuid.UUID]  # <xs:element type="xs:string" name="PERSONID" nillable="true"/>
    REPORTNUMBER: str  # <xs:element type="xs:string" name="REPORTNUMBER"/>
    VEHICLEID: Optional[uuid.UUID]  # <xs:element type="xs:string" name="VEHICLEID" nillable="true"/>


class CircumstancesType(TypedDict):
    """Multiple instance of CircumstanceType"""
    CIRCUMSTANCE: List[CircumstanceType]


###############################
#     acrs_citation_codes     #
###############################
# Inside the CITATIONCODES tag
class CitationCode(Base):
    """Sqlalchemy: Data for table acrs_citation_codes"""
    __tablename__ = "acrs_citation_codes"

    CITATIONNUMBER = Column(String, primary_key=True)  # <xs:element type="xs:string" name="CITATIONNUMBER"/>
    PERSONID = Column(GUID)  # <xs:element type="xs:string" name="PERSONID"/>
    REPORTNUMBER = Column(String)  # <xs:element type="xs:string" name="REPORTNUMBER"/>


class CitationCodeType(TypedDict):
    """Data for table acrs_citation_codes"""
    CITATIONNUMBER: str  # <xs:element type="xs:string" name="CITATIONNUMBER"/>
    PERSONID: uuid.UUID  # <xs:element type="xs:string" name="PERSONID"/>
    REPORTNUMBER: str  # <xs:element type="xs:string" name="REPORTNUMBER"/>


class CitationCodesType(TypedDict):
    """Multiple instance of CitationCodeType"""
    CITATIONCODE: List[CitationCodeType]


###############################
#     acrs_crash_diagrams     #
###############################
# Inside the DIAGRAM tag
class CrashDiagram(Base):
    """Sqlalchemy: Data for table acrs_crash_diagrams"""
    __tablename__ = "acrs_crash_diagrams"

    CRASHDIAGRAM = Column(String)  # <xs:element type="xs:string" name="CRASHDIAGRAM"/>
    CRASHDIAGRAMNATIVE = Column(String)  # <xs:element type="xs:string" name="CRASHDIAGRAMNATIVE"/>
    REPORTNUMBER = Column(String, primary_key=True)  # <xs:element type="xs:string" name="REPORTNUMBER"/>


class CrashDiagramType(TypedDict):
    """Data for table acrs_crash_diagrams"""
    CRASHDIAGRAM: str  # <xs:element type="xs:string" name="CRASHDIAGRAM"/>
    CRASHDIAGRAMNATIVE: str  # <xs:element type="xs:string" name="CRASHDIAGRAMNATIVE"/>
    REPORTNUMBER: str  # <xs:element type="xs:string" name="REPORTNUMBER"/>


####################################
#     acrs_commercial_vehicles     #
####################################
class CommercialVehicles(Base):
    """Sqlalchemy: Data for table acrs_commercial_vehicles"""
    __tablename__ = "acrs_commercial_vehicles"

    BODYTYPE = Column(String)  # <xs:element type="xs:float" name="BODYTYPE" minOccurs="0"/>
    BUSUSE = Column(String)  # <xs:element name="BUSUSE" minOccurs="0"> (restricted to 00, 01, 02, 03, 04, 05, 07, 88, 99 and '')
    CARRIERCLASSIFICATION = Column(Integer)  # <xs:element name="CARRIERCLASSIFICATION" minOccurs="0"> (restricted to 00, 01, 02, 03, 04, 88 and 99)
    CITY = Column(String)  # <xs:element type="xs:string" name="CITY" minOccurs="0"/>
    CONFIGURATION = Column(Integer)  # <xs:element type="xs:byte" name="CONFIGURATION" minOccurs="0"/>
    COUNTRY = Column(String, nullable=True)  # <xs:element type="xs:string" name="COUNTRY" minOccurs="0" nillable="true"/>
    DOTNUMBER = Column(String)  # <xs:element type="xs:string" name="DOTNUMBER" minOccurs="0"/>
    GVW = Column(Integer)  # <xs:element name="GVW" minOccurs="0"> (restricted to 00, 01, 02, 03, 88 and 99)
    HAZMATCLASS = Column(String)  # <xs:element name="HAZMATCLASS" minOccurs="0"> (restricted to 01, 02, 03, 10, and "")
    HAZMATNAME = Column(String, nullable=True)  # <xs:element type="xs:string" name="HAZMATNAME" minOccurs="0" nillable="true"/>
    HAZMATNUMBER = Column(String, nullable=True)  # <xs:element type="xs:string" name="HAZMATNUMBER" minOccurs="0" nillable="true"/>
    HAZMATSPILL = Column(String)  # <xs:element name="HAZMATSPILL" minOccurs="0"> (restricted to Y, N, U, and '')
    MCNUMBER = Column(String)  # <xs:element type="xs:string" name="MCNUMBER" minOccurs="0"/>
    NAME = Column(String)  # <xs:element type="xs:string" name="NAME" minOccurs="0"/>
    NUMBEROFAXLES = Column(String)  # <xs:element type="xs:string" name="NUMBEROFAXLES" minOccurs="0"/>
    PLACARDVISIBLE = Column(String)  # <xs:element name="PLACARDVISIBLE" minOccurs="0"> (restricted to Y, N, U, '')
    POSTALCODE = Column(String)  # <xs:element type="xs:string" name="POSTALCODE" minOccurs="0"/>
    STATE = Column(String)  # <xs:element type="xs:string" name="STATE" minOccurs="0"/>
    STREET = Column(String)  # <xs:element type="xs:string" name="STREET" minOccurs="0"/>
    VEHICLEID = Column(GUID, primary_key=True)  # <xs:element type="xs:string" name="VEHICLEID" minOccurs="0"/>
    WEIGHT = Column(String, nullable=True)  # <xs:element type="xs:string" name="WEIGHT" minOccurs="0" nillable="true"/>
    WEIGHTUNIT = Column(String, nullable=True)  # <xs:element type="xs:string" name="WEIGHTUNIT" minOccurs="0" nillable="true"/>


class CommercialVehicleType(TypedDict):
    """Data for table acrs_commercial_vehicles"""
    BODYTYPE: str  # <xs:element type="xs:float" name="BODYTYPE" minOccurs="0"/>
    BUSUSE: str  # <xs:element name="BUSUSE" minOccurs="0"> (restricted to 00, 01, 02, 03, 04, 05, 07, 88, 99 and '')
    CARRIERCLASSIFICATION: int  # <xs:element name="CARRIERCLASSIFICATION" minOccurs="0"> (restricted to 00, 01, 02, 03, 04, 88 and 99)
    CITY: str  # <xs:element type="xs:string" name="CITY" minOccurs="0"/>
    CONFIGURATION: int  # <xs:element type="xs:byte" name="CONFIGURATION" minOccurs="0"/>
    COUNTRY: Optional[str]  # <xs:element type="xs:string" name="COUNTRY" minOccurs="0" nillable="true"/>
    DOTNUMBER: str  # <xs:element type="xs:string" name="DOTNUMBER" minOccurs="0"/>
    GVW: int  # <xs:element name="GVW" minOccurs="0"> (restricted to 00, 01, 02, 03, 88 and 99)
    HAZMATCLASS: str  # <xs:element name="HAZMATCLASS" minOccurs="0"> (restricted to 01, 02, 03, 10, and "")
    HAZMATNAME: Optional[str]  # <xs:element type="xs:string" name="HAZMATNAME" minOccurs="0" nillable="true"/>
    HAZMATNUMBER: Optional[str]  # <xs:element type="xs:string" name="HAZMATNUMBER" minOccurs="0" nillable="true"/>
    HAZMATSPILL: str  # <xs:element name="HAZMATSPILL" minOccurs="0"> (restricted to Y, N, U, and '')
    MCNUMBER: str  # <xs:element type="xs:string" name="MCNUMBER" minOccurs="0"/>
    NAME: str  # <xs:element type="xs:string" name="NAME" minOccurs="0"/>
    NUMBEROFAXLES: str  # <xs:element type="xs:string" name="NUMBEROFAXLES" minOccurs="0"/>
    PLACARDVISIBLE: str  # <xs:element name="PLACARDVISIBLE" minOccurs="0"> (restricted to Y, N, U, '')
    POSTALCODE: str  # <xs:element type="xs:string" name="POSTALCODE" minOccurs="0"/>
    STATE: str  # <xs:element type="xs:string" name="STATE" minOccurs="0"/>
    STREET: str  # <xs:element type="xs:string" name="STREET" minOccurs="0"/>
    VEHICLEID: uuid.UUID  # <xs:element type="xs:string" name="VEHICLEID" minOccurs="0"/>
    WEIGHT: Optional[str]  # <xs:element type="xs:string" name="WEIGHT" minOccurs="0" nillable="true"/>
    WEIGHTUNIT: Optional[str]  # <xs:element type="xs:string" name="WEIGHTUNIT" minOccurs="0" nillable="true"/>


##############################
#     acrs_damaged_areas     #
##############################
# Inside DAMAGEDAREAs tag
class DamagedArea(Base):
    """Sqlalchemy: Data for table acrs_damaged_areas"""
    __tablename__ = "acrs_damaged_areas"

    DAMAGEID = Column(Integer, primary_key=True)  # <xs:element type="xs:int" name="DAMAGEID"/>
    IMPACTTYPE = Column(Integer)  # <xs:element type="xs:byte" name="IMPACTTYPE"/>
    VEHICLEID = Column(GUID)  # <xs:element type="xs:string" name="VEHICLEID"/>


class DamagedAreaType(TypedDict):
    """Data for table acrs_damaged_areas table"""
    DAMAGEID: int  # <xs:element type="xs:int" name="DAMAGEID"/>
    IMPACTTYPE: int  # <xs:element type="xs:byte" name="IMPACTTYPE"/>
    VEHICLEID: uuid.UUID  # <xs:element type="xs:string" name="VEHICLEID"/>


class DamagedAreasType(TypedDict):
    """Multiple instance of DamagedAreaType"""
    DAMAGEDAREA: List[DamagedAreaType]


####################
#     acrs_ems     #
####################
# Inside EMSes tag
class Ems(Base):
    """Sqlalchemy: Data for table acrs_ems"""
    __tablename__ = "acrs_ems"

    EMSTRANSPORTATIONTYPE = Column(String)  # <xs:element name="EMSTRANSPORTATIONTYPE"> (restricted to G, U and A)
    EMSUNITNUMBER = Column(String, primary_key=True)  # <xs:element name="EMSUNITNUMBER"> (restricted to A-F)
    INJUREDTAKENBY = Column(String)  # <xs:element type="xs:string" name="INJUREDTAKENBY"/> (IE: Medic # 20)
    INJUREDTAKENTO = Column(String)  # <xs:element type="xs:string" name="INJUREDTAKENTO"/>
    REPORTNUMBER = Column(String, primary_key=True)  # <xs:element type="xs:string" name="REPORTNUMBER"/>


class EmsType(TypedDict):
    """Data for table acrs_ems"""
    EMSTRANSPORTATIONTYPE: str  # <xs:element name="EMSTRANSPORTATIONTYPE"> (restricted to G, U and A)
    EMSUNITNUMBER: str  # <xs:element name="EMSUNITNUMBER"> (restricted to A-F)
    INJUREDTAKENBY: str  # <xs:element type="xs:string" name="INJUREDTAKENBY"/> (IE: Medic # 20)
    INJUREDTAKENTO: str  # <xs:element type="xs:string" name="INJUREDTAKENTO"/>
    REPORTNUMBER: str  # <xs:element type="xs:string" name="REPORTNUMBER"/>


class EmsesType(TypedDict):
    """Multiple instance of EmsType"""
    EMS: List[EmsType]


#######################
#     acrs_events     #
#######################
# Inside EVENTS tag
class Event(Base):
    """Sqlalchemy: Data for table acrs_events"""
    __tablename__ = "acrs_events"

    EVENTID = Column(Integer, primary_key=True)  # <xs:element type="xs:int" name="EVENTID"/>
    EVENTSEQUENCE = Column(Integer)  # <xs:element type="xs:byte" name="EVENTSEQUENCE"/>
    EVENTTYPE = Column(Integer)  # <xs:element type="xs:byte" name="EVENTTYPE"/>
    VEHICLEID = Column(GUID)  # <xs:element type="xs:string" name="VEHICLEID"/>


class EventType(TypedDict):
    """Data for table acrs_events"""
    EVENTID: int  # <xs:element type="xs:int" name="EVENTID"/>
    EVENTSEQUENCE: int  # <xs:element type="xs:byte" name="EVENTSEQUENCE"/>
    EVENTTYPE: int  # <xs:element type="xs:byte" name="EVENTTYPE"/>
    VEHICLEID: uuid.UUID  # <xs:element type="xs:string" name="VEHICLEID"/>


class EventsType(TypedDict):
    """Multiple instance of EventType"""
    EVENT: List[EventType]


###########################
#     acrs_pdf_report     #
###########################
# Inside the PDFREPORTs tag
class PdfReport(Base):
    """Sqlalchemy: Data for table acrs_pdf_report"""
    __tablename__ = "acrs_pdf_report"

    CHANGEDBY = Column(String)  # <xs:element type="xs:string" name="CHANGEDBY"/>
    DATESTATUSCHANGED = Column(DateTime)  # <xs:element type="xs:dateTime" name="DATESTATUSCHANGED"/>
    PDFREPORT1 = Column(String)  # <xs:element type="xs:string" name="PDFREPORT1"/>
    PDF_ID = Column(Integer, primary_key=True)  # <xs:element type="xs:int" name="PDF_ID"/>
    REPORTNUMBER = Column(String)  # <xs:element type="xs:string" name="REPORTNUMBER"/>
    STATUS = Column(String)  # <xs:element type="xs:string" name="STATUS"/>


class PdfReportDataType(TypedDict):
    """Data for acrs_pdf_report"""
    CHANGEDBY: str  # <xs:element type="xs:string" name="CHANGEDBY"/>
    DATESTATUSCHANGED: datetime  # <xs:element type="xs:dateTime" name="DATESTATUSCHANGED"/>
    PDFREPORT1: str  # <xs:element type="xs:string" name="PDFREPORT1"/>
    PDF_ID: int  # <xs:element type="xs:int" name="PDF_ID"/>
    REPORTNUMBER: str  # <xs:element type="xs:string" name="REPORTNUMBER"/>
    STATUS: str  # <xs:element type="xs:string" name="STATUS"/>


class PdfReportsType(TypedDict):
    """Multiple instance of PdfReportDataType"""
    PDFREPORT: List[PdfReportDataType]


#######################
#     acrs_person     #
#######################
class Person(Base):
    """Sqlalchemy: Data for table acrs_person"""
    __tablename__ = "acrs_person"

    ADDRESS = Column(String)  # <xs:element type="xs:string" name="ADDRESS"/>
    # CITATIONCODES: CitationCodesType  # <xs:element type="cras:CITATIONCODEType" name="CITATIONCODE" maxOccurs="unbounded" minOccurs="0" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
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
    REPORTNUMBER = Column(String)  # <xs:element type="xs:string" name="REPORTNUMBER"/>
    SEX = Column(String)  # <xs:element name="SEX"> (restricted to 'F', 'M', 'U', and '')
    STATE = Column(String)  # <xs:element type="xs:string" name="STATE"/>
    ZIP = Column(String)  # <xs:element type="xs:string" name="ZIP"/>


# Acts as both the ACRSPERSON tag (inside People tag), PERSON tag, and the OWNER tag
class PersonType(TypedDict):
    """Data for acrs_person"""
    ADDRESS: str  # <xs:element type="xs:string" name="ADDRESS"/>
    CITATIONCODES: CitationCodesType  # <xs:element type="cras:CITATIONCODEType" name="CITATIONCODE" maxOccurs="unbounded" minOccurs="0" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    CITY: str  # <xs:element type="xs:string" name="CITY"/>
    COMPANY: Optional[str]  # <xs:element type="xs:string" name="COMPANY" nillable="true"/>
    COUNTRY: Optional[str]  # <xs:element type="xs:string" name="COUNTRY" nillable="true"/>
    COUNTY: Optional[str]  # <xs:element type="xs:string" name="COUNTY" nillable="true"/>
    DLCLASS: Optional[str]  # <xs:element type="xs:string" name="DLCLASS" nillable="true"/>
    DLNUMBER: str  # <xs:element type="xs:string" name="DLNUMBER"/>
    DLSTATE: str  # <xs:element type="xs:string" name="DLSTATE"/>
    DOB: date  # <xs:element type="xs:string" name="DOB"/>
    FIRSTNAME: str  # <xs:element type="xs:string" name="FIRSTNAME"/>
    HOMEPHONE: Optional[str]  # <xs:element type="xs:string" name="HOMEPHONE" nillable="true"/>
    LASTNAME: str  # <xs:element type="xs:string" name="LASTNAME"/>
    MIDDLENAME: Optional[str]  # <xs:element type="xs:string" name="MIDDLENAME" nillable="true"/>
    OTHERPHONE: str  # <xs:element type="xs:string" name="OTHERPHONE"/>
    PERSONID: uuid.UUID  # <xs:element type="xs:string" name="PERSONID"/>
    RACE: Optional[str]  # <xs:element type="xs:string" name="RACE" nillable="true"/>
    REPORTNUMBER: str  # <xs:element type="xs:string" name="REPORTNUMBER"/>
    SEX: Optional[str]  # <xs:element name="SEX"> (restricted to 'F', 'M', 'U', and '')
    STATE: str  # <xs:element type="xs:string" name="STATE"/>
    ZIP: str  # <xs:element type="xs:string" name="ZIP"/>


class PeopleType(TypedDict):
    """Multiple instance of PersonType"""
    ACRSPERSON: List[PersonType]


####################################
#     acrs_person_info: driver     #
####################################
class PersonInfo(Base):
    """Sqlalchemy: Data for table acrs_person_info"""
    __tablename__ = "acrs_person_info"

    AIRBAGDEPLOYED = Column(Integer)  # <xs:element name="AIRBAGDEPLOYED"> (restricted to values 00, 01, 02, 03, 04, 88 and 99)
    ALCOHOLTESTINDICATOR = Column(Integer)  # <xs:element name="ALCOHOLTESTINDICATOR"> (restricted to 00, 01, 02, 03, 88 and 99)
    ALCOHOLTESTTYPE = Column(String, nullable=True)  # <xs:element name="ALCOHOLTESTTYPE" nillable="true"> (restricted to 00, 01, 02, 88, 99 and '')
    ATFAULT = Column(String)  # <xs:element name="ATFAULT"> (restricted to values Y, N, and U)
    BAC = Column(String, nullable=True)  # <xs:element type="xs:string" name="BAC" nillable="true"/>
    CONDITION = Column(String)  # <xs:element type="xs:float" name="CONDITION"/> (Nonmotorist type is str)
    CONTINUEDIRECTION = Column(String, nullable=True)
    DRIVERDISTRACTEDBY = Column(Integer)  # <xs:element type="xs:byte" name="DRIVERDISTRACTEDBY"/>
    DRUGTESTINDICATOR = Column(Integer)  # <xs:element name="DRUGTESTINDICATOR"> (restricted to 00, 01, 02, 03, 88 and 99)
    DRUGTESTRESULT = Column(String, nullable=True)  # <xs:element name="DRUGTESTRESULT" nillable="true"> (restricted to P, N, U, A, and '')
    EJECTION = Column(Integer)  # <xs:element name="EJECTION"> (restricted to 00, 01, 02, 03, 04, 88, and 99)
    EMSRUNREPORTNUMBER = Column(String, nullable=True)  # <xs:element type="xs:string" name="EMSRUNREPORTNUMBER" nillable="true"/>
    EMSUNITNUMBER = Column(String, nullable=True)  # <xs:element name="EMSUNITNUMBER" nillable="true"> (restricted to A, B, C, D, E, J, K, L and '')
    EQUIPMENTPROBLEM = Column(Integer)  # <xs:element name="EQUIPMENTPROBLEM"> (restricted to 00, 01, 11, 13, 31, 44, 45, 47, 88 and 99)
    GOINGDIRECTION = Column(String, nullable=True)  # <xs:element type="xs:string" name="GOINGDIRECTION" nillable="true"/>
    HASCDL = Column(Boolean)  # <xs:element name="HASCDL">
    INJURYSEVERITY = Column(Integer)  # <xs:element name="INJURYSEVERITY"> (restricted to 01, 02, 03, 04, and 05)
    # PERSON: PersonType  # <xs:element type="cras:PERSONType" name="PERSON" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    PEDESTRIANACTIONS = Column(Integer)  # <xs:element type="xs:byte" name="PEDESTRIANACTIONS"/>
    PEDESTRIANLOCATION = Column(Float)  # <xs:element type="xs:float" name="PEDESTRIANLOCATION"/>
    PEDESTRIANMOVEMENT = Column(Float)  # <xs:element type="xs:float" name="PEDESTRIANMOVEMENT"/>
    PEDESTRIANOBEYTRAFFICSIGNAL = Column(Integer)  # <xs:element name="PEDESTRIANOBEYTRAFFICSIGNAL"> (restricted to 00, 01, 02, 03, 04, 88, and 99)
    PEDESTRIANTYPE = Column(Integer)  # <xs:element name="PEDESTRIANTYPE"> (restricted to 01, 02, 03, 05, 06, 07, 88, and 99)
    PEDESTRIANVISIBILITY = Column(Integer)  # <xs:element name="PEDESTRIANVISIBILITY"> (restricted to 00, 01, 02, 03, 04, 06, 07, 88 and 99)
    PERSONID = Column(GUID, primary_key=True)  # <xs:element type="xs:string" name="PERSONID"/>
    REPORTNUMBER = Column(String)  # <xs:element type="xs:string" name="REPORTNUMBER"/>
    SAFETYEQUIPMENT = Column(Float)  # <xs:element type="xs:float" name="SAFETYEQUIPMENT"/>
    SEAT = Column(Integer)  # <xs:element name="SEAT"> (restricted to 00, 01, 02, 03, 88, and 99)
    SEATINGLOCATION = Column(Float)  # <xs:element type="xs:float" name="SEATINGLOCATION"/>
    SEATINGROW = Column(Integer)  # <xs:element type="xs:byte" name="SEATINGROW"/>
    SUBSTANCEUSE = Column(Integer, nullable=True)  # <xs:element type="xs:byte" name="SUBSTANCEUSE"/>
    UNITNUMBERFIRSTSTRIKE = Column(String)  # <xs:element name="UNITNUMBERFIRSTSTRIKE"> (restricted to 1, 2 and '')
    VEHICLEID = Column(GUID)  # <xs:element type="xs:string" name="VEHICLEID"/>


# Inside the DRIVERs tag
class DriverType(TypedDict):
    """Data for acrs_person_info"""
    AIRBAGDEPLOYED: int  # <xs:element name="AIRBAGDEPLOYED"> (restricted to values 00, 01, 02, 03, 04, 88 and 99)
    ALCOHOLTESTINDICATOR: int  # <xs:element name="ALCOHOLTESTINDICATOR"> (restricted to 00, 01, 02, 03, 88 and 99)
    ALCOHOLTESTTYPE: Optional[str]  # <xs:element name="ALCOHOLTESTTYPE" nillable="true"> (restricted to 00, 01, 02, 88, 99 and '')
    ATFAULT: str  # <xs:element name="ATFAULT"> (restricted to values Y, N, and U)
    BAC: Optional[str]  # <xs:element type="xs:string" name="BAC" nillable="true"/>
    CONDITION: str  # <xs:element type="xs:float" name="CONDITION"/> (Nonmotorist type is str)
    DRIVERDISTRACTEDBY: int  # <xs:element type="xs:byte" name="DRIVERDISTRACTEDBY"/>
    DRUGTESTINDICATOR: int  # <xs:element name="DRUGTESTINDICATOR"> (restricted to 00, 01, 02, 03, 88 and 99)
    DRUGTESTRESULT: Optional[str]  # <xs:element name="DRUGTESTRESULT" nillable="true"> (restricted to P, N, U, A, and '')
    EJECTION: int  # <xs:element name="EJECTION"> (restricted to 00, 01, 02, 03, 04, 88, and 99)
    EMSRUNREPORTNUMBER: Optional[str]  # <xs:element type="xs:string" name="EMSRUNREPORTNUMBER" nillable="true"/>
    EMSUNITNUMBER: Optional[str]  # <xs:element name="EMSUNITNUMBER" nillable="true"> (restricted to A, B, C, D, E, J, K, L and '')
    EQUIPMENTPROBLEM: int  # <xs:element name="EQUIPMENTPROBLEM"> (restricted to 00, 01, 11, 13, 31, 44, 45, 47, 88 and 99)
    HASCDL: bool  # <xs:element name="HASCDL">
    INJURYSEVERITY: int  # <xs:element name="INJURYSEVERITY"> (restricted to 01, 02, 03, 04, and 05)
    PERSON: PersonType  # <xs:element type="cras:PERSONType" name="PERSON" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    PERSONID: uuid.UUID  # <xs:element type="xs:string" name="PERSONID"/>
    SAFETYEQUIPMENT: float  # <xs:element type="xs:float" name="SAFETYEQUIPMENT"/>
    SUBSTANCEUSE: Optional[int]  # <xs:element type="xs:byte" name="SUBSTANCEUSE"/>
    VEHICLEID: uuid.UUID  # <xs:element type="xs:string" name="VEHICLEID"/>


class DriversType(TypedDict):
    """Multiple instance of DriverType"""
    DRIVER: List[DriverType]


########################################
#     acrs_person_info: passengers     #
########################################
# Inside the PASSENGERs tag
class PassengerType(TypedDict):
    """Data for acrs_person_info"""
    AIRBAGDEPLOYED: int  # <xs:element name="AIRBAGDEPLOYED"> (restricted to values 00, 01, 02, 03, 04, 88 and 99)
    EJECTION: int  # <xs:element name="EJECTION"> (restricted to 00, 01, 02, 03, 04, 88, and 99)
    EMSRUNREPORTNUMBER: Optional[str]  # <xs:element type="xs:string" name="EMSRUNREPORTNUMBER" nillable="true"/>
    EMSUNITNUMBER: Optional[str]  # <xs:element name="EMSUNITNUMBER" nillable="true"> (restricted to A, B, C, D, E, J, K, L and '')
    EQUIPMENTPROBLEM: int  # <xs:element name="EQUIPMENTPROBLEM"> (restricted to 00, 01, 11, 13, 31, 44, 45, 47, 88 and 99)
    INJURYSEVERITY: int  # <xs:element name="INJURYSEVERITY"> (restricted to 01, 02, 03, 04, and 05)
    PERSON: PersonType  # <xs:element type="cras:PERSONType" name="PERSON" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    PERSONID: uuid.UUID
    SAFETYEQUIPMENT: float  # <xs:element type="xs:float" name="SAFETYEQUIPMENT"/>
    SEAT: int  # <xs:element name="SEAT"> (restricted to 00, 01, 02, 03, 88, and 99)
    SEATINGLOCATION: float  # <xs:element type="xs:float" name="SEATINGLOCATION"/>
    SEATINGROW: int  # <xs:element type="xs:byte" name="SEATINGROW"/>
    VEHICLEID: uuid.UUID  # <xs:element type="xs:string" name="VEHICLEID"/>


class PassengersType(TypedDict):
    """Multiple instance of PassengerType"""
    PASSENGER: List[PassengerType]


#########################################
#     acrs_person_info: nonmotorist     #
#########################################
# Inside the NONMOTORISTs tag
class NonMotoristType(TypedDict):
    """Data for acrs_person_info"""
    ALCOHOLTESTINDICATOR: int  # <xs:element name="ALCOHOLTESTINDICATOR"> (restricted to 00, 01, 02, 03, 88 and 99)
    ALCOHOLTESTTYPE: Optional[str]  # <xs:element name="ALCOHOLTESTTYPE" nillable="true"> (restricted to 00, 01, 02, 88, 99 and '')
    ATFAULT: str  # <xs:element name="ATFAULT"> (restricted to values Y, N, and U)
    BAC: Optional[str]  # <xs:element type="xs:string" name="BAC" nillable="true"/>
    CONDITION: str  # <xs:element type="xs:float" name="CONDITION"/>
    CONTINUEDIRECTION: Optional[str]
    DRUGTESTINDICATOR: int  # <xs:element name="DRUGTESTINDICATOR"> (restricted to 00, 01, 02, 03, 88 and 99)
    DRUGTESTRESULT: Optional[str]  # <xs:element name="DRUGTESTRESULT" nillable="true"> (restricted to P, N, U, A, and '')
    EMSRUNREPORTNUMBER: Optional[str]  # <xs:element type="xs:string" name="EMSRUNREPORTNUMBER" nillable="true"/>
    EMSUNITNUMBER: Optional[str]  # <xs:element name="EMSUNITNUMBER" nillable="true"> (restricted to A, B, C, D, E, J, K, L and '')
    GOINGDIRECTION: Optional[str]  # <xs:element type="xs:string" name="GOINGDIRECTION" nillable="true"/>
    INJURYSEVERITY: int  # <xs:element name="INJURYSEVERITY"> (restricted to 01, 02, 03, 04, and 05)
    PEDESTRIANACTIONS: int  # <xs:element type="xs:byte" name="PEDESTRIANACTIONS"/>
    PEDESTRIANLOCATION: float  # <xs:element type="xs:float" name="PEDESTRIANLOCATION"/>
    PEDESTRIANMOVEMENT: float  # <xs:element type="xs:float" name="PEDESTRIANMOVEMENT"/>
    PEDESTRIANOBEYTRAFFICSIGNAL: int  # <xs:element name="PEDESTRIANOBEYTRAFFICSIGNAL"> (restricted to 00, 01, 02, 03, 04, 88, and 99)
    PEDESTRIANTYPE: int  # <xs:element name="PEDESTRIANTYPE"> (restricted to 01, 02, 03, 05, 06, 07, 88, and 99)
    PEDESTRIANVISIBILITY: int  # <xs:element name="PEDESTRIANVISIBILITY"> (restricted to 00, 01, 02, 03, 04, 06, 07, 88 and 99)
    PERSON: PersonType  # <xs:element type="cras:PERSONType" name="PERSON" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    PERSONID: uuid.UUID  # <xs:element type="xs:string" name="PERSONID"/>
    REPORTNUMBER: str  # <xs:element type="xs:string" name="REPORTNUMBER"/>
    SAFETYEQUIPMENT: float  # <xs:element type="xs:float" name="SAFETYEQUIPMENT"/>
    SUBSTANCEUSE: int  # <xs:element name="SUBSTANCEUSE"> (restricted to 00, 01, 11, 12, 13, 14, 21, 22, 88, and 99)
    UNITNUMBERFIRSTSTRIKE: str  # <xs:element name="UNITNUMBERFIRSTSTRIKE"> (restricted to 1, 2 and '')


class NonMotoristsType(TypedDict):
    """Multiple instance of NonMotoristType"""
    NONMOTORIST: List[NonMotoristType]


###########################
#     acrs_report_doc     #
###########################
class ReportDocument(Base):
    """Sqlalchemy: Data for table acrs_report_doc"""
    __tablename__ = "acrs_report_doc"
    NULLCOLUMN = Column(String, primary_key=True)


class ReportDocumentType(TypedDict):
    """There is not an example of this data, so this is just a stub for now. For the REPORTDOCUMENTS tag."""


class ReportDocumentsType(TypedDict):
    """Multiple instance of ReportDocumentType"""
    REPORTDOCUMENT: List[ReportDocumentType]


#############################
#     acrs_report_photo     #
#############################
class ReportPhoto(Base):
    """Sqlalchemy: Data for table acrs_report_photo"""
    __tablename__ = "acrs_report_photo"
    NULLCOLUMN = Column(String, primary_key=True)


class ReportPhotoType(TypedDict):
    """There is not an example of this data, so this is just a stub for now"""


class ReportPhotoesType(TypedDict):
    """Multiple instance of ReportPhotoType"""
    REPORTPHOTO: List[ReportPhotoType]


########################
#     acrs_roadway     #
########################
class Roadway(Base):
    """Sqlalchemy: Data for table acrs_roadway"""
    __tablename__ = "acrs_roadway"

    COUNTY = Column(Integer)  # <xs:element name="COUNTY" minOccurs="0"> (restricted to 3, 23, and 24)
    LOGMILE_DIR = Column(String, nullable=True)  # <xs:element name="LOGMILE_DIR" minOccurs="0"> (restricted to N, S, E, W, U, and '')
    MILEPOINT = Column(Float, nullable=True)  # <xs:element type="xs:float" name="MILEPOINT" minOccurs="0"/>
    MUNICIPAL = Column(Integer, nullable=True)  # <xs:element name="MUNICIPAL" minOccurs="0"> (restricted to 999 and 000)
    MUNICIPAL_AREA_CODE = Column(Integer, nullable=True)  # <xs:element name="MUNICIPAL_AREA_CODE" minOccurs="0"> (restricted to 999 and 000)
    REFERENCE_MUNI = Column(Integer, nullable=True)  # <xs:element name="REFERENCE_MUNI" minOccurs="0"> (restricted to 999 and 000)
    REFERENCE_ROADNAME = Column(String, nullable=True)  # <xs:element type="xs:string" name="REFERENCE_ROADNAME" minOccurs="0"/>
    REFERENCE_ROUTE_NUMBER = Column(String, nullable=True)  # <xs:element type="xs:string" name="REFERENCE_ROUTE_NUMBER" minOccurs="0"/>
    REFERENCE_ROUTE_SUFFIX = Column(String, nullable=True)  # <xs:element name="REFERENCE_ROUTE_SUFFIX" minOccurs="0" nillable="true"> (restricted to E, B, AL, AV, 6, IR, and '')
    REFERENCE_ROUTE_TYPE = Column(String, nullable=True)  # <xs:element type="xs:string" name="REFERENCE_ROUTE_TYPE" minOccurs="0"/>
    ROADID = Column(String, primary_key=True)  # <xs:element type="xs:string" name="ROADID" minOccurs="0"/> This is a six digit number, or a UUID
    ROAD_NAME = Column(String, nullable=True)  # <xs:element type="xs:string" name="ROAD_NAME" minOccurs="0"/>
    ROUTE_NUMBER = Column(String, nullable=True)  # <xs:element type="xs:string" name="ROUTE_NUMBER" minOccurs="0"/>
    ROUTE_SUFFIX = Column(String, nullable=True)  # <xs:element name="ROUTE_SUFFIX" minOccurs="0" nillable="true"> (restricted to E, AL, B, A and '')
    ROUTE_TYPE = Column(String, nullable=True)  # <xs:element name="ROUTE_TYPE" minOccurs="0">


class RoadwayType(TypedDict):
    """Data for table acrs_roadway"""
    COUNTY: int  # <xs:element name="COUNTY" minOccurs="0"> (restricted to 3, 23, and 24)
    LOGMILE_DIR: str  # <xs:element name="LOGMILE_DIR" minOccurs="0"> (restricted to N, S, E, W, U, and '')
    MILEPOINT: Optional[float]  # <xs:element type="xs:float" name="MILEPOINT" minOccurs="0"/>
    MUNICIPAL: Optional[int]  # <xs:element name="MUNICIPAL" minOccurs="0"> (restricted to 999 and 000)
    MUNICIPAL_AREA_CODE: Optional[int]  # <xs:element name="MUNICIPAL_AREA_CODE" minOccurs="0"> (restricted to 999 and 000)
    REFERENCE_MUNI: Optional[int]  # <xs:element name="REFERENCE_MUNI" minOccurs="0"> (restricted to 999 and 000)
    REFERENCE_ROADNAME: Optional[str]  # <xs:element type="xs:string" name="REFERENCE_ROADNAME" minOccurs="0"/>
    REFERENCE_ROUTE_NUMBER: Optional[str]  # <xs:element type="xs:string" name="REFERENCE_ROUTE_NUMBER" minOccurs="0"/>
    REFERENCE_ROUTE_SUFFIX: Optional[str]  # <xs:element name="REFERENCE_ROUTE_SUFFIX" minOccurs="0" nillable="true"> (restricted to E, B, AL, AV, 6, IR, and '')
    REFERENCE_ROUTE_TYPE: Optional[str]  # <xs:element type="xs:string" name="REFERENCE_ROUTE_TYPE" minOccurs="0"/>
    ROADID: str  # <xs:element type="xs:string" name="ROADID" minOccurs="0"/>
    ROAD_NAME: Optional[str]  # <xs:element type="xs:string" name="ROAD_NAME" minOccurs="0"/>
    ROUTE_NUMBER: Optional[str]  # <xs:element type="xs:string" name="ROUTE_NUMBER" minOccurs="0"/>
    ROUTE_SUFFIX: Optional[str]  # <xs:element name="ROUTE_SUFFIX" minOccurs="0" nillable="true"> (restricted to E, AL, B, A and '')
    ROUTE_TYPE: Optional[str]  # <xs:element name="ROUTE_TYPE" minOccurs="0">


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
    # OWNER: PersonType  # <xs:element type="cras:OWNERType" name="OWNER" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    OWNERID = Column(GUID)  # <xs:element type="xs:string" name="OWNERID"/>
    TOWEDID = Column(GUID, primary_key=True)  # <xs:element type="xs:string" name="TOWEDID"/>
    UNITNUMBER = Column(String)  # <xs:element type="xs:string" name="UNITNUMBER" nillable="true"/>
    VEHICLEID = Column(GUID)  # <xs:element type="xs:string" name="VEHICLEID"/>
    VEHICLEMAKE = Column(String)  # <xs:element type="xs:string" name="VEHICLEMAKE"/>
    VEHICLEMODEL = Column(String)  # <xs:element type="xs:string" name="VEHICLEMODEL"/>
    VEHICLEYEAR = Column(Integer)  # <xs:element type="xs:short" name="VEHICLEYEAR"/>
    VIN = Column(String)  # <xs:element type="xs:string" name="VIN"/>


class TowedUnitType(TypedDict):
    """Data for table acrs_towed_unit"""
    INSURANCEPOLICYNUMBER: str  # <xs:element type="xs:string" name="INSURANCEPOLICYNUMBER"/>
    INSURER: str  # <xs:element type="xs:string" name="INSURER"/>
    LICENSEPLATENUMBER: str  # <xs:element type="xs:string" name="LICENSEPLATENUMBER"/>
    LICENSEPLATESTATE: str  # <xs:element type="xs:string" name="LICENSEPLATESTATE"/>
    OWNER: PersonType  # <xs:element type="cras:OWNERType" name="OWNER" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    OWNERID: uuid.UUID  # <xs:element type="xs:string" name="OWNERID"/>
    TOWEDID: uuid.UUID  # <xs:element type="xs:string" name="TOWEDID"/>
    UNITNUMBER: str  # <xs:element type="xs:string" name="UNITNUMBER" nillable="true"/>
    VEHICLEID: uuid.UUID  # <xs:element type="xs:string" name="VEHICLEID"/>
    VEHICLEMAKE: str  # <xs:element type="xs:string" name="VEHICLEMAKE"/>
    VEHICLEMODEL: str  # <xs:element type="xs:string" name="VEHICLEMODEL"/>
    VEHICLEYEAR: int  # <xs:element type="xs:short" name="VEHICLEYEAR"/>
    VIN: str  # <xs:element type="xs:string" name="VIN"/>


class TowedUnitsType(TypedDict):
    """Multiple instance of TowedUnitType"""
    TOWEDUNIT: List[TowedUnitType]


#############################
#     acrs_vehicle_uses     #
#############################
# Inside VEHICLEUSEs tag
class VehicleUse(Base):
    """Sqlalchemy: Data for table acrs_vehicle_use"""
    __tablename__ = "acrs_vehicle_use"

    ID = Column(Integer, primary_key=True)  # <xs:element type="xs:int" name="ID"/>
    VEHICLEID = Column(GUID)  # <xs:element type="xs:string" name="VEHICLEID"/>
    VEHICLEUSECODE = Column(Integer)  # <xs:element name="VEHICLEUSECODE"> (restricted to 00, 01, 02, and 03)


class VehicleUseType(TypedDict):
    """Data for table acrs_vehicle_uses"""
    ID: int  # <xs:element type="xs:int" name="ID"/>
    VEHICLEID: uuid.UUID  # <xs:element type="xs:string" name="VEHICLEID"/>
    VEHICLEUSECODE: int  # <xs:element name="VEHICLEUSECODE"> (restricted to 00, 01, 02, and 03)


class VehicleUsesType(TypedDict):
    """Multiple instance of VehicleUseType"""
    VEHICLEUSE: List[VehicleUseType]


##########################
#     acrs_witnesses     #
##########################
class Witness(Base):
    """Sqlalchemy: Data for table acrs_witness"""
    __tablename__ = "acrs_witness"

    # PERSON: PersonType  # <xs:element type="cras:PERSONType" name="PERSON" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    PERSONID = Column(GUID, primary_key=True)  # <xs:element type="xs:string" name="PERSONID"/>
    REPORTNUMBER = Column(String, primary_key=True)  # <xs:element type="xs:string" name="REPORTNUMBER"/>


class WitnessType(TypedDict):
    """Data for table acrs_witnesses"""
    PERSON: PersonType  # <xs:element type="cras:PERSONType" name="PERSON" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    PERSONID: uuid.UUID  # <xs:element type="xs:string" name="PERSONID"/>
    REPORTNUMBER: str  # <xs:element type="xs:string" name="REPORTNUMBER"/>


class WitnessesType(TypedDict):
    """Multiple instance of WitnessType"""
    WITNESS: List[WitnessType]


#########################
#     acrs_vehicles     #
#########################
# Inside the VEHICLEs.ACRSVEHICLE tag
class Vehicles(Base):
    """Sqlalchemy: Data for table acrs_vehicles"""
    __tablename__ = "acrs_vehicles"

    # COMMERCIALVEHICLE: Optional[CommercialVehicleType]  # <xs:element name="COMMERCIALVEHICLE" nillable="true">
    CONTINUEDIRECTION = Column(String)  # <xs:element name="CONTINUEDIRECTION">
    # DAMAGEDAREAs: DamagedAreasType  # <xs:element type="cras:DAMAGEDAREAsType" name="DAMAGEDAREAs" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    DAMAGEEXTENT = Column(Integer)  # <xs:element name="DAMAGEEXTENT"> (restricted to 00, 01, 02, 03, 04, 05, 88 and 99)
    DRIVERLESSVEHICLE = Column(String)  # <xs:element name="DRIVERLESSVEHICLE"> (restricted to 'Y', 'N', and 'U')
    # DRIVERs: DriversType  # <xs:element type="cras:DRIVERsType" name="DRIVERs" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    EMERGENCYMOTORVEHICLEUSE = Column(String)  # <xs:element name="EMERGENCYMOTORVEHICLEUSE"> (restricted to 'Y', 'N', and 'U')
    # EVENTS: EventsType  # <xs:element type="cras:EVENTType" name="EVENT" maxOccurs="unbounded" minOccurs="0" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    FIRE = Column(String)  # <xs:element name="FIRE"> (restricted to 'Y', 'N', and 'U')
    FIRSTIMPACT = Column(String)  # <xs:element type="xs:string" name="FIRSTIMPACT"/>
    GOINGDIRECTION = Column(String)  # <xs:element name="GOINGDIRECTION"> (restricted to N, S, E, W, U, and '')
    HITANDRUN = Column(String)  # <xs:element name="HITANDRUN"> (restricted to 'Y', 'N', and 'U')
    INSURANCEPOLICYNUMBER = Column(String)  # <xs:element type="xs:string" name="INSURANCEPOLICYNUMBER"/>
    INSURER = Column(String)  # <xs:element type="xs:string" name="INSURER"/>
    LICENSEPLATENUMBER = Column(String)  # <xs:element type="xs:string" name="LICENSEPLATENUMBER"/>
    LICENSEPLATESTATE = Column(String)  # <xs:element type="xs:string" name="LICENSEPLATESTATE"/>
    MAINIMPACT = Column(Integer, nullable=True)  # <xs:element type="xs:string" name="MAINIMPACT"/>
    MOSTHARMFULEVENT = Column(Float)  # <xs:element type="xs:float" name="MOSTHARMFULEVENT"/>
    # OWNER: PersonType  # <xs:element type="cras:OWNERType" name="OWNER" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    OWNERID = Column(GUID)  # <xs:element type="xs:string" name="OWNERID"/>
    PARKEDVEHICLE = Column(Boolean)  # <xs:element name="PARKEDVEHICLE">
    # PASSENGERs: PassengersType  # <xs:element name="PASSENGERs">
    REGISTRATIONEXPIRATIONYEAR = Column(String)  # <xs:element type="xs:string" name="REGISTRATIONEXPIRATIONYEAR" nillable="true"/>
    REPORTNUMBER = Column(String)  # <xs:element type="xs:string" name="REPORTNUMBER"/>
    SFVEHICLEINTRANSPORT = Column(Integer)  # <xs:element type="xs:byte" name="SFVEHICLEINTRANSPORT"/>
    SPEEDLIMIT = Column(Integer)  # <xs:element type="xs:byte" name="SPEEDLIMIT"/>
    TOWEDUNITTYPE = Column(Integer)  # <xs:element name="TOWEDUNITTYPE"> (restricted to 00, 01, 03, 06, 07, 88 and 99)
    # TOWEDUNITs: TowedUnitsType  # <xs:element name="TOWEDUNITs">
    UNITNUMBER = Column(Integer)  # <xs:element name="UNITNUMBER"> (restricted to values 1-10)
    VEHICLEBODYTYPE = Column(String)  # <xs:element type="xs:string" name="VEHICLEBODYTYPE"/>
    VEHICLEID = Column(GUID, primary_key=True)  # <xs:element type="xs:string" name="VEHICLEID"/>
    VEHICLEMAKE = Column(String)  # <xs:element type="xs:string" name="VEHICLEMAKE"/>
    VEHICLEMODEL = Column(String)  # <xs:element type="xs:string" name="VEHICLEMODEL"/>
    VEHICLEMOVEMENT = Column(Float, nullable=True)  # <xs:element type="xs:float" name="VEHICLEMOVEMENT"/>
    VEHICLEREMOVEDBY = Column(String, nullable=True)  # <xs:element type="xs:string" name="VEHICLEREMOVEDBY" nillable="true"/>
    VEHICLEREMOVEDTO = Column(String, nullable=True)  # <xs:element type="xs:string" name="VEHICLEREMOVEDTO" nillable="true"/>
    VEHICLETOWEDAWAY = Column(Integer, nullable=True)  # <xs:element name="VEHICLETOWEDAWAY"> (restricted to Y, N, U and '')
    # VEHICLEUSEs: VehicleUsesType  # <xs:element type="cras:VEHICLEUSEsType" name="VEHICLEUSEs" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    VEHICLEYEAR = Column(String)  # <xs:element type="xs:string" name="VEHICLEYEAR"/>
    VIN = Column(String)  # <xs:element type="xs:string" name="VIN"/>


class VehicleType(TypedDict):
    """Data for table acrs_vehicles"""
    COMMERCIALVEHICLE: Optional[CommercialVehicleType]  # <xs:element name="COMMERCIALVEHICLE" nillable="true">
    CONTINUEDIRECTION: str  # <xs:element name="CONTINUEDIRECTION">
    DAMAGEDAREAs: DamagedAreasType  # <xs:element type="cras:DAMAGEDAREAsType" name="DAMAGEDAREAs" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    DAMAGEEXTENT: int  # <xs:element name="DAMAGEEXTENT"> (restricted to 00, 01, 02, 03, 04, 05, 88 and 99)
    DRIVERLESSVEHICLE: str  # <xs:element name="DRIVERLESSVEHICLE"> (restricted to 'Y', 'N', and 'U')
    DRIVERs: DriversType  # <xs:element type="cras:DRIVERsType" name="DRIVERs" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    EMERGENCYMOTORVEHICLEUSE: str  # <xs:element name="EMERGENCYMOTORVEHICLEUSE"> (restricted to 'Y', 'N', and 'U')
    EVENTS: EventsType  # <xs:element type="cras:EVENTType" name="EVENT" maxOccurs="unbounded" minOccurs="0" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    FIRE: str  # <xs:element name="FIRE"> (restricted to 'Y', 'N', and 'U')
    FIRSTIMPACT: str  # <xs:element type="xs:string" name="FIRSTIMPACT"/>
    GOINGDIRECTION: str  # <xs:element name="GOINGDIRECTION"> (restricted to N, S, E, W, U, and '')
    HITANDRUN: str  # <xs:element name="HITANDRUN"> (restricted to 'Y', 'N', and 'U')
    INSURANCEPOLICYNUMBER: str  # <xs:element type="xs:string" name="INSURANCEPOLICYNUMBER"/>
    INSURER: str  # <xs:element type="xs:string" name="INSURER"/>
    LICENSEPLATENUMBER: str  # <xs:element type="xs:string" name="LICENSEPLATENUMBER"/>
    LICENSEPLATESTATE: str  # <xs:element type="xs:string" name="LICENSEPLATESTATE"/>
    MAINIMPACT: Optional[int]  # <xs:element type="xs:string" name="MAINIMPACT"/>
    MOSTHARMFULEVENT: float  # <xs:element type="xs:float" name="MOSTHARMFULEVENT"/>
    OWNER: PersonType  # <xs:element type="cras:OWNERType" name="OWNER" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    OWNERID: uuid.UUID  # <xs:element type="xs:string" name="OWNERID"/>
    PARKEDVEHICLE: bool  # <xs:element name="PARKEDVEHICLE">
    PASSENGERs: PassengersType  # <xs:element name="PASSENGERs">
    REGISTRATIONEXPIRATIONYEAR: str  # <xs:element type="xs:string" name="REGISTRATIONEXPIRATIONYEAR" nillable="true"/>
    REPORTNUMBER: str  # <xs:element type="xs:string" name="REPORTNUMBER"/>
    SFVEHICLEINTRANSPORT: int  # <xs:element type="xs:byte" name="SFVEHICLEINTRANSPORT"/>
    SPEEDLIMIT: int  # <xs:element type="xs:byte" name="SPEEDLIMIT"/>
    TOWEDUNITTYPE: int  # <xs:element name="TOWEDUNITTYPE"> (restricted to 00, 01, 03, 06, 07, 88 and 99)
    TOWEDUNITs: TowedUnitsType  # <xs:element name="TOWEDUNITs">
    UNITNUMBER: int  # <xs:element name="UNITNUMBER"> (restricted to values 1-10)
    VEHICLEBODYTYPE: str  # <xs:element type="xs:string" name="VEHICLEBODYTYPE"/>
    VEHICLEID: uuid.UUID  # <xs:element type="xs:string" name="VEHICLEID"/>
    VEHICLEMAKE: str  # <xs:element type="xs:string" name="VEHICLEMAKE"/>
    VEHICLEMODEL: str  # <xs:element type="xs:string" name="VEHICLEMODEL"/>
    VEHICLEMOVEMENT: Optional[float]  # <xs:element type="xs:float" name="VEHICLEMOVEMENT"/>
    VEHICLEREMOVEDBY: Optional[str]  # <xs:element type="xs:string" name="VEHICLEREMOVEDBY" nillable="true"/>
    VEHICLEREMOVEDTO: Optional[str]  # <xs:element type="xs:string" name="VEHICLEREMOVEDTO" nillable="true"/>
    VEHICLETOWEDAWAY: Optional[int]  # <xs:element name="VEHICLETOWEDAWAY"> (restricted to Y, N, U and '')
    VEHICLEUSEs: VehicleUsesType  # <xs:element type="cras:VEHICLEUSEsType" name="VEHICLEUSEs" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    VEHICLEYEAR: str  # <xs:element type="xs:string" name="VEHICLEYEAR"/>
    VIN: str  # <xs:element type="xs:string" name="VIN"/>


class VehiclesType(TypedDict):
    """Multiple instance of VehicleType"""
    ACRSVEHICLE: List[VehicleType]


########################
#     acrs_crashes     #
########################
class Crashes(Base):
    """Sqlalchemy: Data for table acrs_crashes"""
    __tablename__ = "acrs_crashes"

    ACRSREPORTTIMESTAMP = Column(DateTime)  # <xs:element type="xs:dateTime" name="ACRSREPORTTIMESTAMP"/>
    AGENCYIDENTIFIER = Column(String)  # <xs:element type="xs:string" name="AGENCYIDENTIFIER"/>
    AGENCYNAME = Column(String)  # <xs:element type="xs:string" name="AGENCYNAME"/>
    # APPROVALDATA: ApprovalDataType  # <xs:element type="cras:APPROVALDATAType" name="APPROVALDATA" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    AREA = Column(String)  # <xs:element type="xs:string" name="AREA"/>
    # CIRCUMSTANCES: CircumstancesType  # <xs:element type="cras:CIRCUMSTANCESType" name="CIRCUMSTANCES" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    COLLISIONTYPE = Column(Integer)  # <xs:element type="xs:byte" name="COLLISIONTYPE"/>
    CONMAINCLOSURE = Column(String)  # <xs:element name="CONMAINCLOSURE" nillable="true"> (restricted to values 00, 01, 02, 03, 04, 88, 99, and ''
    CONMAINLOCATION = Column(String)  # <xs:element name="CONMAINLOCATION" nillable="true"> (restricted to values 00, 01, 02, 03, 04, 05, 88, 99, and '')
    CONMAINWORKERSPRESENT = Column(String)  # <xs:element name="CONMAINWORKERSPRESENT" nillable="true"> (restricted to Y, N, U, '')
    CONMAINZONE = Column(Boolean, nullable=True)  # <xs:element name="CONMAINWORKERSPRESENT" nillable="true">
    CRASHDATE = Column(Date)  # <xs:element type="xs:dateTime" name="CRASHDATE"/>
    CRASHTIME = Column(DateTime)  # <xs:element type="xs:dateTime" name="CRASHTIME"/>
    CURRENTASSIGNMENT = Column(String)  # <xs:element name="CURRENTASSIGNMENT"> (restricted to values 999, BCPD, and '')
    CURRENTGROUP = Column(String)  # <xs:element type="xs:string" name="CURRENTGROUP"/>
    DEFAULTASSIGNMENT = Column(String)  # <xs:element name="DEFAULTASSIGNMENT"> (restricted to values 999, BCPD, and '')
    DEFAULTGROUP = Column(String)  # <xs:element type="xs:string" name="DEFAULTGROUP"/>
    # DIAGRAM: CrashDiagramType  # <xs:element type="cras:DIAGRAMType" name="DIAGRAM" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    DOCTYPE = Column(String)  # <xs:element type="xs:string" name="DOCTYPE"/>
    # EMSes: EmsesType  # <xs:element type="cras:EMSType" name="EMS" maxOccurs="unbounded" minOccurs="0" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    FIXEDOBJECTSTRUCK = Column(Float)  # <xs:element type="xs:float" name="FIXEDOBJECTSTRUCK"/>
    HARMFULEVENTONE = Column(Float)  # <xs:element type="xs:float" name="HARMFULEVENTONE"/>
    HARMFULEVENTTWO = Column(Float)  # <xs:element type="xs:float" name="HARMFULEVENTTWO"/>
    HITANDRUN = Column(Boolean, nullable=True)  # <xs:element name="HITANDRUN"> nillable to handle the Unknown option
    INSERTDATE = Column(DateTime)  # <xs:element type="xs:dateTime" name="INSERTDATE"/>
    INTERCHANGEAREA = Column(String)  # <xs:element name="INTERCHANGEAREA"> (restricted to 00, 01, 02, 03, 04, 05, 06, 88, 99, and '')
    INTERCHANGEIDENTIFICATION = Column(String, nullable=True)  # <xs:element type="xs:string" name="INTERCHANGEIDENTIFICATION" nillable="true"/>
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
    MILEPOINTDISTANCEUNITS = Column(String)  # <xs:element name="MILEPOINTDISTANCEUNITS"> (restricted to M, F, U, and '')
    NARRATIVE = Column(String)  # <xs:element type="xs:string" name="NARRATIVE"/>
    # NONMOTORISTs: NonMotoristsType  # <xs:element type="cras:NONMOTORISTType" name="NONMOTORIST" maxOccurs="unbounded" minOccurs="0" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    NONTRAFFIC = Column(Boolean, nullable=True)  # <xs:element name="NONTRAFFIC"> nillable to handle the Unknown option
    NUMBEROFLANES = Column(String)  # <xs:element type="xs:string" name="NUMBEROFLANES"/>
    OFFROADDESCRIPTION = Column(String, nullable=True)  # <xs:element type="xs:string" name="OFFROADDESCRIPTION" nillable="true"/>
    # PDFREPORTs: PdfReportsType  # <xs:element type="cras:PDFREPORTsType" name="PDFREPORTs" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    PHOTOSTAKEN = Column(Boolean, nullable=True)  # <xs:element name="PHOTOSTAKEN"> nillable to handle the Unknown option
    # People: PeopleType  # <xs:element type="cras:PeopleType" name="People" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    RAMP = Column(String)  # <xs:element type="xs:string" name="RAMP" nillable="true"/>
    REPORTCOUNTYLOCATION = Column(Integer)  # <xs:element name="REPORTCOUNTYLOCATION"> (restricted to 03, 23, 24, and 88)
    # REPORTDOCUMENTs: ReportDocumentsType  # <xs:element type="xs:string" name="REPORTDOCUMENTs" nillable="true"/>
    REPORTNUMBER = Column(String, primary_key=True)  # <xs:element type="xs:string" name="REPORTNUMBER"/>
    # REPORTPHOTOes: ReportPhotoesType  # <xs:element type="xs:string" name="REPORTPHOTOes" nillable="true"/>
    REPORTTYPE = Column(String)  # <xs:element name="REPORTTYPE"> (restricted to 'Property Damage Crash', 'Injury Crash', and 'Fatal Crash')
    ROADALIGNMENT = Column(String)  # <xs:element name="ROADALIGNMENT"> (restricted to 00, 01, 02, 03, 88, 99 and '')
    ROADCONDITION = Column(String)  # <xs:element type="xs:string" name="ROADCONDITION"/>
    ROADDIVISION = Column(String)  # <xs:element name="ROADDIVISION"> (restricted to 00, 01, 02, 03, 04, 05.01, 88, 99 and '')
    ROADGRADE = Column(String)  # <xs:element name="ROADGRADE"> (restricted to 00, 01, 02, 03, 04, 05, 06, 88, 99 and '')
    ROADID = Column(String)  # <xs:element type="xs:string" name="ROADID"/> (this is a six digit number or a UUID)
    # ROADWAY: RoadwayType  # <xs:element type="cras:ROADWAYType" name="ROADWAY" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    SCHOOLBUSINVOLVEMENT = Column(Integer)  # <xs:element name="SCHOOLBUSINVOLVEMENT"> (restricted to 00, 01, 02, 03, and 99)
    STATEGOVERNMENTPROPERTYNAME = Column(String, nullable=True)  # <xs:element type="xs:string" name="STATEGOVERNMENTPROPERTYNAME" nillable="true"/>
    SUPERVISOR = Column(String)  # <xs:element type="xs:string" name="SUPERVISOR" nillable="true"/>
    SUPERVISORUSERNAME = Column(String)  # <xs:element type="xs:string" name="SUPERVISORUSERNAME"/>
    SUPERVISORYDATE = Column(DateTime)  # <xs:element type="xs:dateTime" name="SUPERVISORYDATE"/>
    SURFACECONDITION = Column(String)  # <xs:element type="xs:string" name="SURFACECONDITION"/>
    TRAFFICCONTROL = Column(Integer)  # <xs:element type="xs:byte" name="TRAFFICCONTROL"/>
    TRAFFICCONTROLFUNCTIONING = Column(String)  # <xs:element name="TRAFFICCONTROLFUNCTIONING"> (restricted to Y, N, U, and '')
    UPDATEDATE = Column(DateTime)  # <xs:element type="xs:string" name="UPDATEDATE"/>
    UPLOADVERSION = Column(String)  # <xs:element type="xs:string" name="UPLOADVERSION"/>
    # VEHICLEs: VehiclesType  # <xs:element type="cras:VEHICLEsType" name="VEHICLEs" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    VERSIONNUMBER = Column(Integer)  # <xs:element name="VERSIONNUMBER">
    WEATHER = Column(Float)  # <xs:element type="xs:float" name="WEATHER"/>
    # WITNESSes: WitnessesType


class CrashDataType(TypedDict):
    """Typing: Data for table acrs_crashes"""
    ACRSREPORTTIMESTAMP: datetime  # <xs:element type="xs:dateTime" name="ACRSREPORTTIMESTAMP"/>
    AGENCYIDENTIFIER: str  # <xs:element type="xs:string" name="AGENCYIDENTIFIER"/>
    AGENCYNAME: str  # <xs:element type="xs:string" name="AGENCYNAME"/>
    APPROVALDATA: ApprovalDataType  # <xs:element type="cras:APPROVALDATAType" name="APPROVALDATA" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    AREA: str  # <xs:element type="xs:string" name="AREA"/>
    CIRCUMSTANCES: CircumstancesType  # <xs:element type="cras:CIRCUMSTANCESType" name="CIRCUMSTANCES" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    COLLISIONTYPE: int  # <xs:element type="xs:byte" name="COLLISIONTYPE"/>
    CONMAINCLOSURE: Optional[str]  # <xs:element name="CONMAINCLOSURE" nillable="true"> (restricted to values 00, 01, 02, 03, 04, 88, 99, and ''
    CONMAINLOCATION: Optional[str]  # <xs:element name="CONMAINLOCATION" nillable="true"> (restricted to values 00, 01, 02, 03, 04, 05, 88, 99, and '')
    CONMAINWORKERSPRESENT: Optional[str]  # <xs:element name="CONMAINWORKERSPRESENT" nillable="true"> (restricted to Y, N, U, '')
    CONMAINZONE: Optional[bool]  # <xs:element name="CONMAINWORKERSPRESENT" nillable="true">
    CRASHDATE: date  # <xs:element type="xs:dateTime" name="CRASHDATE"/>
    CRASHTIME: datetime  # <xs:element type="xs:dateTime" name="CRASHTIME"/>
    CURRENTASSIGNMENT: str  # <xs:element name="CURRENTASSIGNMENT"> (restricted to values 999, BCPD, and '')
    CURRENTGROUP: str  # <xs:element type="xs:string" name="CURRENTGROUP"/>
    DEFAULTASSIGNMENT: str  # <xs:element name="DEFAULTASSIGNMENT"> (restricted to values 999, BCPD, and '')
    DEFAULTGROUP: str  # <xs:element type="xs:string" name="DEFAULTGROUP"/>
    DIAGRAM: CrashDiagramType  # <xs:element type="cras:DIAGRAMType" name="DIAGRAM" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    DOCTYPE: str  # <xs:element type="xs:string" name="DOCTYPE"/>
    EMSes: EmsesType  # <xs:element type="cras:EMSType" name="EMS" maxOccurs="unbounded" minOccurs="0" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    FIXEDOBJECTSTRUCK: float  # <xs:element type="xs:float" name="FIXEDOBJECTSTRUCK"/>
    HARMFULEVENTONE: float  # <xs:element type="xs:float" name="HARMFULEVENTONE"/>
    HARMFULEVENTTWO: float  # <xs:element type="xs:float" name="HARMFULEVENTTWO"/>
    HITANDRUN: Optional[bool]  # <xs:element name="HITANDRUN"> optional to handle the Unknown option
    INSERTDATE: datetime  # <xs:element type="xs:dateTime" name="INSERTDATE"/>
    INTERCHANGEAREA: str  # <xs:element name="INTERCHANGEAREA"> (restricted to 00, 01, 02, 03, 04, 05, 06, 88, 99, and '')
    INTERCHANGEIDENTIFICATION: Optional[str]  # <xs:element type="xs:string" name="INTERCHANGEIDENTIFICATION" nillable="true"/>
    INTERSECTIONTYPE: str  # <xs:element name="INTERSECTIONTYPE">
    INVESTIGATINGOFFICERUSERNAME: str  # <xs:element type="xs:string" name="INVESTIGATINGOFFICERUSERNAME"/>
    INVESTIGATOR: Optional[str]  # <xs:element type="xs:string" name="INVESTIGATOR" nillable="true"/>
    JUNCTION: str  # <xs:element type="xs:string" name="JUNCTION"/>
    LANEDIRECTION: Optional[str]  # <xs:element name="LANEDIRECTION"> (restricted to N, S, E, W, U and '')
    LANENUMBER: str  # <xs:element name="LANENUMBER"> (restricted to 1, 2, 3, 4, 5, 6 or '')
    LANETYPE: Optional[str]  # <xs:element type="xs:string" name="LANETYPE" nillable="true"/>
    LATITUDE: float  # <xs:element type="xs:float" name="LATITUDE"/>
    LIGHT: float  # <xs:element name="LIGHT">
    LOCALCASENUMBER: str  # <xs:element type="xs:string" name="LOCALCASENUMBER"/>
    LOCALCODES: Optional[str]  # <xs:element type="xs:string" name="LOCALCODES" nillable="true"/>
    LONGITUDE: float  # <xs:element type="xs:float" name="LONGITUDE"/>
    MILEPOINTDIRECTION: str  # <xs:element name="MILEPOINTDIRECTION"> (restrcted to N, S, E, W, U, and '')
    MILEPOINTDISTANCE: str  # <xs:element type="xs:string" name="MILEPOINTDISTANCE"/>
    MILEPOINTDISTANCEUNITS: str  # <xs:element name="MILEPOINTDISTANCEUNITS"> (restricted to M, F, U, and '')
    NARRATIVE: str  # <xs:element type="xs:string" name="NARRATIVE"/>
    NONMOTORISTs: NonMotoristsType  # <xs:element type="cras:NONMOTORISTType" name="NONMOTORIST" maxOccurs="unbounded" minOccurs="0" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    NONTRAFFIC: Optional[bool]  # <xs:element name="NONTRAFFIC"> optional to handle the Unknown option
    NUMBEROFLANES: str  # <xs:element type="xs:string" name="NUMBEROFLANES"/>
    OFFROADDESCRIPTION: Optional[str]  # <xs:element type="xs:string" name="OFFROADDESCRIPTION" nillable="true"/>
    PDFREPORTs: PdfReportsType  # <xs:element type="cras:PDFREPORTsType" name="PDFREPORTs" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    PHOTOSTAKEN: Optional[bool]  # <xs:element name="PHOTOSTAKEN"> optional to handle the Unknown option
    People: PeopleType  # <xs:element type="cras:PeopleType" name="People" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    RAMP: Optional[str]  # <xs:element type="xs:string" name="RAMP" nillable="true"/>
    REPORTCOUNTYLOCATION: int  # <xs:element name="REPORTCOUNTYLOCATION"> (restricted to 03, 23, 24, and 88)
    REPORTDOCUMENTs: ReportDocumentsType  # <xs:element type="xs:string" name="REPORTDOCUMENTs" nillable="true"/>
    REPORTNUMBER: str  # <xs:element type="xs:string" name="REPORTNUMBER"/>
    REPORTPHOTOes: ReportPhotoesType  # <xs:element type="xs:string" name="REPORTPHOTOes" nillable="true"/>
    REPORTTYPE: str  # <xs:element name="REPORTTYPE"> (restricted to 'Property Damage Crash', 'Injury Crash', and 'Fatal Crash')
    ROADALIGNMENT: str  # <xs:element name="ROADALIGNMENT"> (restricted to 00, 01, 02, 03, 88, 99 and '')
    ROADCONDITION: str  # <xs:element type="xs:string" name="ROADCONDITION"/>
    ROADDIVISION: str  # <xs:element name="ROADDIVISION"> (restricted to 00, 01, 02, 03, 04, 05.01, 88, 99 and '')
    ROADGRADE: str  # <xs:element name="ROADGRADE"> (restricted to 00, 01, 02, 03, 04, 05, 06, 88, 99 and '')
    ROADID: str  # <xs:element type="xs:string" name="ROADID"/> (this is a six digit number, not a UUID)
    ROADWAY: RoadwayType  # <xs:element type="cras:ROADWAYType" name="ROADWAY" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    SCHOOLBUSINVOLVEMENT: int  # <xs:element name="SCHOOLBUSINVOLVEMENT"> (restricted to 00, 01, 02, 03, and 99)
    STATEGOVERNMENTPROPERTYNAME: Optional[str]  # <xs:element type="xs:string" name="STATEGOVERNMENTPROPERTYNAME" nillable="true"/>
    SUPERVISOR: Optional[str]  # <xs:element type="xs:string" name="SUPERVISOR" nillable="true"/>
    SUPERVISORUSERNAME: str  # <xs:element type="xs:string" name="SUPERVISORUSERNAME"/>
    SUPERVISORYDATE: datetime  # <xs:element type="xs:dateTime" name="SUPERVISORYDATE"/>
    SURFACECONDITION: str  # <xs:element type="xs:string" name="SURFACECONDITION"/>
    TRAFFICCONTROL: int  # <xs:element type="xs:byte" name="TRAFFICCONTROL"/>
    TRAFFICCONTROLFUNCTIONING: str  # <xs:element name="TRAFFICCONTROLFUNCTIONING"> (restricted to Y, N, U, and '')
    UPDATEDATE: datetime  # <xs:element type="xs:string" name="UPDATEDATE"/>
    UPLOADVERSION: str  # <xs:element type="xs:string" name="UPLOADVERSION"/>
    VEHICLEs: VehiclesType  # <xs:element type="cras:VEHICLEsType" name="VEHICLEs" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    VERSIONNUMBER: int  # <xs:element name="VERSIONNUMBER">
    WEATHER: float  # <xs:element type="xs:float" name="WEATHER"/>
    WITNESSes: WitnessesType
