# Getting Started

## Installation

```bash
pip install async-httpd-data-collector
```

## Prerequisites

You need:

- A device serving sensor data as JSON over HTTP (see
  [arduino-air-state-server](https://github.com/straightchlorine/arduino-air-state-server)
  for the reference implementation)
- An InfluxDB 2.x instance running somewhere accessible

The device must return JSON in this structure at its HTTP endpoint:

```json
{
  "nodemcu": {
    "mq135": {
      "co": "2.56",
      "co2": "402.08",
      "alcohol": "0.94",
      "nh4": "3.30",
      "aceton": "0.32",
      "toulen": "0.38"
    },
    "bmp180": {
      "temperature": "28.60",
      "pressure": "1006.13",
      "seaLevelPressure": "1024.18",
      "altitude": "149.75"
    },
    "ds18b20": {
      "temperature": "27.00"
    },
    "dht22": {
      "temperature": "27.90",
      "humidity": "47.30"
    }
  }
}
```

The top-level key (`"nodemcu"`) is the device name - it can be anything.
Each nested object is a sensor, and the values are string-encoded floats.

## Basic Usage

### 1. Define your sensors

Tell the library which sensors and parameters you care about:

```python
sensors = {
    'bmp180': ['altitude', 'pressure', 'seaLevelPressure', 'temperature'],
    'mq135': ['aceton', 'alcohol', 'co', 'co2', 'nh4', 'toulen'],
    'ds18b20': ['temperature'],
    'dht22': ['humidity', 'temperature'],
}
```

!!! note
    If the same parameter appears in multiple sensors (like `temperature`
    from both BMP180 and DS18B20), the library averages the readings.
    Keep this in mind if you want readings from a specific sensor -
    include that parameter only for that sensor.

### 2. Create the interface

```python
from ahttpdc.read.database_interface import DatabaseInterface

interface = DatabaseInterface(
    sensors,
    db_host='localhost',
    db_port=8086,
    db_token='your-influxdb-token',
    db_org='your-org',
    db_bucket='your-bucket',
    srv_ip='192.168.1.100',
    srv_port=80,
    handle='circumstances',
)
```

### 3. Collect data

Start the background daemon to continuously fetch and store readings:

```python
interface.daemon.enable()
```

The daemon runs in a separate process and fetches data at a configurable
interval (default: 1 second). Stop it with:

```python
interface.daemon.disable()
```

### 4. Query data

```python
# latest reading
df = interface.query_latest()

# last 30 days
df = interface.query_historical('-30d')

# specific time range
df = interface.query_historical(
    '2024-05-16T00:00:00Z',
    '2024-05-21T00:00:00Z'
)

# custom Flux query
df = interface.query_custom_sync(
    'from(bucket:"my-bucket") |> range(start: -1d) |> last()'
)
```

All query methods return a `pandas.DataFrame` with timestamps converted
to your local timezone.

### 5. Export to CSV

```python
df = interface.query_historical('-1d')
df.to_csv('sensor-data.csv')
```

## Loading secrets

The examples in this project load InfluxDB credentials from a JSON file:

```python
import json

with open('secrets/secrets.json', 'r') as f:
    secrets = json.load(f)
```

The expected format:

```json
{
  "host": "localhost",
  "port": 8086,
  "token": "your-influxdb-token",
  "organization": "your-org",
  "bucket": "your-bucket",
  "srv_ip": "192.168.1.100",
  "srv_port": 80,
  "handle": "circumstances"
}
```

You can also use environment variables or any other method you prefer -
`DatabaseInterface` just takes strings.
