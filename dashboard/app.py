from processor_requester import ProcessorRequester
from flask import Flask, render_template, jsonify
import logging
import signal
import sys


def handle_exit(signum, frame):
    __app_logger.info(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)


app = Flask(__name__)
__app_logger = logging.getLogger("dashboard-server")
__app_logger.setLevel(logging.INFO)

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)


@app.route("/", methods=["GET"])
def index():
    headers = ProcessorRequester.get_headers() or ["OLA"]
    return render_template(
        "index.html",
        headers=headers,
    )


@app.route("/get_info", methods=["GET"])
def info():
    data = ProcessorRequester.get_all_info()
    return jsonify(data)


__app_logger.info("All routes are created")


if __name__ == "__main__":
    app.run(debug=True)
