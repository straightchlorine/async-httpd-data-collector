"""Parse JSON response into records compatible with InfluxDB.

Author: Piotr Krzysztof Lis - github.com/straightchlorine
"""

import datetime


class JSONInfluxParser:
    """Parse JSON reponse into records for InfluxDB.

    Required JSON structure:
    {
      "nodemcu": {          # name of the device
        "mq135": {          # sensor, managed by the device
          "co": "2.56",     # measured parameters
          "co2": "402.08",
          "alcohol": "0.94",
          "nh4": "3.30",
          "aceton": "0.32",
          "toulen": "0.38"
        },
        "bmp180": {
          "temperature": "28.60",
          "pressure": "1006.13",
          "seaLevelPressure": "1024.18",
          "altitude": "149.75"
        },
        "ds18b20": {
          "temperature": "27.00"
        },
        "dht22": {
          "temperature": "27.90",
          "humidity": "47.30"
        }
      }
    }

    Args:
        sensors (dict[str, list[str]]): Dict of sensors and parameters to
            collect.
    """

    def __init__(self, sensors):
        self._sensors = sensors

    def _to_fields(self, json_response, device) -> dict[str, float]:
        """Parse measured parameters from JSON response to a dictionary.

        Sensors dictionary defines which parameters will be stored in the
        databse. In case of multiple readings of the same parameter,
        the average is calculated.


        Args:
            json_response (dict): The sensor readings to parse.

        Returns:
            fields (dict[str, float]): Parameter-value pairs extracted from
                the JSON file.
        """

        fields = {}
        for sensor in self._sensors:
            for param in self._sensors[sensor]:
                if param not in fields:
                    fields[param] = float(json_response[device][sensor][param])
                else:
                    # if the measurement already has been recorded, calculate
                    # the average of the measurements
                    previous = fields[param]
                    current = float(json_response[device][sensor][param])
                    average = (previous + current) / 2
                    fields[param] = average

        return fields

    def parse(self, json_measurements):
        """Parse raw json file into records for InfluxDB.

        Note: if one parameter is selected for multiple sensors, the average
        of those measurements will be saved.

        For example: multiple temperature readings from 3 sensors and all of
        them are selected via sensors dictionary.

        Take it into account, if you have dedicated sensors for a specific
        parameters. In such case other utilities might simply make the readings
        less accurate than they could have been otherwise.

        Args:
            json_measurements (dict): The sensor readings to parse.

        Returns:
            records (dict): Measurements from the sensors along with metadata
            for InfluxDB.
        """

        # device name in the first json key
        device = list(json_measurements.keys())[0]
        records = {
            'measurement': 'sensor_data',
            'tags': {'device': device},
            'timestamp': str(datetime.datetime.now()),
        }

        records['fields'] = self._to_fields(json_measurements, device)

        return records
