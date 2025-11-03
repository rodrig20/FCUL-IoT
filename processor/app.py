from flask import Flask, jsonify
from database import Database
import logging
import signal
import sys


def handle_exit(signum, frame):
    __app_logger.info(f"Shutting down")
    sys.exit(0)


app = Flask(__name__)
__app_logger = logging.getLogger("processor-server")
__app_logger.info("All routes are created")

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)


@app.route("/get_headers", methods=["GET"])
def get_headers():
    headers = Database.get_headers()
    return jsonify(headers)


@app.route("/get_all_info", methods=["GET"])
def get_all_info():
    data = Database.get_all_info()
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)
