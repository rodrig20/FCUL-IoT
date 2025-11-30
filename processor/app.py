from flask import Flask, jsonify, request
import requests
from database import Database
import datetime
import logging
import signal
import sys


def handle_exit(signum, frame):
    """Called when receive a exit signal"""
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


@app.route("/get_users", methods=["GET"])
def get_users():
    """Route that provides a list of all unique users

    Returns:
        Response: JSON response containing all users
    """
    users = Database.get_all_users()
    return jsonify(users)


@app.route("/get_all_users_info", methods=["GET"])
def get_all_users_info():
    """Route that provides information for all users combined

    Returns:
        Response: JSON response containing all information for all users
    """
    data = Database.get_all_users_info()
    return jsonify(data)


@app.route("/classify", methods=["POST"])
def classify():
    """
    Receives two feature names, gets the data from the database,
    and calls the ML service to perform clustering.
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Invalid JSON"}), 400

    feat1 = json_data.get("feat1")
    feat2 = json_data.get("feat2")

    if not feat1 or not feat2:
        return jsonify({"error": "Missing feat1 or feat2 in JSON body"}), 400

    # Get data from the database
    db_data = Database.get_values_for_features(feat1, feat2)
    if "error" in db_data:
        return jsonify(db_data), 400

    data = db_data.get("data")
    if not data:
        return jsonify({"error": "No data found for the given features"}), 404

    # Prepare data for the ML service
    feat1_list = [d[feat1] for d in data]
    feat2_list = [d[feat2] for d in data]

    # Convert datetime objects to strings
    feat1_list = [val.isoformat() if isinstance(val, datetime.datetime) else val for val in feat1_list]
    feat2_list = [val.isoformat() if isinstance(val, datetime.datetime) else val for val in feat2_list]

    ml_payload = {
        "feat1_name": feat1,
        "feat2_name": feat2,
        "feat1_list": feat1_list,
        "feat2_list": feat2_list
    }

    try:
        ml_url = "http://ml:5000/classify"
        response = requests.post(ml_url, json=ml_payload)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        __app_logger.error(f"Could not connect to ml service: {e}")
        return jsonify({"error": "Could not connect to ml service"}), 500

if __name__ == "__main__":
    app.run(debug=True)
