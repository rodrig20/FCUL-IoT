from flask import Flask, request, jsonify
import pandas as pd
import logging
import signal
import sys
from ml import perform_clustering


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


@app.route("/classify", methods=["POST"])
def classify():
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "Invalid JSON"}), 400

    feat1_name = payload.get("feat1_name")
    feat2_name = payload.get("feat2_name")
    feat1_list = payload.get("feat1_list")
    feat2_list = payload.get("feat2_list")

    # Validate inputs
    if not feat1_name or not feat2_name:
        return jsonify({"error": "Missing feat1_name or feat2_name in JSON body"}), 400
    if not feat1_list or not feat2_list:
        return jsonify({"error": "Missing feat1_list or feat2_list in JSON body"}), 400
    if len(feat1_list) != len(feat2_list):
        return jsonify({"error": "feat1_list and feat2_list must have the same length"}), 400

    # Reconstruct data in the format expected by perform_clustering
    data = []
    for i in range(len(feat1_list)):
        data.append({
            feat1_name: feat1_list[i],
            feat2_name: feat2_list[i]
        })

    try:
        clustering_result = perform_clustering(data)
        return jsonify(clustering_result)

    except Exception as e:
        __app_logger.error(f"An error occurred during clustering: {e}")
        return jsonify({"error": f"An error occurred during clustering: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
