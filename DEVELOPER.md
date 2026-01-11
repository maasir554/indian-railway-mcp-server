# Developer Documentation

Technical reference for the Indian Railway Live Info MCP Server.

---

## Available Tools

### Utility Tools

| Tool | Description |
|------|-------------|
| `get_current_date_time` | Get current date and time in Indian Standard Time (IST) |
| `get_date_difference` | Calculate absolute difference in days between two dates (format: dd-mm-yyyy) |

---

### PNR Status Tools

All PNR tools accept a `pnr_no` parameter (10-digit PNR code, e.g., `"8341223680"`).

| Tool | Description |
|------|-------------|
| `get_confirm_status` | Get ticket confirmation status of all passengers |
| `get_coaches_and_berths` | Get coach IDs and seat/berth details for all passengers |
| `get_pnr_waitlist_position` | Get updated waitlist position for passengers |
| `get_train_no_from_pnr_no` | Get train number and name from PNR |
| `get_pnr_journey_overview` | Get journey info: stations, fare, date/time, class, passengers |
| `get_pnr_passenger_summary` | Get summary of all passengers with status, coach, and berth |
| `get_complete_pnr_summary` | Get comprehensive PNR summary with all details |

---

### Train Status Tools

| Tool | Parameters | Description |
|------|------------|-------------|
| `get_live_train_status` | `train_number`, `start_day` | Get current live position and status of a train |
| `get_train_status_using_pnr` | `pnr_no` | Get live train status using PNR (auto-calculates correct date) |
| `get_train_arrival_at_station` | `train_number`, `station_code`, `start_day` | Get expected arrival time at a station |
| `get_train_departure_at_station` | `train_number`, `station_code`, `start_day` | Get expected departure time from a station |
| `get_train_arrival_using_pnr` | `pnr_no`, `station_code` | Get arrival time at station using PNR |
| `get_train_complete_route` | `train_number`, `start_day`, `include_non_stops` | Get complete route with all stations |
| `get_next_stations` | `train_number`, `start_day`, `limit` | Get upcoming stations with arrival times and delays |
| `get_last_halt_station` | `train_number`, `start_day` | Get last station where train stopped |
| `get_brief_train_summary` | `train_number`, `start_day` | Get brief summary of train's current status |

#### Parameter Reference

| Parameter | Type | Description |
|-----------|------|-------------|
| `train_number` | string | Train number (e.g., `"12618"`, `"12138"`) |
| `station_code` | string | Station code (e.g., `"HWH"`, `"NDLS"`, `"CSMT"`) |
| `start_day` | integer | Days ago train started from source: `0` = today, `1` = yesterday, `2` = day before, etc. |
| `include_non_stops` | boolean | Whether to include non-halt stations in route (default: `false`) |
| `limit` | integer | Maximum stations to show (default: `5`) |

---

### Search Tools

| Tool | Parameters | Description |
|------|------------|-------------|
| `search_station_codes` | `station_name` | Search station codes by name (e.g., "Howrah", "New Delhi") |
| `search_train_numbers` | `train_name` | Search train numbers by name (e.g., "Rajdhani", "Punjab Mail") |

---

### Combined PNR + Train Status Tools

| Tool | Parameters | Description |
|------|------------|-------------|
| `get_full_journey_status` | `pnr_no` | Complete journey status: PNR details + live train position + upcoming stations |

---

## Understanding `start_day` Parameter

The `start_day` parameter is crucial for tracking trains correctly:

- `0` = Train started **today**
- `1` = Train started **yesterday**
- `2` = Train started **2 days ago**

**Why is this needed?**  
Long-distance trains can run for 2-3 days. If you're tracking a train that left yesterday, you need `start_day=1`.

**Pro Tip:** Use the PNR-based tools (`get_train_status_using_pnr`, `get_full_journey_status`) which **automatically calculate** the correct `start_day` from your ticket's journey date.
