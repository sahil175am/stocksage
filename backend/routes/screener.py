"""
StockSage Stock Screener Route
Filter stocks by RSI range, price range, SMA position, and daily change.
Uses a curated default list of ~100 popular tickers.
Users can also provide their own comma-separated ticker list.
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from backend.services.stock_service import StockService

screener_bp = Blueprint("screener", __name__, url_prefix="/screener")
stock_service = StockService()

# Default universe of popular, liquid tickers across sectors
# Default universe — top 40 most liquid tickers (keeps screener fast and avoids rate limits)
# Users can add their own tickers in the custom field for broader searches
DEFAULT_TICKERS = [
    # Mega-cap tech
    "AAPL","MSFT","NVDA","GOOGL","META","AMZN","TSLA","AMD","NFLX","INTC",
    # Finance
    "JPM","BAC","GS","V","MA","WFC","BRK-B","AXP",
    # Healthcare
    "JNJ","PFE","UNH","LLY","ABBV","AMGN",
    # Energy
    "XOM","CVX","COP","SLB",
    # Consumer
    "WMT","HD","MCD","KO","PEP","NKE","COST",
    # ETFs
    "SPY","QQQ","DIA","GLD",
    # Crypto
    "BTC-USD","COIN",
]


@screener_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    results = []
    filters = {}
    custom_tickers = ""
    ran = False

    if request.method == "POST":
        ran = True
        # Parse filters
        def safe_float(val):
            try:
                v = float(val)
                return v if v != "" else None
            except (TypeError, ValueError):
                return None

        filters = {
            "rsi_min":        safe_float(request.form.get("rsi_min")),
            "rsi_max":        safe_float(request.form.get("rsi_max")),
            "price_min":      safe_float(request.form.get("price_min")),
            "price_max":      safe_float(request.form.get("price_max")),
            "change_pct_min": safe_float(request.form.get("change_pct_min")),
            "change_pct_max": safe_float(request.form.get("change_pct_max")),
            "sma_position":   request.form.get("sma_position") or None,
            "signal":         request.form.get("signal_filter") or None,
        }

        # Ticker universe
        custom_tickers = request.form.get("custom_tickers", "").strip()
        if custom_tickers:
            tickers = [t.strip().upper() for t in custom_tickers.replace(",", " ").split() if t.strip()]
        else:
            tickers = DEFAULT_TICKERS

        # Run screener (service handles the heavy lifting)
        raw_results = stock_service.screen_stocks(tickers, filters)

        # Apply signal filter post-screening
        if filters.get("signal"):
            sig = filters["signal"].upper()
            raw_results = [r for r in raw_results if sig in r.get("signal", "")]

        results = raw_results

    return render_template(
        "screener/screener.html",
        results=results,
        filters=filters,
        custom_tickers=custom_tickers,
        ran=ran,
        default_count=len(DEFAULT_TICKERS),
    )
