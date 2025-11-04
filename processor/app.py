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


# ===========
#  Routes
# ===========
@app.route("/get_headers", methods=["GET"])
def get_headers():
    """Route that provides headers from the database

    Returns:
        Response: JSON response containing headers from the database
    """
    headers = Database.get_headers()
    return jsonify(headers)


@app.route("/get_all_info", methods=["GET"])
def get_all_info():
    """Route that provides all information from the database

    Returns:
        Response: JSON response containing all info from the database
    """
    data = Database.get_all_info()
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)
