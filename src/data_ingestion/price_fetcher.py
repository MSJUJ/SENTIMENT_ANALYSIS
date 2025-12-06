"""
🎓 Learning Corner: Time Series Data
------------------------------------
WHY: To analyze "Impact", we need a baseline. Financial data is 'Time Series' data.
We use 'yfinance' to fetch standardized market candles (OHLCV).
"""
import yfinance as yf
import pandas as pd

class PriceFetcher:
    def get_price_history(self, symbol="BTC", period="7d", interval="1h"):
        """
        Fetches historical price data.
        Args:
            symbol (str): e.g., 'BTC', 'ETH' (Method adds '-USD' automatically)
            period (str): '1d', '5d', '1mo'
            interval (str): '15m', '1h', '1d'
        """
        # Yahoo Finance expects symbols like 'BTC-USD'
        ticker = f"{symbol.upper()}-USD"
        
        try:
            print(f"📉 Fetching prices for {ticker}...")
            # Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
            df = yf.download(ticker, period=period, interval=interval, progress=False)
            
            if df.empty:
                return pd.DataFrame()

            # Flatten multi-index columns if they exist (common yfinance issue)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)
            
            # Reset index so 'Date' becomes a column
            df = df.reset_index()
            return df[['Datetime', 'Close']] if 'Datetime' in df.columns else df[['Date', 'Close']]
            
        except Exception as e:
            print(f"❌ Error fetching prices: {e}")
            return pd.DataFrame()

# Debug
if __name__ == "__main__":
    pf = PriceFetcher()
    print(pf.get_price_history("BTC").head())