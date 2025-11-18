import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import Field, BaseModel

logger = logging.getLogger(__name__)


# Nested models for embedded documents
class RunwayDetail(BaseModel):
    """Runway details embedded in airport information"""

    rw_index: str = Field(
        alias="rw_index",
        description="Runway index",
        examples=["07C", "25L", "01R"]
    )

    operating_carrier: Optional[str] = Field(
        None,
        alias="operating_carrier",
        description="Operating Carrier"
    )
    
    ac_owner: Optional[str] = Field(
        None,
        alias="ac_owner",
        description="Owner of the aircraft"
    )
    
    ac_subtype: Optional[str] = Field(
        None,
        alias="ac_subtype",
        description="Subtype of the aircraft"
    )
    
    rw_length: Optional[int] = Field(
        None,
        alias="rw_length",
        description="Length of Runway (m)"
    )
    
    rw_category: Optional[str] = Field(
        None,
        alias="rw_category",
        description="Category of Runway (e.g. 'ILS')"
    )
    
    rw_plan_visibility: Optional[str] = Field(
        None,
        alias="rw_plan_visibility",
        description="Plan visibility (m)"
    )
    
    rw_decision_height: Optional[str] = Field(
        None,
        alias="rw_decision_height",
        description="Decision Height (m)"
    )
    
    remark: Optional[str] = Field(
        None,
        alias="remark",
        description="Additional remarks"
    )
    
    record_id: Optional[int] = Field(
        None,
        alias="record_id",
        description="Unique identifier for the record"
    )
    
    last_update: Optional[datetime] = Field(
        None,
        alias="last_update",
        description="Timestamp of last update"
    )
    
    last_update_user_id: Optional[str] = Field(
        None,
        alias="last_update_user_id",
        description="User ID of last update"
    )

    class Config:
        populate_by_name = True


class SubtypeDetail(BaseModel):
    """Subtype-specific airport details"""
    
    aircraft_owner: Optional[str] = Field(
        None,
        alias="aircraft_owner",
        description="A/C Owner or * for any."
    )
    
    subfleet_type: Optional[str] = Field(
        None,
        alias="subfleet_type",
        description="A/C Subtype or * for any."
    )
    
    effective_date: Optional[datetime] = Field(
        None,
        alias="effective_date",
        description="Valid From"
    )
    
    discontinue_date: Optional[datetime] = Field(
        None,
        alias="discontinue_date",
        description="Valid To"
    )
    
    standard_taxitime_in: Optional[int] = Field(
        None,
        alias="standard_taxitime_in",
        description="Standard Inbound Taxitime for this AP."
    )
    
    standard_taxitime_out: Optional[int] = Field(
        None,
        alias="standard_taxitime_out",
        description="Standard Outbound Taxitime for this AP"
    )
    
    last_update: Optional[datetime] = Field(
        None,
        alias="last_update",
        description="Last update time stamp"
    )
    
    last_update_user_id: Optional[str] = Field(
        None,
        alias="last_update_user_id",
        description="Last update user id"
    )
    
    record_id: Optional[int] = Field(
        None,
        alias="record_id",
        description="Unique identifier for the record"
    )

    class Config:
        populate_by_name = True


class CityInfo(BaseModel):
    """City information"""
    
    iata_city_code: Optional[str] = Field(
        None,
        alias="iata_city_code",
        description="IATA code of the city"
    )
    
    city: Optional[str] = Field(
        None,
        alias="city",
        description="Name of the city"
    )
    
    iso_country_code: Optional[str] = Field(
        None,
        alias="iso_country_code",
        description="ISO country code"
    )
    
    state_designator: Optional[str] = Field(
        None,
        alias="state_designator",
        description="State designator"
    )
    
    last_update: Optional[datetime] = Field(
        None,
        alias="last_update",
        description="Last update timestamp"
    )
    
    last_update_user_id: Optional[str] = Field(
        None,
        alias="last_update_user_id",
        description="User ID of last update"
    )

    class Config:
        populate_by_name = True


