import re

class TextCleaner:
    def clean(self, text):
        text = text.lower()
        # Keep letters and numbers
        text = re.sub(r'[^a-z0-9\s]', '', text)
        tokens = text.split()
        return tokens
    
    def clean_to_string(self, text):
        """Helper for models that want strings, not lists."""
        return " ".join(self.clean(text))

# Debug check
if __name__ == "__main__":
    tc = TextCleaner()
    print(tc.clean("BTC is $50k!"))