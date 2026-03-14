# API Reference

## DatabaseInterface

[Source](https://github.com/straightchlorine/async-httpd-data-collector/blob/master/ahttpdc/read/database_interface.py#L17)

The main entry point for the library. Manages the background data daemon
and provides query methods.

### Constructor

```python
DatabaseInterface(
    sensors: dict[str, list[str]],
    db_host: str,
    db_port: str,
    db_token: str,
    db_org: str,
    db_bucket: str,
    srv_ip: str,
    srv_port: int | str = 80,
    handle: str = '',
    interval: int = 1,
)
```

| Parameter  | Type                   | Description                                    |
|------------|------------------------|------------------------------------------------|
| sensors    | dict[str, list[str]]   | Sensors and their parameters to track          |
| db_host    | str                    | InfluxDB host address                          |
| db_port    | str                    | InfluxDB port                                  |
| db_token   | str                    | InfluxDB authentication token                  |
| db_org     | str                    | InfluxDB organization                          |
| db_bucket  | str                    | InfluxDB bucket name                           |
| srv_ip     | str                    | Device IP address                              |
| srv_port   | int or str             | Device HTTP port (default: 80)                 |
| handle     | str                    | HTTP endpoint path on device (default: '')     |
| interval   | int                    | Seconds between fetch cycles (default: 1)      |

### Properties

#### `daemon`

Returns the `DataDaemon` instance. Use it to start/stop data collection:

```python
interface.daemon.enable()   # start fetching
interface.daemon.disable()  # stop fetching
```

### Methods

#### `query_latest() -> pd.DataFrame`

[Source](https://github.com/straightchlorine/async-httpd-data-collector/blob/master/ahttpdc/read/database_interface.py#L94)

Query the most recent measurement from InfluxDB (last hour).

```python
df = interface.query_latest()
```

#### `query_historical(start_relative, end='') -> pd.DataFrame`

[Source](https://github.com/straightchlorine/async-httpd-data-collector/blob/master/ahttpdc/read/database_interface.py#L104)

Query data from a time range. Accepts relative times or absolute timestamps.

```python
# relative - last 30 days
df = interface.query_historical('-30d')

# absolute range
df = interface.query_historical(
    '2024-05-16T00:00:00Z',
    '2024-05-21T00:00:00Z'
)
```

#### `query_custom_async(query) -> pd.DataFrame`

[Source](https://github.com/straightchlorine/async-httpd-data-collector/blob/master/ahttpdc/read/database_interface.py#L130)

Execute a custom Flux query using the async InfluxDB client.
Best for small result sets - large queries may cause session issues.

```python
df = interface.query_custom_async(
    'from(bucket:"my-bucket") |> range(start: -1h) |> last()'
)
```

#### `query_custom_sync(query) -> pd.DataFrame`

[Source](https://github.com/straightchlorine/async-httpd-data-collector/blob/master/ahttpdc/read/database_interface.py#L146)

Execute a custom Flux query using the synchronous InfluxDB client.
Use this for large queries.

```python
df = interface.query_custom_sync(
    'from(bucket:"my-bucket") |> range(start: -30d)'
)
```

---

## DataDaemon

[Source](https://github.com/straightchlorine/async-httpd-data-collector/blob/master/ahttpdc/read/daemon.py#L15)

Background process that continuously fetches data from the device and
stores it in InfluxDB. Runs in a separate `multiprocessing.Process`.

You don't create this directly - access it through `DatabaseInterface.daemon`.

### Methods

#### `enable()`

[Source](https://github.com/straightchlorine/async-httpd-data-collector/blob/master/ahttpdc/read/daemon.py#L89)

Start the daemon process. Begins the fetch-store loop.

#### `disable()`

[Source](https://github.com/straightchlorine/async-httpd-data-collector/blob/master/ahttpdc/read/daemon.py#L100)

Stop the daemon process. Terminates and joins the background process.

---

## AsyncFetcher

[Source](https://github.com/straightchlorine/async-httpd-data-collector/blob/master/ahttpdc/read/fetch/fetcher.py#L12)

Async HTTP client that fetches JSON readings from the device.

### Constructor

```python
AsyncFetcher(url: str)
```

### Methods

#### `async request_readings() -> dict`

[Source](https://github.com/straightchlorine/async-httpd-data-collector/blob/master/ahttpdc/read/fetch/fetcher.py#L50)

Send a GET request to the device and return the JSON response as a dict.
Returns `None` if the request fails (non-200 status).

---

## AsyncQuery

[Source](https://github.com/straightchlorine/async-httpd-data-collector/blob/master/ahttpdc/read/query/interface.py#L21)

Handles querying InfluxDB. Supports both async and sync clients.

### Methods

#### `async latest() -> pd.DataFrame`

[Source](https://github.com/straightchlorine/async-httpd-data-collector/blob/master/ahttpdc/read/query/interface.py#L113)

Query the last measurement from the past hour.

#### `async historical(start, end='') -> pd.DataFrame`

[Source](https://github.com/straightchlorine/async-httpd-data-collector/blob/master/ahttpdc/read/query/interface.py#L122)

Query a time range. Uses the sync client internally for large result sets.

#### `async custom_async(query) -> pd.DataFrame`

[Source](https://github.com/straightchlorine/async-httpd-data-collector/blob/master/ahttpdc/read/query/interface.py#L89)

Execute a custom async Flux query.

#### `async custom_sync(query) -> pd.DataFrame`

[Source](https://github.com/straightchlorine/async-httpd-data-collector/blob/master/ahttpdc/read/query/interface.py#L65)

Execute a custom Flux query via the synchronous client.

### Exceptions

#### `InvalidInterval`

[Source](https://github.com/straightchlorine/async-httpd-data-collector/blob/master/ahttpdc/read/query/interface.py#L17)

Raised when `historical()` receives invalid time parameters.

---

## JSONInfluxParser

[Source](https://github.com/straightchlorine/async-httpd-data-collector/blob/master/ahttpdc/read/store/parse/parser.py#L9)

Converts device JSON responses into InfluxDB-compatible records.

### Methods

#### `parse(json_measurements) -> dict`

[Source](https://github.com/straightchlorine/async-httpd-data-collector/blob/master/ahttpdc/read/store/parse/parser.py#L78)

Parse raw JSON into an InfluxDB record with measurement, tags,
timestamp, and fields.

If the same parameter appears in multiple sensors, the values are
averaged.

---

## DataParser

[Source](https://github.com/straightchlorine/async-httpd-data-collector/blob/master/ahttpdc/read/query/parse/data.py#L12)

Converts InfluxDB query results into pandas DataFrames.

### Methods

#### `into_dataframe() -> pd.DataFrame`

[Source](https://github.com/straightchlorine/async-httpd-data-collector/blob/master/ahttpdc/read/query/parse/data.py#L43)

Parse FluxTable results into a DataFrame indexed by local time.
Timestamps are converted from UTC to your local timezone.
