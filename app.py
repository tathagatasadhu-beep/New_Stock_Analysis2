import streamlit as st
from utils.data_fetch import fetch_top50_screener, fetch_analysis_data
from utils.charts import plot_candlestick, plot_fibonacci, plot_rsi_macd
from utils.valuation import dcf_valuation
from utils.news import fetch_news

st.set_page_config(page_title="Stock Analysis Suite", layout="wide")
tab1, tab2 = st.tabs(["Screener", "Analysis"])

# ----------------- Screener ----------------- #
with tab1:
    st.header("Top 50 S&P 500 Stocks Screener")
    st.write("Ranked by undervaluation, PE, PEG, RSI")

    df = fetch_top50_screener()
    st.dataframe(df, use_container_width=True)

    st.subheader("Market News (AAPL default)")
    news_items = fetch_news("AAPL")
    if news_items:
        for n in news_items:
            st.markdown(f"- [{n['headline']}]({n['url']})")
    else:
        st.info("No news available. Check your API key.")

# ----------------- Analysis ----------------- #
with tab2:
    st.header("Detailed Stock Analysis")
    ticker = st.text_input("Enter Ticker Symbol", "AAPL")
    discount_rate = st.number_input("Discount Rate (%)", 10)
    growth_rate = st.number_input("Growth Rate (%)", 5)
    years = st.number_input("Projection Years", 5)

    if st.button("Run Analysis"):
        if not ticker:
            st.error("Please enter a ticker symbol.")
        else:
            data = fetch_analysis_data(ticker)
            if data:
                st.subheader("Candlestick Chart + Support/Resistance")
                plot_candlestick(data["price_data"])

                st.subheader("Fibonacci Retracement")
                plot_fibonacci(data["price_data"])

                st.subheader("RSI + MACD Indicators")
                plot_rsi_macd(data["price_data"])

                st.subheader("DCF Valuation")
                intrinsic_value = dcf_valuation(data["price_data"], discount_rate, growth_rate, years)
                st.success(f"Intrinsic Value: ${intrinsic_value:.2f}")

                st.subheader("Latest Company News")
                news_items = fetch_news(ticker)
                if news_items:
                    for n in news_items:
                        st.markdown(f"- [{n['headline']}]({n['url']})")
                else:
                    st.info("No news available for this ticker.")
            else:
                st.error("Failed to fetch data for this ticker. Check API key or ticker.")
