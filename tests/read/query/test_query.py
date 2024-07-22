"""
Test class for AsyncQuery.

Author: Piotr Krzysztof Lis - github.com/straightchlorine
"""

import asyncio
from datetime import datetime, timedelta
import os
import pytest

from ahttpdc.read.interface import DataDaemon
from ahttpdc.read.query.interface import AsyncQuery


class TestAsyncQuery:
    """Test class for the AsyncQuery class.

    Method custom() is not tested, because it is involved within both of the
    methods.
    """

    def set_up(self):
        """Set up the testing environment."""

        # setting up the addresses
        self.db_ip = os.getenv('INFLUXDB_HOST')
        self.db_port = os.getenv('INFLUXDB_PORT')

        self.db_token = os.getenv('INFLUXDB_TOKEN')
        self.db_org = os.getenv('INFLUXDB_ORG')
        self.db_bucket = os.getenv('INFLUXDB_BUCKET')

        # address to the test server
        self.srv_ip = 'localhost'
        self.srv_port = 9000
        self.handle = 'circumstances'

        # urls
        self.srv_url = f'http://{self.srv_ip}:{self.srv_port}/{self.handle}'
        self.db_url = f'http://{self.db_ip}:{self.db_port}'

        # sensors, which test server provides dummy data for
        sensors = {
            'bmp180': [
                'altitude',
                'pressure',
                'temperature',
                'seaLevelPressure',
            ],
            'mq135': ['aceton', 'alcohol', 'co', 'co2', 'nh4', 'toulen'],
        }

        # set up the required objects
        if (
            isinstance(self.db_ip, str)
            and isinstance(self.db_port, str)
            and isinstance(self.db_token, str)
            and isinstance(self.db_org, str)
            and isinstance(self.db_bucket, str)
        ):
            self.daemon = DataDaemon(
                sensors,
                self.db_url,
                self.db_token,
                self.db_org,
                self.db_bucket,
                self.srv_url,
            )

            self.query = AsyncQuery(
                sensors,
                self.db_url,
                self.db_token,
                self.db_org,
                self.db_bucket,
            )

            self.daemon.enable()

    @staticmethod
    def verify_vals(to_verify: list[float]) -> bool:
        """Checks if the values stored in the DataFrame are correct.

        Values during testing are the same, provided by dev_server.py module.

        Args:
            to_verify (list): The values to verify.
        Returns:
            bool: True if the values are correct, False otherwise.
        """

        values = [
            2.57,
            6.62,
            149.56,
            28.88,
            412.1,
            15.12,
            998.42,
            1016.34,
            26.0,
            3.14,
        ]

        return all(value in to_verify for value in values)

    @pytest.mark.asyncio
    async def test_latest_query(self):
        """Test for the last() query."""

        # wait for some data to flow in
        self.set_up()
        await asyncio.sleep(2)
        self.daemon.disable()

        result = await self.query.latest()

        assert self.verify_vals(result.values.tolist()[0])

    @pytest.mark.asyncio
    async def test_historical_query(self):
        """Test the historical() query."""

        # wait for some data to flow in
        self.set_up()
        await asyncio.sleep(3)
        self.daemon.disable()

        finish = datetime.now()
        start = finish - timedelta(seconds=2)

        result = await self.query.historical(
            start.strftime('%Y-%m-%dT%H:%M:%SZ'),
            finish.strftime('%Y-%m-%dT%H:%M:%SZ'),
        )

        assert not result.empty
