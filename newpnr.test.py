from new_pnr_status import fetch_pnr_status
from new_pnr_schema import PNRResponse


def test_fetch_pnr_status():
    """Test fetching PNR status from the API."""
    pnr_no = "8341223680"
    
    result = fetch_pnr_status(pnr_no)
    
    # Verify return type
    assert isinstance(result, PNRResponse)
    
    # Verify response structure
    assert result.status is True
    assert result.message == "Success"
    assert result.data is not None
    
    # Verify PNR data
    assert result.data.Pnr == pnr_no
    assert result.data.TrainNo is not None
    assert result.data.TrainName is not None
    assert result.data.PassengerCount >= 1
    assert len(result.data.PassengerStatus) == result.data.PassengerCount
    
    print(f"PNR: {result.data.Pnr}")
    print(f"Train: {result.data.TrainNo} - {result.data.TrainName}")
    print(f"From: {result.data.From} -> To: {result.data.To}")
    print(f"Date of Journey: {result.data.Doj}")
    print(f"Passengers: {result.data.PassengerCount}")
    for passenger in result.data.PassengerStatus:
        print(f"  Passenger {passenger.Number}: {passenger.CurrentStatus}")


def test_invalid_length_pnr():
    """Test that PNR with invalid length returns None without API call."""
    # Too short
    assert fetch_pnr_status("123456789") is None
    print("✓ 9 digit PNR returns None")
    
    # Too long
    assert fetch_pnr_status("12345678901") is None
    print("✓ 11 digit PNR returns None")
    
    # Empty
    assert fetch_pnr_status("") is None
    print("✓ Empty PNR returns None")
    
    # Non-numeric
    assert fetch_pnr_status("abcdefghij") is None
    print("✓ Non-numeric PNR returns None")
    
    # Mixed
    assert fetch_pnr_status("12345abcde") is None
    print("✓ Mixed alphanumeric PNR returns None")


def test_invalid_pnr_value():
    """Test that valid format but non-existent PNR returns None."""
    result = fetch_pnr_status("0000000000")
    assert result is None
    print("✓ Invalid PNR (0000000000) returns None")


if __name__ == "__main__":
    print("Test 1: Valid PNR")
    test_fetch_pnr_status()
    print("\n✅ Valid PNR test passed!\n")
    
    print("Test 2: Invalid length PNR")
    test_invalid_length_pnr()
    print("\n✅ Invalid length PNR test passed!\n")
    
    print("Test 3: Invalid PNR value")
    test_invalid_pnr_value()
    print("\n✅ Invalid PNR value test passed!\n")
    
    print("🎉 All tests passed!")
