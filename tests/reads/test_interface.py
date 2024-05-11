"""
Test class for DatabaseInterface.

Author: Piotr Krzysztof Lis - github.com/straightchlorine
"""

import asyncio
import json

import pytest

from reads.interface import DatabaseInterface
from tests.dev_server import DevelopmentServer
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
        # start the test server and specifiy the IP and port
        DevelopmentServer().run_test_server()
        self.test_dev_ip = "localhost"
        self.test_dev_port = 5000

        # load the secrets
        with open("secrets/secrets.json", "r") as f:
            secrets = json.load(f)

        # list of sensors and their parameters
        sensors = {
            "bmp180": ["altitude", "pressure", "temperature", "seaLevelPressure"],
            "mq135": ["aceton", "alcohol", "co", "co2", "nh4", "toulen"],
        }

        # create InfluxDBInterface object
        self.interface = DatabaseInterface(
            secrets["host"],
            secrets["port"],
            secrets["token"],
            secrets["organization"],
            secrets["bucket"],
            sensors,
            self.test_dev_ip,
            self.test_dev_port,
            secrets["handle"],
        )

        self.interface.enable_fetching()

    @pytest.mark.asyncio
    async def test_fetcher(self):
        """
        Test the fetcher object.
        """
        self.set_up()
        await asyncio.sleep(2)
        assert 1 == 1

    @pytest.mark.asyncio
    async def test_latest(self):
        """
        Test the latest query.
        """
        self.set_up()
        await asyncio.sleep(2)
        result = await self.interface.query_latest()
        assert TestQuery.verify_vals(result.values.tolist()[0])

    @pytest.mark.asyncio
    async def test_historical(self):
        """
        Test the historical query.
        """
        self.set_up()
        await asyncio.sleep(2)
        result = await self.interface.query_historical(
            "2024-05-05T18:00:00Z", "2024-05-05T21:00:00Z"
        )
        assert not result.empty
