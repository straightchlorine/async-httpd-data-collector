"""
Test class for DatabaseInterface.

Author: Piotr Krzysztof Lis - github.com/straightchlorine
"""

import asyncio
import os
import pytest

from ahttpdc.read.interface import DatabaseInterface


class TestInterface:
    """Test class test the DatabaseInterface class.

    Testing of the query object within the interface was omitted, as it has
    its own dedicated module.
    """

    def set_up(self):
        """
        Setting up the testing environment.
        """

        # variables are set within workflow
        self.db_ip = os.getenv('INFLUXDB_HOST')
        self.db_port = os.getenv('INFLUXDB_PORT')

        self.db_token = os.getenv('INFLUXDB_TOKEN')
        self.db_org = os.getenv('INFLUXDB_ORG')
        self.db_bucket = os.getenv('INFLUXDB_BUCKET')

        self.srv_ip = 'localhost'
        self.srv_port = 9000
        self.handle = 'circumstances'

        # list of sensors and their parameters
        sensors = {
            'bmp180': [
                'altitude',
                'pressure',
                'temperature',
                'seaLevelPressure',
            ],
            'mq135': ['aceton', 'alcohol', 'co', 'co2', 'nh4', 'toulen'],
        }

        # verify if the variables were assigned correctly and create
        # DatabaseInterface object, and turn on the daemon
        if (
            isinstance(self.db_ip, str)
            and isinstance(self.db_port, str)
            and isinstance(self.db_token, str)
            and isinstance(self.db_org, str)
            and isinstance(self.db_bucket, str)
        ):
            self.interface = DatabaseInterface(
                sensors,
                self.db_ip,
                self.db_port,
                self.db_token,
                self.db_org,
                self.db_bucket,
                self.srv_ip,
                self.srv_port,
                self.handle,
            )

            self.interface.daemon.enable()

    @pytest.mark.asyncio
    async def test_data_daemon(self):
        """Test the daemon object.

        Currently pretty uninspiring, if works it works logic.

        TODO: Expand on this test, along with more experimentation on the
            object.
        """

        self.set_up()
        await asyncio.sleep(1)
        self.interface.daemon.disable()

        assert True
