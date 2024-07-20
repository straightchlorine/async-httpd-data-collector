"""
Interface that control both fetching, writing and querying from the database.

Author: Piotr Krzysztof Lis - github.com/straightchlorine
"""

import asyncio

import pandas as pd

from ahttpdc.read.daemon import DataDaemon
from ahttpdc.read.query.query import AsyncQuery

__all__ = ['DatabaseInterface']


class DatabaseInterface:
    """
    Interface to control fetching, writing and querying from the database.

    Attributes:
        sensors (dict): The sensors and their parameters to read.
        db_host (str): The host of the InfluxDB instance.
        db_port (int): The port of the InfluxDB instance.
        db_token (str): The token to authenticate with InfluxDB.
        db_org (str): The organization to use within InfluxDB.
        db_bucket (str): Bucket within InfluxDB where the data will be stored.
        srv_ip (str): The port of the device providing the readings.
        srv_port (str, optional): The http handle to access the data.
        handle (str, optional): The address of the device in the network.
    """

    def __init__(
        self,
        sensors: dict[str, list[str]],
        db_host: str,
        db_port: str,
        db_token: str,
        db_org: str,
        db_bucket: str,
        srv_ip: str,
        srv_port: int,
        handle: str = '',
        interval: int = 1,
    ):
        self.sensors = sensors

        self._db_host = db_host
        self._db_port = db_port
        self._db_url = f'http://{self._db_host}:{self._db_port}'

        self._db_token = db_token
        self._db_org = db_org
        self._db_bucket = db_bucket

        self._ip = srv_ip
        self._port = srv_port
        self._handle = handle
        self._srv_url = f'http://{self._ip}:{self._port}/{self._handle}'

        self.interval = interval

        self.daemon = DataDaemon(
            self.sensors,
            self._db_url,
            self._db_token,
            self._db_org,
            self._db_bucket,
            self._srv_url,
            self.interval,
        )

        self.query_interface = AsyncQuery(
            self._db_host,
            self._db_port,
            self._db_token,
            self._db_org,
            self._db_bucket,
            self.sensors,
        )

    async def query_latest(self) -> pd.DataFrame:
        """
        Query the latest measurement from the InfluxDB.

        Returns:
            pd.DataFrame: The latest measurement.
        """
        query_task = asyncio.create_task(self.query_interface.latest())
        await query_task
        result = query_task.result()
        return result

    async def query_historical(self, start: str, end: str = '') -> pd.DataFrame:
        """
        Query historical data from the database.

        Args:
            start (str): Start time of the query (e.g., '2024-01-01T00:00:00Z').
            end (str): End time of the query (e.g., '2024-01-02T00:00:00Z').

        Returns:
            pd.DataFrame: Historical data within the specified time range.
        """
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
        query_task = asyncio.create_task(self.query_interface.query(query))
        await query_task
        result = query_task.result()
        return result
