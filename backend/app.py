"""
StockSage App Factory
Creates and configures the Flask application instance.
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()


def create_app():
    app = Flask(
        __name__,
        template_folder="../frontend/templates",
        static_folder="../frontend/static",
    )

    # Configuration
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///stocksage.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["WTF_CSRF_ENABLED"] = True

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access StockSage."
    login_manager.login_message_category = "info"

    # Register blueprints
    from backend.routes.auth import auth_bp
    from backend.routes.dashboard import dashboard_bp
    from backend.routes.stock import stock_bp
    from backend.routes.portfolio import portfolio_bp
    from backend.routes.news import news_bp
    from backend.routes.profile import profile_bp
    from backend.routes.compare import compare_bp
    from backend.routes.admin import admin_bp
    from backend.routes.screener import screener_bp
    from backend.routes.heatmap import heatmap_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(stock_bp)
    app.register_blueprint(portfolio_bp)
    app.register_blueprint(news_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(compare_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(screener_bp)
    app.register_blueprint(heatmap_bp)

    # Custom Jinja2 filters
    @app.template_filter("format_large_num")
    def format_large_num(num):
        if not num:
            return "—"
        try:
            num = float(num)
            if num >= 1e12:
                return f"${num/1e12:.2f}T"
            if num >= 1e9:
                return f"${num/1e9:.2f}B"
            if num >= 1e6:
                return f"${num/1e6:.2f}M"
            return f"${num:,.0f}"
        except Exception:
            return "—"

    # Create DB tables
    with app.app_context():
        db.create_all()

    return app
