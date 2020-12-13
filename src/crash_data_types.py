"""Types used in src/crash_data_ingestor.py"""
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
AttrElement = OrderedDict[str, Union[SingleAttrElement, MultipleAttrElement]]
SqlExecuteType = Sequence[Union[Tuple[Any], Any]]


class CrashDataType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Data for table acrs_crashes"""
    ACRSREPORTTIMESTAMP: datetime
    AGENCYIDENTIFIER: Optional[str]
    AGENCYNAME: Optional[str]
    AREA: Optional[str]
    COLLISIONTYPE: int
    CONMAINCLOSURE: Optional[int]
    CONMAINLOCATION: Optional[int]
    CONMAINWORKERSPRESENT: Optional[bool]
    CONMAINZONE: Optional[str]
    CRASHDATE: date
    CRASHTIME: datetime
    CURRENTASSIGNMENT: Optional[str]
    CURRENTGROUP: int
    DEFAULTASSIGNMENT: str
    DEFAULTGROUP: int
    DOCTYPE: Optional[str]
    FIXEDOBJECTSTRUCK: str
    HARMFULEVENTONE: str
    HARMFULEVENTTWO: str
    HITANDRUN: bool
    INSERTDATE: datetime
    INTERCHANGEAREA: int
    INTERCHANGEIDENTIFICATION: Optional[str]
    INTERSECTIONTYPE: int
    INVESTIGATINGOFFICERUSERNAME: Optional[str]
    INVESTIGATOR: Optional[str]
    JUNCTION: str
    LANEDIRECTION: Optional[str]
    LANENUMBER: int
    LANETYPE: Optional[int]
    LATITUDE: Optional[float]
    LIGHT: str
    LOCALCASENUMBER: str
    LOCALCODES: Optional[str]
    LONGITUDE: Optional[float]
    MILEPOINTDIRECTION: Optional[str]
    MILEPOINTDISTANCE: float
    MILEPOINTDISTANCEUNITS: Optional[str]
    NARRATIVE: Optional[str]
    NONTRAFFIC: bool
    NUMBEROFLANES: int
    OFFROADDESCRIPTION: Optional[str]
    PHOTOSTAKEN: Optional[bool]
    RAMP: Optional[str]
    REPORTCOUNTYLOCATION: int
    REPORTNUMBER: str
    REPORTTYPE: str
    ROADALIGNMENT: int
    ROADCONDITION: int
    ROADDIVISION: str
    ROADGRADE: int
    ROADID: Optional[str]
    SCHOOLBUSINVOLVEMENT: int
    STATEGOVERNMENTPROPERTYNAME: Optional[str]
    SUPERVISOR: Optional[str]
    SUPERVISORUSERNAME: Optional[str]
    SUPERVISORYDATE: datetime
    SURFACECONDITION: str
    TRAFFICCONTROL: Optional[int]
    TRAFFICCONTROLFUNCTIONING: Optional[bool]
    UPDATEDATE: datetime
    UPLOADVERSION: Optional[str]
    VERSIONNUMBER: int
    WEATHER: Optional[str]


class ApprovalDataType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Data for table acrs_approval"""
    AGENCY: Optional[str]
    APPROVALDATE: datetime
    CADSENT: Optional[str]
    CADSENT_DATE: Optional[datetime]
    CC_NUMBER: str
    DATE_INITIATED2: datetime
    GROUP_NUMBER: int
    HISTORICALAPPROVALDATAs: Optional[str]
    INCIDENT_DATE: datetime
    INVESTIGATOR: Optional[str]
    REPORT_TYPE: Optional[str]
    SEQ_GUID: Optional[str]
    STATUS_CHANGE_DATE: datetime
    STATUS_ID: str
    STEP_NUMBER: Optional[int]
    TR_USERNAME: Optional[str]
    UNIT_CODE: str


class CircumstancesType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Data for table acrs_circumstances"""
    CIRCUMSTANCECODE: str
    CIRCUMSTANCEID: int
    CIRCUMSTANCETYPE: Optional[str]
    PERSONID: Optional[UUID]
    REPORTNUMBER: str
    VEHICLEID: Optional[UUID]


class CitationType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Data for table acrs_citation_codes"""
    CITATIONNUMBER: str
    PERSONID: UUID
    REPORTNUMBER: str


