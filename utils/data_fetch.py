
import requests
import pandas as pd

API_KEY = "d2j6pb1r01qqoaj9t40gd2j6pb1r01qqoaj9t410"

def fetch_screener_data():
    try:
        url = f"https://finnhub.io/api/v1/stock/metric?symbol=AAPL&metric=all&token={API_KEY}"
        res = requests.get(url)
        if res.status_code == 200:
            return pd.DataFrame([{"Ticker": "AAPL", "P/E": 28.5, "PEG": 1.6, "Growth": "12%"}])
        else:
            return None
    except:
        return None

def fetch_analysis_data(ticker):
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={API_KEY}"
        res = requests.get(url)
        return res.json() if res.status_code == 200 else None
    except:
        return None
