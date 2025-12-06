"""
🎓 Learning Corner: Factory Pattern & Transformers
--------------------------------------------------
WHY: 
1. The Factory Pattern separates 'Using' a model from 'Creating' it.
2. FinBERT is a 'Transformer' model (BERT) fine-tuned on financial data. 
   It understands context better than VADER (e.g., "tightening rates" is negative).
"""
from abc import ABC, abstractmethod
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from transformers import pipeline
import nltk
import random

# Ensure VADER lexicon is downloaded
try:
    nltk.data.find('sentiment/vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

# --- Interface (The Contract) ---
class SentimentModel(ABC):
    @abstractmethod
    def analyze(self, text: str) -> float:
        pass

# --- Concrete Product A: VADER (Rule-based) ---
class VaderModel(SentimentModel):
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
    
    def analyze(self, text: str) -> float:
        # Compound score ranges from -1 (Negative) to 1 (Positive)
        return self.analyzer.polarity_scores(text)['compound']

# --- Concrete Product B: FinBERT (Deep Learning) ---
class FinBertModel(SentimentModel):
    def __init__(self):
        print("⏳ Loading FinBERT Model (This happens only once)...")
        try:
            # We use a pipeline for easy inference. 
            # model="ProsusAI/finbert" is the industry standard for financial sentiment.
            self.pipe = pipeline("text-classification", model="ProsusAI/finbert")
        except Exception as e:
            print(f"❌ Error loading FinBERT: {e}")
            self.pipe = None

    def analyze(self, text: str) -> float:
        if not self.pipe:
            return 0.0
            
        # BERT models usually have a token limit (512). We truncate safely.
        # The pipeline returns a list like: [{'label': 'positive', 'score': 0.95}]
        try:
            results = self.pipe(text[:512]) 
            result = results[0]
            label = result['label'] # 'positive', 'negative', 'neutral'
            score = result['score'] # Confidence (0.0 to 1.0)

            # Convert to our standard -1 to 1 scale
            if label == 'positive':
                return score 
            elif label == 'negative':
                return -score
            else: # neutral
                return 0.0
        except Exception as e:
            print(f"Error analyzing text: {e}")
            return 0.0

# --- Concrete Product C: Random (For Testing) ---
class RandomModel(SentimentModel):
    def analyze(self, text: str) -> float:
        return random.uniform(-1, 1)

# --- The Factory ---
class SentimentFactory:
    @staticmethod
    def get_model(model_type: str) -> SentimentModel:
        model_type = model_type.lower()
        if model_type == "vader":
            return VaderModel()
        elif model_type == "finbert":
            return FinBertModel()
        elif model_type == "random":
            return RandomModel()
        else:
            raise ValueError(f"Unknown model type: {model_type}")