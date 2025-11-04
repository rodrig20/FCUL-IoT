from processor_requester import ProcessorRequester
from flask import Flask, render_template, jsonify, Response
import logging
import signal
import sys


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
    headers = ProcessorRequester.get_headers() or ["OLA"]
    return render_template(
        "index.html",
        headers=headers,
    )


@app.route("/get_info", methods=["GET"])
def info() -> Response:
    """Route that gives all info from processor

    Returns:
        Response: all info given by processor api
    """
    data = ProcessorRequester.get_all_info()
    return jsonify(data)


__app_logger.info("All routes are created")

if __name__ == "__main__":
    app.run(debug=True)
