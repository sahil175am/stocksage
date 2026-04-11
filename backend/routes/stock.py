"""
StockSage Stock Routes
Handles ticker analysis, RSI/SMA charts, AI insights, and buy/sell/hold recommendations.
"""

import json
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from backend.services.stock_service import StockService
from backend.services.ai_service import AIService
from backend.models import WatchlistItem
from backend.app import db

stock_bp = Blueprint("stock", __name__, url_prefix="/stock")
stock_service = StockService()
ai_service = AIService()


@stock_bp.route("/analyze", methods=["GET", "POST"])
@login_required
def analyze():
    ticker = None
    data = None
    error = None

    if request.method == "POST":
        ticker = request.form.get("ticker", "").strip().upper()
    elif request.args.get("ticker"):
        ticker = request.args.get("ticker", "").strip().upper()

    if ticker:
        result = stock_service.get_full_analysis(ticker)
        if result.get("error"):
            error = result["error"]
        else:
            data = result

    return render_template("stock/analyze.html", ticker=ticker, data=data, error=error)


@stock_bp.route("/api/chart/<ticker>")
@login_required
def chart_data(ticker):
    """Returns JSON data for RSI and SMA charts (20-day)."""
    ticker = ticker.upper()
    result = stock_service.get_chart_data(ticker)
    return jsonify(result)


@stock_bp.route("/api/signal/<ticker>")
@login_required
def get_signal(ticker):
    """Returns buy/sell/hold signal with reasoning."""
    ticker = ticker.upper()
    analysis = stock_service.get_full_analysis(ticker)
    if analysis.get("error"):
        return jsonify({"error": analysis["error"]})
    signal = stock_service.generate_signal(analysis)
    return jsonify(signal)


@stock_bp.route("/api/ai-insight/<ticker>")
@login_required
def ai_insight(ticker):
    """Returns humanized AI insight from Anthropic API."""
    ticker = ticker.upper()
    analysis = stock_service.get_full_analysis(ticker)
    if analysis.get("error"):
        return jsonify({"error": analysis["error"]})
    insight = ai_service.get_insight(ticker, analysis)
    return jsonify({"insight": insight})


@stock_bp.route("/watchlist/add", methods=["POST"])
@login_required
def add_to_watchlist():
    ticker = request.form.get("ticker", "").strip().upper()
    company_name = request.form.get("company_name", "")
    if not ticker:
        return jsonify({"error": "No ticker provided"}), 400

    existing = WatchlistItem.query.filter_by(user_id=current_user.id, ticker=ticker).first()
    if existing:
        return jsonify({"message": f"{ticker} is already in your watchlist."})

    item = WatchlistItem(user_id=current_user.id, ticker=ticker, company_name=company_name)
    db.session.add(item)
    db.session.commit()
    return jsonify({"message": f"{ticker} added to your watchlist!"})


@stock_bp.route("/watchlist/remove/<int:item_id>", methods=["POST"])
@login_required
def remove_from_watchlist(item_id):
    item = WatchlistItem.query.filter_by(id=item_id, user_id=current_user.id).first()
    if not item:
        return jsonify({"error": "Item not found"}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Removed from watchlist."})


@stock_bp.route("/api/ohlc/<ticker>")
@login_required
def ohlc_data(ticker):
    """Returns OHLC candlestick data for the last 30 trading days."""
    ticker = ticker.upper()
    days = int(request.args.get("days", 30))
    result = stock_service.get_ohlc_data(ticker, days)
    return jsonify(result)
