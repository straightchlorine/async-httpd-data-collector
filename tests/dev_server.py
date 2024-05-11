"""
Development server for testing purposes, meant to simulate device sending
readings.

Author: Piotr Krzysztof Lis - github.com/straightchlorine
"""

from flask import Flask, jsonify
from threading import Thread


class DevelopmentServer:
    """
    A simple development server for testing purposes.
    """

    srv: Flask  # The Flask server instance

    # Example JSON response from nodemcu
    example_json = {
        "nodemcu": {
            "bmp180": {
                "altitude": "149.56",
                "pressure": "998.42",
                "seaLevelPressure": "1016.34",
                "temperature": "26.00",
            },
            "mq135": {
                "aceton": "2.57",
                "alcohol": "6.62",
                "co": "28.88",
                "co2": "412.10",
                "nh4": "15.12",
                "toulen": "3.14",
            },
        }
    }

    def __init__(self):
        """
        Setting up the server as well as the handle.
        """
        self.srv = Flask(__name__)

        @self.srv.route("/circumstances", methods=["GET"])
        def get_circumstances():
            return jsonify(self.example_json)

    def run_test_server(self):
        """
        Start the server on a separate thread.
        """
        server_thread = Thread(target=self.srv.run)
        server_thread.start()


if __name__ == "__main__":
    dev_srv = DevelopmentServer()
    dev_srv.run_test_server()
