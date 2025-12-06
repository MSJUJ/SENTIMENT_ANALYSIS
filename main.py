""" # Notice how we now import using the folder paths
from src.data_ingestion.news_fetcher import NewsFetcher
from src.ir_engine.preprocessor import TextCleaner
from src.ir_engine.sentiment import SentimentFactory

def main():
    print("🚀 Starting Crypto Analyzer...")

    # 1. Instantiate our Helper Classes
    fetcher = NewsFetcher()
    cleaner = TextCleaner()
    
    # 2. Get Data
    df = fetcher.get_news()
    
    # 3. Choose Model via Factory
    model_name = input("Choose model (vader/finbert/random): ")
    try:
        model = SentimentFactory.get_model(model_name)
    except ValueError as e:
        print(e)
        return

    print(f"\nAnalyzing using {model_name.upper()}...\n")

    # 4. Run Loop
    for index, row in df.iterrows():
        raw_text = row['title']
        
        # Clean
        clean_text = cleaner.clean_to_string(raw_text)
        
        # Score
        score = model.analyze(clean_text)
        
        print(f"Title: {raw_text}")
        print(f"Score: {score:.4f}")
        print("-" * 20)

if __name__ == "__main__":
    main() """

from src.data_ingestion.news_fetcher import NewsFetcher
from src.ir_engine.preprocessor import TextCleaner
from src.ir_engine.sentiment import SentimentFactory
from src.ir_engine.ranker import Ranker  # <--- NEW IMPORT

def main():
    print("🚀 Crypto Analyzer 2.0 (Search Enabled)...")

    # 1. Instantiate Modules
    fetcher = NewsFetcher()
    cleaner = TextCleaner()
    ranker = Ranker() 
    
    # 2. Get Data
    df = fetcher.get_news()
    documents = df['title'].tolist() # Convert column to list for Ranker
    
    # 3. Fit Ranker (Index the news)
    print("📚 Indexing news articles...")
    ranker.fit(documents)
    
    # 4. Search Loop
    while True:
        query = input("\n🔍 Enter search topic (or 'all' to list everything, 'q' to quit): ")
        
        if query.lower() == 'q':
            break
            
        results_to_process = []

        if query.lower() == 'all':
            # Just take everything
            results_to_process = [{"document": doc} for doc in documents]
        else:
            # Use Ranker
            results = ranker.search(query)
            if not results:
                print("❌ No relevant news found.")
                continue
            results_to_process = results

        # 5. Analyze Sentiment on the Results
        model_name = "vader" # Hardcoded for simplicity, or ask user
        model = SentimentFactory.get_model(model_name)

        print(f"\n--- Analysis Results ({len(results_to_process)} articles) ---")
        for item in results_to_process:
            text = item['document']
            
            # Clean & Score
            clean_text = cleaner.clean_to_string(text)
            sentiment_score = model.analyze(clean_text)
            
            # If it came from search, show relevance score too
            relevance = f" (Relevance: {item['score']})" if 'score' in item else ""
            
            print(f"Title: {text}")
            print(f"Stats: Sentiment: {sentiment_score:.2f}{relevance}")
            print("-" * 20)

if __name__ == "__main__":
    main()