"""
Development server for testing purposes, meant to simulate device sending
readings.

Author: Piotr Krzysztof Lis - github.com/straightchlorine
"""

from flask import Flask, jsonify

srv: Flask  # The Flask server instance

# Example JSON response from nodemcu
example_json = {
    'nodemcu': {
        'bmp180': {
            'altitude': '149.56',
            'pressure': '998.42',
            'seaLevelPressure': '1016.34',
            'temperature': '26.00',
        },
        'mq135': {
            'aceton': '2.57',
            'alcohol': '6.62',
            'co': '28.88',
            'co2': '412.10',
            'nh4': '15.12',
            'toulen': '3.14',
        },
    }
}

srv = Flask(__name__)


@srv.route('/circumstances', methods=['GET'])
def get_circumstances():
    return jsonify(example_json)
