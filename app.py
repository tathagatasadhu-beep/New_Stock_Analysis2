import streamlit as st
from utils.data_fetch import fetch_screener_data, fetch_analysis_data
from utils.news import fetch_news
from utils.charts import generate_fib_chart, generate_technical_chart

st.set_page_config(page_title="Stock Analysis Suite", layout="wide")

# Tabs for single-page navigation
tab1, tab2 = st.tabs(["Screener", "Analysis"])

with tab1:
    st.header("Stock Screener")
    st.write("Discover undervalued S&P 500 stocks with live metrics and news.")

    data = fetch_screener_data()
    if not data.empty:
        st.dataframe(data, use_container_width=True)
    else:
        st.warning("No data available.")

    st.subheader("Market News")
    news_items = fetch_news("AAPL")  # Default news feed
    for item in news_items:
        st.write(f"**{item['headline']}** - {item['source']} ({item['datetime']})")
        st.write(item['summary'])
        st.write("---")

with tab2:
    st.header("Stock Analysis")
    ticker = st.text_input("Enter Ticker Symbol (e.g., AAPL)", "AAPL")

    if st.button("Run Analysis"):
        analysis_data = fetch_analysis_data(ticker)

        if analysis_data:
            st.subheader("Valuation & Metrics")
            st.write(analysis_data["valuation"])
            st.write(analysis_data["metrics"])

            st.subheader("Technical Charts")
            st.plotly_chart(generate_fib_chart(analysis_data["price_data"]), use_container_width=True)
            st.plotly_chart(generate_technical_chart(analysis_data["price_data"]), use_container_width=True)

            st.subheader("Plain English Analysis")
            st.write(analysis_data["analysis_text"])
        else:
            st.error("No analysis data found.")
