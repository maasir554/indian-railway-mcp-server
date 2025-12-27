# Indian Railway Live Info MCP Server

A Model Context Protocol (MCP) server that provides real-time Indian Railways information including PNR status, live train tracking, and station/train search capabilities.

## Features

- **PNR Status Tracking** - Check ticket confirmation status, coach/berth details, and waitlist positions
- **Live Train Status** - Get real-time train location and running status
- **Station & Train Search** - Look up station codes and train numbers by name

## Installation

```bash
# Clone the repository
git clone https://github.com/maasir554/irctc-mcp.git
cd irctc-mcp

# Install dependencies
pip install -r requirements.txt
# or using uv
uv sync
```

## Usage

Run the MCP server:

```bash
python main_mcp.py
```

Or configure it in your MCP client settings.

## Available Tools

### PNR Tools

| Tool | Description |
|------|-------------|
| `get_confirm_status` | Get ticket confirmation status of all passengers for a PNR number |
| `get_coaches_and_berths` | Get coach IDs and seat/berth details for all passengers |
| `get_waitlist_position` | Get updated waitlist position for passengers |
| `get_train_no_from_pnr_no` | Get train number and name from a PNR number |

### Train Status Tools

| Tool | Description |
|------|-------------|
| `get_live_train_status` | Get current live status and position of a train |
| `get_train_arrival_at_station` | Get expected arrival time of a train at a specific station |
| `search_station_codes` | Search for station codes by station name |
| `search_train_numbers` | Search for train numbers by train name |

## Tool Parameters

### PNR Tools
All PNR tools accept a single parameter:
- `pnr_no` (string): 10-digit PNR code (e.g., "8341223680")

### Train Status Tools
- `get_live_train_status`: `train_number` (e.g., "12618")
- `get_train_arrival_at_station`: `train_number` + `station_code` (e.g., "HWH", "NDLS")
- `search_station_codes`: `station_name` (e.g., "Howrah", "New Delhi")
- `search_train_numbers`: `train_name` (e.g., "Rajdhani", "Shatabdi")

## Example Usage

```
User: Check PNR status for 8341223680
Assistant: [Uses get_confirm_status tool]

User: Where is train 12618 right now?
Assistant: [Uses get_live_train_status tool]

User: What's the station code for Howrah?
Assistant: [Uses search_station_codes tool]
```

---

## Disclaimer

**Important Notice**: The information provided by this MCP server is sourced from third-party APIs and is **not guaranteed to be 100% accurate**. This project is **not endorsed by, affiliated with, or officially connected to IRCTC, Indian Railways, or any of their subsidiaries or affiliates**. Always verify critical travel information through official IRCTC channels.

---

## License

MIT License

---
© Mohammad Maasir 2025 - 2026. All rights reserved.
