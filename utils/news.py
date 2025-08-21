import os
import requests
from datetime import datetime, timedelta

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

def fetch_news(ticker):
    if not FINNHUB_API_KEY:
        return []
    today = datetime.today().date()
    past = today - timedelta(days=30)
    url = f"https://urldefense.com/v3/__https://finnhub.io/api/v1/company-news?symbol=*7Bticker*7D&from=*7Bpast*7D&to=*7Btoday*7D&token=*7BFINNHUB_API_KEY*7D__;JSUlJSUlJSU!!Dgr3g5d8opDR!R8s1nwu_OxDljgQympPVdzlkqPr1xleCq42TrGMLnVZbOCd9m_sjNhS6WWOzv52tPCtlVVQnN3FbT75EaEqjvdHQpHc$"
    r = requests.get(url)
    if r.status_code==200:
        return r.json()[:5]
    return []