class AreaRuleWithDescription(BaseModel):
    """Area rule with embedded description"""
    
    res_model_id: Optional[int] = Field(
        None,
        alias="res_model_id",
        description="Resource Model ID"
    )
    
    area_designator: Optional[str] = Field(
        None,
        alias="area_designator",
        description="Area Designator"
    )
    
    element_type: Optional[str] = Field(
        None,
        alias="element_type",
        description="Element Type C/Y/A (Country/City/Airport)"
    )
    
    element_designator: Optional[str] = Field(
        None,
        alias="element_designator",
        description="Element Designator (country/city/airport code)"
    )
    
    included_or_excluded: Optional[str] = Field(
        None,
        alias="included_or_excluded",
        description="Included or Exclude I/X"
    )
    
    description: Optional[str] = Field(
        None,
        alias="description",
        description="Area Description"
    )
    
    record_id: Optional[int] = Field(
        None,
        alias="record_id",
        description="Record ID"
    )
    
    last_update: Optional[datetime] = Field(
        None,
        alias="last_update",
        description="Timestamp of last update"
    )
    
    last_update_user_id: Optional[str] = Field(
        None,
        alias="last_update_user_id",
        description="User ID of last update"
    )

    class Config:
        populate_by_name = True


class AreaRules(BaseModel):
    """Area rules categorized by type"""
    
    airport: Optional[List[AreaRuleWithDescription]] = Field(
        default_factory=list,
        alias="airport",
        description="Area rules for airports"
    )
    
    country: Optional[List[AreaRuleWithDescription]] = Field(
        default_factory=list,
        alias="country",
        description="Area rules for countries"
    )
    
    city: Optional[List[AreaRuleWithDescription]] = Field(
        default_factory=list,
        alias="city",
        description="Area rules for cities"
    )

    class Config:
        populate_by_name = True


