<p align="center">
  <a href="https://pypi.org/project/async-httpd-data-collector/">
    <img src="https://badge.fury.io/py/async-httpd-data-collector.svg" alt="PyPI version">
  </a>
  <a href="https://pepy.tech/project/async-httpd-data-collector">
    <img src="https://static.pepy.tech/badge/async-httpd-data-collector" alt="Total Downloads">
  </a>
  <a href="https://pypi.org/project/async-httpd-data-collector/">
    <img src="https://img.shields.io/pypi/dm/async-httpd-data-collector" alt="PyPI Downloads per Month">
  </a>
  <a href="https://www.gnu.org/licenses/gpl-3.0">
    <img src="https://img.shields.io/badge/License-GPLv3-blue.svg" alt="License: GPL v3">
  </a>
  <a href="https://github.com/straightchlorine/async-httpd-data-collector/actions/workflows/test.yml">
    <img src="https://github.com/straightchlorine/async-httpd-data-collector/actions/workflows/test.yml/badge.svg" alt="CI">
  </a>
</p>

# async-httpd-data-collector

!!! note
    This is an older university project and is not actively maintained.
    It works as-is, but is not extensively tested.

A Python library that acts as an asynchronous gateway between IoT sensor
devices and InfluxDB. It fetches JSON readings from a device (like a
NodeMCU/ESP8266) over HTTP, parses them, and stores them as time-series data.
You can then query the data back as pandas DataFrames.

Started as a university project to get hands-on with async Python,
`asyncio`, `aiohttp`, and time-series databases.

## What it does

- Fetches sensor data from a device over HTTP (expects a specific JSON format)
- Parses and stores readings in InfluxDB as time-series points
- Runs a background daemon process for continuous data collection
- Queries data back as pandas DataFrames with timezone-adjusted timestamps

## The hardware side

The device that produces the data is a NodeMCU (ESP8266) board running
custom firmware:
[arduino-air-state-server](https://github.com/straightchlorine/arduino-air-state-server).
It has several environmental sensors attached:

| Sensor  | Measures                                        |
|---------|-------------------------------------------------|
| MQ135   | CO, CO2, alcohol, NH4, acetone, toluene (ppm)   |
| BMP180  | temperature, pressure, altitude                 |
| DHT22   | temperature, humidity                            |
| DS18B20 | temperature (up to 8 sensors on one wire)        |

The board connects to WiFi and exposes a `/circumstances` HTTP endpoint
returning all sensor readings as JSON.

## Quick links

- [Getting Started](getting-started.md) - installation and first steps
- [Architecture](architecture.md) - how the pieces fit together
- [API Reference](api.md) - classes and methods
- [Data Analysis](analysis/index.md) - plots and analysis from collected data

## Project links

- [PyPI](https://pypi.org/project/async-httpd-data-collector/)
- [GitHub](https://github.com/straightchlorine/async-httpd-data-collector)
- [arduino-air-state-server](https://github.com/straightchlorine/arduino-air-state-server) (firmware)
- [air-quality-data-analysis](https://github.com/straightchlorine/air-quality-data-analysis) (notebooks)
