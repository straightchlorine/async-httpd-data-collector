"""
Test class for DatabaseInterface.

Author: Piotr Krzysztof Lis - github.com/straightchlorine
"""

import asyncio
import os

import pytest

from ahttpdc.read.interface import DatabaseInterface

from tests.reads.query.test_query import TestQuery


class TestInterface:
    """
    Test class test the AsyncQuery class.

    Atributes:
        values (list[float]): The values to test against.
        fetcher (AsyncReadFetcher): The fetcher object.
        query (AsyncQuery): The query object.
        test_dev_ip (str): The IP of the test server.
        test_dev_port (int): The port of the test server.
    """

    values: list[float]
    interface: DatabaseInterface
    test_dev_ip: str
    test_dev_port: int

    def set_up(self):
        """
        Setting up the testing environment.
        """

        self.dbhost = os.getenv('INFLUXDB_HOST')
        self.dbport = os.getenv('INFLUXDB_PORT')

        self.dbtoken = os.getenv('INFLUXDB_TOKEN')
        self.dborg = os.getenv('INFLUXDB_ORG')
        self.dbbudket = os.getenv('INFLUXDB_BUCKET')

        self.test_dev_ip = 'localhost'
        self.test_dev_port = 9000
        self.handle = 'circumstances'

        # list of sensors and their parameters
        sensors = {
            'bmp180': ['altitude', 'pressure', 'temperature', 'seaLevelPressure'],
            'mq135': ['aceton', 'alcohol', 'co', 'co2', 'nh4', 'toulen'],
        }

        # create InfluxDBInterface object
        self.interface = DatabaseInterface(
            self.dbhost,
            self.dbport,
            self.dbtoken,
            self.dborg,
            self.dbbudket,
            sensors,
            self.test_dev_ip,
            self.test_dev_port,
            self.handle,
        )

        self.interface.enable_fetching()

    @pytest.mark.asyncio
    async def test_fetcher(self):
        """
        Test the fetcher object, just check if it runs.
        """

        self.set_up()
        await asyncio.sleep(2)

        self.interface.disable_fetching()
        assert True

    @pytest.mark.asyncio
    async def test_latest(self):
        """
        Test the latest query.
        """

        self.set_up()
        await asyncio.sleep(3)

        result = await self.interface.query_latest()
        self.interface.disable_fetching()

        assert TestQuery.verify_vals(result.values.tolist()[0])

    @pytest.mark.asyncio
    async def test_historical(self):
        """
        Test the historical query.
        """

        self.set_up()
        await asyncio.sleep(5)

        # the date variant tested in test_query.py
        result = await self.interface.query_historical('-3s')
        self.interface.disable_fetching()

        assert not result.empty