class AirportsAndGeographicInformation(BaseModel):
    __version__ = "1.0.0"
    """Airports and Geographic Information - Aggregated Dataset"""

    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Metadata when the record is processed",
    )
    
    # Core airport fields (from ap_basics)
    iata_ap_code: str = Field(
        max_length=3,
        description="IATA airport code"
    )
    
    valid_since: datetime = Field(
        description="Valid from date"
    )
    
    valid_until: datetime = Field(
        description="Valid until date"
    )
    
    icao_code: Optional[str] = Field(
        None,
        max_length=4,
        description="ICAO airport code"
    )
    
    ap_name: str = Field(
        max_length=30,
        description="Airport name"
    )
    
    country_code: str = Field(
        max_length=4,
        description="Country code"
    )
    
    dst_zone_code: str = Field(
        max_length=4,
        description="Daylight saving time zone code"
    )
    
    area: Optional[str] = Field(
        None,
        max_length=3,
        description="Area code"
    )
    
    category: str = Field(
        max_length=1,
        description="Airport category"
    )
    
    time_zone: str = Field(
        max_length=4,
        description="Time zone code"
    )
    
    coord_longitude: str = Field(
        max_length=10,
        description="Longitude coordinate"
    )
    
    coord_latitude: str = Field(
        max_length=9,
        description="Latitude coordinate"
    )
    
    external_reference: Optional[str] = Field(
        None,
        max_length=10,
        description="External reference"
    )
    
    record_id: int = Field(
        default=0,
        description="Record ID"
    )
    
    last_update: Optional[datetime] = Field(
        None,
        description="Last update timestamp"
    )
    
    last_update_user_id: Optional[str] = Field(
        None,
        max_length=32,
        description="Last update user ID"
    )
    
    ap_name_nls: Optional[str] = Field(
        None,
        max_length=60,
        description="Airport name in native language"
    )
    
    # Aggregated fields from lookups
    runways: Optional[List[RunwayDetail]] = Field(
        default_factory=list,
        description="List of runways at this airport"
    )
    
    subtype_details: Optional[List[SubtypeDetail]] = Field(
        default_factory=list,
        description="Subtype-specific airport details"
    )
    
    city_info: Optional[List[CityInfo]] = Field(
        default_factory=list,
        description="City information"
    )
    
    # Flattened fields from city_info
    iata_city_code: Optional[str] = Field(
        None,
        description="IATA city code (from city_info)"
    )
    
    city: Optional[str] = Field(
        None,
        description="City name (from city_info)"
    )
    
    state_designator: Optional[str] = Field(
        None,
        description="State designator (from city_info)"
    )
    
    # Country name (from country lookup)
    country: Optional[str] = Field(
        None,
        description="Country name"
    )
    
    # Time zone information
    diff_utc_lst: Optional[int] = Field(
        None,
        description="Deviation to UTC (signed Minutes)"
    )
    
    # DST information
    diff_lst_dst: Optional[int] = Field(
        None,
        description="Deviation from Local Standard Time (signed Minutes)"
    )
    
    # Area rules
    area_rules: Optional[AreaRules] = Field(
        None,
        description="Area rules categorized by airport, country, and city"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "iata_ap_code": "HKG",
                    "valid_since": "1970-01-01T00:00:00.000Z",
                    "valid_until": "2035-12-31T00:00:00.000Z",
                    "icao_code": "VHHH",
                    "ap_name": "HONG KONG INTL",
                    "country_code": "HK",
                    "dst_zone_code": "HK01",
                    "area": "SEA",
                    "category": "A",
                    "time_zone": "HK01",
                    "coord_longitude": "E11372",
                    "coord_latitude": "N02231",
                    "external_reference": None,
                    "record_id": 15458,
                    "last_update": "2022-03-02T10:38:20.000Z",
                    "last_update_user_id": "netline",
                    "ap_name_nls": "香港國際機場",
                    "iata_city_code": "HKG",
                    "city": "HONG KONG",
                    "state_designator": "00",
                    "country": "HONG KONG",
                    "diff_utc_lst": 480,
                    "diff_lst_dst": 0,
                    "runways": [
                        {
                            "rw_index": "07C",
                            "rw_length": 12467,
                            "rw_category": "ILS",
                            "operating_carrier": "XXX",
                            "ac_owner": "*",
                            "ac_subtype": "*"
                        }
                    ],
                    "subtype_details": [
                        {
                            "aircraft_owner": "CX",
                            "subfleet_type": "*",
                            "effective_date": "2025-11-05T00:00:00",
                            "discontinue_date": "2035-12-31T00:00:00",
                            "standard_taxitime_in": 12,
                            "standard_taxitime_out": 22
                        }
                    ],
                    "area_rules": {
                        "airport": [
                            {
                                "area_designator": "ST-SEA",
                                "element_type": "A",
                                "element_designator": "HKG",
                                "included_or_excluded": "I",
                                "description": "Southeast Asia"
                            }
                        ],
                        "country": [
                            {
                                "area_designator": "ASIA-PAC",
                                "element_type": "C",
                                "element_designator": "HK",
                                "included_or_excluded": "I",
                                "description": "Asia Pacific Region"
                            }
                        ],
                        "city": []
                    }
                }
            ]
        }


