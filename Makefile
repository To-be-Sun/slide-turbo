.PHONY: up down db logs prisma-generate prisma-push prisma-studio setup clean

# ── Docker ────────────────────────────────────────────

up:  ## 全コンテナ起動 (DB + Backend)
	docker compose up -d

down:  ## 全コンテナ停止
	docker compose down

db:  ## DB のみ起動
	docker compose up -d db

logs:  ## Backend ログ表示
	docker compose logs -f backend

# ── Prisma (ホスト側で実行) ────────────────────────────

prisma-generate:  ## Prisma クライアント生成
	cd backend && python3 -m prisma generate

prisma-push:  ## DB にスキーマ反映
	cd backend && python3 -m prisma db push

prisma-studio:  ## Prisma Studio (GUI) 起動
	cd backend && python3 -m prisma studio

# ── Setup ─────────────────────────────────────────────

setup:  ## 初期セットアップ (DB起動 → pip install → prisma generate → db push)
	@echo "==> Starting DB..."
	docker compose up -d db
	@echo "==> Installing Python dependencies..."
	cd backend && pip3 install -r requirements.txt
	@echo "==> Waiting for DB to be ready..."
	@sleep 3
	@echo "==> Generating Prisma client..."
	cd backend && python -m prisma generate
	@echo "==> Pushing schema to DB..."
	cd backend && DATABASE_URL=postgresql://slide_turbo:slide_turbo@localhost:5433/slide_turbo python3 -m prisma db push
	@echo ""
	@echo "✓ Setup complete! Run 'make up' to start everything."

clean:  ## コンテナ + ボリューム完全削除
	docker compose down -v

# ── Dev (ホスト側で Backend 起動) ──────────────────────

dev:  ## DB だけ Docker、Backend はホスト側で起動 (ホットリロード)
	docker compose up -d db
	@sleep 2
	cd backend && DATABASE_URL=postgresql://slide_turbo:slide_turbo@localhost:5433/slide_turbo \
		python3 -m uvicorn app.main:app --host 0.0.0.0 --port 3001 --reload

help:  ## ヘルプ表示
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
