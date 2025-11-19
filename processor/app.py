from flask import Flask, jsonify
from database import Database
import logging
import signal
import sys


def handle_exit(signum, frame):
    """Handles exit signals for graceful shutdown

    This function is called when the application receives a SIGINT or SIGTERM
    signal, allowing for graceful shutdown of the processor server.

    Args:
        signum: Signal number
        frame: Current stack frame
    """
    __app_logger.info(f"Shutting down...")
    sys.exit(0)


# Initialize Flask application
app = Flask(__name__)

# Create logger for the processor server
__app_logger = logging.getLogger("processor-server")
__app_logger.info("All routes are created")

# Register signal handlers for graceful shutdown when running in Docker
signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)


@app.route("/get_headers", methods=["GET"])
def get_headers():
    headers = Database.get_headers()
    return jsonify(headers)


@app.route("/get_user_info/<user_id>", methods=["GET"])
def get_user_info(user_id):
    """Route that provides all information for a specific user from the database

    Args:
        user_id: The ID of the user to retrieve information for

    Returns:
        Response: JSON response containing all info for the specified user from the database
    """
    data = Database.get_info_by_username(user_id)
    return jsonify(data)


@app.route("/get_stations", methods=["GET"])
def get_stations():
    """Route that provides all charging stations with their ID, latitude and longitude

    Returns:
        Response: JSON response containing all charging stations
    """
    stations = Database.get_stations()
    return jsonify(stations)


@app.route("/get_stations_for_user/<user_id>", methods=["GET"])
def get_stations_for_user(user_id):
    """Route that provides all charging stations with visit status for the user

    Args:
        user_id: The ID of the user to retrieve stations for

    Returns:
        Response: JSON response containing all stations and visit status
    """
    stations = Database.get_stations_for_user(user_id)
    return jsonify(stations)


if __name__ == "__main__":
    app.run(debug=True)
