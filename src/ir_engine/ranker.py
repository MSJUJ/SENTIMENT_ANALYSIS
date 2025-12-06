"""
🎓 Learning Corner: TF-IDF & Cosine Similarity
----------------------------------------------
1. TF-IDF (Term Frequency - Inverse Document Frequency):
   - Converts text to numbers.
   - 'Bitcoin' appears often? High TF.
   - 'The' appears everywhere? Low IDF (penalized).
   
2. Cosine Similarity:
   - Measures the angle between two vectors (arrows).
   - 1.0 = Same direction (Perfect Match).
   - 0.0 = 90 degrees (No relevance).
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class Ranker:
    def __init__(self):
        # min_df=1 ensures we don't drop words even if they only appear once
        # stop_words='english' removes "the", "is", "at", etc. automagically
        self.vectorizer = TfidfVectorizer(stop_words='english', min_df=1)
        self.tfidf_matrix = None
        self.documents = []

    def fit(self, documents):
        """
        'Learns' the vocabulary from the news headlines.
        """
        self.documents = documents
        # fit_transform: Learns vocabulary AND creates the matrix
        self.tfidf_matrix = self.vectorizer.fit_transform(documents)

    def search(self, query, top_k=3):
        """
        Ranks documents based on similarity to the query.
        """
        if not self.documents:
            return []

        # 1. Convert Query to Vector (using the same vocabulary we learned)
        query_vec = self.vectorizer.transform([query])

        # 2. Calculate Cosine Similarity (Query vs All Docs)
        # Returns an array like [[0.1], [0.8], [0.0]]
        similarity_scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        # 3. Sort Results
        # argsort() gives indices of sorted elements (ascending)
        # [::-1] flips it to descending (highest score first)
        sorted_indices = similarity_scores.argsort()[::-1]

        results = []
        for idx in sorted_indices[:top_k]:
            score = similarity_scores[idx]
            # Only return relevant results (score > 0)
            if score > 0:
                results.append({
                    "index": idx,
                    "score": round(score, 4),
                    "document": self.documents[idx]
                })
        
        return results

# --- DEBUG / TEST SECTION ---
if __name__ == "__main__":
    # 1. Mock Data
    news = [
        "Bitcoin hits all-time high price",      # Doc 0
        "Hackers steal 50 million from DAO",    # Doc 1
        "Government regulations impacting market", # Doc 2
        "Ethereum upgrade scheduled for next week" # Doc 3
    ]
    
    # 2. Init Ranker
    ranker = Ranker()
    ranker.fit(news)
    
    # 3. Test Search
    # "market" appears in Doc 2. "price" appears in Doc 0.
    test_query = "market price" 
    
    print(f"🔎 Searching for: '{test_query}'")
    hits = ranker.search(test_query)
    
    for hit in hits:
        print(f"   [Score: {hit['score']}] {hit['document']}")