"""
Tests for Train Status API functions.
Run with: python test_train_status.py
Or with pytest: pytest test_train_status.py -v
"""

import asyncio
import pytest
from train_status_functions import (
    fetch_train_status,
    get_station_codes_from_name,
    get_train_numbers_from_name,
    get_expected_arrival_at_station,
    get_current_train_position,
)
from train_status_schemas import (
    TrainStatusResponse,
    TrainStatusData,
    CurrentPosition,
    LatLng,
    RouteStation,
    StationSearchResult,
    TrainSearchResult,
)


# ==================== Mock Data ====================

MOCK_TRAIN_STATUS_JSON = {
    "success": True,
    "data": {
        "currentPosition": {
            "latLng": {
                "latitude": 22.583649,
                "longitude": 88.34213
            },
            "stationCode": "HWH",
            "status": 2,
            "distanceFromOriginKm": 199.2,
            "distanceFromLastStationKm": 0
        },
        "arrivalStatus": "DELAYED",
        "lastUpdatedTimestamp": 1766805925,
        "route": [
            {
                "platformNumber": "7",
                "stationCode": "ASN",
                "scheduledArrivalTime": 1766793600,
                "scheduledDepartureTime": 1766793600,
                "stopIndex": 0,
                "station_name": "Asansol Junction"
            },
            {
                "platformNumber": "4",
                "stationCode": "DGR",
                "scheduledArrivalDelaySecs": 720,
                "scheduledDepartureDelaySecs": 852,
                "actualArrivalTime": 1766796180,
                "actualDepartureTime": 1766796432,
                "scheduledArrivalTime": 1766795460,
                "scheduledDepartureTime": 1766795580,
                "stopIndex": 16,
                "station_name": "Durgapur"
            },
            {
                "platformNumber": "12",
                "stationCode": "HWH",
                "actualArrivalTime": 1766805522,
                "scheduledArrivalTime": 1766806200,
                "stopIndex": 61,
                "station_name": "Howrah Junction"
            }
        ],
        "dataSource": "OFFICIAL",
        "unmappedField_13": ""
    }
}

# Create mock TrainStatusResponse from JSON
MOCK_TRAIN_STATUS = TrainStatusResponse(**MOCK_TRAIN_STATUS_JSON)

MOCK_ROUTE_STATION_DELAYED = RouteStation(
    platformNumber="4",
    stationCode="DGR",
    station_name="Durgapur",
    stopIndex=16,
    scheduledArrivalTime=1766795460,
    scheduledDepartureTime=1766795580,
    actualArrivalTime=1766796180,
    actualDepartureTime=1766796432,
    scheduledArrivalDelaySecs=720,
    scheduledDepartureDelaySecs=852,
)

MOCK_ROUTE_STATION_EARLY = RouteStation(
    platformNumber="12",
    stationCode="HWH",
    station_name="Howrah Junction",
    stopIndex=61,
    scheduledArrivalTime=1766806200,
    actualArrivalTime=1766805522,
    scheduledArrivalDelaySecs=-678,  # Early by ~11 mins
)

MOCK_ROUTE_STATION_NO_ACTUAL = RouteStation(
    platformNumber="7",
    stationCode="ASN",
    station_name="Asansol Junction",
    stopIndex=0,
    scheduledArrivalTime=1766793600,
    scheduledDepartureTime=1766793600,
)


# ==================== Schema Tests ====================

