from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import google_slides, slides, projects, templates
from app.database import Base, engine
from datetime import datetime

# データベーステーブルを作成（接続エラーは無視）
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"⚠️  Database connection error (this is OK if DB is not set up yet): {e}")

app = FastAPI(
    title="Slide Gen Backend",
    description="Google Slides APIとGemini 3を使用したスライド生成バックエンド",
    version="0.1.0",
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターを登録
app.include_router(google_slides.router)
app.include_router(slides.router)
app.include_router(projects.router)
app.include_router(templates.router)


@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.node_env == "development",
    )

