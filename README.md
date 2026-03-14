<div align="center">

[![PyPI version](https://badge.fury.io/py/async-httpd-data-collector.svg)](https://pypi.org/project/async-httpd-data-collector/)
[![Total Downloads](https://static.pepy.tech/badge/async-httpd-data-collector)](https://pepy.tech/project/async-httpd-data-collector)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/async-httpd-data-collector)](https://pypi.org/project/async-httpd-data-collector/)
</div>

# async-httpd-data-collector

> **Note:** This is an older university project and is not actively maintained.
> It works as-is, but is not extensively tested.

A Python library that acts as an asynchronous gateway between IoT sensor
devices and InfluxDB. It fetches JSON readings from a device (like a
NodeMCU/ESP8266) over HTTP, parses them, and stores them as time-series data.
You can then query the data back as pandas DataFrames.

Started as a university project to get hands-on with async Python,
`asyncio`, `aiohttp`, and time-series databases. The hardware side runs on
an [arduino-air-state-server](https://github.com/straightchlorine/arduino-air-state-server) -
a NodeMCU board with air quality sensors (MQ135, BMP180, DHT22, DS18B20)
that exposes readings at an HTTP endpoint.

## Installation

```bash
pip install async-httpd-data-collector
```

## Quick Start

```python
from ahttpdc.read.database_interface import DatabaseInterface

# define which sensors and parameters to track
sensors = {
    'bmp180': ['altitude', 'pressure', 'seaLevelPressure', 'temperature'],
    'mq135': ['aceton', 'alcohol', 'co', 'co2', 'nh4', 'toulen'],
    'ds18b20': ['temperature'],
    'dht22': ['humidity', 'temperature'],
}

# connect to InfluxDB and the device
interface = DatabaseInterface(
    sensors,
    db_host='localhost',
    db_port=8086,
    db_token='your-influxdb-token',
    db_org='your-org',
    db_bucket='your-bucket',
    srv_ip='192.168.1.100',  # device IP
    srv_port=80,
    handle='circumstances',  # HTTP endpoint on the device
)

# start the background daemon - fetches and stores data continuously
interface.daemon.enable()

# query the last 30 days of data as a DataFrame
df = interface.query_historical('-30d')
print(df.head())

# stop the daemon when done
interface.daemon.disable()
```

## How It Works

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

The `DatabaseInterface` is the main entry point. It manages two things:

- **DataDaemon** - a background process (via `multiprocessing`) that
  periodically fetches sensor data from the device and stores it in InfluxDB.
- **AsyncQuery** - queries InfluxDB and returns results as pandas DataFrames
  with local timezone-adjusted timestamps.

### Querying

```python
# latest reading
df = interface.query_latest()

# last 3 hours
df = interface.query_historical('-3h')

# specific time range
df = interface.query_historical('2024-05-16T00:00:00Z', '2024-05-21T00:00:00Z')

# custom Flux query
df = interface.query_custom_sync('from(bucket:"my-bucket") |> range(start: -1d) |> last()')
```

## Related Projects

- [arduino-air-state-server](https://github.com/straightchlorine/arduino-air-state-server) -
  the NodeMCU firmware that collects sensor readings and serves them over HTTP
- [air-quality-data-analysis](https://github.com/straightchlorine/air-quality-data-analysis) -
  Jupyter notebooks with data analysis (heatmaps, correlations, anomaly detection)
  and SARIMAX time-series forecasting on the collected data