class TestTrainStatusSchemas:
    """Tests for Pydantic schema validation."""

    def test_train_status_response_parsing(self):
        """Test that TrainStatusResponse correctly parses JSON."""
        response = TrainStatusResponse(**MOCK_TRAIN_STATUS_JSON)
        assert response.success is True
        assert response.data.arrival_status == "DELAYED"
        assert response.data.data_source == "OFFICIAL"
        assert len(response.data.route) == 3

    def test_current_position_parsing(self):
        """Test CurrentPosition parsing with camelCase aliases."""
        response = TrainStatusResponse(**MOCK_TRAIN_STATUS_JSON)
        position = response.data.current_position
        assert position.station_code == "HWH"
        assert position.status == 2
        assert position.distance_from_origin_km == 199.2
        assert position.lat_lng.latitude == 22.583649
        assert position.lat_lng.longitude == 88.34213

    def test_route_station_parsing(self):
        """Test RouteStation parsing with optional fields."""
        response = TrainStatusResponse(**MOCK_TRAIN_STATUS_JSON)
        
        # Station with delay info
        dgr = response.data.route[1]
        assert dgr.station_code == "DGR"
        assert dgr.station_name == "Durgapur"
        assert dgr.scheduled_arrival_delay_secs == 720
        assert dgr.actual_arrival_time == 1766796180
        
        # Station without delay info (origin)
        asn = response.data.route[0]
        assert asn.station_code == "ASN"
        assert asn.scheduled_arrival_delay_secs is None

    def test_route_station_helper_methods(self):
        """Test RouteStation helper methods."""
        station = MOCK_ROUTE_STATION_DELAYED
        assert station.get_arrival_delay_minutes() == 12
        assert station.get_departure_delay_minutes() == 14
        assert station.get_scheduled_arrival_datetime() is not None
        assert station.get_actual_arrival_datetime() is not None

    def test_station_search_result(self):
        """Test StationSearchResult schema."""
        result = StationSearchResult(code="RKMP", name="Rani Kamlapati(Bhopal)")
        assert result.code == "RKMP"
        assert result.name == "Rani Kamlapati(Bhopal)"

    def test_train_search_result(self):
        """Test TrainSearchResult schema with aliases."""
        result = TrainSearchResult(
            number="12137",
            name="Punjab Mail",
            fromStnCode="CSMT",
            toStnCode="FZR"
        )
        assert result.number == "12137"
        assert result.name == "Punjab Mail"
        assert result.from_stn_code == "CSMT"
        assert result.to_stn_code == "FZR"


# ==================== Function Tests ====================

class TestGetExpectedArrivalAtStation:
    """Tests for get_expected_arrival_at_station function."""

    def test_station_with_actual_arrival_delayed(self):
        """Test arrival info for a delayed station with actual arrival time."""
        result = get_expected_arrival_at_station(MOCK_TRAIN_STATUS, "DGR")
        assert "Durgapur" in result
        assert "DGR" in result
        assert "Scheduled:" in result
        assert "Actual:" in result
        assert "Delayed by 12 mins" in result
        assert "Platform: 4" in result

    def test_station_with_actual_arrival_early(self):
        """Test arrival info for station that arrived early."""
        # Create a response with early arrival
        early_json = MOCK_TRAIN_STATUS_JSON.copy()
        early_json["data"] = MOCK_TRAIN_STATUS_JSON["data"].copy()
        early_json["data"]["route"] = [
            {
                "platformNumber": "12",
                "stationCode": "HWH",
                "actualArrivalTime": 1766805522,
                "scheduledArrivalTime": 1766806200,
                "scheduledArrivalDelaySecs": -678,
                "stopIndex": 61,
                "station_name": "Howrah Junction"
            }
        ]
        early_response = TrainStatusResponse(**early_json)
        result = get_expected_arrival_at_station(early_response, "HWH")
        assert "Howrah Junction" in result
        assert "Early by" in result

    def test_station_with_only_scheduled_time(self):
        """Test arrival info for station with only scheduled time."""
        result = get_expected_arrival_at_station(MOCK_TRAIN_STATUS, "ASN")
        assert "Asansol Junction" in result
        assert "Scheduled:" in result

    def test_station_not_found(self):
        """Test response when station is not in route."""
        result = get_expected_arrival_at_station(MOCK_TRAIN_STATUS, "NDLS")
        assert "not found" in result.lower()
        assert "NDLS" in result

    def test_station_code_case_insensitive(self):
        """Test that station code lookup is case insensitive."""
        result_upper = get_expected_arrival_at_station(MOCK_TRAIN_STATUS, "DGR")
        result_lower = get_expected_arrival_at_station(MOCK_TRAIN_STATUS, "dgr")
        result_mixed = get_expected_arrival_at_station(MOCK_TRAIN_STATUS, "DgR")
        
        assert "Durgapur" in result_upper
        assert "Durgapur" in result_lower
        assert "Durgapur" in result_mixed


