"""
StockSage Portfolio Routes
Manages user's stock portfolio - add, remove, and view positions with P&L.
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from backend.app import db
from backend.models import PortfolioItem
from backend.services.stock_service import StockService

portfolio_bp = Blueprint("portfolio", __name__, url_prefix="/portfolio")
stock_service = StockService()


@portfolio_bp.route("/")
@login_required
def view():
    items = PortfolioItem.query.filter_by(user_id=current_user.id).all()
    enriched = []
    total_invested = 0
    total_current = 0

    for item in items:
        price_data = stock_service.get_current_price(item.ticker)
        current_price = price_data.get("price", item.buy_price)
        invested = item.shares * item.buy_price
        current_value = item.shares * current_price
        pnl = current_value - invested
        pnl_pct = ((current_value - invested) / invested * 100) if invested > 0 else 0

        total_invested += invested
        total_current += current_value

        enriched.append({
            "id": item.id,
            "ticker": item.ticker,
            "company_name": item.company_name or item.ticker,
            "shares": item.shares,
            "buy_price": item.buy_price,
            "current_price": current_price,
            "invested": invested,
            "current_value": current_value,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "buy_date": item.buy_date.strftime("%b %d, %Y"),
            "notes": item.notes or "",
        })

    total_pnl = total_current - total_invested
    total_pnl_pct = ((total_current - total_invested) / total_invested * 100) if total_invested > 0 else 0

    return render_template(
        "portfolio/portfolio.html",
        items=enriched,
        total_invested=total_invested,
        total_current=total_current,
        total_pnl=total_pnl,
        total_pnl_pct=total_pnl_pct,
    )


@portfolio_bp.route("/add", methods=["POST"])
@login_required
def add():
    ticker = request.form.get("ticker", "").strip().upper()
    shares = request.form.get("shares", "0")
    buy_price = request.form.get("buy_price", "0")
    notes = request.form.get("notes", "").strip()
    company_name = request.form.get("company_name", "").strip()

    try:
        shares = float(shares)
        buy_price = float(buy_price)
        if shares <= 0 or buy_price <= 0:
            raise ValueError
    except ValueError:
        flash("Please enter valid shares and price.", "danger")
        return redirect(url_for("portfolio.view"))

    if not ticker:
        flash("Ticker symbol is required.", "danger")
        return redirect(url_for("portfolio.view"))

    item = PortfolioItem(
        user_id=current_user.id,
        ticker=ticker,
        company_name=company_name,
        shares=shares,
        buy_price=buy_price,
        notes=notes,
    )
    db.session.add(item)
    db.session.commit()
    flash(f"✅ {ticker} added to your portfolio!", "success")
    return redirect(url_for("portfolio.view"))


@portfolio_bp.route("/remove/<int:item_id>", methods=["POST"])
@login_required
def remove(item_id):
    item = PortfolioItem.query.filter_by(id=item_id, user_id=current_user.id).first()
    if not item:
        flash("Position not found.", "danger")
        return redirect(url_for("portfolio.view"))
    ticker = item.ticker
    db.session.delete(item)
    db.session.commit()
    flash(f"Removed {ticker} from your portfolio.", "info")
    return redirect(url_for("portfolio.view"))


@portfolio_bp.route("/api/summary")
@login_required
def api_summary():
    """JSON summary for dashboard widget."""
    items = PortfolioItem.query.filter_by(user_id=current_user.id).all()
    total_invested = sum(i.shares * i.buy_price for i in items)
    return jsonify({
        "count": len(items),
        "total_invested": round(total_invested, 2),
        "tickers": [i.ticker for i in items],
    })
