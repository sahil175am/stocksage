"""
StockSage Compare Route
Side-by-side comparison of two ticker symbols.
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from backend.services.stock_service import StockService

compare_bp = Blueprint("compare", __name__, url_prefix="/compare")
stock_service = StockService()


@compare_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    ticker1 = ticker2 = None
    data1 = data2 = None
    error1 = error2 = None

    if request.method == "POST":
        ticker1 = request.form.get("ticker1", "").strip().upper()
        ticker2 = request.form.get("ticker2", "").strip().upper()
    elif request.args.get("t1"):
        ticker1 = request.args.get("t1", "").strip().upper()
        ticker2 = request.args.get("t2", "").strip().upper()

    if ticker1:
        r1 = stock_service.get_full_analysis(ticker1)
        if r1.get("error"):
            error1 = r1["error"]
        else:
            data1 = r1

    if ticker2:
        r2 = stock_service.get_full_analysis(ticker2)
        if r2.get("error"):
            error2 = r2["error"]
        else:
            data2 = r2

    return render_template(
        "compare/compare.html",
        ticker1=ticker1, ticker2=ticker2,
        data1=data1, data2=data2,
        error1=error1, error2=error2,
    )


@compare_bp.route("/api/chart")
@login_required
def compare_chart():
    """Returns chart data for both tickers in one call."""
    t1 = request.args.get("t1", "").upper()
    t2 = request.args.get("t2", "").upper()
    result = {}
    if t1:
        result["t1"] = stock_service.get_chart_data(t1)
    if t2:
        result["t2"] = stock_service.get_chart_data(t2)
    return jsonify(result)
