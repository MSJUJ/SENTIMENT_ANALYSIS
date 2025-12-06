"""
🎓 Learning Corner
------------------
WHY: This class handles the 'External Interface' of our application.
It implements a 'Fallback Pattern':
1. Try the Real API (Happy Path).
2. If it fails (Network error, Rate limit), use Mock Data (Resiliency).
"""
import pandas as pd
import requests
import random
import datetime
from src.config import Config

class NewsFetcher:
    def __init__(self):
        # Load API Key from Config Singleton
        self.api_key = Config().CRYPTO_PANIC_API_KEY
        self.base_url = "https://cryptopanic.com/api/v1/posts/"

    def get_news(self, symbol="BTC"):
        """
        Main entry point. Decides whether to use Real API or Mock Data.
        """
        # Check if we have a real key and it's not the default demo string
        if self.api_key and self.api_key != "DEMO_KEY":
            try:
                # Attempt to fetch real data
                print(f"📡 Connecting to CryptoPanic API for {symbol}...")
                return self._fetch_real_news(symbol)
            except Exception as e:
                # If anything goes wrong (WiFi down, Invalid Key), log it and fallback
                print(f"❌ API Connection Failed: {e}")
                print("⚠️ Falling back to Mock Data.")
                return self._fetch_mock_news(symbol)
        else:
            print("⚠️ No valid API Key found. Using Mock Data.")
            return self._fetch_mock_news(symbol)

    def _fetch_real_news(self, symbol):
        """
        Hits the CryptoPanic API and normalizes the data.
        """
        params = {
            "auth_token": self.api_key,
            "currencies": symbol,
            "kind": "news",
            "filter": "important", # Optional: gets only trending news
            "public": "true"
        }
        
        # Timeout is crucial in SE to prevent hanging processes
        response = requests.get(self.base_url, params=params, timeout=10)
        response.raise_for_status() # Raises error if status != 200
        
        data = response.json()
        results = data.get("results", [])
        
        # Normalize to our app's format (Standardizing the interface)
        normalized_data = []
        for item in results:
            # Handle cases where source might be missing
            source_info = item.get("domain", "CryptoPanic")
            
            # Use .get() to prevent crashes if 'url' or 'title' is missing
            normalized_data.append({
                "title": item.get("title", "No Title"),
                "date": item.get("published_at", datetime.datetime.now().isoformat()),
                "source": source_info,
                "url": item.get("url", "#") 
            })
            
        if not normalized_data:
            print("⚠️ API returned empty list. Switching to mock.")
            return self._fetch_mock_news(symbol)

        return pd.DataFrame(normalized_data)

    def _fetch_mock_news(self, symbol):
        """
        Generates random fake news for testing/offline mode.
        """
        headlines_pool = [
            f"{symbol} hits all-time high!", 
            f"Regulatory concerns crash the {symbol} market.", 
            f"{symbol} network upgrade successful.", 
            "Hackers steal $50M from exchange.",
            "Elon Musk tweets about crypto.",
            f"SEC approves new {symbol} ETF.",
            f"Gas fees on {symbol} drop significantly.",
            "New privacy coin gains popularity."
        ]
        
        # Select 3 to 6 random headlines to make it feel dynamic
        selected_headlines = random.sample(headlines_pool, k=random.randint(3, 6))
        
        news_data = []
        for title in selected_headlines:
            random_hours = random.randint(1, 24)
            date_time = datetime.datetime.now() - datetime.timedelta(hours=random_hours)
            
            news_data.append({
                "title": title, 
                "date": date_time.strftime("%Y-%m-%d %H:%M"),
                "source": "MockSource",
                "url": "#"
            })
            
        return pd.DataFrame(news_data)