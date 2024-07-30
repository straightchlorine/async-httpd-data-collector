"""Interface to communicate with the database.

Manages appropriate objects and provides an interface for the user to utilise.

Author: Piotr Krzysztof Lis - github.com/straightchlorine
"""

import pandas as pd
import asyncio

from ahttpdc.read.daemon import DataDaemon
from ahttpdc.read.query.interface import AsyncQuery

__all__ = ['DatabaseInterface']


class DatabaseInterface:
    """Control data-daemon and querying data.

    Attributes:
        daemon (DataDaemon): Object manages the process of fetching and
            collecting data.

    You can enable data-daemon like this:

        interface = DatabaseInterface(args)
        interface.daemon.enable()

    Args:
        sensors (dict): The sensors and their parameters to read.
        db_host (str): The host of the InfluxDB instance.
        db_port (int): The port of the InfluxDB instance.
        db_token (str): The token to authenticate with InfluxDB.
        db_org (str): The organization to use within InfluxDB.
        db_bucket (str): Bucket within InfluxDB where the data will be stored.
        srv_ip (str): The port of the device providing the readings.
        srv_port (str, optional): The http handle to access the data.
            Defaults to 8000.
        handle (str, optional): The address of the device in the network.
            Defaults to ''.
        interval(int, optional): Interval between fetch-collect cycle.
            Defaults to 1.
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
        srv_port: int | str = 80,
        handle: str = '',
        interval: int = 1,
    ):
        self._sensors = sensors

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

        self._interval = interval

        self.daemon = DataDaemon(
            self._sensors,
            self._db_url,
            self._db_token,
            self._db_org,
            self._db_bucket,
            self._srv_url,
            self._interval,
        )

        # query object
        self._query = AsyncQuery(
            self._sensors,
            self._db_url,
            self._db_token,
            self._db_org,
            self._db_bucket,
        )

    def query_latest(self) -> pd.DataFrame:
        """Query the latest measurement from InfluxDB.

        Returns:
            pd.DataFrame: The latest measurement.
        """
        loop = asyncio.get_event_loop()
        task = asyncio.create_task(self._query.latest())
        return loop.run_until_complete(task)

    def query_historical(
        self, start_relative: str, end: str = ''
    ) -> pd.DataFrame:
        """Query historical data from the database.

        Args:
            start_relative (str): Start of the time interval or a relative
                interval.
            end (str, optional): End of the time interval. Defaults to ''

        Returns:
            pd.DataFrame: Data from selected time interval.

        Examples:
            Requires a time interval or relative interval to be passed.
            * interval:
                query_historical('2024-01-01T00:00:00Z',
                    '2024-01-02T00:00:00Z')
            * relative relative:
                query_historical('-30d')
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._query.historical(start_relative, end)
        )

    def query_custom_async(self, query: str) -> pd.DataFrame:
        """Perform a custom asyncronous query on the database.

        Note: Use it for queries that you are certain provide small amounts of
        data. Otherwise, if you can have problems with unclosed sessions.

        Args:
            query (str): The Flux query to execute.

        Returns:
            pd.DataFrame: Response to the query.
        """
        loop = asyncio.get_event_loop()
        task = asyncio.create_task(self._query.custom_async(query))
        return loop.run_until_complete(task)

    def query_custom_sync(self, query: str) -> pd.DataFrame:
        """Perform a custom syncronous query on the database.

        Note: For large queries.

        Args:
            query (str): The Flux query to execute.

        Returns:
            pd.DataFrame: Response to the query.
        """
        loop = asyncio.get_event_loop()
        task = asyncio.create_task(self._query.custom_sync(query))
        return loop.run_until_complete(task)
