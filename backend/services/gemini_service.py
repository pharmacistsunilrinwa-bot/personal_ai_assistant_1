import google.generativeai as genai
from config import Config
import logging

class GeminiService:
    def __init__(self):
        self._setup_client()

    def _setup_client(self):
        api_key = Config.get_gemini_api_key()
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')

    async def generate_content(self, prompt, context=None):
        full_prompt = f"{context}\n\nUser: {prompt}" if context else prompt
        
        for _ in range(len(Config.GEMINI_API_KEYS)):
            try:
                # Utilizing non-blocking async method from the SDK
                response = await self.model.generate_content_async(full_prompt)
                return response.text
            except Exception as e:
                logging.error(f"Error with current API key: {e}")
                if "429" in str(e) or "quota" in str(e).lower():
                    logging.info("Rotating API key due to rate limit/quota...")
                    api_key = Config.rotate_key()
                    genai.configure(api_key=api_key)
                    self.model = genai.GenerativeModel('gemini-1.5-pro')
                else:
                    raise e
        raise Exception("All API keys exhausted or failed.")

    async def text_to_speech(self, text):
        # Placeholder for Gemini multimodal TTS representation
        return f"Audio data for: {text}" 

    async def speech_to_text(self, audio_bytes):
        # Utilizing non-blocking async method from the SDK for multimodal audio ingestion
        try:
            response = await self.model.generate_content_async([
                "Transcribe this audio exactly.",
                {"mime_type": "audio/wav", "data": audio_bytes}
            ])
            return response.text
        except Exception as e:
            return f"STT Error: {str(e)}"
