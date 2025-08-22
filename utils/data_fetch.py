import os
import time
import requests
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

BASE_URL = "https://finnhub.io/api/v1"

# ---------- API Key helpers ----------
def get_api_key() -> str:
    # Try Streamlit Secrets (several common names), then environment
    for k in ("FINNHUB_API_KEY", "finnhub_api_key", "FINNHUB_TOKEN", "FINNHUB"):
        try:
            v = st.secrets.get(k)  # st.secrets exists on Streamlit Cloud
            if v:
                return str(v).strip()
        except Exception:
            pass
    for k in ("FINNHUB_API_KEY", "finnhub_api_key", "FINNHUB_TOKEN", "FINNHUB"):
        v = os.getenv(k)
        if v:
            return v.strip()
    return ""

API_KEY = get_api_key()

def _safe_get(path: str, params: dict, timeout: int = 12):
    """GET wrapper that returns {} on any failure."""
    try:
        url = f"{BASE_URL}/{path.lstrip('/')}"
        r = requests.get(url, params=params, timeout=timeout)
        if r.status_code == 200:
            return r.json()
        return {"_http_status": r.status_code, "_body": r.text}
    except Exception as e:
        return {"_error": str(e)}

def ping_quote(symbol: str = "AAPL"):
    """Quick connectivity & key check."""
    if not API_KEY:
        return False, "No API key detected."
    j = _safe_get("quote", {"symbol": symbol, "token": API_KEY})
    if "c" in j and isinstance(j["c"], (int, float)):
        return True, ""
    if "_http_status" in j:
        return False, f"HTTP {j['_http_status']}: {j.get('_body', '')[:120]}"
    if "_error" in j:
        return False, j["_error"]
    return False, str(j)[:120]

# ---------- Price History ----------
def fetch_stock_price_history(symbol: str, days: int = 365) -> pd.DataFrame:
    """Daily OHLC for `days` back. Returns empty DataFrame on failure."""
    if not API_KEY:
        return pd.DataFrame()
    end = int(time.time())
    start = end - days * 24 * 60 * 60
    j = _safe_get("stock/candle", {
        "symbol": symbol,
        "resolution": "D",
        "from": start,
        "to": end,
        "token": API_KEY
    })
    if not j or j.get("s") != "ok":
        return pd.DataFrame()
    df = pd.DataFrame({
        "Date": pd.to_datetime(j["t"], unit="s"),
        "Open": j["o"],
        "High": j["h"],
        "Low": j["l"],
        "Close": j["c"],
        "Volume": j["v"],
    })
    return df

# ---------- Screener ----------
DEFAULT_UNIVERSE = [
    "AAPL","MSFT","GOOGL","AMZN","NVDA","META","TSLA","JPM","UNH","XOM",
    "V","PG","HD","MA","LLY","COST","ADBE","PEP","KO","BAC"
]

def _ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()

def fetch_screener_data(max_rsi: float = 55.0, min_pct_below_200ema: float = -3.0, top_n: int = 12) -> pd.DataFrame:
    """
    Robust screener (works on free Finnhub):
      - Universe: DEFAULT_UNIVERSE
      - Uses price history only (avoid premium metric endpoints)
      - Compute RSI(14), 50-EMA, 200-EMA, % distance to 200-EMA
      - Filter by RSI and % below 200-EMA (negative), rank by score (lower RSI + more below 200-EMA)
    """
    rows = []
    if not API_KEY:
        return pd.DataFrame()

    for sym in DEFAULT_UNIVERSE:
        df = fetch_stock_price_history(sym, days=220)
        if df.empty or len(df) < 50:
            continue
        close = df["Close"]
        rsi = _compute_rsi(close).iloc[-1]
        ema50 = _ema(close, 50).iloc[-1]
        ema200 = _ema(close, 200).iloc[-1] if len(df) >= 200 else _ema(close, len(df)).iloc[-1]
        last = float(close.iloc[-1])
        pct_below_200 = (last - float(ema200)) / float(ema200) * 100.0  # negative if below
        score = max(0.0, rsi - 30) + max(0.0, pct_below_200 + 5)  # prefer RSI near 30 & below 200-EMA

        rows.append({
            "Ticker": sym,
            "Last": round(last, 2),
            "RSI": round(float(rsi), 1),
            "% to 200-EMA": round(pct_below_200, 2),
            "Score (↓ better)": round(score, 2),
        })
        time.sleep(0.12)  # keep under rate limits

    df_all = pd.DataFrame(rows)
    if df_all.empty:
        return df_all

    filt = (df_all["RSI"] <= max_rsi) & (df_all["% to 200-EMA"] <= min_pct_below_200ema)
    out = df_all[filt].copy()
    if out.empty:
        out = df_all.copy()  # relax filters if too tight

    out = out.sort_values(by=["Score (↓ better)", "RSI", "% to 200-EMA"], ascending=[True, True, True]).head(top_n)
    return out.reset_index(drop=True)

def _compute_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    delta = prices.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
    rs = avg_gain / (avg_loss.replace(0, 1e-9))
    return 100 - (100 / (1 + rs))

# ---------- News ----------
def fetch_company_news(symbol: str):
    """Company news (last 14 days). Returns [] on failure/rate-limit."""
    if not API_KEY:
        return []
    to_date = datetime.now().date()
    from_date = to_date - timedelta(days=14)
    j = _safe_get("company-news", {
        "symbol": symbol,
        "from": str(from_date),
        "to": str(to_date),
        "token": API_KEY
    })
    if not isinstance(j, list):
        return []
    cleaned = []
    for n in j[:20]:
        cleaned.append({
            "headline": n.get("headline"),
            "url": n.get("url"),
            "source": n.get("source"),
            "datetime": n.get("datetime"),
            "summary": n.get("summary"),
        })
    return cleaned
