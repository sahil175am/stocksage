"""
StockSage Admin Dashboard
Shows platform-wide stats. Only accessible by admin users (is_admin=True).
"""

from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from backend.app import db
from backend.models import User, PortfolioItem, WatchlistItem, PriceAlert

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Admin access required.", "danger")
            return redirect(url_for("dashboard.home"))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    total_portfolios = PortfolioItem.query.count()
    total_watchlists = WatchlistItem.query.count()
    total_alerts = PriceAlert.query.count()
    triggered_alerts = PriceAlert.query.filter_by(is_triggered=True).count()

    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()

    # Most tracked tickers
    from sqlalchemy import func
    top_tickers_portfolio = db.session.query(
        PortfolioItem.ticker, func.count(PortfolioItem.ticker).label("cnt")
    ).group_by(PortfolioItem.ticker).order_by(func.count(PortfolioItem.ticker).desc()).limit(10).all()

    top_tickers_watchlist = db.session.query(
        WatchlistItem.ticker, func.count(WatchlistItem.ticker).label("cnt")
    ).group_by(WatchlistItem.ticker).order_by(func.count(WatchlistItem.ticker).desc()).limit(10).all()

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_portfolios=total_portfolios,
        total_watchlists=total_watchlists,
        total_alerts=total_alerts,
        triggered_alerts=triggered_alerts,
        recent_users=recent_users,
        top_tickers_portfolio=top_tickers_portfolio,
        top_tickers_watchlist=top_tickers_watchlist,
    )
