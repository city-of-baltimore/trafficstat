"""Types used in src/crash_data_ingestor.py"""
# pylint:disable=line-too-long
from collections import OrderedDict
from typing import Any, List, Optional, Sequence, Tuple, TypedDict, Union
from datetime import date, datetime
from uuid import UUID

# The 'unsubscriptable-object' disable is because of issue https://github.com/PyCQA/pylint/issues/3882 with subscripting
# Optional. When thats fixed, we can remove those disables.
# pylint:disable=unsubscriptable-object

# The 'E0239: Inheriting 'TypedDict', which is not a class. (inherit-non-class)' is because of issue
# https://github.com/PyCQA/pylint/issues/3876. When that's fixed, we can remove those disables

# pylint:disable=too-few-public-methods

# definitions for typing
SingleAttrElement = OrderedDict[str, Optional[str]]
MultipleAttrElement = List[SingleAttrElement]
SqlExecuteType = Sequence[Union[Tuple[Any], Any]]


class ApprovalDataType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
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


# Inside the CIRCUMSTANCEs tag
class CircumstanceType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Data for table acrs_circumstances"""
    CIRCUMSTANCECODE: float  # <xs:element type="xs:float" name="CIRCUMSTANCECODE"/>
    CIRCUMSTANCEID: int  # <xs:element type="xs:int" name="CIRCUMSTANCEID"/>
    CIRCUMSTANCETYPE: str  # <xs:element name="CIRCUMSTANCETYPE"> (restricted to values 'weather', 'road', 'person', and 'vehicle')
    PERSONID: Optional[UUID]  # <xs:element type="xs:string" name="PERSONID" nillable="true"/>
    REPORTNUMBER: str  # <xs:element type="xs:string" name="REPORTNUMBER"/>
    VEHICLEID: Optional[UUID]  # <xs:element type="xs:string" name="VEHICLEID" nillable="true"/>


class CircumstancesType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Multiple instance of CircumstanceType"""
    CIRCUMSTANCE: List[CircumstanceType]


# Inside the CITATIONCODES tag
class CitationCodeType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Data for table acrs_citation_codes"""
    CITATIONNUMBER: str  # <xs:element type="xs:string" name="CITATIONNUMBER"/>
    PERSONID: UUID  # <xs:element type="xs:string" name="PERSONID"/>
    REPORTNUMBER: str  # <xs:element type="xs:string" name="REPORTNUMBER"/>


class CitationCodesType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Multiple instance of CitationCodeType"""
    CITATIONCODE: List[CitationCodeType]


# Inside the DIAGRAM tag
class CrashDiagramType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Data for table acrs_crash_diagrams"""
    CRASHDIAGRAM: str  # <xs:element type="xs:string" name="CRASHDIAGRAM"/>
    CRASHDIAGRAMNATIVE: str  # <xs:element type="xs:string" name="CRASHDIAGRAMNATIVE"/>
    REPORTNUMBER: str  # <xs:element type="xs:string" name="REPORTNUMBER"/>


class CommercialVehicleType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
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
    VEHICLEID: UUID  # <xs:element type="xs:string" name="VEHICLEID" minOccurs="0"/>
    WEIGHT: Optional[str]  # <xs:element type="xs:string" name="WEIGHT" minOccurs="0" nillable="true"/>
    WEIGHTUNIT: Optional[str]  # <xs:element type="xs:string" name="WEIGHTUNIT" minOccurs="0" nillable="true"/>


# Inside DAMAGEDAREAs tag
class DamagedAreaType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Data for table acrs_damaged_areas_table"""
    DAMAGEID: int  # <xs:element type="xs:int" name="DAMAGEID"/>
    IMPACTTYPE: int  # <xs:element type="xs:byte" name="IMPACTTYPE"/>
    VEHICLEID: UUID  # <xs:element type="xs:string" name="VEHICLEID"/>


class DamagedAreasType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Multiple instance of DamagedAreaType"""
    DAMAGEDAREA: List[DamagedAreaType]


# Inside EMSes tag
class EmsType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Data for table acrs_ems"""
    EMSTRANSPORTATIONTYPE: str  # <xs:element name="EMSTRANSPORTATIONTYPE"> (restricted to G, U and A)
    EMSUNITNUMBER: str  # <xs:element name="EMSUNITNUMBER"> (restricted to A-F)
    INJUREDTAKENBY: str  # <xs:element type="xs:string" name="INJUREDTAKENBY"/> (IE: Medic # 20)
    INJUREDTAKENTO: str  # <xs:element type="xs:string" name="INJUREDTAKENTO"/>
    REPORTNUMBER: str  # <xs:element type="xs:string" name="REPORTNUMBER"/>


