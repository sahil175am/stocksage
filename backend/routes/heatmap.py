"""
StockSage Sector Heatmap Route
Shows performance of major sectors using ETFs as proxies (free via yfinance).
"""
from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from backend.services.stock_service import StockService

heatmap_bp = Blueprint("heatmap", __name__, url_prefix="/heatmap")
stock_service = StockService()

# Sector ETF proxies (all free via yfinance)
SECTOR_ETFS = {
    "Technology":        {"etf": "XLK",  "tickers": ["AAPL","MSFT","NVDA","AMD","INTC","CRM","ADBE","ORCL"]},
    "Healthcare":        {"etf": "XLV",  "tickers": ["JNJ","PFE","UNH","ABBV","LLY","BMY","AMGN","GILD"]},
    "Financials":        {"etf": "XLF",  "tickers": ["JPM","BAC","GS","MS","WFC","V","MA","AXP"]},
    "Energy":            {"etf": "XLE",  "tickers": ["XOM","CVX","COP","SLB","OXY","MPC","VLO"]},
    "Consumer Discr.":   {"etf": "XLY",  "tickers": ["AMZN","TSLA","HD","MCD","NKE","SBUX"]},
    "Consumer Staples":  {"etf": "XLP",  "tickers": ["WMT","PG","KO","PEP","COST","TGT"]},
    "Industrials":       {"etf": "XLI",  "tickers": ["GE","CAT","BA","HON","UPS","RTX"]},
    "Materials":         {"etf": "XLB",  "tickers": ["LIN","APD","SHW","FCX","NEM","DOW"]},
    "Real Estate":       {"etf": "XLRE", "tickers": ["AMT","PLD","CCI","EQIX","PSA","SPG"]},
    "Utilities":         {"etf": "XLU",  "tickers": ["NEE","DUK","SO","D","AEP","EXC"]},
    "Comm. Services":    {"etf": "XLC",  "tickers": ["GOOGL","META","NFLX","CMCSA","DIS","T"]},
    "Crypto":            {"etf": "BITO", "tickers": ["BTC-USD","ETH-USD","COIN","MSTR","MARA"]},
}


@heatmap_bp.route("/")
@login_required
def index():
    return render_template("heatmap/heatmap.html", sectors=list(SECTOR_ETFS.keys()))


@heatmap_bp.route("/api/data")
@login_required
def heatmap_data():
    """Returns live sector ETF performance data for the heatmap."""
    results = []
    for sector, info in SECTOR_ETFS.items():
        data = stock_service.get_full_analysis(info["etf"])
        if data.get("error"):
            results.append({"sector": sector, "etf": info["etf"], "change_pct": 0, "price": 0, "error": True})
        else:
            results.append({
                "sector": sector,
                "etf": info["etf"],
                "price": data.get("current_price", 0),
                "change_pct": data.get("change_pct", 0),
                "rsi": data.get("rsi"),
                "volume": data.get("volume", 0),
            })
    return jsonify(results)


@heatmap_bp.route("/api/sector/<sector_name>")
@login_required
def sector_detail(sector_name):
    """Returns individual stock data for a sector's tickers."""
    info = SECTOR_ETFS.get(sector_name)
    if not info:
        return jsonify({"error": "Sector not found"}), 404
    results = []
    for ticker in info["tickers"]:
        data = stock_service.get_full_analysis(ticker)
        if not data.get("error"):
            results.append({
                "ticker": ticker,
                "company_name": data.get("company_name", ticker),
                "price": data.get("current_price", 0),
                "change_pct": data.get("change_pct", 0),
                "rsi": data.get("rsi"),
            })
    return jsonify(results)
