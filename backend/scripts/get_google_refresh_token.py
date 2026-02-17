#!/usr/bin/env python3
"""
Google OAuth2 リフレッシュトークン取得スクリプト

このスクリプトを実行してブラウザでGoogle認証を行うと、
GOOGLE_REFRESH_TOKENが表示されます。それを.envに設定してください。

Usage:
    python scripts/get_google_refresh_token.py
"""

import os
import sys

# backendディレクトリからの実行を想定
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive",
]

def main():
    # .envから読み込み
    from dotenv import load_dotenv
    load_dotenv()
    
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("❌ GOOGLE_CLIENT_ID と GOOGLE_CLIENT_SECRET を .env に設定してください")
        sys.exit(1)
    
    print("🔐 Google認証を開始します...")
    print(f"   Client ID: {client_id[:30]}...")
    print()
    
    # OAuth フロー（ポート8080を使用）
    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost:8080/"],
        }
    }
    
    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    
    # ブラウザで認証（ポート8080を使用）
    creds = flow.run_local_server(port=8080, prompt="consent", access_type="offline")
    
    print()
    print("✅ 認証成功！")
    print()
    print("=" * 60)
    print("以下の行を backend/.env に追加してください：")
    print("=" * 60)
    print()
    print(f"GOOGLE_REFRESH_TOKEN={creds.refresh_token}")
    print()
    print("=" * 60)
    print()
    print("追加後、バックエンドを再起動してください。")

if __name__ == "__main__":
    main()
