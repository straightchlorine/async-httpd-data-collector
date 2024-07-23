"""Handle querying the database.

Author: Piotr Krzysztof Lis - github.com/straightchlorine
"""

from influxdb_client.client.exceptions import InfluxDBError
from influxdb_client.client.flux_table import TableList
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from influxdb_client.client.influxdb_client import InfluxDBClient
import pandas as pd

from ahttpdc.read.query.parse.data import DataParser

__all__ = ['AsyncQuery']


class InvalidInterval(Exception):
    pass


class AsyncQuery:
    """Query the database.

    Args:
        sensors (dict): Which sensors device has and what do they measure.
        db_url (str): URL address of the server with database.
        db_token (str): InfluxDB token to authenticate the user.
        db_org (str): Name of the InfluxDB organization
        db_bucket (str): Name of the InfluxDB bucket.
    """

    def __init__(
        self,
        sensors: dict[str, list[str]],
        db_url: str,
        db_token: str,
        db_org: str,
        db_bucket: str,
    ) -> None:
        self.sensors = sensors
        self.db_url = db_url

        self._token = db_token
        self._org = db_org
        self._bucket = db_bucket

    async def _async_client(self) -> InfluxDBClientAsync:
        """Helper funtion, provides ascyncronous InfluxDB client."""

        return InfluxDBClientAsync(
            url=self.db_url,
            token=self._token,
            org=self._org,
        )

    async def _client(self) -> InfluxDBClient:
        """Helper funtion, provides ascyncronous InfluxDB client."""

        return InfluxDBClient(
            url=self.db_url,
            token=self._token,
            org=self._org,
        )

    async def custom_sync(self, query: str) -> pd.DataFrame:
        """Pass to the database given query.

        Returns:
            pd.DataFrame: Response to the given query.
        """
        tables: TableList = TableList()
        try:
            # secure the connection
            client = await self._client()
            query_api = client.query_api()

            # query the database
            tables = query_api.query(query)

            # close the connection
            client.close()

        except InfluxDBError as e:
            print(f'Exception while querying the database:\n\n{e.message}')

        parser = DataParser(tables)
        return parser.into_dataframe()

    async def custom_async(self, query: str) -> pd.DataFrame:
        """Pass to the database given query.

        Returns:
            pd.DataFrame: Response to the given query.
        """
        tables: TableList = TableList()
        try:
            # secure the connection
            client = await self._async_client()
            query_api = client.query_api()

            # query the database
            tables = await query_api.query(query)

            # close the connection
            await client.close()

        except InfluxDBError as e:
            print(f'Exception while querying the database:\n\n{e.message}')

        parser = DataParser(tables)
        return parser.into_dataframe()

    async def latest(self) -> pd.DataFrame:
        """Query the database for the latest measurement.

        Returns:
            pd.DataFrame: The latest measurement of every parameter.
        """
        query = f'from(bucket:"{self._bucket}") |> range(start: -1h) |> last()'
        return await self.custom_async(query)

    async def historical(self, start: str, end: str = '') -> pd.DataFrame:
        """Query historical data from the database.

        Args:
            start (str): Start of the time interval or a relative interval.
            end (str, optional): End of the time interval. Defaults to ''.

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
        try:
            # TODO: experiment a bit and try to do it asyncronously if possible
            # tried futures
            if start is not None and end == '':
                return await self.custom_sync(
                    f'from(bucket:"{self._bucket}") |> range(start: {start})'
                )
            elif start is not None and end != '':
                return await self.custom_sync(
                    (
                        f'from(bucket:"{self._bucket}")'
                        f' |> range(start: {start}, stop: {end})'
                    )
                )
            else:
                raise InvalidInterval()
        except InvalidInterval:
            print('Invalid interval for the historical query!')
            return pd.DataFrame()
