import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def plot_candlestick(data):
    df = pd.DataFrame({
        "Open": data["o"],
        "High": data["h"],
        "Low": data["l"],
        "Close": data["c"]
    }, index=pd.to_datetime(data["t"], unit='s'))
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close']
    )])
    st.plotly_chart(fig, use_container_width=True)

def plot_fibonacci(data):
    closes = data["c"]
    high, low = max(closes), min(closes)
    levels = [high - (high - low) * r for r in [0.236,0.382,0.5,0.618,0.786]]
    fig = go.Figure()
    fig.add_scatter(y=closes, mode='lines', name='Close Price')
    for lvl in levels:
        fig.add_hline(y=lvl, line_dash="dot")
    st.plotly_chart(fig, use_container_width=True)

def plot_rsi_macd(data):
    closes = pd.Series(data["c"])
    # RSI
    delta = closes.diff()
    gain = delta.where(delta>0,0)
    loss = -delta.where(delta<0,0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain/avg_loss
    rsi = 100 - (100/(1+rs))
    # MACD
    exp1 = closes.ewm(span=12, adjust=False).mean()
    exp2 = closes.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    fig = go.Figure()
    fig.add_scatter(y=rsi, mode='lines', name='RSI')
    fig.add_scatter(y=macd, mode='lines', name='MACD')
    st.plotly_chart(fig, use_container_width=True)
