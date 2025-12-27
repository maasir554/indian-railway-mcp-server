import asyncio
import os
from dotenv import load_dotenv
from train_status_functions import (
    fetch_train_status,
    get_station_codes_from_name,
    get_train_numbers_from_name,
    get_expected_arrival_at_station,
    get_current_train_position,
)

load_dotenv()

async def test_api():
    # Debug: print the base URL
    base_url = os.getenv("TRAIN_STATUS_API_BASE", "").rstrip("/")
    print(f"API Base URL: '{base_url}'")
    print()
    
    print("=" * 50)
    print("Testing Station Search API")
    print("=" * 50)
    stations = await get_station_codes_from_name("Howrah")
    if stations:
        for s in stations:
            print(f"  {s.name} - Code: {s.code}")
    else:
        print("  No stations found")

    print("\n" + "=" * 50)
    print("Testing Train Search API")
    print("=" * 50)
    trains = await get_train_numbers_from_name("Punjab")
    if trains:
        for t in trains:
            print(f"  {t.number} - {t.name} ({t.from_stn_code} → {t.to_stn_code})")
    else:
        print("  No trains found")

    print("\n" + "=" * 50)
    print("Testing Train Live Status API")
    print("=" * 50)
    status = await fetch_train_status("12618")
    if status:
        print(get_current_train_position(status))
        print("\n" + "-" * 40)
        # Use a station on this train's route (Ernakulam Junction - destination)
        print(get_expected_arrival_at_station(status, "ERS"))
    else:
        print("  Could not fetch train status")


if __name__ == "__main__":
    asyncio.run(test_api())
