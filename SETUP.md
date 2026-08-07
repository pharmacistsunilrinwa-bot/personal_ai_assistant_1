# Personal AI Assistant Setup Guide

## 1. Backend Setup (FastAPI)

### Step A: Create and Activate Virtual Environment
```bash
cd personal_ai_assistant/backend
python -m venv venv
source venv/bin/activate  # On Linux/Android/Mac
# venv\Scripts\activate  # On Windows
```

### Step B: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step C: Run the Server
```bash
python main.py
```

## 2. Tunneling (Expose Local Server)

To allow your Android device to communicate with the local server, use `ngrok` or `localtunnel`.

### Using Localtunnel:
```bash
npm install -g localtunnel
lt --port 8000
```
*Copy the public URL provided (e.g., `https://XXXX.loca.lt`) and update `_baseUrl` in `frontend/lib/main.dart`.*

## 3. Frontend Setup (Flutter)

### Step A: Get Dependencies
```bash
cd ../frontend
flutter pub get
```

### Step B: Compile to APK
```bash
flutter build apk --release
```
*The APK will be located at `build/app/outputs/flutter-apk/app-release.apk`.*

## 4. Environment Variables (.env)
The `.env` file in `backend/` manages API key rotation.
- `GEMINI_API_KEYS`: A comma-separated list of keys.
- `GOOGLE_CLIENT_ID` & `GOOGLE_CLIENT_SECRET`: Obtained from Google Cloud Console for OAuth.

## 5. Failover Rotation Logic
The `GeminiService` automatically detects `429` (Rate Limit) or `Quota Exceeded` errors. It then calls `Config.rotate_key()` to switch to the next key in the list and retries the request.
