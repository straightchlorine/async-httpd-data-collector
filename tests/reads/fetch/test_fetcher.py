"""
Test class for AsyncReadFetcher.

Author: Piotr Krzysztof Lis - github.com/straightchlorine
"""

Author: Piotr Krzysztof Lis - github.com/straightchlorine
"""

import asyncio
import json

import pytest

from reads.fetch.async_fetch import AsyncReadFetcher
from test.dev_server import DevelopmentServer


class TestFetcher:
    test_dev_ip: str
    test_dev_port: int

    def set_up(self):
        # start the test server
        DevelopmentServer().run_test_server()

        # load the secrets
        with open("secrets/secrets.json", "r") as f:
            secrets = json.load(f)

        # test server simulating the device
        self.test_dev_ip = "localhost"
        self.test_dev_port = 5000

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

    @pytest.mark.asyncio
    async def test_query(self):
        self.set_up()
        asyncio.create_task(self.fetcher.schedule_fetcher())
        await asyncio.sleep(2)
        assert 1 == 1
