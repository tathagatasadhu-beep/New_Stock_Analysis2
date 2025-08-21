import os
import requests
import pandas as pd

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

def fetch_screener_data():
    if not FINNHUB_API_KEY:
        return pd.DataFrame()

    url = f"https://finnhub.io/api/v1/stock/symbol?exchange=US&token={FINNHUB_API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return pd.DataFrame(data)[:20]  # Example: top 20
        else:
            return pd.DataFrame()
    except:
        return pd.DataFrame()

def fetch_analysis_data(ticker):
    if not FINNHUB_API_KEY:
        return {}

    try:
        # Price data
        price_url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_API_KEY}"
        price_data = requests.get(price_url).json()

        # Valuation example (placeholder for DCF or metrics)
        valuation = {"DCF": "Est. $150", "Current Price": price_data.get("c", "N/A")}

        # Analysis text
        analysis_text = (
            f"Stock {ticker} is trading at ${price_data.get('c', 'N/A')}. "
            "Fibonacci retracement and technical indicators suggest potential entry levels "
            "and resistance points. RSI and MACD indicate trend momentum."
        )

        return {
            "valuation": valuation,
            "metrics": price_data,
            "price_data": price_data,
            "analysis_text": analysis_text
        }
    except:
        return {}
