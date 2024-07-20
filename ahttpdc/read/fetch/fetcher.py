"""
Module asyncronously fetches the data from given device and writes the readings
into InfluxDB as records.

Author: Piotr Krzysztof Lis - github.com/straightchlorine
"""

import aiohttp


__all__ = ['AsyncFetcher']


class AsyncFetcher:
    """Asyncronously fetch JSON response from device providing readings.

    TODO: Add some verification module to check if the JSON response is
    appropriate for further processing, i.e. it follows:

    {
      "nodemcu": {
        "mq135": {
          "co": "2.56",
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

    Attributes:
        url (str): URL address of the device with data.
    """

    def __init__(self, url):
        self._url = url

    async def request_readings(self):
        """
        Request JSON response from the server.


        Returns:
            dict: JSON response from the device.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(self._url) as response:
                if response.status != 200:
                    print(f'Error fetching data: {response.status}')
                else:
                    read = await response.json()
                    return read
