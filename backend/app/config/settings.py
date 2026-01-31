from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/slide_gen")
    
    # Gemini API
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    
    # Google API
    google_client_id: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    google_redirect_uri: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3001/auth/callback")
    google_refresh_token: Optional[str] = os.getenv("GOOGLE_REFRESH_TOKEN")
    google_credentials_path: Optional[str] = os.getenv("GOOGLE_CREDENTIALS_PATH")
    
    # Server
    port: int = int(os.getenv("PORT", "3001"))
    node_env: str = os.getenv("NODE_ENV", "development")
    
    # CORS
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

