#!/usr/bin/env python

"""
Example script, which enables process of fetching and storing data to the
InfluxDB database.

Author: Piotr Krzysztof Lis - github.com/straightchlorine
"""

import json
from ahttpdc.read.database_interface import DatabaseInterface

# load the secrets
with open('secrets/secrets.json', 'r') as f:
    secrets = json.load(f)

# define the sensors and parameters to fetch, according to the JSON response:
# {
#   "nodemcu": {
#     "mq135": {
#       "co": "2.56",
#       "co2": "402.08",
#       "alcohol": "0.94",
#       "nh4": "3.30",
#       "aceton": "0.32",
#       "toulen": "0.38"
#     },
#     "bmp180": {
#       "temperature": "28.60",
#       "pressure": "1006.13",
#       "seaLevelPressure": "1024.18",
#       "altitude": "149.75"
#     },
#     "ds18b20": {
#       "temperature": "27.00"
#     },
#     "dht22": {
#       "temperature": "27.90",
#       "humidity": "47.30"
#     }
#   }
# }
# response above is an example from my own setup.
sensors = {
    'bmp180': ['altitude', 'pressure', 'seaLevelPressure'],
    'mq135': ['aceton', 'alcohol', 'co', 'co2', 'nh4', 'toulen'],
    'ds18b20': ['temperature'],
    'dht22': ['humidity'],
}

# create the DatabaseInterface object
interface = DatabaseInterface(
    sensors,
    secrets['host'],
    secrets['port'],
    secrets['token'],
    secrets['organization'],
    secrets['bucket'],
    secrets['srv_ip'],
    secrets['srv_port'],
    secrets['handle'],
    1,
)

if __name__ == '__main__':
    interface.daemon.enable()
