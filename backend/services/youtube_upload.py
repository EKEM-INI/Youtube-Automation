"""
YouTube Data API v3 Upload Integration
Handles OAuth2 authentication and automated video publishing.
"""
import os
import json

try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    GOOGLE_LIBS_AVAILABLE = True
except ImportError:
    GOOGLE_LIBS_AVAILABLE = False

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def get_authenticated_service(client_secrets_path: str = "client_secrets.json", token_path: str = "token.json"):
    """
    Authenticates with YouTube OAuth2 and returns the API client.
    """
    if not GOOGLE_LIBS_AVAILABLE:
        raise RuntimeError("Google API client libraries are not installed.")
        
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(client_secrets_path):
                raise FileNotFoundError(f"Missing {client_secrets_path}. Download your OAuth client secret from Google Cloud Console.")
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open(token_path, "w") as token_file:
            token_file.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)


def upload_video_to_youtube(
    video_path: str,
    title: str,
    description: str,
    tags: list = None,
    privacy_status: str = "private",
    client_secrets_path: str = "client_secrets.json",
    token_path: str = "token.json"
) -> dict:
    """
    Uploads a video to YouTube.
    """
    if not os.path.exists(client_secrets_path) and not os.path.exists(token_path):
        return {
            "status": "simulated",
            "message": "Demo Mode: YouTube client_secrets.json not configured yet. Download the video directly or add your Google OAuth secret to auto-post.",
            "video_url": f"https://www.youtube.com/shorts/demo_{os.path.basename(video_path)}"
        }

    youtube = get_authenticated_service(client_secrets_path, token_path)

    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags or ["shorts", "viral", "ai"],
            "categoryId": "22"  # People & Blogs
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        
    video_id = response.get("id")
    return {
        "status": "success",
        "video_id": video_id,
        "video_url": f"https://www.youtube.com/shorts/{video_id}"
    }
