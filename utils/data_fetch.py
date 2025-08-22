import os
import requests
import pandas as pd
from datetime import datetime, timedelta

API_KEY = os.getenv("FINNHUB_API_KEY")  # set in Streamlit Secrets or Env

BASE_URL = "https://finnhub.io/api/v1"

def fetch_top50_screener():
    """Fetches a sample screener list from Finnhub"""
    try:
        url = f"{BASE_URL}/stock/symbol?exchange=US&token={API_KEY}"
        resp = requests.get(url)
        if resp.status_code != 200:
            return pd.DataFrame()
        data = resp.json()

        # Dummy scoring - filter large cap and random sample
        df = pd.DataFrame(data)
        if "symbol" not in df:
            return pd.DataFrame()
        df["PE"] = 15  # mock values for now
        df["Undervalued"] = True
        return df[["symbol", "description", "PE", "Undervalued"]].head(50)

    except Exception:
        return pd.DataFrame()

def fetch_analysis_data(symbol):
    """Fetch historical prices + basic valuation"""
    try:
        end = int(datetime.now().timestamp())
        start = int((datetime.now() - timedelta(days=180)).timestamp())
        url = f"{BASE_URL}/stock/candle?symbol={symbol}&resolution=D&from={start}&to={end}&token={API_KEY}"
        resp = requests.get(url)
        if resp.status_code != 200:
            return {}

        candles = resp.json()
        if candles.get("s") != "ok":
            return {}

        df = pd.DataFrame({
            "Date": pd.to_datetime(candles["t"], unit="s"),
            "Open": candles["o"],
            "High": candles["h"],
            "Low": candles["l"],
            "Close": candles["c"],
            "Volume": candles["v"]
        })

        return {
            "price_data": df,
            "valuation": {"DCF": 150, "Current Price": df["Close"].iloc[-1]}  # Mock valuation
        }

    except Exception:
        return {}

def fetch_company_news(symbol):
    """Fetches company news from Finnhub"""
    try:
        today = datetime.now().date()
        start_date = today - timedelta(days=30)
        url = f"{BASE_URL}/company-news?symbol={symbol}&from={start_date}&to={today}&token={API_KEY}"
        resp = requests.get(url)
        if resp.status_code == 200:
            return resp.json()
        return []
    except Exception:
        return []
