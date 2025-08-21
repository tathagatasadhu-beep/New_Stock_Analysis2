
import matplotlib.pyplot as plt
import yfinance as yf

def plot_fibonacci_chart(ticker):
    try:
        data = yf.download(ticker, period="6mo")
        max_price = data['Close'].max()
        min_price = data['Close'].min()

        levels = [max_price - (max_price - min_price) * r for r in [0, 0.236, 0.382, 0.5, 0.618, 1]]
        fig, ax = plt.subplots(figsize=(10,5))
        ax.plot(data.index, data['Close'], label="Close Price", color='blue')
        colors = ['red', 'orange', 'green', 'purple', 'brown', 'pink']
        for lvl, c in zip(levels, colors):
            ax.axhline(lvl, linestyle='--', alpha=0.8, linewidth=2, color=c)
        ax.set_title(f"Fibonacci Retracement - {ticker}")
        ax.legend()
        return fig
    except:
        return None
