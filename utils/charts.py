import plotly.graph_objects as go
import pandas as pd

def plot_candlestick(df):
    """Generates candlestick chart"""
    fig = go.Figure(
        data=[go.Candlestick(
            x=df['Date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close']
        )]
    )
    fig.update_layout(
        title="Candlestick Chart",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        height=500
    )
    return fig


def plot_rsi_macd_fib(df):
    """Placeholder RSI + MACD + Fibonacci Retracement chart"""
    fig = go.Figure()

    # RSI (Mock)
    df['RSI'] = 50  # Placeholder constant value

    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['RSI'],
        name='RSI',
        line=dict(color='yellow')
    ))

    # Fibonacci Retracement (Mock)
    high = df['High'].max()
    low = df['Low'].min()
    levels = [0.236, 0.382, 0.5, 0.618, 0.786]
    for lvl in levels:
        value = high - (high - low) * lvl
        fig.add_hline(y=value, line_dash="dash", annotation_text=f"Fib {lvl*100:.1f}%")

    fig.update_layout(
        title="RSI + Fibonacci Levels (Demo)",
        xaxis_title="Date",
        yaxis_title="Indicator Value",
        template="plotly_dark",
        height=500
    )

    return fig