class CrashDiagramType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Data for table acrs_crash_diagrams"""
    CRASHDIAGRAM: Optional[str]
    CRASHDIAGRAMNATIVE: Optional[str]
    REPORTNUMBER: Optional[str]


class CommercialVehiclesType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Data for table acrs_commercial_vehicles"""
    BODYTYPE: Optional[str]
    BUSUSE: Optional[int]
    CARRIERCLASSIFICATION: Optional[int]
    CITY: Optional[str]
    CONFIGURATION: Optional[int]
    COUNTRY: Optional[str]
    DOTNUMBER: Optional[str]
    GVW: Optional[int]
    HAZMATCLASS: Optional[str]
    HAZMATNAME: Optional[str]
    HAZMATNUMBER: Optional[str]
    HAZMATSPILL: Optional[str]
    MCNUMBER: Optional[str]
    NAME: Optional[str]
    NUMBEROFAXLES: Optional[int]
    PLACARDVISIBLE: Optional[str]
    POSTALCODE: Optional[str]
    STATE: Optional[str]
    STREET: Optional[str]
    VEHICLEID: UUID
    WEIGHT: Optional[str]
    WEIGHTUNIT: Optional[str]


class DamagedAreasType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Data for table acrs_damaged_areas_table"""
    DAMAGEID: int
    IMPACTTYPE: int
    VEHICLEID: UUID


class EmsType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Data for table acrs_ems"""
    EMSTRANSPORTATIONTYPE: Optional[str]
    EMSUNITNUMBER: Optional[str]
    INJUREDTAKENBY: Optional[str]
    INJUREDTAKENTO: Optional[str]
    REPORTNUMBER: str


class EventType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Data for table acrs_events"""
    EVENTID: int
    EVENTSEQUENCE: Optional[int]
    EVENTTYPE: Optional[int]
    VEHICLEID: UUID


class PdfReportData(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Data for acrs_pdf_report"""
    CHANGEDBY: Optional[str]
    DATESTATUSCHANGED: datetime
    PDFREPORT1: Optional[str]
    PDF_ID: int
    REPORTNUMBER: str
    STATUS: str


class PersonType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Data for acrs_person"""
    ADDRESS: Optional[str]
    CITY: Optional[str]
    COMPANY: Optional[str]
    COUNTRY: Optional[str]
    COUNTY: Optional[str]
    DLCLASS: Optional[str]
    DLNUMBER: Optional[str]
    DLSTATE: Optional[str]
    DOB: Optional[date]
    FIRSTNAME: Optional[str]
    HOMEPHONE: Optional[str]
    LASTNAME: Optional[str]
    MIDDLENAME: Optional[str]
    OTHERPHONE: Optional[str]
    PERSONID: UUID
    RACE: Optional[str]
    REPORTNUMBER: str
    SEX: Optional[str]
    STATE: Optional[str]
    ZIP: Optional[str]


class PersonInfoType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Data for acrs_person_info"""
    AIRBAGDEPLOYED: Optional[int]
    ALCOHOLTESTINDICATOR: Optional[int]
    ALCOHOLTESTTYPE: Optional[str]
    ATFAULT: Optional[bool]
    BAC: Optional[str]
    CONDITION: Optional[str]
    CONTINUEDIRECTION: Optional[str]
    DRIVERDISTRACTEDBY: Optional[int]
    DRUGTESTINDICATOR: Optional[int]
    DRUGTESTRESULT: Optional[str]
    EJECTION: Optional[int]
    EMSRUNREPORTNUMBER: Optional[str]
    EMSUNITNUMBER: Optional[str]
    EQUIPMENTPROBLEM: Optional[int]
    GOINGDIRECTION: Optional[str]
    HASCDL: Optional[bool]
    INJURYSEVERITY: int
    PEDESTRIANACTIONS: Optional[int]
    PEDESTRIANLOCATION: Optional[float]
    PEDESTRIANMOVEMENT: Optional[str]
    PEDESTRIANOBEYTRAFFICSIGNAL: Optional[int]
    PEDESTRIANTYPE: Optional[int]
    PEDESTRIANVISIBILITY: Optional[int]
    PERSONID: UUID
    REPORTNUMBER: str
    SAFETYEQUIPMENT: str
    SEAT: Optional[int]
    SEATINGLOCATION: Optional[int]
    SEATINGROW: Optional[int]
    SUBSTANCEUSE: Optional[int]
    UNITNUMBERFIRSTSTRIKE: Optional[int]
    VEHICLEID: Optional[UUID]


