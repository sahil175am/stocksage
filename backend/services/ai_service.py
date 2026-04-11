"""
StockSage AI Service
Uses Anthropic's Claude API (free tier) to generate humanized stock insights.
Falls back to rule-based insights if API key is not set.
"""

import os
import anthropic


class AIService:
    """Generates humanized AI insights for stock analysis."""

    def __init__(self):
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None

    def get_insight(self, ticker: str, analysis: dict) -> str:
        """
        Returns a brief, humanized AI insight about the stock.
        Uses Claude if API key is available, otherwise falls back to rule-based.
        """
        if self.client:
            return self._claude_insight(ticker, analysis)
        else:
            return self._fallback_insight(ticker, analysis)

    def _claude_insight(self, ticker: str, analysis: dict) -> str:
        """Call Anthropic API for a humanized insight."""
        prompt = f"""You are a friendly, experienced stock market analyst. 
Provide a brief 3-4 sentence humanized insight about {ticker} ({analysis.get('company_name', ticker)}) 
based on these metrics:
- Current Price: ${analysis.get('current_price')}
- Change Today: {analysis.get('change_pct')}%
- RSI (14): {analysis.get('rsi')}
- SMA 20: ${analysis.get('sma20')}
- 52-Week High: ${analysis.get('week_52_high')}
- 52-Week Low: ${analysis.get('week_52_low')}
- Market Cap: ${analysis.get('market_cap')}
- P/E Ratio: {analysis.get('pe_ratio')}
- Sector: {analysis.get('sector')}

Write like you're talking to a friend — clear, helpful, no jargon. 
Keep it under 80 words. End with one actionable thought.
Do NOT give direct financial advice or guarantees."""

        try:
            message = self.client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text.strip()
        except Exception as e:
            return self._fallback_insight(ticker, analysis)

    def _fallback_insight(self, ticker: str, analysis: dict) -> str:
        """Rule-based humanized insight when API key is unavailable."""
        name = analysis.get("company_name", ticker)
        rsi = analysis.get("rsi")
        change_pct = analysis.get("change_pct", 0)
        price = analysis.get("current_price", 0)
        sma20 = analysis.get("sma20", price)
        sector = analysis.get("sector", "the market")

        parts = []

        # Price movement
        if change_pct > 2:
            parts.append(f"{name} is having a strong session today, up {change_pct}%.")
        elif change_pct < -2:
            parts.append(f"{name} is under some pressure today, down {change_pct}%.")
        else:
            parts.append(f"{name} is relatively stable today with a modest {change_pct}% move.")

        # RSI comment
        if rsi:
            if rsi < 35:
                parts.append(f"With RSI at {rsi}, the stock appears oversold — historically a zone where buyers start showing interest.")
            elif rsi > 65:
                parts.append(f"RSI at {rsi} puts it in overbought territory, so short-term profit-taking could occur.")
            else:
                parts.append(f"The RSI of {rsi} suggests balanced momentum — neither extreme greed nor fear is driving the price.")

        # SMA context
        if price > sma20:
            parts.append(f"Trading above its 20-day average is a constructive sign for near-term direction.")
        else:
            parts.append(f"It's trading below its 20-day average, which bears watching for a potential trend shift.")

        # Sector note
        if sector and sector != "N/A":
            parts.append(f"Keep an eye on broader {sector} sector trends as they often move this stock.")

        return " ".join(parts[:3])
