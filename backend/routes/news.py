"""
StockSage News Routes
Fetches real-time stock news via RSS feeds (free, no API key needed).
Falls back to NewsAPI if key is set.
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from backend.services.news_service import NewsService

news_bp = Blueprint("news", __name__, url_prefix="/news")
news_service = NewsService()


@news_bp.route("/")
@login_required
def index():
    ticker = request.args.get("ticker", "")
    articles = news_service.get_market_news()
    return render_template("news/news.html", articles=articles, ticker=ticker)


@news_bp.route("/api/<ticker>")
@login_required
def ticker_news(ticker):
    """JSON endpoint for ticker-specific news."""
    ticker = ticker.upper()
    articles = news_service.get_ticker_news(ticker)
    return jsonify(articles)


@news_bp.route("/api/market")
@login_required
def market_news():
    """JSON endpoint for general market news."""
    articles = news_service.get_market_news()
    return jsonify(articles)