class EmsesType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Multiple instance of EmsType"""
    EMS: List[EmsType]


# Inside EVENTS tag
class EventType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Data for table acrs_events"""
    EVENTID: int  # <xs:element type="xs:int" name="EVENTID"/>
    EVENTSEQUENCE: int  # <xs:element type="xs:byte" name="EVENTSEQUENCE"/>
    EVENTTYPE: int  # <xs:element type="xs:byte" name="EVENTTYPE"/>
    VEHICLEID: UUID  # <xs:element type="xs:string" name="VEHICLEID"/>


class EventsType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Multiple instance of EventType"""
    EVENT: List[EventType]


# Inside the PDFREPORTs tag
class PdfReportDataType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Data for acrs_pdf_report"""
    CHANGEDBY: str  # <xs:element type="xs:string" name="CHANGEDBY"/>
    DATESTATUSCHANGED: datetime  # <xs:element type="xs:dateTime" name="DATESTATUSCHANGED"/>
    PDFREPORT1: str  # <xs:element type="xs:string" name="PDFREPORT1"/>
    PDF_ID: int  # <xs:element type="xs:int" name="PDF_ID"/>
    REPORTNUMBER: str  # <xs:element type="xs:string" name="REPORTNUMBER"/>
    STATUS: str  # <xs:element type="xs:string" name="STATUS"/>


class PdfReportsType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Multiple instance of PdfReportDataType"""
    PDFREPORT: List[PdfReportDataType]


# Acts as both the ACRSPERSON tag (inside People tag), PERSON tag, and the OWNER tag
class PersonType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
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
    PERSONID: UUID  # <xs:element type="xs:string" name="PERSONID"/>
    RACE: Optional[str]  # <xs:element type="xs:string" name="RACE" nillable="true"/>
    REPORTNUMBER: str  # <xs:element type="xs:string" name="REPORTNUMBER"/>
    SEX: Optional[str]  # <xs:element name="SEX"> (restricted to 'F', 'M', 'U', and '')
    STATE: str  # <xs:element type="xs:string" name="STATE"/>
    ZIP: str  # <xs:element type="xs:string" name="ZIP"/>


class PeopleType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Multiple instance of PersonType"""
    ACRSPERSON: List[PersonType]


################
# Person Types #
################

# Inside the DRIVERs tag
class DriverType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
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
    PERSONID: UUID  # <xs:element type="xs:string" name="PERSONID"/>
    SAFETYEQUIPMENT: float  # <xs:element type="xs:float" name="SAFETYEQUIPMENT"/>
    SUBSTANCEUSE: Optional[int]  # <xs:element type="xs:byte" name="SUBSTANCEUSE"/>
    VEHICLEID: UUID  # <xs:element type="xs:string" name="VEHICLEID"/>


class DriversType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Multiple instance of DriverType"""
    DRIVER: List[DriverType]


# Inside the PASSENGERs tag
class PassengerType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Data for acrs_person_info"""
    AIRBAGDEPLOYED: int  # <xs:element name="AIRBAGDEPLOYED"> (restricted to values 00, 01, 02, 03, 04, 88 and 99)
    EJECTION: int  # <xs:element name="EJECTION"> (restricted to 00, 01, 02, 03, 04, 88, and 99)
    EMSRUNREPORTNUMBER: Optional[str]  # <xs:element type="xs:string" name="EMSRUNREPORTNUMBER" nillable="true"/>
    EMSUNITNUMBER: Optional[str]  # <xs:element name="EMSUNITNUMBER" nillable="true"> (restricted to A, B, C, D, E, J, K, L and '')
    EQUIPMENTPROBLEM: int  # <xs:element name="EQUIPMENTPROBLEM"> (restricted to 00, 01, 11, 13, 31, 44, 45, 47, 88 and 99)
    INJURYSEVERITY: int  # <xs:element name="INJURYSEVERITY"> (restricted to 01, 02, 03, 04, and 05)
    PERSON: PersonType  # <xs:element type="cras:PERSONType" name="PERSON" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    SAFETYEQUIPMENT: float  # <xs:element type="xs:float" name="SAFETYEQUIPMENT"/>
    SEAT: int  # <xs:element name="SEAT"> (restricted to 00, 01, 02, 03, 88, and 99)
    SEATINGLOCATION: float  # <xs:element type="xs:float" name="SEATINGLOCATION"/>
    SEATINGROW: int  # <xs:element type="xs:byte" name="SEATINGROW"/>
    VEHICLEID: UUID  # <xs:element type="xs:string" name="VEHICLEID"/>


