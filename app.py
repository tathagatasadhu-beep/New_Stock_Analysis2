import os
import streamlit as st
import pandas as pd

from utils.data_fetch import (
    get_api_key,
    ping_quote,
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

# ===== Diagnostics (masked) =====
api_key = get_api_key()
masked = f"{api_key[:2]}…{api_key[-2:]}" if api_key else "None"
ok_quote, quote_msg = ping_quote("AAPL")
with st.expander("Diagnostics", expanded=False):
    st.write(f"Finnhub key detected: **{bool(api_key)}** ({masked})")
    st.write(f"Quote ping (AAPL): **{'OK' if ok_quote else 'FAIL'}** {quote_msg or ''}")

tab_screener, tab_analysis = st.tabs(["📊 Screener", "🔍 Analysis"])

# ========================= Screener =========================
with tab_screener:
    st.subheader("Idea Finder (technical undervaluation)")

    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        max_rsi = st.number_input("Max RSI", value=55.0, min_value=1.0, max_value=100.0, step=1.0)
    with c2:
        min_pct_below_200ema = st.number_input("Min % below 200-EMA (negative)", value=-3.0, step=0.5)
    with c3:
        top_n = st.number_input("Top N results", value=12, min_value=5, max_value=30, step=1)

    df = fetch_screener_data(
        max_rsi=max_rsi,
        min_pct_below_200ema=min_pct_below_200ema,
        top_n=top_n,
    )

    if df is None or df.empty:
        st.warning("No screener data available. Check your API key in Streamlit Secrets.")
    else:
        st.dataframe(df, use_container_width=True)
        jump = st.selectbox("Open in Analysis", ["— select —"] + df["Ticker"].tolist())
        if jump != "— select —":
            st.session_state["analysis_tkr"] = jump
            st.success(f"{jump} loaded into Analysis tab.")

    st.subheader("Market News")
    news_items = fetch_company_news("AAPL")
    if not news_items:
        st.info("No news available (or API key missing / rate-limited).")
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

    default_ticker = st.session_state.get("analysis_tkr", "AAPL")
    c1, c2, c3 = st.columns([2,1,1])
    with c1:
        ticker = st.text_input("Ticker", value=default_ticker).upper().strip()
    with c2:
        lookback_days = st.number_input("History (days)", value=365, min_value=90, max_value=2000, step=5)
    with c3:
        run_btn = st.button("Run Analysis")

    # Valuation controls
    st.markdown("**DCF Inputs**")
    v1, v2, v3, v4 = st.columns(4)
    with v1:
        discount_rate = st.number_input("Discount Rate (%)", value=10.0, min_value=0.1, step=0.5)
    with v2:
        growth_rate = st.number_input("Years 1–5 Growth (%)", value=5.0, min_value=0.0, step=0.5)
    with v3:
        terminal_growth = st.number_input("Terminal Growth (%)", value=2.5, min_value=0.0, step=0.1)
    with v4:
        years = st.number_input("Projection Years", value=5, min_value=3, max_value=10, step=1)

    if run_btn:
        df_px = fetch_stock_price_history(ticker, days=lookback_days)
        if df_px is None or df_px.empty:
            st.error("Price data unavailable. Check API key or ticker (see Diagnostics).")
        else:
            # Charts
            st.plotly_chart(make_candlestick_with_sr(df_px), use_container_width=True)
            fig_fib, fib_levels = make_fibonacci_chart(df_px)
            st.plotly_chart(fig_fib, use_container_width=True)
            st.plotly_chart(make_rsi_macd_chart(df_px), use_container_width=True)

            # S/R + DCF quick plan
            supports, resistances = find_support_resistance_levels(df_px)
            last = float(df_px["Close"].iloc[-1])
            est_fcf_default = round(last * 0.05, 2)
            est_fcf = st.slider("Est. Starting FCF per Share ($)", 0.0, max(50.0, est_fcf_default*3), est_fcf_default, 0.1)
            intrinsic = dcf_valuation(
                start_fcf_per_share=est_fcf,
                growth_rate=growth_rate,
                discount_rate=discount_rate,
                terminal_growth=terminal_growth,
                years=years
            )
            st.success(f"Intrinsic Value (per share): **${intrinsic:,.2f}**  |  Last Price: **${last:,.2f}**")

            nearest_support = max([s for s in supports if s < last], default=None)
            nearest_resistance = min([r for r in resistances if r > last], default=None)
            st.markdown("### Plain-English Summary")
            lines = []
            if "38.2%" in fib_levels:
                lines.append(f"- Pullback entry near **Fib 38.2% ≈ ${fib_levels['38.2%']:.2f}**; deeper value near **61.8% ≈ ${fib_levels['61.8%']:.2f}**.")
            if nearest_support:
                lines.append(f"- Nearest support: **${nearest_support:.2f}** (consider stop just below).")
            if nearest_resistance:
                lines.append(f"- First target zone: **${nearest_resistance:.2f}**.")
            relation = "discount" if intrinsic > last else "premium"
            lines.append(f"- DCF suggests a {relation}: Intrinsic **${intrinsic:,.2f}** vs Price **${last:,.2f}**.")
            st.markdown("\n".join(lines))

            st.subheader("Latest Company News")
            news = fetch_company_news(ticker)
            if not news:
                st.info("No ticker-specific news (or API limit reached).")
            else:
                for n in news[:8]:
                    headline = n.get("headline") or "No headline"
                    url = n.get("url") or ""
                    source = n.get("source") or ""
                    dt = n.get("datetime")
                    when = pd.to_datetime(dt, unit="s").strftime("%Y-%m-%d %H:%M") if isinstance(dt, (int, float)) else ""
                    st.markdown(f"- [{headline}]({url})  \n  <small>{source} • {when}</small>", unsafe_allow_html=True)
