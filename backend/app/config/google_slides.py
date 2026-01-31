import os
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from app.config.settings import settings
from typing import Optional


_auth_client: Optional[Flow] = None
_credentials: Optional[Credentials] = None


def load_credentials_from_file() -> Optional[dict]:
    """JSONファイルから認証情報を読み込む"""
    # 環境変数でJSONファイルのパスが指定されている場合
    credentials_path = settings.google_credentials_path
    
    # デフォルトのパスを試す（プロジェクトルートのclient_secret_*.json）
    possible_paths = []
    
    if credentials_path:
        possible_paths.append(credentials_path)
    
    # プロジェクトルートを検索
    backend_dir = Path(__file__).parent.parent.parent
    for file in backend_dir.glob("client_secret_*.json"):
        possible_paths.append(str(file))
    
    # client_secret.jsonも試す
    default_path = backend_dir / "client_secret.json"
    if default_path.exists():
        possible_paths.append(str(default_path))
    
    for path in possible_paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                creds_data = json.load(f)
            
            # web または installed のいずれかから取得
            creds = creds_data.get("web") or creds_data.get("installed")
            if creds and creds.get("client_id") and creds.get("client_secret"):
                return {
                    "client_id": creds["client_id"],
                    "client_secret": creds["client_secret"],
                }
        except Exception:
            continue
    
    return None


def get_google_slides_auth() -> Flow:
    """Google Slides API認証クライアントを取得"""
    global _auth_client
    
    if _auth_client:
        return _auth_client
    
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    
    # まずJSONファイルから読み込む
    file_creds = load_credentials_from_file()
    if file_creds:
        client_id = file_creds["client_id"]
        client_secret = file_creds["client_secret"]
        print("✅ Google認証情報をJSONファイルから読み込みました")
    else:
        # JSONファイルがない場合は環境変数から取得
        client_id = settings.google_client_id
        client_secret = settings.google_client_secret
        print("✅ Google認証情報を環境変数から読み込みました")
    
    if not client_id or not client_secret:
        raise ValueError(
            "Google認証情報が見つかりません。\n"
            "以下のいずれかの方法で設定してください：\n"
            "1. JSONファイル: backend/client_secret_*.json を配置\n"
            "2. 環境変数: GOOGLE_CLIENT_ID と GOOGLE_CLIENT_SECRET を設定\n"
            "詳細は docs/GOOGLE_API_SETUP.md を参照してください"
        )
    
    redirect_uri = settings.google_redirect_uri
    
    _auth_client = Flow.from_client_config(
        {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri],
            }
        },
        scopes=[
            "https://www.googleapis.com/auth/presentations.readonly",
            "https://www.googleapis.com/auth/drive.readonly",
        ],
    )
    _auth_client.redirect_uri = redirect_uri
    
    return _auth_client


def get_google_slides_client():
    """Google Slides APIクライアントを取得"""
    global _credentials
    
    if _credentials is None:
        if settings.google_refresh_token:
            # リフレッシュトークンから認証情報を作成
            file_creds = load_credentials_from_file()
            if file_creds:
                _credentials = Credentials(
                    token=None,
                    refresh_token=settings.google_refresh_token,
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=file_creds["client_id"],
                    client_secret=file_creds["client_secret"],
                )
            else:
                _credentials = Credentials(
                    token=None,
                    refresh_token=settings.google_refresh_token,
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=settings.google_client_id,
                    client_secret=settings.google_client_secret,
                )
        else:
            raise ValueError("GOOGLE_REFRESH_TOKEN is required. Please authenticate first.")
    
    # トークンをリフレッシュ
    if _credentials.expired and _credentials.refresh_token:
        _credentials.refresh(Request())
    
    return build("slides", "v1", credentials=_credentials)


def get_auth_url() -> str:
    """認証URLを生成"""
    auth = get_google_slides_auth()
    auth_url, _ = auth.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
    )
    return auth_url


def set_auth_token(code: str) -> str:
    """認証トークンを設定"""
    global _credentials
    auth = get_google_slides_auth()
    auth.fetch_token(code=code)
    
    _credentials = auth.credentials
    
    if _credentials.refresh_token:
        print(f"Refresh token: {_credentials.refresh_token}")
        print("Set this as GOOGLE_REFRESH_TOKEN in your .env file")
        return _credentials.refresh_token
    
    return ""

