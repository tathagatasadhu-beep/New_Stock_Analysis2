import plotly.graph_objects as go

def generate_fib_chart(price_data):
    fig = go.Figure()
    if price_data and "c" in price_data:
        close_price = price_data["c"]
        levels = [close_price * (1 - x) for x in [0, 0.236, 0.382, 0.5, 0.618, 1]]
        for lvl in levels:
            fig.add_hline(y=lvl, line_dash="dot")
        fig.add_scatter(y=[close_price], x=[0], mode="markers", marker=dict(size=12, color='red'))
        fig.update_layout(title="Fibonacci Retracement Levels")
    return fig

def generate_technical_chart(price_data):
    fig = go.Figure()
    if price_data and "c" in price_data:
        close_price = price_data["c"]
        fig.add_candlestick(open=[close_price-1], high=[close_price+1],
                            low=[close_price-2], close=[close_price])
        fig.update_layout(title="Candlestick with RSI/MACD (Simplified)")
    return fig
