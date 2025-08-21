import streamlit as st
import sys, os

# Ensure utils folder is in Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_fetch import fetch_screener_data, fetch_analysis_data
from utils.news import get_stock_news
from utils.charts import plot_fibonacci_chart

st.set_page_config(page_title="Stock Analysis Suite", layout="wide")
st.title("Stock Analysis Suite")

tab1, tab2 = st.tabs(["Screener", "Analysis"])

# --- Screener Tab ---
with tab1:
    st.subheader("Stock Screener - Live (S&P 500)")
    data = fetch_screener_data()
    if data is not None:
        st.dataframe(data)
        selected_stock = st.selectbox("Select a stock for news", data['Ticker'])
        if selected_stock:
            st.subheader(f"Latest News for {selected_stock}")
            news_items = get_stock_news(selected_stock)
            if news_items:
                for n in news_items:
                    st.write(f"**{n['headline']}** - {n['datetime']}")
                    st.write(n['summary'])
                    st.markdown("---")
            else:
                st.write("No news available.")
    else:
        st.write("No data available.")

# --- Analysis Tab ---
with tab2:
    st.subheader("Stock Analysis")
    ticker = st.text_input("Enter a Stock Ticker (e.g., AAPL)", "AAPL")

    if ticker:
        analysis = fetch_analysis_data(ticker)
        if analysis:
            st.write(analysis)
            st.subheader("Fibonacci Retracement")
            fib_chart = plot_fibonacci_chart(ticker)
            st.pyplot(fib_chart)
        else:
            st.write("Unable to retrieve analysis data.")