class PassengersType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Multiple instance of PassengerType"""
    PASSENGER: List[PassengerType]


# Inside the NONMOTORISTs tag
class NonMotoristType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
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
    PERSONID: UUID  # <xs:element type="xs:string" name="PERSONID"/>
    REPORTNUMBER: str  # <xs:element type="xs:string" name="REPORTNUMBER"/>
    SAFETYEQUIPMENT: float  # <xs:element type="xs:float" name="SAFETYEQUIPMENT"/>
    SUBSTANCEUSE: int  # <xs:element name="SUBSTANCEUSE"> (restricted to 00, 01, 11, 12, 13, 14, 21, 22, 88, and 99)
    UNITNUMBERFIRSTSTRIKE: str  # <xs:element name="UNITNUMBERFIRSTSTRIKE"> (restricted to 1, 2 and '')


class NonMotoristsType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Multiple instance of NonMotoristType"""
    NONMOTORIST: List[NonMotoristType]


class ReportDocumentType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """There is not an example of this data, so this is just a stub for now. For the REPORTDOCUMENTS tag."""


class ReportDocumentsType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Multiple instance of ReportDocumentType"""
    REPORTDOCUMENT: List[ReportDocumentType]


class ReportPhotoType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """There is not an example of this data, so this is just a stub for now"""


class ReportPhotoesType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Multiple instance of ReportPhotoType"""
    REPORTPHOTO: List[ReportPhotoType]


class RoadwayType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
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
    ROADID: UUID  # <xs:element type="xs:string" name="ROADID" minOccurs="0"/>
    ROAD_NAME: Optional[str]  # <xs:element type="xs:string" name="ROAD_NAME" minOccurs="0"/>
    ROUTE_NUMBER: Optional[str]  # <xs:element type="xs:string" name="ROUTE_NUMBER" minOccurs="0"/>
    ROUTE_SUFFIX: Optional[str]  # <xs:element name="ROUTE_SUFFIX" minOccurs="0" nillable="true"> (restricted to E, AL, B, A and '')
    ROUTE_TYPE: Optional[str]  # <xs:element name="ROUTE_TYPE" minOccurs="0">


# Inside the TOWEDUNITs tag
class TowedUnitType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Data for table acrs_towed_unit"""
    INSURANCEPOLICYNUMBER: str  # <xs:element type="xs:string" name="INSURANCEPOLICYNUMBER"/>
    INSURER: str  # <xs:element type="xs:string" name="INSURER"/>
    LICENSEPLATENUMBER: str  # <xs:element type="xs:string" name="LICENSEPLATENUMBER"/>
    LICENSEPLATESTATE: str  # <xs:element type="xs:string" name="LICENSEPLATESTATE"/>
    OWNER: PersonType  # <xs:element type="cras:OWNERType" name="OWNER" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    OWNERID: UUID  # <xs:element type="xs:string" name="OWNERID"/>
    TOWEDID: UUID  # <xs:element type="xs:string" name="TOWEDID"/>
    UNITNUMBER: str  # <xs:element type="xs:string" name="UNITNUMBER" nillable="true"/>
    VEHICLEID: UUID  # <xs:element type="xs:string" name="VEHICLEID"/>
    VEHICLEMAKE: str  # <xs:element type="xs:string" name="VEHICLEMAKE"/>
    VEHICLEMODEL: str  # <xs:element type="xs:string" name="VEHICLEMODEL"/>
    VEHICLEYEAR: int  # <xs:element type="xs:short" name="VEHICLEYEAR"/>
    VIN: str  # <xs:element type="xs:string" name="VIN"/>


class TowedUnitsType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Multiple instance of TowedUnitType"""
    TOWEDUNIT: List[TowedUnitType]


# Inside VEHICLEUSEs tag
class VehicleUseType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Data for table acrs_vehicle_uses"""
    ID: int  # <xs:element type="xs:int" name="ID"/>
    VEHICLEID: UUID  # <xs:element type="xs:string" name="VEHICLEID"/>
    VEHICLEUSECODE: int  # <xs:element name="VEHICLEUSECODE"> (restricted to 00, 01, 02, and 03)


class VehicleUsesType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Multiple instance of VehicleUseType"""
    VEHICLEUSE: List[VehicleUseType]


