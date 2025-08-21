
import requests

API_KEY = "d2j6pb1r01qqoaj9t40gd2j6pb1r01qqoaj9t410"

def get_stock_news(ticker):
    try:
        url = f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from=2025-07-01&to=2025-08-01&token={API_KEY}"
        res = requests.get(url)
        return res.json() if res.status_code == 200 else []
    except:
        return []
