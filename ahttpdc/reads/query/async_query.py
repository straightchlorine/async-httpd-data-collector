"""
Interface for passing queries to the database.

Author: Piotr Krzysztof Lis - github.com/straightchlorine
"""

from datetime import datetime, timedelta

from influxdb_client.client.exceptions import InfluxDBError
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from influxdb_client import InfluxDBClient
import pandas as pd

__all__ = ['AsyncQuery']


class AsyncQuery:
    """
    Interface to query the InfluxDB.

    Attributes:
        _influxdb_host (str): The host of the InfluxDB instance.
        _influxdb_port (int): The port of the InfluxDB instance.
        _influxdb_token (str): The token to authenticate with InfluxDB.
        _influxdb_organization (str): The organization to use within InfluxDB.
        _influxdb_bucket (str): Bucket within InfluxDB where the data will be stored.
        _db_url (str): The URL of the InfluxDB instance.
        sensors_and_params (dict): The sensors and their parameters to read.
    """

    _influxdb_host: str  # host of the influxdb instance
    _influxdb_port: int  # port of the influxdb instance
    _influxdb_token: str  # token to authenticate with influxdb
    _influxdb_organization: str  # organization to use within influxdb
    _influxdb_bucket: str  # bucket to save the data into

    _db_url: str  # address of the influxdb instance

    sensors: dict  # sensors and their parameters to read

    def __init__(self, host, port, token, org, bucket, sensors):
        """
        Initialize the fetcher with the required information.

        Args:
            host (str): The host of the InfluxDB instance.
            port (int): The port of the InfluxDB instance.
            token (str): The token to authenticate with InfluxDB.
            org (str): The organization to use within InfluxDB.
            bucket (str): Bucket within InfluxDB where the data will be stored.
            sensors (dict): The sensors and their parameters to read.
        """

        self._influxdb_host = host
        self._influxdb_port = port
        self._influxdb_token = token
        self._influxdb_organization = org
        self._influxdb_bucket = bucket

        self._db_url = f'http://{self._influxdb_host}:{self._influxdb_port}'

        self.sensors = sensors

    async def _get_InfluxDB_client(self) -> InfluxDBClientAsync:
        """Returns an InfluxDB client."""

        return InfluxDBClientAsync(
            url=self._db_url,
            token=self._influxdb_token,
            org=self._influxdb_organization,
        )

    def _convert_to_local_time(self, timestamps):
        """
        Convert a collection of UTC timestamps to local time.

        Args:
            timestamps (list): A list of UTC timestamps.
        Returns:
            list: A list of timestamps in local time.
        """

        local_timestamps = []

        # get the local offset from UTC
        local_offset = timedelta(
            seconds=datetime.now().astimezone().utcoffset().total_seconds()
        )

        # add the offset to the timestamps
        for timestamp in timestamps:
            utc_time = pd.to_datetime(timestamp)
            local_time = utc_time + local_offset
            local_timestamps.append(local_time)

        return local_timestamps

    def _into_dataframe(self, tables) -> pd.DataFrame:
        """
        Turns the tables into a pandas DataFrame with time of measurement as
        as index.

        Args:
            tables (list): The tables to turn into a DataFrame.
        Returns:
            pd.DataFrame: procured measurements as a DataFrame sorted by time.
        """
        read: dict = {}
        timestamps = set()

        # unpacking the table
        for table in tables:
            for record in table.records:
                # get the measurements
                parameter = record.get_field()
                measurement = record.get_value()
                timestamps.add(record.get_time())

                # ensure every parameter is present in the dict
                if parameter not in read:
                    read[parameter] = []
                read[parameter].append(float(measurement))

        # convert timestamps to local time
        local_timestamps = self._convert_to_local_time(timestamps)

        # if there is no time key, create one
        if 'time' not in read:
            read['time'] = []

        # add the timestamps to the data dict
        for timestamp in local_timestamps:
            read['time'].append(pd.to_datetime(timestamp))

        df = pd.DataFrame(read)
        df.set_index('time', inplace=True)
        df.sort_index(inplace=True)

        return df

    async def latest(self) -> pd.DataFrame:
        """
        Query the database for the latest measurement.

        Returns:
            pd.DataFrame: The latest measurement of every parameter.
        """

        # get the connection to the database via query api
        client = await self._get_InfluxDB_client()
        query_api = client.query_api()

        # query the latest measurement
        query = f'from(bucket:"{self._influxdb_bucket}") |> range(start: -1h) |> last()'

        tables = None
        try:
            tables = await query_api.query(query)
        except InfluxDBError as e:
            print(f'Exception caught while querying the database:\n\n {e.message}')

        # close the connection
        await client.close()

        # turn the tables into a DataFrame and return it
        if tables is not None:
            return self._into_dataframe(tables)
        else:
            return pd.DataFrame()

    def historical_query(self, query: str) -> pd.DataFrame:
        tables = None
        try:
            with InfluxDBClient(
                url=self._db_url,
                token=self._influxdb_token,
                org=self._influxdb_organization,
            ) as client:
                query_api = client.query_api()
                tables = query_api.query(query)
        except InfluxDBError as e:
            print(f'Exception caught while querying the database:\n\n {e.message}')

        if tables is not None:
            return self._into_dataframe(tables)
        else:
            return pd.DataFrame()

    async def historical_data(self, start: str, end: str = '') -> pd.DataFrame:
        """
        Query the database synchronously for historical data within the specified
        range.
        Query the database for historical data within the specified time range.
        Use when dealing with large time intervals. Uses regular client, not the
        async one.

        Args:
            start(str): start time (e.g., '2024-01-02T00:00:00Z') of the query
                        or relative time string (e.g., '-30d') for end unspecified
            end (str): End time of the query (e.g., '2024-01-02T00:00:00Z')

        Example:
            interface.historical_data('-30d')

            finish = datetime.now()
            start = finish - timedelta(minuts=30)
            start = start.strftime('%Y-%m-%dT%H:%M:%SZ')
            finish = finish.strftime('%Y-%m-%dT%H:%M:%SZ')

            interface.historical_data(start, finish)

        Returns:
            pd.DataFrame: Historical data within the specified time range.
        """

        if start is not None and end == '':
            query = f'from(bucket:"{self._influxdb_bucket}") |> range(start: {start})'
            return self.historical_query(query)
        elif start is not None and end != '':
            query = f'from(bucket:"{self._influxdb_bucket}") |> range(start: {start}, stop: {end})'
            return self.historical_query(query)
        else:
            return pd.DataFrame()

    async def query(self, query: str) -> pd.DataFrame:
        """
        Perform a custom query on the database.

        Args:
            query (str): The InfluxDB query to execute.

        Returns:
            pd.DataFrame: The result of the custom query.
        """
        client = await self._get_InfluxDB_client()
        query_api = client.query_api()

        tables = None

        try:
            tables = await query_api.query(query)
        except InfluxDBError as e:
            print(f'Exception caught while querying the database:\n\n {e.message}')

        await client.close()

        if tables is not None:
            return self._into_dataframe(tables)
        else:
            return pd.DataFrame()
