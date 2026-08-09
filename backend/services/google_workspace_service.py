import os
import pickle
import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from config import Config

class GoogleWorkspaceService:
    # Essential scopes for Gmail and Drive access
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/drive.readonly',
        'https://www.googleapis.com/auth/drive.file'
    ]

    def __init__(self, token_path='token.pickle'):
        self.token_path = token_path
        self.creds = self._load_credentials()

    def _load_credentials(self):
        """Loads credentials from token pickle if it exists and is valid."""
        creds = None
        if os.path.exists(self.token_path):
            try:
                with open(self.token_path, 'rb') as token_file:
                    creds = pickle.load(token_file)
            except Exception:
                pass
        
        # If credentials exist but are expired, refresh them
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                with open(self.token_path, 'wb') as token_file:
                    pickle.dump(creds, token_file)
            except Exception:
                creds = None
        return creds

    def is_authenticated(self) -> bool:
        """Checks if valid credentials are loaded."""
        return self.creds is not None and self.creds.valid

    def get_authorization_url(self, redirect_uri: str) -> str:
        """Generates an OAuth authorization URL using client credentials."""
        client_config = {
            "web": {
                "client_id": Config.GOOGLE_CLIENT_ID,
                "client_secret": Config.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri]
            }
        }
        
        flow = Flow.from_client_config(
            client_config,
            scopes=self.SCOPES,
            redirect_uri=redirect_uri
        )
        
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        return auth_url

    def fetch_token_from_code(self, code: str, redirect_uri: str):
        """Exchanges authorization code for tokens and saves them."""
        client_config = {
            "web": {
                "client_id": Config.GOOGLE_CLIENT_ID,
                "client_secret": Config.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri]
            }
        }
        
        flow = Flow.from_client_config(
            client_config,
            scopes=self.SCOPES,
            redirect_uri=redirect_uri
        )
        
        flow.fetch_token(code=code)
        self.creds = flow.credentials
        
        # Save credentials for future use
        with open(self.token_path, 'wb') as token_file:
            pickle.dump(self.creds, token_file)
        
        return self.creds

    # --- Gmail Services ---

    def list_emails(self, max_results=10, query=None):
        """Lists metadata of recent emails in the inbox."""
        if not self.is_authenticated():
            raise ValueError("Google Workspace API: OAuth 2.0 authentication required.")

        service = build('gmail', 'v1', credentials=self.creds)
        response = service.users().messages().list(
            userId='me', 
            maxResults=max_results, 
            q=query
        ).execute()
        
        messages = response.get('messages', [])
        email_list = []
        
        for msg in messages:
            msg_id = msg['id']
            msg_detail = service.users().messages().get(userId='me', id=msg_id, format='metadata', metadataHeaders=['Subject', 'From', 'Date']).execute()
            
            headers = msg_detail.get('payload', {}).get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
            
            email_list.append({
                "id": msg_id,
                "subject": subject,
                "sender": sender,
                "date": date,
                "snippet": msg_detail.get('snippet', '')
            })
            
        return email_list

    def send_email(self, to: str, subject: str, body: str):
        """Sends an email from the authenticated user's account."""
        if not self.is_authenticated():
            raise ValueError("Google Workspace API: OAuth 2.0 authentication required.")

        service = build('gmail', 'v1', credentials=self.creds)
        
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        sent_msg = service.users().messages().send(
            userId='me', 
            body={'raw': raw_message}
        ).execute()
        
        return sent_msg

    # --- Google Drive Services ---

    def list_drive_files(self, max_results=10, query=None):
        """Lists files on Google Drive."""
        if not self.is_authenticated():
            raise ValueError("Google Workspace API: OAuth 2.0 authentication required.")

        service = build('drive', 'v3', credentials=self.creds)
        
        # Build query to restrict to user-owned files or search filters
        q = "trashed = false"
        if query:
            q += f" and {query}"
            
        response = service.files().list(
            pageSize=max_results, 
            fields="nextPageToken, files(id, name, mimeType, size)", 
            q=q
        ).execute()
        
        return response.get('files', [])

    def upload_drive_file(self, file_path: str, mime_type: str = 'application/octet-stream', folder_id: str = None):
        """Uploads a local file to Google Drive."""
        if not self.is_authenticated():
            raise ValueError("Google Workspace API: OAuth 2.0 authentication required.")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Local file not found: {file_path}")

        from googleapiclient.http import MediaFileUpload
        service = build('drive', 'v3', credentials=self.creds)
        
        file_name = os.path.basename(file_path)
        file_metadata = {'name': file_name}
        if folder_id:
            file_metadata['parents'] = [folder_id]
            
        media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink'
        ).execute()
        
        return file
