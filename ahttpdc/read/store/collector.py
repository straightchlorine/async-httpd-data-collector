"""
Module asyncronously stores data

Author: Piotr Krzysztof Lis - github.com/straightchlorine
"""

from ahttpdc.read.store.parse.parser import JSONInfluxParser

from influxdb_client.client.write.point import Point
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync


class AsyncCollector:
    """Class stores the data asyncronously within InfluxDB.

    Attributes:
        sensors (dict[str, list[str]]): readings to store from each sensor.
        db_url (str): url link to the InfluxDB.
        db_token (str): token to the InfluxDB.
        db_org (str): organization in the InfluxDB
        db_bucket (str): bucket to store data within in InfluxDB

    """

    def __init__(
        self,
        sensors: dict[str, list[str]],
        db_url: str,
        db_token: str,
        db_org: str,
        db_bucket: str,
    ) -> None:
        self._sensors = sensors
        self._parser = JSONInfluxParser(self._sensors)

        # influxdb variables
        self._url = db_url
        self._token = db_token
        self._org = db_org
        self._bucket = db_bucket

    async def store_sensor_readings(self, json_response):
        """
        Store sensor readings within InfluxDB.

        Args:
            records (dict): The sensor readings in the form of InfluxDB records.
        """
        # crating the time-series point out of the record
        record = self._parser.parse(json_response)
        point = Point.from_dict(record, write_precision='ms')

        async with InfluxDBClientAsync(
            url=self._url,
            token=self._token,
            org=self._org,
        ) as client:
            await client.write_api().write(
                bucket=self._bucket, org=self._org, record=point
            )