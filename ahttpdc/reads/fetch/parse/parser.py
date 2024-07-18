"""
Module parses JSON data into InfluxDB records.

Author: Piotr Krzysztof Lis - github.com/straightchlorine
"""

import datetime


class JSONInfluxParser:
    def __init__(self, sensors):
        self._sensors = sensors

    def __get_reads(self, data, device) -> dict[str, float]:
        """
        Based on sensors specified in sensors attribute fill the fields
        with appropriate key-value pairs for InfluxDB storage.

        Args:
            data (dict): The sensor readings to parse.

        Returns:
            dict: parameter-reading pairs extracted from the JSON file.
        """

        fields = {}
        for sensor in self._sensors:
            for param in self._sensors[sensor]:
                if param not in fields:
                    fields[param] = float(data[device][sensor][param])
                else:
                    # if the measurement already has been recorded, calculate
                    # the average of the measurements
                    previous = fields[param]
                    current = float(data[device][sensor][param])
                    average = (previous + current) / 2
                    fields[param] = average

        return fields

    def parse(self, json_measurements):
        """
        Parse raw json file into records for InfluxDB.

        Args:
            data (dict): The sensor readings to parse.
            device_name (str): The name of the device (default is 'nodemcu').

        Returns:
            dict: parameters parsed and decorated into InfluxDB record.
        """

        # device name in the first json key
        device = list(json_measurements.keys())[0]
        records = {
            'measurement': 'sensor_data',
            'tags': {'device': device},
            'timestamp': str(datetime.datetime.now()),
        }

        records['fields'] = self.__get_reads(json_measurements, device)
        return records
