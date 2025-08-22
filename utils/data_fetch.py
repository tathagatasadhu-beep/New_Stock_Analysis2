import os
import time
import requests
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

# Finnhub key: prefer Streamlit Secrets, then environment
FINNHUB_API_KEY = st.secrets.get("FINNHUB_API_KEY", os.getenv("FINNHUB_API_KEY", "")).strip()
BASE_URL = "https://finnhub.io/api/v1"

# A small, liquid universe to keep API calls light & fast (you can extend this)
DEFAULT_UNIVERSE = [
    "AAPL","MSFT","GOOGL","AMZN","NVDA","META","TSLA","BRK.B","JPM","UNH",
    "XOM","JNJ","V","PG","AVGO","HD","MA","LLY","COST","ADBE"
]

def _safe_get(url, params=None, timeout=12):
    try:
        r = requests.get(url, params=params, timeout=timeout)
        if r.status_code == 200:
            return r.json()
        return {}
    except Exception:
        return {}

def fetch_stock_price_history(symbol: str, days: int = 365) -> pd.DataFrame:
    """Daily OHLC for `days` back. Returns empty DataFrame on failure."""
    if not FINNHUB_API_KEY:
        return pd.DataFrame()

    end = int(time.time())
    start = end - days * 24 * 60 * 60
    url = f"{BASE_URL}/stock/candle"
    data = _safe_get(url, params={
        "symbol": symbol,
        "resolution": "D",
        "from": start,
        "to": end,
        "token": FINNHUB_API_KEY
    })
    if not data or data.get("s") != "ok":
        return pd.DataFrame()

    df = pd.DataFrame({
        "Date": pd.to_datetime(data["t"], unit="s"),
        "Open": data["o"],
        "High": data["h"],
        "Low": data["l"],
        "Close": data["c"],
        "Volume": data["v"],
    })
    return df

def _compute_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    delta = prices.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
    rs = avg_gain / (avg_loss.replace(0, 1e-9))
    return 100 - (100 / (1 + rs))

def fetch_screener_data(max_pe: float = 30.0, max_peg: float = 2.0, max_rsi: float = 55.0, top_n: int = 15) -> pd.DataFrame:
    """
    Lightweight screener:
      - Universe: DEFAULT_UNIVERSE
      - Attempts to use /stock/metric for PE/PEG; falls back gracefully
      - Computes RSI from price history
      - Ranks with a simple score favoring low PE/PEG and mid-low RSI
    """
    rows = []
    if not FINNHUB_API_KEY:
        return pd.DataFrame()

    for sym in DEFAULT_UNIVERSE:
        # Metrics (PE/PEG if available)
        metric = _safe_get(f"{BASE_URL}/stock/metric", params={"symbol": sym, "metric": "all", "token": FINNHUB_API_KEY})
        pe = None
        peg = None
        if metric and "metric" in metric:
            pe = metric["metric"].get("peBasicExclExtraTTM") or metric["metric"].get("peTTM")
            peg = metric["metric"].get("pegAnnual") or metric["metric"].get("pegQuarterly")

        # Price for RSI
        df = fetch_stock_price_history(sym, days=180)
        if df.empty:
            continue
        rsi = float(_compute_rsi(df["Close"]).iloc[-1])

        # Score (lower is better for PE/PEG, and RSI close to 45 is preferred)
        # Handle None safely
        pe_eff = pe if isinstance(pe, (int, float)) and pe > 0 else 40.0
        peg_eff = peg if isinstance(peg, (int, float)) and peg > 0 else 3.0
        rsi_penalty = abs(rsi - 45) / 45  # favor mid-range RSI
        score = (pe_eff / 15.0) + (peg_eff / 1.5) + rsi_penalty

        rows.append({
            "Ticker": sym,
            "PE": None if pe is None else round(pe, 2),
            "PEG": None if peg is None else round(peg, 2),
            "RSI": round(rsi, 1),
            "Score (↓ better)": round(score, 3),
            "Last": float(df["Close"].iloc[-1]),
        })

        # Be gentle on rate limits
        time.sleep(0.15)

    df_all = pd.DataFrame(rows)
    if df_all.empty:
        return df_all

    # Filters (treat None as failing the filter)
    def pass_num(x, maxv): return (isinstance(x, (int, float))) and (x <= maxv)
    mask = df_all.apply(
        lambda r: (pass_num(r["PE"], max_pe) if r["PE"] is not None else False)
                  and (pass_num(r["PEG"], max_peg) if r["PEG"] is not None else False)
                  and (isinstance(r["RSI"], (int, float)) and r["RSI"] <= max_rsi),
        axis=1
    )
    filtered = df_all[mask].copy()
    if filtered.empty:
        # If filters too tight, show best scores anyway
        filtered = df_all.copy()

    filtered = filtered.sort_values(by=["Score (↓ better)", "PE"], ascending=[True, True]).head(top_n)
    return filtered.reset_index(drop=True)

def fetch_company_news(symbol: str):
    """Company news (last 14 days). Returns [] on failure."""
    if not FINNHUB_API_KEY:
        return []
    to_date = datetime.now().date()
    from_date = to_date - timedelta(days=14)
    data = _safe_get(f"{BASE_URL}/company-news", params={
        "symbol": symbol,
        "from": str(from_date),
        "to": str(to_date),
        "token": FINNHUB_API_KEY
    })
    if not isinstance(data, list):
        return []
    # Keep essential fields
    cleaned = []
    for n in data[:20]:
        cleaned.append({
            "headline": n.get("headline"),
            "url": n.get("url"),
            "source": n.get("source"),
            "datetime": n.get("datetime"),
            "summary": n.get("summary")
        })
    return cleaned