if __name__ == "__main__":
    """
    Test script to validate the AircraftConfiguration schema against the
    JSON dataset.
    """
    import json
    import sys
    from pathlib import Path
    from pydantic import ValidationError

    # Configure logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Locate the JSON file
    json_file = Path(__file__).resolve()
    logger.info(f"Script location: {json_file}")
    json_path = json_file.with_suffix('.json')
    logger.info(f"Looking for JSON file at: {json_path}")

    if not json_path.exists():
        logger.error(f"JSON file not found: {json_path}")
        sys.exit(1)

    # Load the JSON data
    logger.info("Loading JSON data...")
    with open(json_path, 'r') as f:
        data = json.load(f)

    logger.info(f"Loaded {len(data)} records from JSON file")

    # Statistics
    total_records = len(data)
    successful_validations = 0
    failed_validations = 0
    validation_errors = []

    # Test each record
    logger.info("Starting validation...")
    for idx, record in enumerate(data, 1):
        try:
            # Remove MongoDB-specific fields
            if '_id' in record:
                del record['_id']

            # Convert MongoDB date format to ISO string
            def convert_dates(obj):
                if isinstance(obj, dict):
                    if '$date' in obj:
                        return obj['$date']
                    return {k: convert_dates(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_dates(item) for item in obj]
                return obj

            record = convert_dates(record)

            # Validate the record
            airports_and_geographic_information = AirportsAndGeographicInformation(**record)
            successful_validations += 1

            # Log first successful validation as example
            if successful_validations == 1:
                logger.info("✓ First record validated successfully:")
                logger.info(
                    f"  IATA AP Code: {airports_and_geographic_information.iata_ap_code}"
                )
                logger.info(
                    f"  Valid Since: {airports_and_geographic_information.valid_since}"
                )
                logger.info(
                    f"  Valid Until: {airports_and_geographic_information.valid_until}"
                )
                logger.info(
                    f"  ICAO Code: {airports_and_geographic_information.icao_code}"
                )
                logger.info(
                    f"  AP Name: {airports_and_geographic_information.ap_name}"
                )

        except ValidationError as e:
            failed_validations += 1
            error_info = {
                'record_index': idx,
                'iata_ap_code': record.get('iata_ap_code', 'UNKNOWN'),
                'errors': e.errors()
            }
            validation_errors.append(error_info)

            # Log first few errors in detail
            if failed_validations <= 3:
                apt = record.get('iata_ap_code', 'UNKNOWN')
                logger.error(
                    f"✗ Validation failed for record {idx} "
                    f"(IATA Code: {apt})"
                )
                logger.error(f"  Errors: {e.errors()}")

        except Exception as e:
            failed_validations += 1
            error_info = {
                'record_index': idx,
                'iata_ap_code': record.get('iata_ap_code', 'UNKNOWN'),
                'errors': str(e)
            }
            validation_errors.append(error_info)
            logger.error(f"✗ Unexpected error for record {idx}: {e}")

        # Progress indicator every 100 records
        if idx % 100 == 0:
            logger.info(
                f"Progress: {idx}/{total_records} records processed..."
            )

    # Summary
    logger.info("\n" + "="*70)
    logger.info("VALIDATION SUMMARY")
    logger.info("="*70)
    logger.info(f"Total Records:        {total_records}")
    success_pct = successful_validations/total_records*100
    logger.info(
        f"Successful:           {successful_validations} "
        f"({success_pct:.2f}%)"
    )
    fail_pct = failed_validations/total_records*100
    logger.info(
        f"Failed:               {failed_validations} ({fail_pct:.2f}%)"
    )
    logger.info("="*70)

    # Show error breakdown if there are failures
    if failed_validations > 0:
        logger.warning(
            f"\n{failed_validations} validation errors found."
        )
        logger.warning("First 5 failed records:")
        for error_info in validation_errors[:5]:
            apt = error_info['iata_ap_code']
            idx_val = error_info['record_index']
            logger.warning(
                f"  - Record {idx_val} (IATA Code: {apt})"
            )
            if isinstance(error_info['errors'], list):
                # Show first 2 errors per record
                for err in error_info['errors'][:2]:
                    logger.warning(f"    • {err}")
            else:
                logger.warning(f"    • {error_info['errors']}")

        # Save detailed errors to file
        error_file = json_file.with_name('validation_errors.json')
        with open(error_file, 'w') as f:
            json.dump(validation_errors, f, indent=2, default=str)
        logger.info(f"\nDetailed errors saved to: {error_file}")
    else:
        logger.info("\n✓ All records validated successfully!")
        logger.info("Schema is correctly built and matches the dataset.")

    # Exit with appropriate code
    sys.exit(0 if failed_validations == 0 else 1)
