#!/usr/bin/env python
import json
import asyncio
import pandas as pd
from ahttpdc.reads.interface import DatabaseInterface

# load the secrets
with open('secrets/rpi-secrets.json', 'r') as f:
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


async def query():
    result = await interface.query_historical('-30d')
    return result


if __name__ == '__main__':
    dataframe: pd.DataFrame = asyncio.run(query())
    dataframe.to_csv('sensor-data.csv')
