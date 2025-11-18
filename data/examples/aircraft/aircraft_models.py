from datetime import datetime
from typing import Optional, Dict, Any, List
import logging

from pydantic import Field, BaseModel


logger = logging.getLogger(__name__)

class Aircraft(BaseModel):
    __version__ = "1.0.0"
    metadata: Dict[str, Any] = Field(
        description="Metadata when the record is processed",
    )
    registration: str = Field(
        ...,
        alias="REGISTRATION",
        max_length=10,
        description="Registration of the Aircraft",
        examples=["BHNR", "LD33F"]
    )
    valid_since: datetime = Field(
        ...,
        alias="VALID_SINCE",
        description="Start of validity",
    )
    valid_until: datetime = Field(
        ...,
        alias="VALID_UNTIL",
        description="End of validity",
    )
    ac_operator: str = Field(
        ...,
        alias="AC_OPERATOR",
        max_length=3,
        description="Aircraft Operator",
        examples=["LD", "CX"]
    )
    ac_owner: str = Field(
        ...,
        alias="AC_OWNER",
        max_length=3,
        description="Owner of the aircraft",
        examples=["LD", "CX"]
    )
    ac_subtype: str = Field(
        ...,
        alias="AC_SUBTYPE",
        max_length=3,
        description="Subtype of the aircraft",
    )
    ac_logical_no: int = Field(
        ...,
        alias="AC_LOGICAL_NO",
        description="Logical number of the Aircraft",
    )
    ac_state: str = Field(
        ...,
        alias="AC_STATE",
        max_length=1,
        description="Status of Aircraft(''R''=real and ''O''=overflow)",
        enum=["R", "O"]
    )
    dry_operating_wgt: int = Field(
        ...,
        alias="DRY_OPERATING_WGT",
        description="Dry Operating Weight (kg)",
    )
    max_takeoff_wgt: int = Field(
        ...,
        alias="MAX_TAKEOFF_WGT",
        description="Max Takeoff Weight (kg)",
    )
    cargo_capacity: int = Field(
        ...,
        alias="CARGO_CAPACITY",
        description="Cargo Capacity (kg)",
    )
    fuel_capacity: int = Field(
        ...,
        alias="FUEL_CAPACITY",
        description="Fuel Capacity (kg)",
    )
    avg_fuel_consump: int = Field(
        ...,
        alias="AVG_FUEL_CONSUMP",
        description="Average Fuel Consumption (kg per hour)",
    )
    ac_index: int = Field(
        ...,
        alias="AC_INDEX",
        description="Aircraft index",
    )
    crewsize_cockpit: int = Field(
        ...,
        alias="CREWSIZE_COCKPIT",
        description="Number of Cockpit Crewmembers",
    )
    crewsize_cabin: int = Field(
        ...,
        alias="CREWSIZE_CABIN",
        description="Number of Cabin Crewmembers",
    )
    std_version: str = Field(
        ...,
        alias="STD_VERSION",
        max_length=20,
        description="Aircraft Standard Version",
    )
    ap_restriction: str = Field(
        ...,
        alias="AP_RESTRICTION",
        max_length=1,
        description="Airport Restriction - e.g. Political Reason, Performance(''Y'' or ''N'')",
        examples=["N", "Y", "R"]
    )
    ac_owner_name: str = Field(
        ...,
        alias="AC_OWNER_NAME",
        max_length=30,
        description="Full Name of Owner",
    )
    ac_subtype_name: str = Field(
        ...,
        alias="AC_SUBTYPE_NAME",
        max_length=30,
        description="Full Name of Subtype",
    )
    ac_category: str = Field(
        ...,
        alias="AC_CATEGORY",
        max_length=1,
        description="SSIM-Category of Aircraft",
    )
    remark: Optional[str] = Field(
        None,
        alias="REMARK",
        max_length=80,
        description="Additional remarks",
    )
    fuel_measure_unit: str = Field(
        ...,
        alias="FUEL_MEASURE_UNIT",
        max_length=3,
        description="Unit for fuel",
    )
    ac_callsign: Optional[str] = Field(
        None,
        alias="AC_CALLSIGN",
        max_length=5,
        description="Callsign of aircraft",
    )
    radio: Optional[str] = Field(
        None,
        alias="RADIO",
        max_length=1,
        description="Radio type",
    )
    noise: Optional[int] = Field(
        None,
        alias="NOISE",
        description="ICAO noise chapter",
    )
    phone: Optional[str] = Field(
        None,
        alias="PHONE",
        max_length=20,
        description="Onboard mobile phone number",
    )
    special_equipment: Optional[str] = Field(
        None,
        alias="SPECIAL_EQUIPMENT",
        max_length=40,
        description="Special equipment",
    )
    acars: Optional[str] = Field(
        None,
        alias="ACARS",
        max_length=1,
        description="ACARS type",
        enum=["V", "H", "S"]
    )
    alt_reg: Optional[str] = Field(
        None,
        alias="ALT_REG",
        max_length=10,
        description="Alternate Registration",
    )
    record_id: int = Field(
        default=0,
        alias="RECORD_ID",
        description="Record ID",
    )
    last_update: Optional[datetime] = Field(
        None,
        alias="LAST_UPDATE",
        description="Timestamp of last update",
    )
    last_update_user_id: Optional[str] = Field(
        None,
        alias="LAST_UPDATE_USER_ID",
        max_length=32,
        description="User ID of last update",
    )
    std_version_alt_1: Optional[str] = Field(
        None,
        alias="STD_VERSION_ALT_1",
        max_length=20,
        description="Alternative Aircraft Version 1",
    )
    std_version_alt_2: Optional[str] = Field(
        None,
        alias="STD_VERSION_ALT_2",
        max_length=20,
        description="Alternative Aircraft Version 2",
    )
    std_version_alt_3: Optional[str] = Field(
        None,
        alias="STD_VERSION_ALT_3",
        max_length=20,
        description="Alternative Aircraft Version 3",
    )
    std_version_alt_4: Optional[str] = Field(
        None,
        alias="STD_VERSION_ALT_4",
        max_length=20,
        description="Alternative Aircraft Version 4",
    )
    ils_equipment: str = Field(
        default="I",
        alias="ILS_EQUIPMENT",
        max_length=4,
        description="aircraft equipment supporting ILS CAT approaches(I, II, IIIa, IIIb)",
        enum=["I", "II", "IIIa", "IIIb"]
    )
    autoland: str = Field(
        default="N",
        alias="AUTOLAND",
        max_length=1,
        description="Autoland capability indicator",
        enum=["Y", "N"]
    )
    homebase: Optional[str] = Field(
        None,
        alias="HOMEBASE",
        max_length=3,
        description="Homebase of the aircraft (IATA CODE)",
    )

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "examples": [
                {
                    "registration": "BLXN",
                    "valid_since": "2025-08-01T00:00:00.000Z",
                    "valid_until": "2025-08-31T00:00:00.000Z",
                    "ac_operator": "CX",
                    "ac_owner": "CX",
                    "ac_subtype": "35J",
                    "homebase": None,
                    "ac_logical_no": 15,
                    "ac_state": "R",
                    "dry_operating_wgt": 0,
                    "max_takeoff_wgt": 268000,
                    "cargo_capacity": 0,
                    "fuel_capacity": 0,
                    "avg_fuel_consump": 0,
                    "ac_index": 15,
                    "crewsize_cockpit": 0,
                    "crewsize_cabin": 0,
                    "std_version": "STN",
                    "ap_restriction": "N",
                    "ac_owner_name": "CX",
                    "ac_subtype_name": "35J",
                    "ac_category": "J",
                    "remark": "46J/32W/256Y = 334",
                    "fuel_measure_unit": "kg",
                    "ac_callsign": None,
                    "radio": None,
                    "noise": None,
                    "phone": None,
                    "special_equipment": None,
                    "acars": "S",
                    "alt_reg": None,
                    "record_id": 608495,
                    "last_update": "2025-08-01T00:00:00.000Z",
                    "last_update_user_id": "netline",
                    "std_version_alt_1": None,
                    "std_version_alt_2": None,
                    "std_version_alt_3": None,
                    "std_version_alt_4": None,
                    "ils_equipment": "I",
                    "autoland": "Y",
                }
            ]
        }

    @staticmethod
    def get_query():
        return "SELECT * FROM SCHEDOPS.AIRCRAFT"

    @staticmethod
    def get_params() -> Dict[str, Any]:
        return {}

    @classmethod
    def validate(cls, data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        validated_doc, invalid_doc = [], []

        for doc in data:
            try:
                validated_data = cls(**doc)
                validated_doc.append(validated_data.model_dump(by_alias=False, exclude_unset=False))
            except Exception as e:
                invalid_doc.append({"document": doc, "error": str(e)})
                logger.warning(f"Invalid document found: {str(e)}")

        return {"valid": validated_doc, "invalid": invalid_doc}

