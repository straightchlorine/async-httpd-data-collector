"""
Example dashboard application using DatabaseInterface class.

Author: Piotr Krzysztof Lis - github.com/straightchlorine
"""

import asyncio
import json
import multiprocessing

from dash import Dash, Input, Output, callback, dcc, html
import pandas as pd

# adding current directory to the path
from pathlib import Path
import sys

path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))

from reads.interface import DatabaseInterface
from test.dev_server import DevelopmentServer

# start the test server and specifiy the IP and port
DevelopmentServer().run_test_server()
test_dev_ip = "localhost"
test_dev_port = 5000

# load the secrets
with open("secrets/secrets.json", "r") as f:
    secrets = json.load(f)

# list of sensors and the parameters they measure
sensors = {
    "bmp180": ["altitude", "pressure", "temperature", "seaLevelPressure"],
    "mq135": ["aceton", "alcohol", "co", "co2", "nh4", "toulen"],
}

# create the DatabaseInterface object
interface = DatabaseInterface(
    secrets["host"],
    secrets["port"],
    secrets["token"],
    secrets["organization"],
    secrets["bucket"],
    sensors,
    test_dev_ip,
    test_dev_port,
    secrets["handle"],
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
            html.H4("NodeMCU Sensor Data"),
            html.Div(id="live-update-text"),
            dcc.Interval(id="interval-component", interval=1000, n_intervals=0),
        ]
    )
)


# live updating the text
@callback(
    Output("live-update-text", "children"), Input("interval-component", "n_intervals")
)
def update_metrics(n):
    measurement_dataframe: pd.DataFrame = asyncio.run(update_data())

    if not measurement_dataframe.empty:
        time = measurement_dataframe["time"].iloc[-1]
        altitude = measurement_dataframe["altitude"].iloc[-1]
        pressure = measurement_dataframe["pressure"].iloc[-1]
        temperature = measurement_dataframe["temperature"].iloc[-1]
        sea_level_pressure = measurement_dataframe["seaLevelPressure"].iloc[-1]
        aceton = measurement_dataframe["aceton"].iloc[-1]
        alcohol = measurement_dataframe["alcohol"].iloc[-1]
        co = measurement_dataframe["co"].iloc[-1]
        co2 = measurement_dataframe["co2"].iloc[-1]
        nh4 = measurement_dataframe["nh4"].iloc[-1]
        toulen = measurement_dataframe["toulen"].iloc[-1]
        style = {"padding": "5px", "fontSize": "16px"}
        return [
            html.Span("Time: {0}".format(time), style=style),
            html.Span("Altitude: {0:.2f}".format(altitude), style=style),
            html.Span("Pressure: {0:.2f}".format(pressure), style=style),
            html.Span("Temperature: {0:.2f}".format(temperature), style=style),
            html.Span(
                "Sea Level Pressure: {0:.2f}".format(sea_level_pressure), style=style
            ),
            html.Span("Aceton: {0:.2f}".format(aceton), style=style),
            html.Span("Alcohol: {0:.2f}".format(alcohol), style=style),
            html.Span("CO: {0:.2f}".format(co), style=style),
            html.Span("CO2: {0:.2f}".format(co2), style=style),
            html.Span("NH4: {0:.2f}".format(nh4), style=style),
            html.Span("Toulen: {0:.2f}".format(toulen), style=style),
        ]
    else:
        return [html.Span("probing data...")]


def run():
    dashboard_server.scripts.config.serve_locally = True
    dashboard_server.run_server(port=8050, debug=False, processes=4, threaded=False)


if __name__ == "__main__":
    server_process = multiprocessing.Process(target=run, name="dash")
    server_process.start()
    interface.enable_fetching()
