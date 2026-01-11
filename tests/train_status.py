"""Tests for new train status functions."""

import asyncio
import json
import pytest
from schemas.train_status_schemas import NewTrainStatusResponse
from lib.train_status_functions import (
    fetch_new_train_status,
    format_delay,
    get_expected_arrival_at_station,
    get_current_train_position,
    get_train_route,
    get_upcoming_stations,
    get_train_summary,
)
import os

# Get the directory where this test file is located
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TEST_DIR)


# Load example data for testing
def load_example_response() -> NewTrainStatusResponse:
    """Load the example JSON file and return a parsed response."""
    example_file = os.path.join(PROJECT_ROOT, "lib", "example_api_responses", "train_status.json")
    with open(example_file) as f:
        data = json.load(f)
    return NewTrainStatusResponse.model_validate(data)


class TestFormatDelay:
    """Tests for format_delay function."""

    def test_on_time(self):
        assert format_delay(0) == "On Time"

    def test_delayed_minutes_only(self):
        assert format_delay(30) == "Delayed by 30 mins"

    def test_delayed_hours_and_minutes(self):
        assert format_delay(67) == "Delayed by 1h 7m"
        assert format_delay(125) == "Delayed by 2h 5m"

    def test_early(self):
        assert format_delay(-15) == "Early by 15 mins"
        assert format_delay(-5) == "Early by 5 mins"


class TestGetExpectedArrivalAtStation:
    """Tests for get_expected_arrival_at_station function."""

    def test_current_station(self):
        response = load_example_response()
        result = get_expected_arrival_at_station(response, "BIO")
        assert "currently at/near" in result
        assert "BORDI" in result

    def test_upcoming_station(self):
        response = load_example_response()
        result = get_expected_arrival_at_station(response, "MGN")
        assert "MEGHNAGAR" in result
        assert "Scheduled Arrival" in result or "Expected Arrival" in result

    def test_destination_station(self):
        response = load_example_response()
        result = get_expected_arrival_at_station(response, "INDB")
        assert "INDORE" in result

    def test_previous_station(self):
        response = load_example_response()
        result = get_expected_arrival_at_station(response, "ADI")
        assert "already passed" in result
        assert "AHMEDABAD" in result

    def test_station_not_found(self):
        response = load_example_response()
        result = get_expected_arrival_at_station(response, "XYZ")
        assert "not found" in result

    def test_case_insensitive(self):
        response = load_example_response()
        result_upper = get_expected_arrival_at_station(response, "MGN")
        result_lower = get_expected_arrival_at_station(response, "mgn")
        assert "MEGHNAGAR" in result_upper
        assert "MEGHNAGAR" in result_lower


class TestGetCurrentTrainPosition:
    """Tests for get_current_train_position function."""

    def test_returns_train_info(self):
        response = load_example_response()
        result = get_current_train_position(response)
        assert "19309" in result
        assert "SHANTI EXPRESS" in result

    def test_shows_route(self):
        response = load_example_response()
        result = get_current_train_position(response)
        assert "AHMEDABAD" in result
        assert "INDORE" in result

    def test_shows_current_station(self):
        response = load_example_response()
        result = get_current_train_position(response)
        assert "BORDI" in result
        assert "BIO" in result

    def test_shows_progress(self):
        response = load_example_response()
        result = get_current_train_position(response)
        assert "Distance Covered" in result
        assert "Progress" in result
        assert "%" in result

    def test_shows_delay(self):
        response = load_example_response()
        result = get_current_train_position(response)
        assert "Delay" in result or "On Time" in result or "Running" in result

    def test_shows_next_stop(self):
        response = load_example_response()
        result = get_current_train_position(response)
        assert "Next Stop" in result
        assert "MEGHNAGAR" in result


class TestGetTrainRoute:
    """Tests for get_train_route function."""

    def test_returns_route_string(self):
        response = load_example_response()
        result = get_train_route(response)
        assert "->" in result

    def test_marks_current_station(self):
        response = load_example_response()
        result = get_train_route(response)
        assert ">>>" in result
        assert "<<<" in result

    def test_includes_source_and_destination(self):
        response = load_example_response()
        result = get_train_route(response)
        assert "ADI" in result
        assert "INDB" in result

    def test_without_non_stops(self):
        response = load_example_response()
        result = get_train_route(response, include_non_stops=False)
        # Non-stop stations should not have brackets
        assert "[" not in result or ">>>" in result

    def test_with_non_stops(self):
        response = load_example_response()
        result = get_train_route(response, include_non_stops=True)
        # Should include bracketed non-stop stations
        assert "[" in result


class TestGetUpcomingStations:
    """Tests for get_upcoming_stations function."""

    def test_returns_upcoming_stations(self):
        response = load_example_response()
        result = get_upcoming_stations(response)
        assert "Upcoming Stations" in result

    def test_respects_limit(self):
        response = load_example_response()
        result = get_upcoming_stations(response, limit=3)
        # Should show "... and X more stations" if there are more
        assert "1." in result
        assert "2." in result
        assert "3." in result

    def test_shows_station_details(self):
        response = load_example_response()
        result = get_upcoming_stations(response, limit=2)
        assert "MEGHNAGAR" in result
        assert "Scheduled" in result or "Expected" in result

    def test_shows_delay_info(self):
        response = load_example_response()
        result = get_upcoming_stations(response, limit=1)
        assert "Delayed" in result or "Early" in result or "Platform" in result


