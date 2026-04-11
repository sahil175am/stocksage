"""
StockSage Profile & Settings Routes
- View/edit profile (username, password, theme)
- Price alerts management
- Portfolio CSV export
"""

import csv
import io
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, Response
from flask_login import login_required, current_user
from backend.app import db, bcrypt
from backend.models import User, PortfolioItem, PriceAlert
from backend.services.stock_service import StockService
from backend.services.email_service import EmailService

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")
stock_service = StockService()
email_service = EmailService()


@profile_bp.route("/")
@login_required
def settings():
    alerts = PriceAlert.query.filter_by(user_id=current_user.id).order_by(PriceAlert.created_at.desc()).all()
    portfolio = PortfolioItem.query.filter_by(user_id=current_user.id).all()
    return render_template("profile/settings.html", alerts=alerts, portfolio_count=len(portfolio))


@profile_bp.route("/update", methods=["POST"])
@login_required
def update():
    action = request.form.get("action")

    if action == "update_username":
        new_username = request.form.get("username", "").strip()
        if len(new_username) < 3 or len(new_username) > 30:
            flash("Username must be 3–30 characters.", "danger")
        elif User.query.filter(User.username == new_username, User.id != current_user.id).first():
            flash("That username is already taken.", "danger")
        else:
            current_user.username = new_username
            db.session.commit()
            flash("Username updated successfully.", "success")

    elif action == "update_password":
        current_pw = request.form.get("current_password", "")
        new_pw = request.form.get("new_password", "")
        confirm_pw = request.form.get("confirm_password", "")
        if not bcrypt.check_password_hash(current_user.password_hash, current_pw):
            flash("Current password is incorrect.", "danger")
        elif len(new_pw) < 8:
            flash("New password must be at least 8 characters.", "danger")
        elif new_pw != confirm_pw:
            flash("New passwords do not match.", "danger")
        else:
            current_user.password_hash = bcrypt.generate_password_hash(new_pw).decode("utf-8")
            db.session.commit()
            flash("Password changed successfully.", "success")

    elif action == "update_theme":
        theme = request.form.get("theme", "dark")
        if theme in ("dark", "light"):
            current_user.theme = theme
            db.session.commit()
            return jsonify({"ok": True, "theme": theme})

    return redirect(url_for("profile.settings"))


@profile_bp.route("/theme", methods=["POST"])
@login_required
def toggle_theme():
    """Quick toggle endpoint called from JS."""
    new_theme = "light" if current_user.theme == "dark" else "dark"
    current_user.theme = new_theme
    db.session.commit()
    return jsonify({"theme": new_theme})


# ── PRICE ALERTS ──

@profile_bp.route("/alerts/add", methods=["POST"])
@login_required
def add_alert():
    ticker = request.form.get("ticker", "").strip().upper()
    company_name = request.form.get("company_name", "").strip()
    alert_type = request.form.get("alert_type", "above")
    target_price = request.form.get("target_price", "0")

    try:
        target_price = float(target_price)
        if target_price <= 0:
            raise ValueError
    except ValueError:
        flash("Please enter a valid target price.", "danger")
        return redirect(url_for("profile.settings"))

    if not ticker:
        flash("Ticker symbol is required.", "danger")
        return redirect(url_for("profile.settings"))

    alert = PriceAlert(
        user_id=current_user.id,
        ticker=ticker,
        company_name=company_name,
        alert_type=alert_type,
        target_price=target_price,
    )
    db.session.add(alert)
    db.session.commit()
    flash(f"Alert set: notify when {ticker} goes {alert_type} ${target_price:.2f}", "success")
    return redirect(url_for("profile.settings"))


@profile_bp.route("/alerts/remove/<int:alert_id>", methods=["POST"])
@login_required
def remove_alert(alert_id):
    alert = PriceAlert.query.filter_by(id=alert_id, user_id=current_user.id).first()
    if not alert:
        return jsonify({"error": "Not found"}), 404
    db.session.delete(alert)
    db.session.commit()
    flash("Alert removed.", "info")
    return redirect(url_for("profile.settings"))


@profile_bp.route("/alerts/check")
@login_required
def check_alerts():
    """
    Check all active alerts for current user against live prices.
    Sends email if SMTP is configured, otherwise logs to console.
    Returns list of triggered alerts as JSON.
    """
    alerts = PriceAlert.query.filter_by(user_id=current_user.id, is_triggered=False).all()
    triggered = []
    for alert in alerts:
        price_data = stock_service.get_current_price(alert.ticker)
        current_price = price_data.get("price", 0)
        if current_price <= 0:
            continue
        hit = (alert.alert_type == "above" and current_price >= alert.target_price) or \
              (alert.alert_type == "below" and current_price <= alert.target_price)
        if hit:
            alert.is_triggered = True
            alert.triggered_at = datetime.utcnow()
            triggered.append({
                "ticker": alert.ticker,
                "type": alert.alert_type,
                "target": alert.target_price,
                "current": current_price,
            })
    db.session.commit()

    # Send email notification if any alerts fired
    if triggered:
        email_service.send_alert_email(
            to_email=current_user.email,
            username=current_user.username,
            triggered_alerts=triggered,
        )

    return jsonify({"triggered": triggered})


# ── PORTFOLIO CSV EXPORT ──

@profile_bp.route("/portfolio/export")
@login_required
def export_portfolio():
    """Download portfolio as CSV file."""
    items = PortfolioItem.query.filter_by(user_id=current_user.id).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Ticker", "Company", "Shares", "Buy Price ($)", "Current Price ($)",
                     "Invested ($)", "Current Value ($)", "P&L ($)", "Return (%)", "Buy Date", "Notes"])

    for item in items:
        price_data = stock_service.get_current_price(item.ticker)
        current_price = price_data.get("price", item.buy_price)
        invested = item.shares * item.buy_price
        current_value = item.shares * current_price
        pnl = current_value - invested
        pnl_pct = (pnl / invested * 100) if invested > 0 else 0

        writer.writerow([
            item.ticker,
            item.company_name or item.ticker,
            item.shares,
            f"{item.buy_price:.2f}",
            f"{current_price:.2f}",
            f"{invested:.2f}",
            f"{current_value:.2f}",
            f"{pnl:.2f}",
            f"{pnl_pct:.2f}",
            item.buy_date.strftime("%Y-%m-%d") if item.buy_date else "",
            item.notes or "",
        ])

    output.seek(0)
    filename = f"stocksage_portfolio_{datetime.utcnow().strftime('%Y%m%d')}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
