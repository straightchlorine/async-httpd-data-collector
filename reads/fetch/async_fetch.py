"""
Module asyncronously fetches the data from given device and writes the readings
into InfluxDB as records.

Author: Piotr Krzysztof Lis - github.com/straightchlorine
"""

import asyncio
import datetime

from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from influxdb_client.client.write.point import Point

import aiohttp


class AsyncReadFetcher:
    """
    Manage fetching the readings from the sensor asyncronously via aiohttp and
    handling received data so that it can be stored within InfluxDB.

    Attributes:
        _influxdb_host (str): The host of the InfluxDB instance.
        _influxdb_port (int): The port of the InfluxDB instance.
        _influxdb_token (str): The token to authenticate with InfluxDB.
        _influxdb_organization (str): The organization to use within InfluxDB.
        _influxdb_bucket (str): Bucket within InfluxDB where the data will be stored.
        _device_ip (str): The IP address of device providing sensor readings.
        _device_port (str): The port of the device providing the readings.
        _http_handle (str): The http handle to access the data.
        _device_address (str): The address of the device in the network.
        _database_address (str): The address of the InfluxDB instance.
        _sensors (dict): Sensors attached to the device.
    """

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
            host (str): Host of the InfluxDB instance.
            port (int): Port of the InfluxDB instance.
            token (str): Token to authenticate with InfluxDB.
            org (str): Organization to use within InfluxDB.
            bucket (str): Bucket within InfluxDB where the data will be stored.
            dev_ip (str):IP address of device providing sensor readings.
            dev_port (str): Port of the device providing the readings.
            handle (str): Http handle to access the data ("" by default).
            sensors (dict): Which sensors device has and what do they measure.
        """

        # InfluxDB authentication data
        self._influxdb_host = host
        self._influxdb_port = port
        self._influxdb_token = token
        self._influxdb_organization = org
        self._influxdb_bucket = bucket

        # device identification
        self._dev_ip = dev_ip
        self._dev_port = dev_port
        self._dev_handle = handle

        # device and database URLs
        self._dev_url = f"http://{self._dev_ip}:{self._dev_port}/{self._dev_handle}"
        self._db_url = f"http://{self._influxdb_host}:{self._influxdb_port}"

        self._sensors = sensors

    def _get_reads(self, data) -> dict[str, float]:
        """
        Based on sensors specified in sensors attribute fill the fields
        with appropriate key-value pairs for InfluxDB storage.

        Args:
            data (dict): The sensor readings to parse.
        """

        fields = {}
        for sensor in self._sensors:
            for param in self._sensors[sensor]:
                fields[param] = float(data["nodemcu"][sensor][param])
        return fields

    def _parse_into_records(self, data, device_name="nodemcu"):
        """
        Parse raw json file into records for InfluxDB.

        Args:
            data (dict): The sensor readings to parse.
            device_name (str): The name of the device (default is 'nodemcu').
        """

        records = {
            "measurement": "sensor_data",
            "tags": {"device": device_name},
            "timestamp": str(datetime.datetime.now()),
        }

        records["fields"] = self._get_reads(data)
        return records

    async def _write_to_db(self, client, record):
        """
        Write the sensor readings to InfluxDB.

        Args:
            client (InfluxDBClientAsync): The InfluxDB client to write to.
            records (dict): The sensor readings as records for InfluxDB.
        """

        print("<.> writing new read into database...")
        write_api = client.write_api()
        point = Point.from_dict(record, write_precision="ns")
        await write_api.write(
            bucket=self._influxdb_bucket, org=self._influxdb_organization, record=point
        )

    async def _store_sensor_readings(self, record):
        """
        Store sensor readings within InfluxDB.

        Args:
            records (dict): The sensor readings in the form of InfluxDB records.
        """

        async with InfluxDBClientAsync(
            url=self._db_url,
            token=self._influxdb_token,
            org=self._influxdb_organization,
        ) as client:
            await self._write_to_db(client, record)

    async def _request_sensor_readings(self, session):
        """
        Fetch the sensor readings from the device via http request.

        Args:
            session: The aiohttp session to use for the request.
        """

        async with session.get(self._dev_url) as response:
            if response.status != 200:
                print(f"Error fetching data: {response.status}")
            else:
                read = await response.json()
                return read

    async def _request_and_store(self):
        """
        Request sensor reading via aiohttp and store them in InfluxDB.
        """

        async with aiohttp.ClientSession() as session:
            json = await self._request_sensor_readings(session)
            await self._store_sensor_readings(self._parse_into_records(json))

    async def _fetching_loop(self):
        """
        Main fetcher loop to request and store sensor readings.

        Loop is infinite and receives readings every second, meant to run in
        the background.
        """

        while True:
            await asyncio.sleep(1)
            await self._request_and_store()

    async def schedule_fetcher(self):
        """
        Create a task group managing the fetching loop.

        Tested using asyncio.run()
        """

        async with asyncio.TaskGroup() as tg:
            await tg.create_task(self._fetching_loop())
