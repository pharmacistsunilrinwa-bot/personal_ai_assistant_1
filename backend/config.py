import os
import sys
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Initialize the key list
    GEMINI_API_KEYS = []
    _current_key_index = 0

    # Load and clean Gemini keys from the environment variable
    raw_keys = os.getenv("GEMINI_API_KEYS", "")
    if raw_keys:
        GEMINI_API_KEYS = [k.strip() for k in raw_keys.split(",") if k.strip()]

    # Load Google Colab key if provided
    COLAB_API_KEY = os.getenv("COLAB_API_KEY", "").strip()
    if COLAB_API_KEY and COLAB_API_KEY not in GEMINI_API_KEYS:
        GEMINI_API_KEYS.append(COLAB_API_KEY)

    # Automatically check if running inside Google Colab, and attempt to load its secrets
    try:
        # Check if the google.colab module is present in sys.modules or can be imported
        import google.colab
        from google.colab import userdata
        try:
            colab_secret = userdata.get('GEMINI_API_KEY')
            if colab_secret and colab_secret.strip() not in GEMINI_API_KEYS:
                GEMINI_API_KEYS.append(colab_secret.strip())
        except Exception:
            pass
    except ImportError:
        pass

    @classmethod
    def get_gemini_api_key(cls) -> str:
        """Retrieves the currently selected Gemini API Key."""
        if not cls.GEMINI_API_KEYS:
            raise ValueError(
                "No GEMINI_API_KEYS or COLAB_API_KEY found in environment variables.\n"
                "Please configure your .env file inside 'backend/.env' with valid keys."
            )
        
        key = cls.GEMINI_API_KEYS[cls._current_key_index]
        return key

    @classmethod
    def rotate_key(cls) -> str:
        """Rotates to the next available API key in the list and returns it."""
        if not cls.GEMINI_API_KEYS:
            raise ValueError("No keys available to rotate.")
            
        cls._current_key_index = (cls._current_key_index + 1) % len(cls.GEMINI_API_KEYS)
        return cls.get_gemini_api_key()

    # Google Client OAuth Credentials for Workspace Integration
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/v1/google-workspace/oauth2callback")
    GOOGLE_CLOUD_KEY = os.getenv("GOOGLE_CLOUD_KEY")