class ReportDocument(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """There is not an example of this data, so this is just a stub for now"""


class ReportPhoto(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """There is not an example of this data, so this is just a stub for now"""


class RoadwayType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Data for table acrs_roadway"""
    COUNTY: Optional[int]
    LOGMILE_DIR: Optional[str]
    MILEPOINT: Optional[float]
    MUNICIPAL: Optional[int]
    MUNICIPAL_AREA_CODE: Optional[int]
    REFERENCE_MUNI: Optional[int]
    REFERENCE_ROADNAME: Optional[str]
    REFERENCE_ROUTE_NUMBER: Optional[str]
    REFERENCE_ROUTE_SUFFIX: Optional[str]
    REFERENCE_ROUTE_TYPE: Optional[str]
    ROADID: UUID
    ROAD_NAME: Optional[str]
    ROUTE_NUMBER: Optional[str]
    ROUTE_SUFFIX: Optional[str]
    ROUTE_TYPE: Optional[str]


class VehicleType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Data for table acrs_vehicles"""
    COMMERCIALVEHICLE: Optional[str]
    CONTINUEDIRECTION: str
    DAMAGEEXTENT: Optional[int]
    DRIVERLESSVEHICLE: Optional[bool]
    EMERGENCYMOTORVEHICLEUSE: Optional[bool]
    FIRE: Optional[bool]
    FIRSTIMPACT: Optional[int]
    GOINGDIRECTION: Optional[str]
    HITANDRUN: Optional[bool]
    INSURANCEPOLICYNUMBER: Optional[str]
    INSURER: Optional[str]
    LICENSEPLATENUMBER: Optional[str]
    LICENSEPLATESTATE: Optional[str]
    MAINIMPACT: Optional[int]
    MOSTHARMFULEVENT: Optional[str]
    OWNERID: Optional[UUID]
    PARKEDVEHICLE: Optional[bool]
    REGISTRATIONEXPIRATIONYEAR: Optional[int]
    REPORTNUMBER: str
    SFVEHICLEINTRANSPORT: Optional[int]
    SPEEDLIMIT: Optional[int]
    TOWEDUNITTYPE: Optional[int]
    UNITNUMBER: Optional[str]
    VEHICLEBODYTYPE: Optional[str]
    VEHICLEID: UUID
    VEHICLEMAKE: Optional[int]
    VEHICLEMODEL: Optional[int]
    VEHICLEMOVEMENT: Optional[float]
    VEHICLEREMOVEDBY: Optional[int]
    VEHICLEREMOVEDTO: Optional[int]
    VEHICLETOWEDAWAY: Optional[int]
    VEHICLEYEAR: Optional[int]
    VIN: Optional[int]


class TowedUnitType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Data for table acrs_towed_unit"""
    INSURANCEPOLICYNUMBER: Optional[str]
    INSURER: Optional[str]
    LICENSEPLATENUMBER: Optional[str]
    LICENSEPLATESTATE: Optional[str]
    OWNERID: UUID
    TOWEDID: UUID
    UNITNUMBER: Optional[str]
    VEHICLEID: UUID
    VEHICLEMAKE: Optional[str]
    VEHICLEMODEL: Optional[str]
    VEHICLEYEAR: Optional[int]
    VIN: Optional[str]


class VehicleUseType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Data for table acrs_vehicle_uses"""
    ID: int
    VEHICLEID: UUID
    VEHICLEUSECODE: int


class WitnessType(TypedDict):  # pylint:disable=inherit-non-class ; See comment above
    """Data for table acrs_witnesses"""
    PERSONID: UUID
    REPORTNUMBER: str
