"""
StockSage Keep-Alive Route
Provides a /ping endpoint that returns 200 OK.
Used by UptimeRobot (free) to ping the app every 5 minutes
and prevent Render's free tier from spinning down.
"""
from flask import Blueprint, jsonify
from datetime import datetime

keepalive_bp = Blueprint("keepalive", __name__)

@keepalive_bp.route("/ping")
def ping():
    return jsonify({"status": "alive", "time": datetime.utcnow().isoformat()}), 200
