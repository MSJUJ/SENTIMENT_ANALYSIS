"""
🎓 Learning Corner: The Presentation Layer
------------------------------------------
WHY:
1. This file orchestrates the interaction between User and System.
2. It maintains 'Session State' to remember data between clicks.
3. It integrates all modules: Ingestion (News/Price), IR (Cleaning/Ranking), and SE (Sentiment).
"""

import streamlit as st
import pandas as pd
import sys
import os
import time
import plotly.graph_objects as go # <--- For advanced charting
from plotly.subplots import make_subplots

# --- PATH SETUP ---
# Add project root to path so we can import src modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.data_ingestion.news_fetcher import NewsFetcher
from src.data_ingestion.price_fetcher import PriceFetcher
from src.ir_engine.preprocessor import TextCleaner
from src.ir_engine.sentiment import SentimentFactory
from src.ir_engine.ranker import Ranker

st.set_page_config(page_title="Crypto IR Engine", layout="wide")

def main():
    st.title("🚀 Crypto News & Sentiment Impact Analyzer")
    
    # --- SIDEBAR CONFIGURATION ---
    st.sidebar.header("⚙️ Configuration")
    symbol = st.sidebar.selectbox("Select Asset", ["BTC", "ETH", "SOL", "ADA", "XRP"])
    model_type = st.sidebar.selectbox("Sentiment Model", ["vader", "finbert", "random"])
    
    if st.sidebar.button("🔄 Clear Cache & Reset"):
        st.cache_data.clear()
        if 'news_data' in st.session_state:
            del st.session_state['news_data']
        if 'price_data' in st.session_state:
            del st.session_state['price_data']
        st.rerun()

    # --- HELPER FUNCTIONS ---
    def load_news(sym):
        fetcher = NewsFetcher()
        return fetcher.get_news(symbol=sym)

    def load_prices(sym):
        fetcher = PriceFetcher()
        # Fetch 7 days of hourly data for a good chart comparison
        return fetcher.get_price_history(symbol=sym, period="7d", interval="1h")

    # --- STEP 1: FETCH DATA ---
    if st.sidebar.button("📡 Fetch Market Data"):
        with st.spinner(f"Fetching news and prices for {symbol}..."):
            # 1. Fetch News
            news_df = load_news(symbol)
            st.session_state['news_data'] = news_df
            
            # 2. Fetch Prices
            price_df = load_prices(symbol)
            st.session_state['price_data'] = price_df
            
            st.session_state['fetch_time'] = time.strftime("%H:%M:%S")

    # --- DISPLAY LOGIC ---
    if 'news_data' in st.session_state:
        df = st.session_state['news_data']
        price_df = st.session_state.get('price_data', pd.DataFrame())
        fetch_time = st.session_state.get('fetch_time', '')
        
        st.success(f"Data Loaded at {fetch_time} ({len(df)} articles)")

        # --- STEP 2: PREPROCESSING (IR) ---
        cleaner = TextCleaner()
        df['clean_text'] = df['title'].apply(cleaner.clean_to_string)
        
        # --- STEP 3: SEARCH / RANKING (IR) ---
        st.divider()
        st.subheader("🔍 Semantic Search Engine")
        
        col_search, col_help = st.columns([3, 1])
        with col_search:
            search_query = st.text_input("Filter news (e.g., 'hack', 'ETF', 'price')")
        
        # Initialize and Train Ranker on current data
        ranker = Ranker()
        ranker.fit(df['clean_text'].tolist())
        
        display_df = df
        if search_query:
            results = ranker.search(search_query)
            if results:
                st.info(f"Found {len(results)} relevant documents using TF-IDF.")
                indices = [res['index'] for res in results]
                display_df = df.iloc[indices]
            else:
                st.warning("No relevant articles found matching your query. Showing all.")

        # --- STEP 4: SENTIMENT ANALYSIS (SE) ---
        st.subheader(f"Sentiment Analysis ({model_type.upper()})")
        
        model = SentimentFactory.get_model(model_type)
        
        # Copy df to avoid pandas warnings
        display_df = display_df.copy()
        display_df['sentiment_score'] = display_df['clean_text'].apply(model.analyze)
        
        # --- STEP 5: VISUALIZATION (IMPACT ANALYZER) ---
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Show Table
            st.dataframe(
                display_df[['date', 'title', 'sentiment_score']], 
                use_container_width=True
            )
            
            # Metric
            avg_score = display_df['sentiment_score'].mean()
            st.metric(label="Market Sentiment Signal", value=f"{avg_score:.4f}")
            if avg_score > 0.05:
                st.success("📈 SIGNAL: BUY")
            elif avg_score < -0.05:
                st.error("📉 SIGNAL: SELL")
            else:
                st.warning("⚖️ SIGNAL: HOLD")

        with col2:
            st.markdown("### 📉 Price vs Sentiment Correlation")
            
            # Create Dual Axis Chart
            fig = make_subplots(specs=[[{"secondary_y": True}]])

            # 1. Price Line
            if not price_df.empty:
                # Handle flexible column names from yfinance
                date_col = 'Datetime' if 'Datetime' in price_df.columns else 'Date'
                fig.add_trace(
                    go.Scatter(x=price_df[date_col], y=price_df['Close'], name="Price (USD)", line=dict(color='blue')),
                    secondary_y=False
                )

            # 2. Sentiment Scatter
            # Map colors: Green (Positive), Red (Negative)
            colors = ['green' if x > 0 else 'red' for x in display_df['sentiment_score']]
            
            fig.add_trace(
                go.Bar(
                    x=display_df['date'], 
                    y=display_df['sentiment_score'], 
                    name="News Sentiment",
                    marker_color=colors,
                    opacity=0.6
                ),
                secondary_y=True
            )

            fig.update_layout(title_text=f"{symbol} Price & News Impact")
            fig.update_yaxes(title_text="Price ($)", secondary_y=False)
            fig.update_yaxes(title_text="Sentiment Score", secondary_y=True, range=[-1, 1])

            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()