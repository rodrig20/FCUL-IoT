from processor_requester import ProcessorRequester
from flask import Flask, render_template, jsonify, request
import logging
import signal
import sys
import os


def handle_exit(signum, frame):
    """Called when receive a exit signal"""
    __app_logger.info(f"Shutting down...")
    sys.exit(0)


app = Flask(__name__)

# Create logger
__app_logger = logging.getLogger("dashboard-server")
__app_logger.setLevel(logging.INFO)

# Exit Program on docker SIGTERM
signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)


# ===========
#  Routes
# ===========
@app.route("/", methods=["GET"])
def index() -> str:
    """Main dashboard page

    Returns:
        str: html page (index.html)
    """
    headers = ProcessorRequester.get_headers()
    # Get list of users for the filter
    users = ProcessorRequester.get_all_users()
    return render_template("index.html", headers=headers, users=users)


@app.route("/get_info", methods=["GET"])
def info():
    """Route that gives all info from processor for a specific user or all users

    Returns:
        Response: all info given by processor api for the specified user or all users
    """
    username = request.args.get("username")
    if not username or username == "ALL_USERS":
        # If no username provided, return data for all users
        data = ProcessorRequester.get_all_users_info()
        return jsonify(data)
    else:
        # Get data for specific user
        data = ProcessorRequester.get_user_info(username)
        return jsonify(data)


@app.route("/get_stations", methods=["GET"])
def get_stations():
    """Route that provides all charging stations with their ID, latitude and longitude

    Returns:
        Response: JSON response containing all charging stations
    """
    username = request.args.get("username")
    if not username or username == "ALL_USERS":
        data = ProcessorRequester.get_stations()
        if data:
            stations = [
                {
                    "station_id": station.get("station_id"),
                    "latitude": station.get("latitude"),
                    "longitude": station.get("longitude"),
                    "visited": False,
                }
                for station in data
            ]
            return jsonify(stations)
    else:
        data = ProcessorRequester.get_stations_for_user(username)
        return jsonify(data)


@app.route("/get_users", methods=["GET"])
def get_users():
    """Route that provides a list of all users

    Returns:
        Response: JSON response containing all users
    """
    users = ProcessorRequester.get_all_users()
    return jsonify({"users": users})


@app.route("/classify", methods=['POST'])
def classify():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Invalid JSON"}), 400

    feat1 = json_data.get("feat1")
    feat2 = json_data.get("feat2")

    if not feat1 or not feat2:
        return jsonify({"error": "Missing feat1 or feat2 in JSON body"}), 400

    data = ProcessorRequester.classify(feat1, feat2)

    if data:
        return jsonify(data)
    else:
        return jsonify({"error": "Failed to get classification from processor"}), 500


__app_logger.info("All routes are created")

if __name__ == "__main__":
    app.run(debug=True)
