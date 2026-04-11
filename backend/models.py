"""
StockSage Database Models
Defines User, Portfolio, Watchlist, PriceAlert models with privacy-focused design.
"""

from datetime import datetime
from flask_login import UserMixin
from backend.app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    theme = db.Column(db.String(10), default="dark")
    is_admin = db.Column(db.Boolean, default=False)

    portfolio_items = db.relationship("PortfolioItem", backref="owner", lazy=True, cascade="all, delete-orphan")
    watchlist_items = db.relationship("WatchlistItem", backref="owner", lazy=True, cascade="all, delete-orphan")
    price_alerts = db.relationship("PriceAlert", backref="owner", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"


class PortfolioItem(db.Model):
    __tablename__ = "portfolio_items"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    ticker = db.Column(db.String(10), nullable=False)
    company_name = db.Column(db.String(100))
    shares = db.Column(db.Float, nullable=False)
    buy_price = db.Column(db.Float, nullable=False)
    buy_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.String(300))

    def __repr__(self):
        return f"<Portfolio {self.ticker} x{self.shares}>"


class WatchlistItem(db.Model):
    __tablename__ = "watchlist_items"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    ticker = db.Column(db.String(10), nullable=False)
    company_name = db.Column(db.String(100))
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Watchlist {self.ticker}>"


class PriceAlert(db.Model):
    __tablename__ = "price_alerts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    ticker = db.Column(db.String(10), nullable=False)
    company_name = db.Column(db.String(100))
    alert_type = db.Column(db.String(10), nullable=False)   # "above" or "below"
    target_price = db.Column(db.Float, nullable=False)
    is_triggered = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    triggered_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<Alert {self.ticker} {self.alert_type} ${self.target_price}>"
