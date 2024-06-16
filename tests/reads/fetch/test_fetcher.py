"""
Test class for AsyncReadFetcher.

Author: Piotr Krzysztof Lis - github.com/straightchlorine
"""

import asyncio
import os
import multiprocessing

import pytest

from ahttpdc.reads.fetch.async_fetch import AsyncReadFetcher


class TestFetcher:
    test_dev_ip: str
    test_dev_port: int

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

        # list of sensors to fetch and their paramters
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

    @pytest.mark.asyncio
    async def test_query(self):
        """
        Testing the fetcher, if works, it works.
        """

        self.set_up()

        def _start_fetching():
            asyncio.run(self.fetcher.schedule_fetcher())

        fetching_process = multiprocessing.Process(
            target=_start_fetching, name='asyncfetcher'
        )
        fetching_process.start()

        # let it work for some time
        await asyncio.sleep(2)

        fetching_process.terminate()
        fetching_process.join()

        assert 1 == 1
