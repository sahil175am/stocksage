"""
StockSage News Service
Fetches stock market news using free RSS feeds from:
- Yahoo Finance RSS (no API key needed)
- Google Finance RSS
- Reuters RSS
Falls back to NewsAPI if key is available.
"""

import os
import feedparser
import requests
from datetime import datetime
import time


class NewsService:
    """Fetches and humanizes financial news from free RSS feeds."""

    MARKET_FEEDS = [
        "https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC,^DJI,^IXIC&region=US&lang=en-US",
        "https://feeds.finance.yahoo.com/rss/2.0/headline?s=SPY,QQQ,DIA&region=US&lang=en-US",
        "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best",
    ]

    def get_ticker_news(self, ticker: str, max_articles: int = 8) -> list:
        """Fetch news for a specific ticker via Yahoo Finance RSS."""
        feed_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"
        articles = self._parse_feed(feed_url, max_articles)

        # Fallback to Google News search RSS
        if not articles:
            google_url = f"https://news.google.com/rss/search?q={ticker}+stock&hl=en-US&gl=US&ceid=US:en"
            articles = self._parse_feed(google_url, max_articles)

        # Fallback to NewsAPI if key present
        if not articles and os.environ.get("NEWS_API_KEY"):
            articles = self._newsapi_fetch(ticker, max_articles)

        return articles

    def get_market_news(self, max_articles: int = 12) -> list:
        """Fetch general market news."""
        all_articles = []

        for feed_url in self.MARKET_FEEDS:
            articles = self._parse_feed(feed_url, 5)
            all_articles.extend(articles)
            if len(all_articles) >= max_articles:
                break

        # Deduplicate by title
        seen = set()
        unique = []
        for a in all_articles:
            if a["title"] not in seen:
                seen.add(a["title"])
                unique.append(a)

        return unique[:max_articles]

    def _parse_feed(self, url: str, limit: int = 8) -> list:
        """Parse RSS feed and return normalized article list."""
        try:
            feed = feedparser.parse(url)
            articles = []
            for entry in feed.entries[:limit]:
                published = self._parse_date(entry.get("published", ""))
                summary = entry.get("summary", "") or entry.get("description", "")
                # Clean up HTML tags in summary
                summary = self._clean_html(summary)
                if len(summary) > 200:
                    summary = summary[:200] + "..."

                articles.append({
                    "title": entry.get("title", "No title"),
                    "summary": summary or "Read the full article for details.",
                    "link": entry.get("link", "#"),
                    "published": published,
                    "source": feed.feed.get("title", "Financial News"),
                })
            return articles
        except Exception:
            return []

    def _newsapi_fetch(self, query: str, limit: int = 8) -> list:
        """Fallback: fetch from NewsAPI (free tier = 100 req/day)."""
        try:
            api_key = os.environ.get("NEWS_API_KEY")
            url = (
                f"https://newsapi.org/v2/everything?"
                f"q={query}&sortBy=publishedAt&pageSize={limit}"
                f"&language=en&apiKey={api_key}"
            )
            resp = requests.get(url, timeout=5)
            data = resp.json()
            articles = []
            for item in data.get("articles", [])[:limit]:
                articles.append({
                    "title": item.get("title", ""),
                    "summary": item.get("description", "") or "Read the full article.",
                    "link": item.get("url", "#"),
                    "published": self._parse_date(item.get("publishedAt", "")),
                    "source": item.get("source", {}).get("name", "NewsAPI"),
                })
            return articles
        except Exception:
            return []

    def _parse_date(self, date_str: str) -> str:
        """Convert various date formats to readable string."""
        if not date_str:
            return "Recently"
        formats = [
            "%a, %d %b %Y %H:%M:%S %z",
            "%a, %d %b %Y %H:%M:%S %Z",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S%z",
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%b %d, %Y")
            except ValueError:
                continue
        return date_str[:10] if len(date_str) >= 10 else "Recently"

    def _clean_html(self, text: str) -> str:
        """Remove basic HTML tags from text."""
        import re
        clean = re.compile("<.*?>")
        return re.sub(clean, "", text).strip()
