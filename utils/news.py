import os
import requests
from datetime import datetime, timedelta

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

def fetch_news(ticker):
    if not FINNHUB_API_KEY:
        return []

    try:
        today = datetime.today().strftime('%Y-%m-%d')
        past = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')
        url = f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from={past}&to={today}&token={FINNHUB_API_KEY}"
        r = requests.get(url)
        return r.json()[:5] if r.status_code == 200 else []
    except:
        return []
