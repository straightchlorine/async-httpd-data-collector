#!/usr/bin/env python

"""
Example dashboard application using DatabaseInterface class.

Author: Piotr Krzysztof Lis - github.com/straightchlorine
"""

import asyncio
import json
import multiprocessing

import pandas as pd

from ahttpdc.reads.interface import DatabaseInterface
from dash import Dash, Input, Output, callback, dcc, html

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
    'bmp180': ['altitude', 'pressure', 'temperature', 'seaLevelPressure'],
    'mq135': ['aceton', 'alcohol', 'co', 'co2', 'nh4', 'toulen'],
}

# create the DatabaseInterface object
interface = DatabaseInterface(
    secrets['host'],
    secrets['port'],
    secrets['token'],
    secrets['organization'],
    secrets['bucket'],
    sensors,
    secrets['dev_ip'],
    secrets['dev_port'],
    secrets['handle'],
)


# data update task
async def update_data():
    # get the data
    data = await interface.query_latest()
    return data


# initializing and setting up the dashboard
dashboard_server = Dash(__name__)
dashboard_server.layout = html.Div(
    html.Div(
        [
            html.H4('Sensor Data'),
            html.Div(id='live-update-text'),
            dcc.Interval(id='interval-component', interval=1000, n_intervals=0),
        ]
    )
)


# live updating the text
@callback(
    Output('live-update-text', 'children'), Input('interval-component', 'n_intervals')
)
def update_metrics(n):
    measurement_dataframe: pd.DataFrame = asyncio.run(update_data())

    if not measurement_dataframe.empty:
        time = measurement_dataframe['time'].iloc[-1]
        altitude = measurement_dataframe['altitude'].iloc[-1]
        pressure = measurement_dataframe['pressure'].iloc[-1]
        temperature = measurement_dataframe['temperature'].iloc[-1]
        sea_level_pressure = measurement_dataframe['seaLevelPressure'].iloc[-1]
        aceton = measurement_dataframe['aceton'].iloc[-1]
        alcohol = measurement_dataframe['alcohol'].iloc[-1]
        co = measurement_dataframe['co'].iloc[-1]
        co2 = measurement_dataframe['co2'].iloc[-1]
        nh4 = measurement_dataframe['nh4'].iloc[-1]
        toulen = measurement_dataframe['toulen'].iloc[-1]
        style = {'padding': '5px', 'fontSize': '16px'}
        return [
            html.Span('Time: {0}'.format(time), style=style),
            html.Span('Altitude: {0:.2f}'.format(altitude), style=style),
            html.Span('Pressure: {0:.2f}'.format(pressure), style=style),
            html.Span('Temperature: {0:.2f}'.format(temperature), style=style),
            html.Span(
                'Sea Level Pressure: {0:.2f}'.format(sea_level_pressure), style=style
            ),
            html.Span('Aceton: {0:.2f}'.format(aceton), style=style),
            html.Span('Alcohol: {0:.2f}'.format(alcohol), style=style),
            html.Span('CO: {0:.2f}'.format(co), style=style),
            html.Span('CO2: {0:.2f}'.format(co2), style=style),
            html.Span('NH4: {0:.2f}'.format(nh4), style=style),
            html.Span('Toulen: {0:.2f}'.format(toulen), style=style),
        ]
    else:
        return [html.Span('probing data...')]


# separate method to run server in a separate process
def run():
    dashboard_server.scripts.config.serve_locally = True
    dashboard_server.run_server(port=8050, debug=False, processes=4, threaded=False)


# run the server
if __name__ == '__main__':
    interface.enable_fetching()
    server_process = multiprocessing.Process(target=run, name='dash')
    server_process.start()
