"""
Google Slides API クライアント
OAuth 認証フロー + Slides/Drive API のラッパー。
"""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.core.config import settings


class GoogleSlidesClient:
    """Google Slides / Drive API との通信を担当"""

    def __init__(self) -> None:
        self._slides_service = None
        self._drive_service = None

    def _get_credentials(self) -> Credentials:
        """OAuth2 クレデンシャルを構築"""
        return Credentials(
            token=None,
            refresh_token=settings.google_refresh_token,
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret,
            token_uri="https://oauth2.googleapis.com/token",
        )

    @property
    def slides(self):
        """Google Slides API service (lazy init)"""
        if self._slides_service is None:
            creds = self._get_credentials()
            self._slides_service = build("slides", "v1", credentials=creds)
        return self._slides_service

    @property
    def drive(self):
        """Google Drive API service (lazy init)"""
        if self._drive_service is None:
            creds = self._get_credentials()
            self._drive_service = build("drive", "v3", credentials=creds)
        return self._drive_service

    def get_presentation(self, presentation_id: str) -> dict:
        """プレゼンテーションの全データを取得"""
        return (
            self.slides.presentations()
            .get(presentationId=presentation_id)
            .execute()
        )

    def get_slide_thumbnail(
        self, presentation_id: str, page_id: str
    ) -> str:
        """スライドのサムネイル URL を取得"""
        resp = (
            self.slides.presentations()
            .pages()
            .getThumbnail(
                presentationId=presentation_id,
                pageObjectId=page_id,
            )
            .execute()
        )
        return resp.get("contentUrl", "")