class TestGetCurrentTrainPosition:
    """Tests for get_current_train_position function."""

    def test_current_position_output(self):
        """Test that current position returns all expected fields."""
        result = get_current_train_position(MOCK_TRAIN_STATUS)
        
        assert "Current Train Position:" in result
        assert "Howrah Junction" in result
        assert "HWH" in result
        assert "22.583649" in result
        assert "88.34213" in result
        assert "199.2 km" in result
        assert "At Station" in result
        assert "DELAYED" in result
        assert "Last Updated:" in result
        assert "IST" in result

    def test_status_interpretation(self):
        """Test that status codes are correctly interpreted."""
        # Status 2 = At Station
        result = get_current_train_position(MOCK_TRAIN_STATUS)
        assert "At Station" in result

    def test_station_name_lookup(self):
        """Test that station name is looked up from route."""
        result = get_current_train_position(MOCK_TRAIN_STATUS)
        # Should show "Howrah Junction (HWH)" not just "Station Code: HWH"
        assert "Howrah Junction" in result


class TestGetCurrentTrainPositionEdgeCases:
    """Edge case tests for get_current_train_position."""

    def test_station_not_in_route(self):
        """Test when current station is not in route list."""
        modified_json = MOCK_TRAIN_STATUS_JSON.copy()
        modified_json["data"] = MOCK_TRAIN_STATUS_JSON["data"].copy()
        modified_json["data"]["currentPosition"] = {
            "latLng": {"latitude": 22.0, "longitude": 88.0},
            "stationCode": "XXX",  # Not in route
            "status": 1,
            "distanceFromOriginKm": 100.0,
            "distanceFromLastStationKm": 5.0
        }
        response = TrainStatusResponse(**modified_json)
        result = get_current_train_position(response)
        
        # Should still work, just show station code
        assert "Station Code: XXX" in result

    def test_distance_from_last_station(self):
        """Test when train is between stations."""
        modified_json = MOCK_TRAIN_STATUS_JSON.copy()
        modified_json["data"] = MOCK_TRAIN_STATUS_JSON["data"].copy()
        modified_json["data"]["currentPosition"] = {
            "latLng": {"latitude": 22.0, "longitude": 88.0},
            "stationCode": "DGR",
            "status": 1,  # In Transit
            "distanceFromOriginKm": 150.0,
            "distanceFromLastStationKm": 10.5
        }
        response = TrainStatusResponse(**modified_json)
        result = get_current_train_position(response)
        
        assert "In Transit" in result
        assert "10.5 km" in result


# ==================== Integration Tests (require network) ====================

class TestIntegrationTrainStatus:
    """Integration tests that call the actual API. These may be skipped in CI."""

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires network access and valid API")
    async def test_fetch_train_status_real(self):
        """Test fetching real train status."""
        result = await fetch_train_status("12618")
        if result:
            assert result.success is True
            assert result.data.route is not None
            assert len(result.data.route) > 0

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires network access and valid API")
    async def test_search_station_codes_real(self):
        """Test searching for station codes."""
        results = await get_station_codes_from_name("Howrah")
        assert len(results) > 0
        assert any(s.code == "HWH" for s in results)

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires network access and valid API")
    async def test_search_train_numbers_real(self):
        """Test searching for train numbers."""
        results = await get_train_numbers_from_name("Rajdhani")
        assert len(results) > 0
        assert all(hasattr(r, "number") for r in results)


# ==================== Timestamp and IST Tests ====================

class TestTimestampConversion:
    """Tests for timestamp to IST conversion."""

    def test_ist_timezone_in_output(self):
        """Test that output times are in IST."""
        result = get_expected_arrival_at_station(MOCK_TRAIN_STATUS, "DGR")
        assert "IST" in result

    def test_timestamp_format(self):
        """Test that timestamps are formatted correctly."""
        result = get_expected_arrival_at_station(MOCK_TRAIN_STATUS, "DGR")
        # Should contain date in format like "26 Dec 2025, 05:43 PM IST"
        assert "Dec" in result or "Jan" in result  # Month abbreviation
        assert "PM" in result or "AM" in result  # 12-hour format


# ==================== Run Tests ====================

def run_tests():
    """Run all tests."""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    run_tests()
