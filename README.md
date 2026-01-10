# Indian Railway Live Info MCP Server

A **read-only** Model Context Protocol (MCP) server that provides real-time Indian Railways information including PNR status, live train tracking, and station/train search capabilities.

> ⚠️ **Read-Only Server**: This MCP server only retrieves information. It does not perform any write operations, bookings, or modifications to any railway systems.

---

## Features

- 🎫 **PNR Status Tracking** - Check ticket confirmation status, coach/berth details, waitlist positions, and complete journey information
- 🚂 **Live Train Status** - Real-time train location, delays, expected arrivals/departures, and route information
- 🔍 **Station & Train Search** - Look up station codes and train numbers by name
- 📅 **Date & Time Utilities** - Get current IST time and calculate date differences
- 🔗 **PNR + Train Integration** - Automatically track trains using PNR with correct journey dates

---

## Connect Your AI App

### MCP Server URL
```
https://indian-railways-live-status.fastmcp.app/mcp
```

---

### 1. Qordinate

1. **Sign up / Login** to [app.qordinate.ai](https://app.qordinate.ai)
2. Go to **Apps** in the side panel
3. Scroll down and click **"Connect any App using MCP"** button
4. In the modal:
   - **Name**: Enter any name (e.g., "Indian Railways")
   - **MCP Server URL**: `https://indian-railways-live-status.fastmcp.app/mcp`
   - **API Key**: Leave empty
5. Now you can start using it in **Chat** or via **WhatsApp**!

![Qordinate Setup Step 1](screenshots/qordinate-1.png)


---

### 2. ChatGPT

1. Go to **Settings**
2. Navigate to **Apps** section → **Advanced Settings** → **Create App**
3. Paste the MCP Server URL: `https://indian-railways-live-status.fastmcp.app/mcp`
4. To use: Enable **Dev Mode** in chat, click the **"+"** button, and select the tool

![ChatGPT Setup Step 1](screenshots/chatgpt-1.png)


---

## Available Tools

### Utility Tools

| Tool | Description |
|------|-------------|
| `get_current_date_time` | Get current date and time in Indian Standard Time (IST) |
| `get_date_difference` | Calculate absolute difference in days between two dates (format: dd-mm-yyyy) |

---

̌̌̌̌̌̌### PNR Status Tools

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

## Example Usage

```
User: Check PNR status for 8341223680
Assistant: [Uses get_complete_pnr_summary tool]

User: Where is train 12618 right now?
Assistant: [Uses get_live_train_status tool]

User: When will Punjab Mail arrive at Mathura?
Assistant: [Uses search_train_numbers then get_train_arrival_at_station]

User: What's the station code for Howrah?
Assistant: [Uses search_station_codes tool]

User: Track my train using PNR 2341567890
Assistant: [Uses get_full_journey_status tool - automatically handles dates]
```

---

## Understanding `start_day` Parameter

The `start_day` parameter is crucial for tracking trains correctly:

- `0` = Train started **today**
- `1` = Train started **yesterday**
- `2` = Train started **2 days ago**

**Why is this needed?**  
Long-distance trains can run for 2-3 days. If you're tracking a train that left yesterday, you need `start_day=1`.

**Pro Tip:** Use the PNR-based tools (`get_train_status_using_pnr`, `get_full_journey_status`) which **automatically calculate** the correct `start_day` from your ticket's journey date.

---

## Disclaimer

> **Important Notice**: The information provided by this MCP server is sourced from third-party APIs and is **not guaranteed to be 100% accurate**. This project is **not endorsed by, affiliated with, or officially connected to IRCTC, Indian Railways, or any of their subsidiaries or affiliates**.
>
> Always verify critical travel information through official IRCTC channels.

---

## License

MIT License

---

© Mohammad Maasir 2025 - 2026. All rights reserved.
