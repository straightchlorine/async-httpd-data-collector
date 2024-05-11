"""
Interface that control both fetching, writing and querying from the database.

Author: Piotr Krzysztof Lis - github.com/straightchlorine
"""

import asyncio

import pandas as pd
from reads.fetch.async_fetch import AsyncReadFetcher
from reads.query.async_query import AsyncQuery


class DatabaseInterface:
    _influxdb_host: str  # host of the influxdb instance
    _influxdb_port: int  # port of the influxdb instance
    _influxdb_token: str  # token to authenticate with influxdb
    _influxdb_organization: str  # organization to use within influxdb
    _influxdb_bucket: str  # bucket to save the data into

    _dev_ip: str  # ip of the device sending the data
    _dev_port: int  # port of the device sending the data
    _dev_handle: str  # handle to access the data

    _dev_url: str  # address of the device in the network
    _db_url: str  # address of the influxdb instance

    def __init__(
        self, host, port, token, org, bucket, sensors, dev_ip, dev_port, handle=""
    ):
        """
        Initialize the fetcher with the required information.

        Args:
            host (str): The host of the InfluxDB instance.
            port (int): The port of the InfluxDB instance.
            token (str): The token to authenticate with InfluxDB.
            org (str): The organization to use within InfluxDB.
            bucket (str): Bucket within InfluxDB where the data will be stored.
            dev_ip (str): The IP address of device providing sensor readings.
            dev_port (str): The port of the device providing the readings.
            handle (str): The http handle to access the data ("" by default).
            sensors (dict): The sensors and their parameters to read.
        """

        self._influxdb_host = host
        self._influxdb_port = port
        self._influxdb_token = token
        self._influxdb_organization = org
        self._influxdb_bucket = bucket

        self._dev_ip = dev_ip
        self._dev_port = dev_port
        self._dev_handle = handle

        self._dev_url = f"http://{self._dev_ip}:{self._dev_port}/{self._dev_handle}"
        self._db_url = f"http://{self._influxdb_host}:{self._influxdb_port}"

        self.sensors = sensors

        self._fetcher = AsyncReadFetcher(
            self._influxdb_host,
            self._influxdb_port,
            self._influxdb_token,
            self._influxdb_organization,
            self._influxdb_bucket,
            self.sensors,
            self._dev_ip,
            self._dev_port,
            self._dev_handle,
        )

        self.query_interface = AsyncQuery(
            self._influxdb_host,
            self._influxdb_port,
            self._influxdb_token,
            self._influxdb_organization,
            self._influxdb_bucket,
            self.sensors,
        )

    def enable_fetching(self):
        """
        Enable fetching from the device specified by dev_ip, dev_port and handle.

        Starts the fetching task in the background, thus should be invoked last
        in order to avoid blocking the main thread.
        """

        asyncio.run(self._fetcher.schedule_fetcher())

    async def query_latest(self) -> pd.DataFrame:
        """
        Query the latest measurement from the InfluxDB.

        Returns:
            pd.DataFrame: The latest measurement.
        """

        print("<.> querying latest measurement...")
        query_task = asyncio.create_task(self.query_interface.latest())
        await query_task
        result = query_task.result()
        return result

    async def query_historical(self, start: str, end: str) -> pd.DataFrame:
        """
        Query historical data from the database.

        Args:
            start (str): Start time of the query (e.g., '2024-01-01T00:00:00Z').
            end (str): End time of the query (e.g., '2024-01-02T00:00:00Z').

        Returns:
            pd.DataFrame: Historical data within the specified time range.
        """
        print("<.> querying historical data...")
        query_task = asyncio.create_task(
            self.query_interface.historical_data(start, end)
        )
        await query_task
        result = query_task.result()
        return result

    async def query(self, query: str) -> pd.DataFrame:
        """
        Perform a custom query on the database.

        Args:
            query (str): The InfluxDB query to execute.

        Returns:
            pd.DataFrame: The result of the custom query.
        """
        print("<.> custom query...")
        query_task = asyncio.create_task(self.query_interface.query(query))
        await query_task
        result = query_task.result()
        return result
