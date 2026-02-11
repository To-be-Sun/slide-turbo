"""
アプリケーション設定
環境変数から読み込み、各層に提供する。
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- Database ---
    database_url: str = "postgresql://user:password@localhost:5432/slide_turbo"

    # --- Auth / Security ---
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24  # 24h

    # --- Google API ---
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:3001/auth/callback"
    google_refresh_token: str = ""
    google_credentials_path: str = ""

    # --- Gemini API ---
    gemini_api_key: str = ""

    # --- Server ---
    port: int = 3001
    env: str = "development"
    frontend_url: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # 旧 .env の未知キーを無視


settings = Settings()
