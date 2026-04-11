# 📈 StockSage — AI-Powered Stock Market Intelligence Platform

<div align="center">

![StockSage](https://img.shields.io/badge/StockSage-v2.1-00ff88?style=for-the-badge&labelColor=0d1117)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![PWA](https://img.shields.io/badge/PWA-Ready-5A0FC8?style=for-the-badge)
![Free](https://img.shields.io/badge/Cost-100%25%20Free-00ff88?style=for-the-badge)

**Real-time market intelligence · AI insights · Portfolio tracker · Sector heatmap · Stock screener**

[Live Demo](#) · [Report Bug](../../issues) · [Request Feature](../../issues)

</div>

---

## 🚀 About

**StockSage** is a full-stack, production-grade stock market analysis platform. It gives investors and traders a Bloomberg-terminal-style interface to analyze any publicly traded stock using 100% free APIs — no subscriptions, no credit card.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 **Secure Auth** | Register/login with bcrypt passwords, session management |
| 📊 **Live Analysis** | Real-time price, volume, market cap, P/E for any ticker |
| 📉 **RSI & SMA Charts** | Interactive line + candlestick charts (last 20–30 days) |
| 🕯️ **Candlestick Charts** | OHLC candlestick view with SMA overlay — toggle on demand |
| 🤖 **AI Insights** | Claude-powered humanized analysis with rule-based fallback |
| 🎯 **Buy/Sell/Hold Signal** | Multi-factor: RSI + SMA + 52-week position scoring |
| 📰 **Market News** | Real-time news from Yahoo Finance & Google News RSS (no key) |
| 💼 **Portfolio Tracker** | Track positions with live P&L, return %, notes |
| ⇌ **Stock Comparison** | Side-by-side normalized chart + metrics table for 2 tickers |
| 🔍 **Stock Screener** | Filter 100+ stocks by RSI, price, change %, SMA position, signal |
| 🔥 **Sector Heatmap** | 12-sector live performance grid with drill-down stock view |
| 🔔 **Price Alerts** | Set above/below alerts, check manually, email notifications |
| ☀️ **Light/Dark Theme** | Theme preference stored per user in database |
| ⬇️ **CSV Export** | Download portfolio with live P&L as a CSV file |
| ★ **Admin Dashboard** | User stats, top tickers, recent signups (admin-only) |
| 📱 **PWA / Mobile** | Installable as a mobile app, offline fallback, service worker |
| 🔒 **Privacy First** | No tracking, no ads, minimal data — only what you need |

---

## 🏗 Project Structure

```
stocksage/
├── run.py                         # Entry point
├── requirements.txt               # All dependencies
├── Procfile                       # Render/Railway deploy
├── render.yaml                    # Render config
├── railway.toml                   # Railway config
├── .env.example                   # Environment variable template
├── .gitignore
├── README.md
│
├── backend/
│   ├── app.py                     # Flask factory + 10 blueprints
│   ├── models.py                  # User, PortfolioItem, WatchlistItem, PriceAlert
│   ├── routes/
│   │   ├── auth.py                # Register, login, logout
│   │   ├── dashboard.py           # Home dashboard
│   │   ├── stock.py               # Analyze, chart, OHLC, signal, AI, watchlist
│   │   ├── portfolio.py           # Portfolio CRUD + P&L
│   │   ├── news.py                # News feed (RSS)
│   │   ├── profile.py             # Settings, theme, alerts, CSV export
│   │   ├── compare.py             # Side-by-side comparison
│   │   ├── screener.py            # Stock screener with filters
│   │   ├── heatmap.py             # Sector performance heatmap
│   │   └── admin.py               # Admin dashboard
│   └── services/
│       ├── stock_service.py       # yfinance, RSI, SMA, OHLC, signals, screener
│       ├── ai_service.py          # Anthropic Claude + fallback
│       ├── news_service.py        # RSS + NewsAPI fallback
│       └── email_service.py       # SMTP email alerts (Gmail free)
│
└── frontend/
    ├── templates/
    │   ├── base.html              # Layout, navbar, theme, PWA
    │   ├── auth/{login,register}.html
    │   ├── dashboard/home.html
    │   ├── stock/analyze.html     # Line + candlestick charts, signal, AI, news
    │   ├── portfolio/portfolio.html
    │   ├── compare/compare.html
    │   ├── screener/screener.html
    │   ├── heatmap/heatmap.html
    │   ├── news/news.html
    │   ├── profile/settings.html
    │   └── admin/dashboard.html
    └── static/
        ├── css/main.css           # Full Bloomberg terminal dark + light theme
        ├── js/main.js             # SW registration, theme toggle, utilities
        ├── manifest.json          # PWA manifest
        ├── sw.js                  # Service worker (offline support)
        └── icons/
            ├── icon-192.png
            └── icon-512.png
```

---

## ⚡ Quick Start

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/stocksage.git
cd stocksage

# 2. Virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env — at minimum set a SECRET_KEY

# 5. Run
python run.py
# → http://localhost:5000
```

---

## 🔑 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | ✅ Yes | Random secret for Flask sessions |
| `DATABASE_URL` | No | SQLite default, PostgreSQL for prod |
| `ANTHROPIC_API_KEY` | No | AI insights (falls back to rule-based) |
| `NEWS_API_KEY` | No | Backup news (RSS feeds work without it) |
| `SMTP_USER` | No | Gmail address for email alerts |
| `SMTP_PASS` | No | Gmail App Password (not real password) |

**Getting free API keys:**
- **Anthropic**: [console.anthropic.com](https://console.anthropic.com) — free $5 credit
- **NewsAPI**: [newsapi.org](https://newsapi.org) — 100 req/day free
- **Gmail SMTP**: Enable 2FA → [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

---

## 🌐 Deploy Free in 5 Minutes

### Render.com (Recommended)
1. Push to GitHub
2. [render.com](https://render.com) → New Web Service → connect repo
3. Build: `pip install -r requirements.txt`
4. Start: `gunicorn run:app --workers 2 --bind 0.0.0.0:$PORT`
5. Add env vars → Deploy ✓

### Railway.app
1. [railway.app](https://railway.app) → New from GitHub
2. Add env vars in dashboard → Deploy ✓

---

## 📊 How the Signal Engine Works

Three technical factors produce a composite score:

| Indicator | Bullish (+) | Bearish (-) |
|---|---|---|
| RSI (14) | < 30 oversold (+2) / < 45 (+1) | > 70 overbought (-2) / > 55 (-1) |
| Price vs SMA20 | > SMA by 2%+ (+1) | < SMA by 2%+ (-1) |
| 52-Week Range | Near 52W low < 20% (+1) | Near 52W high > 85% (-1) |

Score ≥ 3 → **STRONG BUY** · 1–2 → **BUY** · 0 → **HOLD** · -1 to -2 → **SELL** · ≤ -3 → **STRONG SELL**

---

## 🔒 Privacy

- Only username, email, bcrypt-hashed password stored
- Portfolio data scoped to your account only
- No analytics, tracking scripts, or ads — ever
- Open source — audit the code yourself

---

## 📜 Disclaimer

> StockSage is for **educational and informational purposes only**. It does not constitute financial advice. Always do your own research before investing.

---

## 🤝 Contributing

PRs welcome! Fork → branch → commit → PR.

---

## 📄 License

MIT License — see `LICENSE` for details.

---

<div align="center">

**Built with Python, Flask, yfinance, Chart.js, and Anthropic Claude**

⭐ Star this repo if it helped you!

</div>
