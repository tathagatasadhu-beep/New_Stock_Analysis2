import numpy as np
import pandas as pd
import plotly.graph_objects as go
from typing import Tuple, Dict, List

def _ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()

def _macd(series: pd.Series):
    fast = _ema(series, 12)
    slow = _ema(series, 26)
    macd = fast - slow
    signal = _ema(macd, 9)
    return macd, signal

def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
    rs = avg_gain / (avg_loss.replace(0, 1e-9))
    return 100 - (100 / (1 + rs))

def find_support_resistance_levels(df: pd.DataFrame, window: int = 10) -> Tuple[List[float], List[float]]:
    closes = df["Close"].values
    supports, resistances = [], []
    for i in range(window, len(closes) - window):
        local = closes[i-window:i+window+1]
        c = closes[i]
        if c == local.min():
            supports.append(float(c))
        if c == local.max():
            resistances.append(float(c))
    def dedupe(levels, tol=0.005):
        levels = sorted(levels)
        out = []
        for lvl in levels:
            if not out or abs(lvl - out[-1]) / max(out[-1], 1e-9) > tol:
                out.append(lvl)
        return out
    return dedupe(supports), dedupe(resistances)

def make_candlestick_with_sr(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(data=[go.Candlestick(
        x=df["Date"], open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
        increasing_line_color="#16a34a", decreasing_line_color="#dc2626"
    )])
    supports, resistances = find_support_resistance_levels(df)
    for s in supports[-5:]:
        fig.add_hline(y=s, line_dash="dot", line_color="#93c5fd", annotation_text="Support", annotation_position="right")
    for r in resistances[-5:]:
        fig.add_hline(y=r, line_dash="dash", line_color="#fca5a5", annotation_text="Resistance", annotation_position="right")
    fig.update_layout(title="Candlestick with Support/Resistance", xaxis_rangeslider_visible=False, height=520)
    return fig

def make_fibonacci_chart(df: pd.DataFrame, lookback: int = 180) -> Tuple[go.Figure, Dict[str, float]]:
    data = df.tail(lookback).copy()
    hi = float(data["High"].max())
    lo = float(data["Low"].min())
    levels = {
        "0%": hi,
        "23.6%": hi - (hi - lo) * 0.236,
        "38.2%": hi - (hi - lo) * 0.382,
        "50%": (hi + lo) / 2,
        "61.8%": hi - (hi - lo) * 0.618,
        "78.6%": hi - (hi - lo) * 0.786,
        "100%": lo,
    }
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data["Date"], y=data["Close"], name="Close", mode="lines"))
    for name, lvl in levels.items():
        fig.add_hline(y=lvl, line_dash="dot", annotation_text=f"Fib {name}", annotation_position="right")
    fig.update_layout(title=f"Fibonacci Retracement (High {hi:.2f} / Low {lo:.2f})", height=420)
    return fig, levels

def make_rsi_macd_chart(df: pd.DataFrame) -> go.Figure:
    close = df["Close"]
    rsi = _rsi(close)
    macd, signal = _macd(close)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Date"], y=rsi, name="RSI", mode="lines"))
    fig.add_hline(y=70, line_dash="dash", line_color="#ef4444")
    fig.add_hline(y=30, line_dash="dash", line_color="#10b981")
    fig.add_trace(go.Scatter(x=df["Date"], y=macd, name="MACD", mode="lines"))
    fig.add_trace(go.Scatter(x=df["Date"], y=signal, name="Signal", mode="lines"))
    fig.update_layout(title="RSI & MACD", height=420)
    return fig
