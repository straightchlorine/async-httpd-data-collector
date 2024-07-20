"""
Daemon facilitating continous fetching and storing.

Author: Piotr Krzysztof Lis - github.com/straightchlorine
"""

import multiprocessing
import asyncio

from ahttpdc.read.fetch.fetcher import AsyncFetcher
from ahttpdc.read.store.collector import AsyncCollector


class DataDaemon:
    """Background process managing asyncronous data fetching and collecting.

    Args:
        sensors (dict): Which sensors device has and what do they measure.
        db_url (str): URL address of the server with database.
        db_token (str): InfluxDB token to authenticate the user.
        db_org (str): Name of the InfluxDB organization
        db_bucket (str): Name of the InfluxDB bucket.
        srv_url (str): URL address of the server, handling JSON data.
        interval (int): Interval between each fetch-collect cycle.
    """

    def __init__(
        self,
        sensors: dict[str, list[str]],
        db_url: str,
        db_token: str,
        db_org: str,
        db_bucket: str,
        srv_url: str,
        interval: int = 1,
    ):
        self.sensors = sensors
        self.interval = interval

        # influxdb
        self._db_url = db_url
        self._token = db_token
        self._org = db_org
        self._bucket = db_bucket

        # server
        self._srv_url = srv_url

        # objects
        self._fetcher = AsyncFetcher(self._srv_url)
        self._collector = AsyncCollector(
            self.sensors,
            self._db_url,
            self._token,
            self._org,
            self._bucket,
        )

        def _daemon_coroutine():
            """Helper method to send asyncio coroutine to another process.

            TODO: Create a proper process queue for this process and ensure
            elegant shutdown of the coroutine along with mantaining results.
            """
            asyncio.run(self._schedule_daemon())

        self._data_daemon = multiprocessing.Process(
            target=_daemon_coroutine, name='data-daemon'
        )

    async def _fetch_to_db(self):
        """Request sensor readings and store the ones selected in the sensors
        dictionary."""
        json = await self._fetcher.request_readings()
        await self._collector.store_readings(json)

    async def _background_loop(self):
        """Start main loop of the daemon.

        Regulates the interval between each cycle in the infinite loop.
        """
        while True:
            await asyncio.sleep(self.interval)
            await self._fetch_to_db()

    async def _schedule_daemon(self):
        """Schedule the background loop coroutine."""
        async with asyncio.TaskGroup() as tg:
            await tg.create_task(self._background_loop())

    def enable(self):
        """Enable the daemon.

        Data daemon process will start in another process and start requesting
        readings from the server (srv_* attributes) with specified interval.

        Data is then decorated, parsed and stored as InfluxDB-compatible
        records.
        """
        self._data_daemon.start()

    def disable(self):
        """Disable the daemon."""
        self._data_daemon.terminate()
        self._data_daemon.join()
