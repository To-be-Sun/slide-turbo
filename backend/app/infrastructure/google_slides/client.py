"""
Google Slides API クライアント
OAuth 認証フロー + Slides/Drive API のラッパー。
"""

from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

from app.core.config import settings
from app.shared.exceptions import (
    ForbiddenException,
    UnauthorizedException,
    ValidationException,
)


class GoogleSlidesClient:
    """Google Slides / Drive API との通信を担当"""
    _SCOPES = [
        "https://www.googleapis.com/auth/presentations",
        "https://www.googleapis.com/auth/drive",
    ]

    def __init__(self, access_token: str | None = None) -> None:
        self._slides_service = None
        self._drive_service = None
        self._access_token = access_token

    def _get_credentials(self) -> Credentials:
        """OAuth2 クレデンシャルを構築"""
        if self._access_token:
            return Credentials(
                token=self._access_token,
                token_uri="https://oauth2.googleapis.com/token",
                scopes=self._SCOPES,
            )
        if not settings.google_refresh_token:
            raise ValidationException(
                "Google authentication is missing. "
                "Pass X-Google-Access-Token header or set GOOGLE_REFRESH_TOKEN."
            )
        if (
            not settings.google_client_id
            or not settings.google_client_secret
        ):
            raise ValidationException(
                "GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are required "
                "when using GOOGLE_REFRESH_TOKEN."
            )
        return Credentials(
            token=None,
            refresh_token=settings.google_refresh_token,
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret,
            token_uri="https://oauth2.googleapis.com/token",
            scopes=self._SCOPES,
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
        try:
            return (
                self.slides.presentations()
                .get(presentationId=presentation_id)
                .execute()
            )
        except RefreshError as e:
            raise UnauthorizedException(
                "Google access token is invalid or expired. "
                "Please sign in again."
            ) from e
        except HttpError as e:
            if e.resp.status == 403 and "ACCESS_TOKEN_SCOPE_INSUFFICIENT" in str(e):
                raise ForbiddenException(
                    "Google OAuth scopes are insufficient. "
                    "Please sign in again with presentations.readonly "
                    "and drive.readonly scopes."
                ) from e
            if e.resp.status == 401:
                raise UnauthorizedException(
                    "Google access token is invalid or expired. "
                    "Please sign in again."
                ) from e
            raise

    def get_slide_thumbnail(
        self, presentation_id: str, page_id: str
    ) -> str:
        """スライドのサムネイル URL を取得"""
        try:
            resp = (
                self.slides.presentations()
                .pages()
                .getThumbnail(
                    presentationId=presentation_id,
                    pageObjectId=page_id,
                )
                .execute()
            )
        except RefreshError as e:
            raise UnauthorizedException(
                "Google access token is invalid or expired. "
                "Please sign in again."
            ) from e
        except HttpError as e:
            if e.resp.status == 403 and "ACCESS_TOKEN_SCOPE_INSUFFICIENT" in str(e):
                raise ForbiddenException(
                    "Google OAuth scopes are insufficient. "
                    "Please sign in again with presentations.readonly "
                    "and drive.readonly scopes."
                ) from e
            if e.resp.status == 401:
                raise UnauthorizedException(
                    "Google access token is invalid or expired. "
                    "Please sign in again."
                ) from e
            raise
        return resp.get("contentUrl", "")
