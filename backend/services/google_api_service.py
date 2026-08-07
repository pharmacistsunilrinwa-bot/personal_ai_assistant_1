from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from config import Config
import os
import pickle

class GoogleApiService:
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/drive.readonly',
        'https://www.googleapis.com/auth/photoslibrary.readonly'
    ]

    def __init__(self, token_path='token.pickle'):
        self.token_path = token_path
        self.creds = self._get_credentials()
        self.api_key = Config.GOOGLE_CLOUD_KEY

    def _get_credentials(self):
        creds = None
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # In a real app, this would redirect to a login page
                # For this implementation, we assume credentials will be provided
                pass
        return creds

    def get_gmail_messages(self, limit=10):
        # Technical Note: Gmail strictly requires OAuth 2.0 user credentials.
        # An API Key (developerKey) alone cannot authorize access to user private emails.
        # We use OAuth credentials if available; otherwise we show an authentication notice.
        if not self.creds: 
            return "Gmail Access: OAuth 2.0 Credentials are required. Simple API Keys are not authorized for private user inbox access."
        
        service = build('gmail', 'v1', credentials=self.creds, developerKey=self.api_key)
        results = service.users().messages().list(userId='me', maxResults=limit).execute()
        return results.get('messages', [])

    def get_drive_files(self, limit=10):
        # Technical Note: Drive API requires OAuth 2.0 for private user files.
        # Public files can theoretically be queried using developerKey (API Key).
        if not self.creds and not self.api_key:
            return "Drive Access: Either OAuth 2.0 or Google Cloud API Key is required."
        
        if self.creds:
            service = build('drive', 'v3', credentials=self.creds, developerKey=self.api_key)
        else:
            # Fallback to API Key only (restricted to public data access)
            service = build('drive', 'v3', developerKey=self.api_key)
            
        results = service.files().list(pageSize=limit, fields="nextPageToken, files(id, name)").execute()
        return results.get('files', [])

    def get_recent_photos(self, limit=10):
        # Photos API requires OAuth 2.0 user-authorized scopes.
        return "Photos API integration placeholder (Requires OAuth 2.0 User Credentials)"