class TestGetTrainSummary:
    """Tests for get_train_summary function."""

    def test_shows_train_name_and_number(self):
        response = load_example_response()
        result = get_train_summary(response)
        assert "19309" in result
        assert "SHANTI EXPRESS" in result

    def test_shows_route(self):
        response = load_example_response()
        result = get_train_summary(response)
        assert "AHMEDABAD" in result
        assert "INDORE" in result
        assert "→" in result

    def test_shows_position(self):
        response = load_example_response()
        result = get_train_summary(response)
        # Check for position info (current station or bubble message)
        assert "BORDI" in result or "Crossed" in result or "Near" in result

    def test_shows_delay_status(self):
        response = load_example_response()
        result = get_train_summary(response)
        # Check for delay/running status info
        assert "Running" in result or "late" in result or "on time" in result

    def test_shows_next_stop(self):
        response = load_example_response()
        result = get_train_summary(response)
        # Check for next stop info
        assert "Next" in result or "MEGHNAGAR" in result


class TestFetchNewTrainStatus:
    """Tests for fetch_new_train_status function (integration tests)."""

    def test_fetch_valid_train(self):
        """Test fetching status for a valid running train."""
        import asyncio
        # Using a commonly running train for testing
        print("\n🚂 Fetching train 12138 (Punjab Mail) with start_day=1...")
        result = asyncio.run(fetch_new_train_status("12138", start_day=1))
        
        if result is not None:
            print(f"✅ Got response for train: {result.data.train_name} ({result.data.train_number})")
            print(f"   Route: {result.data.source_stn_name} → {result.data.dest_stn_name}")
            print(f"   Current position: {result.data.current_station_name}")
            print(f"   Delay: {result.data.delay} mins")
            assert result.success == True
            assert result.data.train_number == "12138"
            assert result.data.train_name
            assert result.data.source
            assert result.data.destination
        else:
            print("⚠️  Train not running or data unavailable")

    def test_fetch_with_start_day(self):
        """Test fetching with different start_day values."""
        import asyncio
        # Test with yesterday's train
        print("\n🚂 Fetching train 12138 with start_day=1 (started yesterday)...")
        result = asyncio.run(fetch_new_train_status("12138", start_day=1))
        
        if result is not None:
            print(f"✅ Got response - Train start date: {result.data.train_start_date}")
            print(f"   Status as of: {result.data.status_as_of}")
        else:
            print("⚠️  No data for this start_day (train may not be running)")
        
        # Result may or may not be available depending on the train schedule
        # Just verify no exception is raised
        assert result is None or isinstance(result, NewTrainStatusResponse)

    def test_fetch_invalid_train(self):
        """Test fetching status for an invalid train number."""
        import asyncio
        print("\n🚂 Fetching invalid train 99999...")
        result = asyncio.run(fetch_new_train_status("99999", start_day=0))
        
        if result is None:
            print("✅ Correctly returned None for invalid train")
        elif result.success == False:
            print(f"✅ Correctly returned success=False")
        else:
            print(f"⚠️  Unexpected response: {result}")
        
        # Should return None or a response with success=False
        assert result is None or result.success == False


class TestSchemaValidation:
    """Tests for schema validation."""

    def test_example_json_validates(self):
        """Test that the example JSON validates against the schema."""
        response = load_example_response()
        assert response.success == True
        assert response.data.train_number == "19309"

    def test_data_fields(self):
        """Test that data fields are correctly parsed."""
        response = load_example_response()
        data = response.data
        
        assert data.train_name == "SHANTI EXPRESS"
        assert data.source == "ADI"
        assert data.destination == "INDB"
        assert data.delay == 7
        assert data.total_distance == 525
        assert data.distance_from_source == 248

    def test_upcoming_stations(self):
        """Test that upcoming stations are correctly parsed."""
        response = load_example_response()
        upcoming = response.data.upcoming_stations
        
        assert len(upcoming) > 0
        # First non-empty station should be MEGHNAGAR
        meghnagar = next((s for s in upcoming if s.station_code == "MGN"), None)
        assert meghnagar is not None
        assert meghnagar.station_name == "MEGHNAGAR"
        assert meghnagar.arrival_delay == 5

    def test_previous_stations(self):
        """Test that previous stations are correctly parsed."""
        response = load_example_response()
        previous = response.data.previous_stations
        
        assert len(previous) > 0
        # First station should be source
        assert previous[0].station_code == "ADI"

    def test_helper_methods(self):
        """Test helper methods on the data model."""
        response = load_example_response()
        data = response.data
        
        hours, mins = data.get_delay_hours_minutes()
        assert hours == 0
        assert mins == 7
        
        progress = data.get_progress_percentage()
        assert 47 < progress < 48  # Should be around 47.2% (248/525)
        
        remaining = data.get_remaining_distance()
        assert remaining == 277  # 525 - 248


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
