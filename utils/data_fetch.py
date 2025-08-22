import os
import requests
import pandas as pd
from datetime import datetime, timedelta

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

BASE_URL = "https://finnhub.io/api/v1"

def _get_json(url, params=None):
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data or (isinstance(data, dict) and data.get("error")):
            return None
        return data
    except Exception:
        return None

def fetch_price_data(ticker):
    """Fetch historical price data for charts"""
    url = f"{BASE_URL}/stock/candle"
    params = {
        "symbol": ticker,
        "resolution": "D",
        "from": int((datetime.now() - timedelta(days=180)).timestamp()),
        "to": int(datetime.now().timestamp()),
        "token": FINNHUB_API_KEY,
    }
    data = _get_json(url, params)
    if not data or data.get("s") != "ok":
        return None
    return pd.DataFrame({
        "Date": pd.to_datetime(data["t"], unit="s"),
        "Open": data["o"],
        "High": data["h"],
        "Low": data["l"],
        "Close": data["c"],
        "Volume": data["v"],
    })

def fetch_news(ticker):
    """Fetch recent market news for ticker"""
    url = f"{BASE_URL}/company-news"
    params = {
        "symbol": ticker,
        "from": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
        "to": datetime.now().strftime("%Y-%m-%d"),
        "token": FINNHUB_API_KEY,
    }
    data = _get_json(url, params)
    if not data:
        return []
    return [{"headline": n.get("headline"), "url": n.get("url")} for n in data if n.get("url")]

def fetch_top50_screener():
    """Return mock screener (Finnhub has no native screener API)"""
    # Placeholder: Fetch large-cap list, then filter by P/E, etc.
    # Here we simulate with AAPL to avoid empty UI
    return pd.DataFrame([
        {"Ticker": "AAPL", "PE": 28.5, "Undervalued": True},
        {"Ticker": "MSFT", "PE": 31.2, "Undervalued": False},
    ])
