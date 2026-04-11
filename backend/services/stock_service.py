"""
StockSage Stock Service - Fixed for Yahoo Finance rate limiting
Uses curl_cffi session for reliable data fetching.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# Fix Yahoo Finance blocking by using curl_cffi if available
try:
    from curl_cffi import requests as curl_requests
    CURL_AVAILABLE = True
except ImportError:
    CURL_AVAILABLE = False


def _make_ticker(symbol: str):
    """Create a yfinance Ticker with curl_cffi session if available."""
    if CURL_AVAILABLE:
        try:
            session = curl_requests.Session(impersonate="chrome")
            return yf.Ticker(symbol, session=session)
        except Exception:
            pass
    return yf.Ticker(symbol)


class StockService:
    """Core service for stock data fetching and technical analysis."""

    def get_current_price(self, ticker: str) -> dict:
        try:
            stock = _make_ticker(ticker)
            hist = stock.history(period="2d")
            if not hist.empty:
                price = round(float(hist["Close"].iloc[-1]), 2)
                return {"ticker": ticker, "price": price}
            info = stock.info
            price = (info.get("currentPrice") or info.get("regularMarketPrice")
                     or info.get("previousClose") or 0)
            return {"ticker": ticker, "price": float(price) if price else 0}
        except Exception as e:
            return {"ticker": ticker, "price": 0, "error": str(e)}

    def get_full_analysis(self, ticker: str) -> dict:
        try:
            stock = _make_ticker(ticker)

            # Get history first — more reliable than info
            hist = stock.history(period="60d")
            if hist.empty:
                return {"error": f"No data found for '{ticker}'. Please check the symbol and try again."}

            closes = hist["Close"]
            rsi = self._calculate_rsi(closes)
            sma20 = closes.rolling(20).mean()
            sma50 = closes.rolling(50).mean()

            current_price = round(float(closes.iloc[-1]), 2)
            prev_close    = round(float(closes.iloc[-2]), 2) if len(closes) > 1 else current_price
            change        = round(current_price - prev_close, 2)
            change_pct    = round((change / prev_close) * 100, 2) if prev_close else 0
            current_rsi   = round(float(rsi.iloc[-1]), 2) if not rsi.empty else None
            sma20_val     = round(float(sma20.iloc[-1]), 2) if not pd.isna(sma20.iloc[-1]) else None
            sma50_val     = round(float(sma50.iloc[-1]), 2) if len(closes) >= 50 and not pd.isna(sma50.iloc[-1]) else None

            # Info is secondary — don't fail if it errors
            info = {}
            try:
                info = stock.info or {}
            except Exception:
                pass

            # 52-week high/low from history if info unavailable
            hist_1y = None
            week_high = info.get("fiftyTwoWeekHigh")
            week_low  = info.get("fiftyTwoWeekLow")
            if not week_high or not week_low:
                try:
                    hist_1y = stock.history(period="1y")
                    if not hist_1y.empty:
                        week_high = round(float(hist_1y["High"].max()), 2)
                        week_low  = round(float(hist_1y["Low"].min()),  2)
                except Exception:
                    pass

            company_name = (info.get("longName") or info.get("shortName") or ticker)

            return {
                "ticker":        ticker,
                "company_name":  company_name,
                "sector":        info.get("sector",   "N/A"),
                "industry":      info.get("industry", "N/A"),
                "current_price": current_price,
                "prev_close":    prev_close,
                "change":        change,
                "change_pct":    change_pct,
                "volume":        int(hist["Volume"].iloc[-1]) if "Volume" in hist.columns else 0,
                "avg_volume":    info.get("averageVolume", 0),
                "market_cap":    info.get("marketCap"),
                "pe_ratio":      info.get("trailingPE") or info.get("forwardPE"),
                "week_52_high":  week_high,
                "week_52_low":   week_low,
                "dividend_yield":info.get("dividendYield"),
                "beta":          info.get("beta"),
                "rsi":           current_rsi,
                "sma20":         sma20_val,
                "sma50":         sma50_val,
                "description":   info.get("longBusinessSummary", ""),
                "error":         None,
            }

        except Exception as e:
            return {"error": f"Could not fetch data for '{ticker}'. ({str(e)})"}

    def get_chart_data(self, ticker: str) -> dict:
        try:
            stock = _make_ticker(ticker)
            hist  = stock.history(period="60d")
            if hist.empty:
                return {"error": "No data available"}

            closes  = hist["Close"]
            rsi     = self._calculate_rsi(closes)
            sma20   = closes.rolling(20).mean()

            last20_closes = closes.tail(20)
            last20_rsi    = rsi.tail(20)
            last20_sma    = sma20.tail(20)

            return {
                "ticker": ticker,
                "dates":  [d.strftime("%b %d") for d in last20_closes.index],
                "prices": [round(float(v), 2) for v in last20_closes.values],
                "rsi":    [round(float(v), 2) if not np.isnan(v) else None for v in last20_rsi.values],
                "sma20":  [round(float(v), 2) if not np.isnan(v) else None for v in last20_sma.values],
            }
        except Exception as e:
            return {"error": str(e)}

    def get_ohlc_data(self, ticker: str, days: int = 30) -> dict:
        try:
            stock  = _make_ticker(ticker)
            period = "60d" if days <= 30 else "90d"
            hist   = stock.history(period=period).tail(days)
            if hist.empty:
                return {"error": "No OHLC data available"}

            closes = hist["Close"]
            sma20  = closes.rolling(20).mean()
            rsi    = self._calculate_rsi(closes)

            candles = []
            for i, (idx, row) in enumerate(hist.iterrows()):
                candles.append({
                    "date":   idx.strftime("%b %d"),
                    "open":   round(float(row["Open"]),  2),
                    "high":   round(float(row["High"]),  2),
                    "low":    round(float(row["Low"]),   2),
                    "close":  round(float(row["Close"]), 2),
                    "volume": int(row["Volume"]) if not np.isnan(row["Volume"]) else 0,
                    "sma20":  round(float(sma20.iloc[i]), 2) if not np.isnan(sma20.iloc[i]) else None,
                    "rsi":    round(float(rsi.iloc[i]),   2) if not np.isnan(rsi.iloc[i])   else None,
                })
            return {"ticker": ticker, "candles": candles}
        except Exception as e:
            return {"error": str(e)}

    def generate_signal(self, analysis: dict) -> dict:
        rsi        = analysis.get("rsi")
        price      = analysis.get("current_price", 0)
        sma20      = analysis.get("sma20", price)
        week_high  = analysis.get("week_52_high")
        week_low   = analysis.get("week_52_low")
        score      = 0
        reasons    = []

        if rsi is not None:
            if rsi < 30:
                score += 2
                reasons.append(f"RSI is at {rsi} — the stock is oversold and may be due for a bounce.")
            elif rsi < 45:
                score += 1
                reasons.append(f"RSI sits at {rsi}, on the lower side — some buying pressure could build soon.")
            elif rsi > 70:
                score -= 2
                reasons.append(f"RSI is at {rsi} — overbought territory, a pullback is possible.")
            elif rsi > 55:
                score -= 1
                reasons.append(f"RSI of {rsi} shows mild bullish momentum, getting closer to overbought.")
            else:
                reasons.append(f"RSI at {rsi} is neutral — no extreme signals in either direction.")

        if sma20 and price:
            if price > sma20 * 1.02:
                score += 1
                reasons.append(f"Price (${price}) is trading above its 20-day average (${sma20}) — constructive sign.")
            elif price < sma20 * 0.98:
                score -= 1
                reasons.append(f"Price (${price}) is below its 20-day moving average (${sma20}) — short-term weakness.")
            else:
                reasons.append(f"Stock is trading near its 20-day average (${sma20}) — price consolidation.")

        if week_high and week_low and price:
            rng = week_high - week_low
            if rng > 0:
                pos = (price - week_low) / rng * 100
                if pos < 20:
                    score += 1
                    reasons.append(f"Near its 52-week low (${week_low}) — could represent a value opportunity.")
                elif pos > 85:
                    score -= 1
                    reasons.append(f"Near its 52-week high (${week_high}) — risk of short-term correction.")

        if score >= 3:
            signal, color, emoji = "STRONG BUY", "success", "🚀"
            summary = "Multiple indicators align positively. This looks like a solid buying opportunity."
        elif score >= 1:
            signal, color, emoji = "BUY", "success", "✅"
            summary = "The overall indicators lean bullish. Consider adding this to your portfolio."
        elif score <= -3:
            signal, color, emoji = "STRONG SELL", "danger", "🔴"
            summary = "Several warning signs are flashing. It may be wise to reduce or exit your position."
        elif score <= -1:
            signal, color, emoji = "SELL", "danger", "⚠️"
            summary = "Indicators suggest caution. Consider trimming your position or avoiding new entries."
        else:
            signal, color, emoji = "HOLD", "warning", "⏸️"
            summary = "The stock is in a neutral zone. Holding your current position seems reasonable."

        return {"signal": signal, "color": color, "emoji": emoji,
                "summary": summary, "reasons": reasons, "score": score}

    def screen_stocks(self, tickers: list, filters: dict) -> list:
        results = []
        for ticker in tickers:
            data = self.get_full_analysis(ticker)
            if data.get("error"):
                continue
            rsi   = data.get("rsi") or 50
            price = data.get("current_price") or 0
            chg   = data.get("change_pct") or 0
            sma20 = data.get("sma20") or price
            if filters.get("rsi_min")        is not None and rsi   < filters["rsi_min"]:        continue
            if filters.get("rsi_max")        is not None and rsi   > filters["rsi_max"]:        continue
            if filters.get("price_min")      is not None and price < filters["price_min"]:      continue
            if filters.get("price_max")      is not None and price > filters["price_max"]:      continue
            if filters.get("change_pct_min") is not None and chg   < filters["change_pct_min"]: continue
            if filters.get("change_pct_max") is not None and chg   > filters["change_pct_max"]: continue
            if filters.get("sma_position") == "above" and price < sma20: continue
            if filters.get("sma_position") == "below" and price > sma20: continue
            sig = self.generate_signal(data)
            data["signal"]       = sig["signal"]
            data["signal_color"] = sig["color"]
            results.append(data)
        return results

    def _calculate_rsi(self, closes: pd.Series, period: int = 14) -> pd.Series:
        delta    = closes.diff()
        gain     = delta.where(delta > 0, 0.0)
        loss     = -delta.where(delta < 0, 0.0)
        avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
        avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
        rs       = avg_gain / avg_loss.replace(0, np.nan)
        return (100 - (100 / (1 + rs))).fillna(50)