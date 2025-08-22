import streamlit as st
from utils.data_fetch import fetch_top50_screener, fetch_analysis_data, fetch_company_news
from utils.charts import plot_candlestick, plot_rsi_macd_fib

st.set_page_config(page_title="Stock Analysis Suite", layout="wide")

st.title("Stock Analysis Suite")

tab1, tab2 = st.tabs(["📊 Screener", "🔍 Analysis"])

# ------------------- SCREENER TAB -------------------
with tab1:
    st.subheader("Top Undervalued S&P 500 Stocks")
    try:
        df = fetch_top50_screener()
        if df is not None and not df.empty:
            st.dataframe(df)
        else:
            st.warning("No screener data available. Check API key or endpoint.")
    except Exception as e:
        st.error(f"Screener Error: {e}")

    st.subheader("Market News")
    news = fetch_company_news("AAPL")
    if news:
        for n in news[:5]:
            st.write(f"**{n.get('headline', 'No headline')}**")
            st.caption(n.get('summary', ''))
    else:
        st.info("No news available. Check your API key or try again later.")

# ------------------- ANALYSIS TAB -------------------
with tab2:
    st.subheader("Stock Technical & Fundamental Analysis")

    ticker = st.text_input("Enter Ticker Symbol:", "AAPL").upper()
    if st.button("Run Analysis"):
        try:
            data = fetch_analysis_data(ticker)

            if "price_data" not in data or data["price_data"] is None:
                st.error("Price data unavailable. Check API key or ticker.")
            else:
                st.plotly_chart(plot_candlestick(data["price_data"]), use_container_width=True)
                st.plotly_chart(plot_rsi_macd_fib(data["price_data"]), use_container_width=True)

            if "valuation" in data:
                st.subheader("Valuation (DCF Approximation)")
                st.json(data["valuation"])
            else:
                st.info("No valuation data available.")

        except Exception as e:
            st.error(f"Analysis Error: {e}")
