"""
🎓 Learning Corner: Unit Testing & TDD
--------------------------------------
WHY: 
1. Verification: Proves your manual 'TextCleaner' logic actually works (e.g., handles URLs, removes stopwords).
2. Regression Testing: If you cahange code later, these tests warn you if you broke something.
3. Documentation: Tests show exactly how your classes are expected to behave.

SEARCH TERMS:
- "Python unittest vs pytest"
- "Mocking in Python unit tests"
- "Test Driven Development cycles"
"""

import unittest
import sys
import os

# 1. Add the project root to the system path so Python can find 'src'
# This is necessary because tests/ is a separate folder from src/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.ir_engine.preprocessor import TextCleaner
from src.ir_engine.ranker import Ranker

class TestIREngine(unittest.TestCase):
    
    def setUp(self):
        """Runs BEFORE every test method. Great for initialization."""
        self.cleaner = TextCleaner()
        self.ranker = Ranker()

    # --- PART 1: Preprocessor Tests (TextCleaner) ---

    def test_cleaner_basic(self):
        """Test simple tokenization and lowercase."""
        raw_text = "Bitcoin IS rising!"
        expected = ["bitcoin", "is", "rising"]
        # Our cleaner removes punctuation, so '!' goes away.
        self.assertEqual(self.cleaner.clean(raw_text), expected)

    def test_cleaner_stopwords(self):
        """Test if it handles common words (logic depends on your implementation)."""
        # If you implemented stopword removal in preprocessor, this checks it.
        # If your preprocessor keeps them (and Ranker removes them), this tests tokenization.
        raw = "The price of BTC"
        tokens = self.cleaner.clean(raw)
        self.assertIn("btc", tokens)
        self.assertIn("price", tokens)

    def test_cleaner_edge_cases(self):
        """Test URLs and Numbers."""
        raw = "Buy at $50000 https://crypto.com"
        tokens = self.cleaner.clean(raw)
        # Check that numbers are kept (if your regex allows) or removed
        # Based on your previous regex r'[^a-z0-9\s]', numbers should be KEPT
        self.assertIn("50000", tokens)
        # URL handling: regex usually strips punctuation, so 'https://...' might break into parts
        # Just ensure it doesn't crash
        self.assertTrue(len(tokens) > 0)

    # --- PART 2: Ranker Tests (TF-IDF) ---

    def test_ranker_indexing(self):
        """Ensure Ranker can learn a vocabulary."""
        docs = ["Bitcoin price", "Ethereum smart contracts"]
        self.ranker.fit(docs)
        # After fitting, the matrix should exist
        self.assertIsNotNone(self.ranker.tfidf_matrix)
        # Vocabulary size should be > 0
        self.assertTrue(len(self.ranker.vectorizer.vocabulary_) > 0)

    def test_ranker_search_exact_match(self):
        """Searching for 'Bitcoin' should find the Bitcoin document."""
        docs = ["Bitcoin is king", "Ethereum is queen"]
        self.ranker.fit(docs)
        
        results = self.ranker.search("bitcoin")
        # Should return 1 result (or 2 if 'is' matches, but bitcoin should be top)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]['index'], 0) # Index 0 is the Bitcoin doc

    def test_ranker_search_no_match(self):
        """Searching for 'Pizza' should return nothing."""
        docs = ["Bitcoin mining", "Crypto trading"]
        self.ranker.fit(docs)
        
        results = self.ranker.search("pizza")
        self.assertEqual(results, [])

if __name__ == '__main__':
    unittest.main()