"""
Test class for DatabaseInterface.

Author: Piotr Krzysztof Lis - github.com/straightchlorine
"""

import asyncio
import json

import pytest

from test.reads.query.test_query import TestQuery
from reads.interface import DatabaseInterface
from test.dev_server import DevelopmentServer



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

        # needs to ba called directly because of the running loop
        asyncio.create_task(self.interface._fetcher._fetching_loop())

    @pytest.mark.asyncio
    async def test_fetcher(self):
        self.set_up()
        await asyncio.sleep(5)
        assert 1 == 1

    @pytest.mark.asyncio
    async def test_latest(self):
        self.set_up()
        await asyncio.sleep(2)
        result = await self.interface.query_latest()
        assert TestQuery.verify_vals(result.values.tolist()[0])

    @pytest.mark.asyncio
    async def test_historical(self):
        self.set_up()
        await asyncio.sleep(2)
        result = await self.interface.query_historical(
            "2024-05-05T18:00:00Z", "2024-05-05T21:00:00Z"
        )
        print(result)
        # assert TestQuery.verify_vals(result.values.tolist()[0])
