"""
StockSage Dashboard Routes
Main dashboard - shows market overview and user's watchlist.
"""

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from backend.models import PortfolioItem, WatchlistItem

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def home():
    watchlist = WatchlistItem.query.filter_by(user_id=current_user.id).all()
    portfolio_count = PortfolioItem.query.filter_by(user_id=current_user.id).count()
    return render_template(
        "dashboard/home.html",
        watchlist=watchlist,
        portfolio_count=portfolio_count,
    )
