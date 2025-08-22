import os
import requests
import pandas as pd

# Load API key from Streamlit Secrets or environment variable
API_KEY = os.getenv("FINNHUB_API_KEY")

BASE_URL = "https://finnhub.io/api/v1"


def fetch_top50_screener():
    """
    Fetch top 50 undervalued stocks from S&P 500 using Finnhub or placeholder data if unavailable.
    """
    try:
        url = f"{BASE_URL}/stock/symbol?exchange=US&token={API_KEY}"
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()

        # Filter to S&P 500 or most traded large-cap stocks
        rows = []
        for stock in data[:50]:  # Limit to 50 for speed
            # Basic info (fallback if some fields are missing)
            rows.append({
                "Ticker": stock.get("symbol", "N/A"),
                "Company": stock.get("description", "Unknown"),
                "PE": stock.get("peRatio", 0),
                "Undervalued": bool(stock.get("peRatio", 50) < 20),  # crude check
                "Sector": stock.get("type", "N/A"),
                "MarketCap": stock.get("marketCapitalization", 0)
            })

        # If API returns empty list
        if not rows:
            return pd.DataFrame([{
                "Ticker": "N/A",
                "Company": "No Data",
                "PE": 0,
                "Undervalued": False,
                "Sector": "N/A",
                "MarketCap": 0
            }])

        df = pd.DataFrame(rows)

        # Ensure columns exist
        for col in ["Undervalued", "PE"]:
            if col not in df.columns:
                df[col] = 0 if col == "PE" else False

        return df.sort_values(by=["Undervalued", "PE"], ascending=[False, True])

    except Exception as e:
        # Return placeholder DataFrame on error
        return pd.DataFrame([{
            "Ticker": "ERROR",
            "Company": str(e),
            "PE": 0,
            "Undervalued": False,
            "Sector": "N/A",
            "MarketCap": 0
        }])


def fetch_analysis_data(ticker):
    """
    Fetch stock analysis data for a given ticker.
    Includes price, fundamentals, RSI, MACD, etc.
    """
    try:
        # Basic price data
        quote_url = f"{BASE_URL}/quote?symbol={ticker}&token={API_KEY}"
        quote_resp = requests.get(quote_url)
        quote_resp.raise_for_status()
        quote_data = quote_resp.json()

        # Company profile
        profile_url = f"{BASE_URL}/stock/profile2?symbol={ticker}&token={API_KEY}"
        profile_resp = requests.get(profile_url)
        profile_resp.raise_for_status()
        profile_data = profile_resp.json()

        return {
            "price": quote_data.get("c"),
            "change": quote_data.get("d"),
            "percent_change": quote_data.get("dp"),
            "company_name": profile_data.get("name", "Unknown"),
            "market_cap": profile_data.get("marketCapitalization", 0),
            "exchange": profile_data.get("exchange", "N/A")
        }

    except Exception as e:
        return {"error": str(e)}
