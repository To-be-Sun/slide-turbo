FROM python:3.11-slim

WORKDIR /app

# システム依存パッケージ
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Python 依存インストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Prisma スキーマ & アプリコード
COPY prisma ./prisma
COPY app ./app

# Prisma クライアント生成 (ビルド時)
RUN python -m prisma generate

EXPOSE 3001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3001"]
