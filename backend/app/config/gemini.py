import google.generativeai as genai
from app.config.settings import settings
from typing import Optional


_genai_client: Optional[genai.GenerativeModel] = None


def get_genai_client() -> genai.GenerativeModel:
    """Gemini APIクライアントを取得（遅延初期化）"""
    global _genai_client
    
    if _genai_client is None:
        api_key = settings.gemini_api_key
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is required. "
                "Please set it in your .env file. "
                "Get your API key from: https://aistudio.google.com/app/apikey"
            )
        
        # APIキーの最初の10文字だけ表示（セキュリティのため）
        masked_key = api_key[:10] + "..."
        print(f"✅ Gemini API key loaded: {masked_key}")
        
        genai.configure(api_key=api_key)
        # Gemini 3 Pro (Nanobanana Pro) モデルを使用
        try:
            _genai_client = genai.GenerativeModel("gemini-3.0-pro")
        except Exception:
            # フォールバック: 利用可能なモデルを試す
            print("⚠️ gemini-3.0-pro not available, trying gemini-pro")
            _genai_client = genai.GenerativeModel("gemini-pro")
    
    return _genai_client


def get_available_model() -> genai.GenerativeModel:
    """利用可能なモデルを取得"""
    try:
        return get_genai_client()
    except Exception as e:
        print(f"⚠️ Error getting model: {e}")
        # フォールバック
        genai.configure(api_key=settings.gemini_api_key)
        return genai.GenerativeModel("gemini-pro")

