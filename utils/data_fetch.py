import os
import requests
import pandas as pd
import time

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

# --- Screener: top undervalued S&P 500 stocks ---
def fetch_screener_data():
    # For simplicity, top few S&P 500 stocks with dummy valuation metrics
    data = [
        {"Ticker":"AAPL","PE":28,"PEG":1.5,"RSI":45,"Undervalued":True},
        {"Ticker":"MSFT","PE":32,"PEG":2.0,"RSI":55,"Undervalued":False},
        {"Ticker":"GOOGL","PE":25,"PEG":1.2,"RSI":40,"Undervalued":True},
        {"Ticker":"AMZN","PE":60,"PEG":2.5,"RSI":70,"Undervalued":False},
        {"Ticker":"NVDA","PE":45,"PEG":2.1,"RSI":60,"Undervalued":False}
    ]
    return pd.DataFrame(data)

# --- Analysis: fetch historical candles ---
def fetch_analysis_data(ticker):
    if not FINNHUB_API_KEY:
        return None
    now = int(time.time())
    past = now - 365*24*60*60  # 1 year
    url = f"https://finnhub.io/api/v1/stock/candle?symbol={ticker}&resolution=D&from={past}&to={now}&token={FINNHUB_API_KEY}"
    r = requests.get(url).json()
    if r.get("s") != "ok":
        return None
    return {"price_data": r}
