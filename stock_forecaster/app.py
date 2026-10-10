import streamlit as st
import plotly.graph_objects as go
from data_processor import fetch_stock_data, fetch_news_sentiment
from model import train_and_predict

st.set_page_config(page_title="AI Stock Forecaster", layout="wide")

st.title("📈 Stock Price Forecasting & NLP Sentiment Engine")
st.caption("A multi-modal data pipeline mapping real-time text analysis onto historic pricing trends.")

# Sidebar Controls
st.sidebar.header("Pipeline Hyperparameters")
ticker = st.sidebar.selectbox("Select Asset Ticker", ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA"])
lookback = st.sidebar.slider("Lookback Delay Window (Days)", min_value=2, max_value=10, value=5)
range_days = st.sidebar.slider("Historical Dataset Depth (Days)", min_value=90, max_value=500, value=365)

if st.sidebar.button("⚡ Run ML Execution Pipeline"):
    with st.spinner("Processing live network queries..."):
        
        # Pull Data Streams
        stock_df = fetch_stock_data(ticker, days=range_days)
        sentiment_val = fetch_news_sentiment(ticker)
        
        # Display Metrics
        st.subheader(f"Real-Time Metrics Environment: {ticker}")
        m1, m2, m3 = st.columns(3)
        
        current_price = stock_df['Close'].iloc[-1]
        m1.metric("Latest Market Close", f"${current_price:.2f}")
        m2.metric("Extracted Sentiment Index", f"{sentiment_val:.2f}")
        
        status = "BULLISH 🟢" if sentiment_val > 0.05 else ("BEARISH 🔴" if sentiment_val < -0.05 else "NEUTRAL 🟡")
        m3.metric("NLP Categorization", status)
        
        # Compute Inference Engine Results
        prediction = train_and_predict(stock_df, sentiment_val, lookback=lookback)
        
        if prediction:
            st.success(f"🔮 **Model Estimated Next Close Target Value:** ${prediction:.2f}")
            
            # Interactive Candlestick Chart Output
            fig = go.Figure(data=[go.Candlestick(
                x=stock_df['Date'],
                open=stock_df['Open'],
                high=stock_df['High'],
                low=stock_df['Low'],
                close=stock_df['Close'],
                name="Market Path"
            )])
            fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, title=f"Historical Candlestick Profile ({ticker})")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Engine failure: Lookback constraint parameters exceed data dataframe limits.")