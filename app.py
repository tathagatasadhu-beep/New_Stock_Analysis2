import os
import streamlit as st
import pandas as pd

from utils.data_fetch import (
    fetch_screener_data,
    fetch_stock_price_history,
    fetch_company_news,
)
from utils.charts import (
    make_candlestick_with_sr,
    make_fibonacci_chart,
    make_rsi_macd_chart,
    find_support_resistance_levels,
)
from utils.valuation import dcf_valuation

st.set_page_config(page_title="Stock Analysis Suite", layout="wide")
st.title("Stock Analysis Suite")

# Show whether key is wired (not the key itself)
api_ok = bool(st.secrets.get("FINNHUB_API_KEY", os.getenv("FINNHUB_API_KEY", "")))
st.caption(f"Finnhub API: {'✅ detected' if api_ok else '⚠️ missing'}")

tab_screener, tab_analysis = st.tabs(["📊 Screener", "🔍 Analysis"])

# ========================= Screener =========================
with tab_screener:
    st.subheader("Discover ideas (ranking by valuation + momentum)")

    # Screener controls
    colf1, colf2, colf3, colf4 = st.columns([1,1,1,1])
    with colf1:
        max_pe = st.number_input("Max P/E", value=30.0, min_value=0.0, step=1.0)
    with colf2:
        max_peg = st.number_input("Max PEG", value=2.0, min_value=0.0, step=0.1)
    with colf3:
        max_rsi = st.number_input("Max RSI", value=55.0, min_value=0.0, max_value=100.0, step=1.0)
    with colf4:
        top_n = st.number_input("Show Top N", value=15, min_value=5, max_value=50, step=1)

    screener_df = fetch_screener_data(max_pe=max_pe, max_peg=max_peg, max_rsi=max_rsi, top_n=top_n)

    if screener_df is None or screener_df.empty:
        st.warning("No screener data available. Check your API key in Streamlit Secrets.")
    else:
        st.dataframe(screener_df, use_container_width=True)

        # Quick open in Analysis
        tickers = screener_df["Ticker"].head(10).tolist()
        selected = st.selectbox("Open a ticker in Analysis", options=["— select —"] + tickers, index=0)
        if selected != "— select —":
            st.session_state.setdefault("analysis_ticker", selected)
            st.success(f"Loaded {selected} into Analysis tab. Switch to the Analysis tab to run.")

    st.subheader("Market News")
    # Default to AAPL for broad-interest headlines
    news_items = fetch_company_news("AAPL")
    if not news_items:
        st.info("No news available (or API key missing).")
    else:
        for n in news_items:
            headline = n.get("headline") or "No headline"
            url = n.get("url") or ""
            source = n.get("source") or ""
            dt = n.get("datetime")
            when = pd.to_datetime(dt, unit="s").strftime("%Y-%m-%d %H:%M") if isinstance(dt, (int, float)) else ""
            st.markdown(f"- [{headline}]({url})  \n  <small>{source} • {when}</small>", unsafe_allow_html=True)

# ========================= Analysis =========================
with tab_analysis:
    st.subheader("Deep Dive: Technicals + DCF")

    default_ticker = st.session_state.get("analysis_ticker", "AAPL")
    c1, c2, c3 = st.columns([2,1,1])
    with c1:
        ticker = st.text_input("Ticker", value=default_ticker).upper().strip()
    with c2:
        lookback_days = st.number_input("History (days)", value=365, min_value=60, max_value=2000, step=5)
    with c3:
        run_btn = st.button("Run Analysis")

    # Valuation controls
    st.markdown("**DCF Inputs**")
    v1, v2, v3, v4 = st.columns(4)
    with v1:
        discount_rate = st.number_input("Discount Rate (%)", value=10.0, min_value=0.0, step=0.5)
    with v2:
        growth_rate = st.number_input("Years 1–5 Growth (%)", value=5.0, min_value=0.0, step=0.5)
    with v3:
        terminal_growth = st.number_input("Terminal Growth (%)", value=2.5, min_value=0.0, step=0.1)
    with v4:
        years = st.number_input("Projection Years", value=5, min_value=3, max_value=10, step=1)

    if run_btn:
        df = fetch_stock_price_history(ticker, days=lookback_days)

        if df is None or df.empty:
            st.error("Price data unavailable. Check API key or ticker.")
        else:
            # Main candlestick + S/R
            fig_candle = make_candlestick_with_sr(df)
            st.plotly_chart(fig_candle, use_container_width=True)

            # Fibonacci
            fig_fib, fib_levels = make_fibonacci_chart(df)
            st.plotly_chart(fig_fib, use_container_width=True)

            # RSI + MACD
            fig_ind = make_rsi_macd_chart(df)
            st.plotly_chart(fig_ind, use_container_width=True)

            # Compute S/R for narrative
            supports, resistances = find_support_resistance_levels(df)
            last = float(df["Close"].iloc[-1])

            # DCF – estimate starting FCF/share as 5% of price (editable via slider)
            est_fcf_share_default = round(last * 0.05, 2)
            est_fcf_share = st.slider("Est. Starting FCF per Share ($)", 0.0, max(50.0, est_fcf_share_default*3), est_fcf_share_default, 0.1)
            intrinsic = dcf_valuation(
                start_fcf_per_share=est_fcf_share,
                growth_rate=growth_rate,
                discount_rate=discount_rate,
                terminal_growth=terminal_growth,
                years=years
            )
            st.success(f"Intrinsic Value (per share): **${intrinsic:,.2f}**  |  Last Price: **${last:,.2f}**")

            # Trading plan (simple heuristic)
            nearest_support = max([s for s in supports if s < last], default=None)
            nearest_resistance = min([r for r in resistances if r > last], default=None)
            fib_382 = fib_levels.get("38.2%")
            fib_618 = fib_levels.get("61.8%")

            st.markdown("### Plain-English Summary")
            bullets = []
            if fib_382:
                bullets.append(f"- Pullback entry near **Fib 38.2% ≈ ${fib_382:,.2f}**; deeper value near **61.8% ≈ ${fib_618:,.2f}**.")
            if nearest_support:
                bullets.append(f"- Nearest support: **${nearest_support:,.2f}** (place stop slightly below).")
            if nearest_resistance:
                bullets.append(f"- First target/trim zone: **${nearest_resistance:,.2f}**.")
            premium_disc = "discount" if intrinsic > last else "premium"
            bullets.append(f"- DCF suggests a {premium_disc} vs. price (Intrinsic **${intrinsic:,.2f}** vs. **${last:,.2f}**).")
            if not bullets:
                bullets.append("- Price structure is mixed; wait for clearer setup or tighten risk.")

            st.markdown("\n".join(bullets))

            # Latest company news for this ticker
            st.subheader("Latest News")
            news = fetch_company_news(ticker) or []
            if not news:
                st.info("No news found for this ticker (or API limit reached).")
            else:
                for n in news[:8]:
                    headline = n.get("headline") or "No headline"
                    url = n.get("url") or ""
                    source = n.get("source") or ""
                    dt = n.get("datetime")
                    when = pd.to_datetime(dt, unit="s").strftime("%Y-%m-%d %H:%M") if isinstance(dt, (int, float)) else ""
                    st.markdown(f"- [{headline}]({url})  \n  <small>{source} • {when}</small>", unsafe_allow_html=True)
