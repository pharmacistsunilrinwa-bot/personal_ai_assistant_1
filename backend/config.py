import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Multiple API Keys separated by commas
    GEMINI_API_KEYS = os.getenv("GEMINI_API_KEYS", "").split(",")
    _current_key_index = 0

    @classmethod
    def get_gemini_api_key(cls):
        if not cls.GEMINI_API_KEYS or cls.GEMINI_API_KEYS == [""]:
            raise ValueError("No GEMINI_API_KEYS found in environment variables.")
        
        key = cls.GEMINI_API_KEYS[cls._current_key_index].strip()
        return key

    @classmethod
    def rotate_key(cls):
        cls._current_key_index = (cls._current_key_index + 1) % len(cls.GEMINI_API_KEYS)
        return cls.get_gemini_api_key()

    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/callback")
    GOOGLE_CLOUD_KEY = os.getenv("GOOGLE_CLOUD_KEY")
