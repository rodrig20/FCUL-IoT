from processor_requester import ProcessorRequester
from flask import Flask, render_template, jsonify, session, redirect, url_for
import logging
import signal
import sys
import os


def handle_exit(signum, frame):
    """Called when receive a exit signal"""
    __app_logger.info(f"Shutting down...")
    sys.exit(0)


app = Flask(__name__)
# Set a secret key for sessions - in production, use a more secure random key
app.secret_key = os.getenv("SERVER_KEY", "your-secret-key-here-change-in-production")

# Create logger
__app_logger = logging.getLogger("dashboard-server")
__app_logger.setLevel(logging.INFO)


def login_required(f):
    """Decorator to require login for certain routes"""

    def decorated_function(*args, **kwargs):
        if "logged_in" not in session or not session["logged_in"]:
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)

    decorated_function.__name__ = f.__name__  # Fix for Flask endpoint naming
    return decorated_function


# Exit Program on docker SIGTERM
signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)


# ===========
#  Routes
# ===========
@app.route("/", methods=["GET"])
@login_required
def index() -> str:
    """Main dashboard page

    Returns:
        str: html page (index.html)
    """
    headers = ProcessorRequester.get_headers()
    username = session.get("username", "User")
    return render_template("index.html", headers=headers, username=username)


@app.route("/get_info", methods=["GET"])
@login_required
def info():
    """Route that gives all info from processor for the logged-in user

    Returns:
        Response: all info given by processor api for the user
    """
    username = session.get("username")
    if not username:
        return jsonify({"success": False, "message": "User not logged in"}), 401

    data = ProcessorRequester.get_user_info(username)
    return jsonify(data)


@app.route("/get_stations", methods=["GET"])
@login_required
def get_stations():
    """Route that provides all charging stations with their ID, latitude and longitude

    Returns:
        Response: JSON response containing all charging stations
    """
    username = session.get("username")
    if not username:
        return jsonify({"success": False, "message": "User not logged in"}), 401

    data = ProcessorRequester.get_stations_for_user(username)
    return jsonify(data)


@app.route("/login", methods=["GET"])
def login_page() -> str:
    """Login page

    Returns:
        str: html page (login.html)
    """
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    """Handle login

    Returns:
        Response: JSON response with login result
    """
    from flask import request

    data = request.get_json()

    # In a real implementation, you would validate credentials against a database
    # For now, we'll just accept any non-empty credentials as valid
    username = data.get("username", "") if data else ""
    password = data.get("password", "") if data else ""

    if username and password:
        if username == "User_1" and password == "12345":
            session["logged_in"] = True
            session["username"] = username
            return jsonify({"success": True, "message": "Login successful"})
    return jsonify({"success": False, "message": "Invalid credentials"}), 401


@app.route("/logout", methods=["POST"])
def logout():
    """Handle logout by clearing the session

    Returns:
        Response: JSON response with logout result
    """
    session.pop("logged_in", None)
    session.pop("username", None)
    return jsonify({"success": True, "message": "Logout successful"})


__app_logger.info("All routes are created")

if __name__ == "__main__":
    app.run(debug=True)
