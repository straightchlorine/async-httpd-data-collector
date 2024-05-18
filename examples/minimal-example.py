#!/usr/bin/env python
import json

from ahttpdc.reads.interface import DatabaseInterface

# load the secrets
with open('secrets/pc-secret.json', 'r') as f:
    secrets = json.load(f)

sensors = {
    'bmp180': ['altitude', 'pressure', 'seaLevelPressure'],
    'mq135': ['aceton', 'alcohol', 'co', 'co2', 'nh4', 'toulen'],
    'ds18b20': ['temperature'],
    'dht22': ['humidity'],
}

dev_ip = '192.168.10.101'
dev_port = '80'

# create the DatabaseInterface object
interface = DatabaseInterface(
    secrets['host'],
    secrets['port'],
    secrets['token'],
    secrets['organization'],
    secrets['bucket'],
    sensors,
    dev_ip,
    dev_port,
    secrets['handle'],
)

if __name__ == '__main__':
    interface.enable_fetching()
