"""
🎓 Learning Corner
------------------
WHY: We use the Singleton Pattern to load configuration only once.
We use 'python-dotenv' to securely load secrets from the .env file.
"""
import os
from dotenv import load_dotenv

# Load variables from .env file into the environment
load_dotenv()

class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize configuration variables."""
        # Reads the key from your new .env file, defaults to DEMO_KEY if missing
        self.CRYPTO_PANIC_API_KEY = os.getenv("CRYPTO_PANIC_API_KEY", "DEMO_KEY")
        self.DATA_PATH = os.path.join(os.getcwd(), "data")
        self.SYMBOLS = ["BTC", "ETH"]