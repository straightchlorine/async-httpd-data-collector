# Architecture

## Overview

The library sits between a sensor device and InfluxDB, handling the
fetch-parse-store cycle asynchronously. Here's the data flow:

```
NodeMCU device          async-httpd-data-collector            InfluxDB
  (sensors)                                                  (storage)
     |                                                          |
     |--- HTTP GET /circumstances -->  AsyncFetcher             |
     |                                     |                    |
     |                              JSONInfluxParser            |
     |                                     |                    |
     |                              AsyncCollector  -------->   |
     |                                                          |
     |                              AsyncQuery     <--------    |
     |                                     |                    |
     |                               DataParser                 |
     |                                     |                    |
     |                              pandas DataFrame            |
```

## Components

### DatabaseInterface

The main entry point. Coordinates everything and provides the user-facing
API. Internally it creates and manages a `DataDaemon` and an `AsyncQuery`.

[Source](https://github.com/straightchlorine/async-httpd-data-collector/blob/master/ahttpdc/read/database_interface.py#L17)

### DataDaemon

Runs the fetch-store cycle in a separate `multiprocessing.Process`.
Uses `asyncio.run()` to manage an async event loop in that process.
The loop calls `AsyncFetcher` then `AsyncCollector` on each tick,
with a configurable interval between cycles.

[Source](https://github.com/straightchlorine/async-httpd-data-collector/blob/master/ahttpdc/read/daemon.py#L15)

### AsyncFetcher

Makes async HTTP GET requests to the device using `aiohttp`.
Returns the raw JSON response as a Python dict.

[Source](https://github.com/straightchlorine/async-httpd-data-collector/blob/master/ahttpdc/read/fetch/fetcher.py#L12)

### JSONInfluxParser

Takes the raw JSON from the device and converts it into an InfluxDB
record (measurement name, tags, timestamp, fields). Handles the case
where multiple sensors measure the same parameter by averaging.

[Source](https://github.com/straightchlorine/async-httpd-data-collector/blob/master/ahttpdc/read/store/parse/parser.py#L9)

### AsyncCollector

Writes parsed records to InfluxDB as time-series Points using the
`influxdb-client` async API.

[Source](https://github.com/straightchlorine/async-httpd-data-collector/blob/master/ahttpdc/read/store/collector.py#L12)

### AsyncQuery

Queries InfluxDB using Flux and returns results via `DataParser`.
Supports both async and sync InfluxDB clients. The sync client is
used for large historical queries (to avoid session timeout issues
with the async client).

[Source](https://github.com/straightchlorine/async-httpd-data-collector/blob/master/ahttpdc/read/query/interface.py#L21)

### DataParser

Converts InfluxDB query results (FluxTable records) into pandas
DataFrames. Handles UTC-to-local timezone conversion.

[Source](https://github.com/straightchlorine/async-httpd-data-collector/blob/master/ahttpdc/read/query/parse/data.py#L12)

## Package structure

```
ahttpdc/
  __init__.py              # version
  read/
    __init__.py
    database_interface.py  # DatabaseInterface (main entry point)
    daemon.py              # DataDaemon (background process)
    fetch/
      __init__.py
      fetcher.py           # AsyncFetcher (HTTP client)
    store/
      __init__.py
      collector.py         # AsyncCollector (InfluxDB writer)
      parse/
        __init__.py
        parser.py          # JSONInfluxParser (JSON -> InfluxDB record)
    query/
      __init__.py
      interface.py         # AsyncQuery (InfluxDB reader)
      parse/
        data.py            # DataParser (FluxTable -> DataFrame)
```

## The hardware

The device firmware is a separate project:
[arduino-air-state-server](https://github.com/straightchlorine/arduino-air-state-server).

It runs on a NodeMCU v2 (ESP8266) with these sensors:

- **MQ135** - gas sensor (CO, CO2, alcohol, NH4, acetone, toluene)
- **BMP180** - barometric pressure and temperature
- **DHT22** - humidity and temperature
- **DS18B20** - temperature (supports up to 8 on one wire)
- **SSD1306** - OLED display for local readout

The firmware creates an async web server (ESPAsyncWebServer) that responds
to `GET /circumstances` with the JSON structure described in
[Getting Started](getting-started.md#prerequisites).

## Dependencies

Core runtime dependencies:

- `influxdb-client[async]` - InfluxDB client with async support
- `aiohttp` - async HTTP client for fetching device data
- `pandas` + `numpy` - data manipulation and DataFrame support
- `reactivex` - required by influxdb-client
- `python-dateutil` + `pytz` - timezone handling
- `aiocsv` - async CSV support