class WitnessType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Data for table acrs_witnesses"""
    PERSON: PersonType  # <xs:element type="cras:PERSONType" name="PERSON" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    PERSONID: UUID  # <xs:element type="xs:string" name="PERSONID"/>
    REPORTNUMBER: str  # <xs:element type="xs:string" name="REPORTNUMBER"/>


class WitnessesType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Multiple instance of WitnessType"""
    WITNESS: List[WitnessType]


# Inside the VEHICLEs.ACRSVEHICLE tag
class VehicleType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
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
    OWNERID: UUID  # <xs:element type="xs:string" name="OWNERID"/>
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
    VEHICLEID: UUID  # <xs:element type="xs:string" name="VEHICLEID"/>
    VEHICLEMAKE: str  # <xs:element type="xs:string" name="VEHICLEMAKE"/>
    VEHICLEMODEL: str  # <xs:element type="xs:string" name="VEHICLEMODEL"/>
    VEHICLEMOVEMENT: Optional[float]  # <xs:element type="xs:float" name="VEHICLEMOVEMENT"/>
    VEHICLEREMOVEDBY: Optional[str]  # <xs:element type="xs:string" name="VEHICLEREMOVEDBY" nillable="true"/>
    VEHICLEREMOVEDTO: Optional[str]  # <xs:element type="xs:string" name="VEHICLEREMOVEDTO" nillable="true"/>
    VEHICLETOWEDAWAY: Optional[int]  # <xs:element name="VEHICLETOWEDAWAY"> (restricted to Y, N, U and '')
    VEHICLEUSEs: VehicleUsesType  # <xs:element type="cras:VEHICLEUSEsType" name="VEHICLEUSEs" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    VEHICLEYEAR: str  # <xs:element type="xs:string" name="VEHICLEYEAR"/>
    VIN: str  # <xs:element type="xs:string" name="VIN"/>


class VehiclesType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Multiple instance of VehicleType"""
    ACRSVEHICLE: List[VehicleType]


class CrashDataType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Data for table acrs_crashes"""
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
    CONMAINZONE: bool  # <xs:element name="CONMAINWORKERSPRESENT" nillable="true">
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
    HITANDRUN: bool  # <xs:element name="HITANDRUN">
    INSERTDATE: datetime  # <xs:element type="xs:dateTime" name="INSERTDATE"/>
    INTERCHANGEAREA: str  # <xs:element name="INTERCHANGEAREA"> (restricted to 00, 01, 02, 03, 04, 05, 06, 88, 99, and '')
    INTERCHANGEIDENTIFICATION: Optional[str]  # <xs:element type="xs:string" name="INTERCHANGEIDENTIFICATION" nillable="true"/>
    INTERSECTIONTYPE: str  # <xs:element name="INTERSECTIONTYPE">
    INVESTIGATINGOFFICERUSERNAME: str  # <xs:element type="xs:string" name="INVESTIGATINGOFFICERUSERNAME"/>
    INVESTIGATOR: Optional[str]  # <xs:element type="xs:string" name="INVESTIGATOR" nillable="true"/>
    JUNCTION: str  # <xs:element type="xs:string" name="JUNCTION"/>
    LANEDIRECTION: Optional[str]  # <xs:element name="LANEDIRECTION"> (restricted to N, S, E, W, U and '')
    LANENUMBER: str  # <xs:element name="LANENUMBER"> (restricted to 1, 2, 3, 4, 5, 6 or '')
    LANETYPE: str  # <xs:element type="xs:string" name="LANETYPE" nillable="true"/>
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
    NONTRAFFIC: bool  # <xs:element name="NONTRAFFIC">
    NUMBEROFLANES: str  # <xs:element type="xs:string" name="NUMBEROFLANES"/>
    OFFROADDESCRIPTION: str  # <xs:element type="xs:string" name="OFFROADDESCRIPTION" nillable="true"/>
    PDFREPORTs: PdfReportsType  # <xs:element type="cras:PDFREPORTsType" name="PDFREPORTs" xmlns:cras="http://schemas.datacontract.org/2004/07/CrashReport.DataLayer.v20170201"/>
    PHOTOSTAKEN: bool  # <xs:element name="PHOTOSTAKEN">
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
