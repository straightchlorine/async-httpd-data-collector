"""
Test class for AsyncQuery.

Author: Piotr Krzysztof Lis - github.com/straightchlorine
"""

import pytest
import json
import asyncio

from reads.fetch.async_fetch import AsyncReadFetcher
from reads.query.async_query import AsyncQuery
from test.dev_server import DevelopmentServer


class TestQuery:
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
    test_dev_ip: str
    test_dev_port: int

    fetcher: AsyncReadFetcher
    query: AsyncQuery

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

        # create the AcyncReadFetcher object
        self.fetcher = AsyncReadFetcher(
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

        self.query = AsyncQuery(
            secrets["host"],
            secrets["port"],
            secrets["token"],
            secrets["organization"],
            secrets["bucket"],
            sensors,
        )

        # needs to ba called directly because of the running loop
        asyncio.create_task(self.fetcher._fetching_loop())

    @staticmethod
    def verify_vals(to_verify):
        """
        Checks if the values stored in the DataFrame are correct.

        Args:
            to_verify (list): The values to verify.
        Returns:
            bool: True if the values are correct, False otherwise.
        """
        values = [2.57, 6.62, 149.56, 28.88, 412.1, 15.12, 998.42, 1016.34, 26.0, 3.14]

        index = 0
        if to_verify is None:
            return False
        else:
            for num in to_verify:
                if num in values:
                    index += 1
        if index == len(values):
            return True

    @pytest.mark.asyncio
    async def test_latest(self):
        """
        Test the latest() method of the AsyncQuery class.
        """
        self.set_up()

        # wait for some readings
        await asyncio.sleep(2)

        result = await self.query.latest()
        assert self.verify_vals(result.values.tolist()[0])

    @pytest.mark.asyncio
    async def test_historical(self):
        """
        Test the historical_data() method of the AsyncQuery class.
        """
        self.set_up()

        result = await self.query.historical_data(
            "2024-05-05T18:00:00Z", "2024-05-05T21:00:00Z"
        )
        assert not result.empty
