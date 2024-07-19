"""
Test class for AsyncQuery.

Author: Piotr Krzysztof Lis - github.com/straightchlorine
"""

import asyncio
from datetime import datetime, timedelta
import os
import multiprocessing
import pytest

from ahttpdc.read.fetch.fetcher import AsyncReadFetcher
from ahttpdc.read.query.query import AsyncQuery


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
        """
        Set up the testing environment.
        """

        self.dbhost = os.getenv('INFLUXDB_HOST')
        self.dbport = os.getenv('INFLUXDB_PORT')

        self.dbtoken = os.getenv('INFLUXDB_TOKEN')
        self.dborg = os.getenv('INFLUXDB_ORG')
        self.dbbudket = os.getenv('INFLUXDB_BUCKET')

        self.test_dev_ip = 'localhost'
        self.test_dev_port = 9000
        self.handle = 'circumstances'

        # list of sensors to fetch and their parameters
        sensors = {
            'bmp180': ['altitude', 'pressure', 'temperature', 'seaLevelPressure'],
            'mq135': ['aceton', 'alcohol', 'co', 'co2', 'nh4', 'toulen'],
        }

        # create the AcyncReadFetcher object
        self.fetcher = AsyncReadFetcher(
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

        self.query = AsyncQuery(
            self.dbhost,
            self.dbport,
            self.dbtoken,
            self.dborg,
            self.dbbudket,
            sensors,
        )

        def _start_fetching():
            asyncio.run(self.fetcher.schedule_fetcher())

        self.fetching_process = multiprocessing.Process(
            target=_start_fetching, name='asyncfetcher'
        )
        self.fetching_process.start()

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
        await asyncio.sleep(4)
        result = await self.query.latest()

        self.fetching_process.terminate()
        self.fetching_process.join()

        assert self.verify_vals(result.values.tolist()[0])

    @pytest.mark.asyncio
    async def test_historical(self):
        """
        Test the historical_data() method of the AsyncQuery class.
        """

        self.set_up()

        # wait for some readings
        await asyncio.sleep(5)

        finish = datetime.now()
        start = finish - timedelta(seconds=4)
        result = await self.query.historical_data(
            start.strftime('%Y-%m-%dT%H:%M:%SZ'), finish.strftime('%Y-%m-%dT%H:%M:%SZ')
        )

        self.fetching_process.terminate()
        self.fetching_process.join()

        assert not result.empty
