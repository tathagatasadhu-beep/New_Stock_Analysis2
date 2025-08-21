import os
import requests
import pandas as pd
import time

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

# --- Top 50 S&P 500 Screener ---
def fetch_top50_screener():
    # Placeholder: Add top 50 tickers manually or from a static CSV
    top50 = ["AAPL","MSFT","GOOGL","AMZN","NVDA","TSLA","META","BRK.B","JNJ","V",
             "UNH","PG","HD","MA","DIS","PYPL","ADBE","CMCSA","NFLX","XOM",
             "KO","PFE","NKE","ABBV","PEP","MRK","TMO","CSCO","VZ","ABT",
             "CRM","INTC","ACN","COST","AVGO","MCD","MDT","NEE","TXN","WMT",
             "HON","LIN","QCOM","DHR","LOW","PM","BMY","ORCL","AMGN","IBM"]

    rows = []
    for ticker in top50:
        try:
            # Fundamental metrics
            url = f"https://urldefense.com/v3/__https://finnhub.io/api/v1/quote?symbol=*7Bticker*7D&token=*7BFINNHUB_API_KEY*7D__;JSUlJQ!!Dgr3g5d8opDR!R8s1nwu_OxDljgQympPVdzlkqPr1xleCq42TrGMLnVZbOCd9m_sjNhS6WWOzv52tPCtlVVQnN3FbT75EaEqjlqINiTI$"
            r = requests.get(url).json()
            price = r.get("c", None)
            if price is None:
                continue

            # Placeholder PE, PEG, RSI for example purposes
            pe = round(price/5,2)
            peg = round(pe/10,2)
            rsi = 50
            undervalued = pe<30
            rows.append({"Ticker": ticker, "Price": price, "PE": pe, "PEG": peg, "RSI": rsi, "Undervalued": undervalued})
        except:
            continue
    return pd.DataFrame(rows).sort_values(by=["Undervalued","PE"], ascending=[False,True])

# --- Analysis Data ---
def fetch_analysis_data(ticker):
    if not FINNHUB_API_KEY:
        return None
    now = int(time.time())
    past = now - 365*24*60*60
    url = f"https://urldefense.com/v3/__https://finnhub.io/api/v1/stock/candle?symbol=*7Bticker*7D&resolution=D&from=*7Bpast*7D&to=*7Bnow*7D&token=*7BFINNHUB_API_KEY*7D__;JSUlJSUlJSU!!Dgr3g5d8opDR!R8s1nwu_OxDljgQympPVdzlkqPr1xleCq42TrGMLnVZbOCd9m_sjNhS6WWOzv52tPCtlVVQnN3FbT75EaEqjWHcdPt4$"
    r = requests.get(url).json()
    if r.get("s") != "ok":
        return None
    return {"price_data": r}
