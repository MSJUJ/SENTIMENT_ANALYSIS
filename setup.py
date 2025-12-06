"""
Helper script to initialize the project environment.
"""
import nltk
import os

def setup_project():
    print("⬇️  Downloading necessary NLTK corpora...")
    try:
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('vader_lexicon')
        nltk.download('wordnet')
        print("✅ NLTK data downloaded successfully.")
    except Exception as e:
        print(f"❌ Error downloading NLTK data: {e}")

    print("\n📂 checking directory structure...")
    dirs = ['data', 'src', 'tests']
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)
            print(f"   - Created missing directory: {d}/")
        else:
            print(f"   - Found directory: {d}/")

    print("\n🚀 Project is ready! Run the app with:")
    print("   streamlit run src/dashboard/app.py")

if __name__ == "__main__":
    setup_project()