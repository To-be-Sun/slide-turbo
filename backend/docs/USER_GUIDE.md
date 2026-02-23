# Slide Turbo - ユーザーガイド

## 目次
1. [システム概要](#システム概要)
2. [アーキテクチャ](#アーキテクチャ)
3. [セットアップ](#セットアップ)
4. [使用方法](#使用方法)
5. [API仕様](#api仕様)
6. [データフロー](#データフロー)
7. [トラブルシューティング](#トラブルシューティング)

---

## システム概要

### 概要
Slide Turboは、AI（Gemini）を活用してプレゼンテーションスライドを自動生成するWebアプリケーションです。

### 主な機能
- **マルチエージェントスライド生成**: 5つの専門エージェント（Planner, Copywriter, Visual, LayoutPlanner, Layout）による高品質なスライド生成
- **テンプレート管理**: Google Slidesからテンプレートをインポートし、スロット（変数）を自動解析
- **HTMLプレビュー**: 生成したスライドをブラウザでプレビュー
- **Google Slides エクスポート**: 生成したスライドをGoogle Slidesに出力
- **バージョン管理**: スライドの編集履歴を管理

### 技術スタック
- **バックエンド**: Python 3.14, FastAPI, Prisma ORM
- **フロントエンド**: Next.js, React, TypeScript
- **データベース**: PostgreSQL 16
- **AI**: Google Gemini API
- **認証**: Google OAuth 2.0
- **コンテナ**: Docker, Docker Compose

---

## アーキテクチャ

### システム構成
```
┌─────────────────┐
│   Frontend      │  Next.js (Port 3000)
│   (Next.js)     │
└────────┬────────┘
         │ HTTP/REST
         │
┌────────▼────────┐
│   Backend       │  FastAPI (Port 8000)
│   (FastAPI)     │
└────┬────┬───┬───┘
     │    │   │
     │    │   └─────────┐
     │    │             │
┌────▼────▼─────┐  ┌───▼──────────┐
│  PostgreSQL   │  │  Gemini API  │
│  (Port 5432)  │  │  (External)  │
└───────────────┘  └──────────────┘
```

### データフロー（スライド生成）
```
1. ユーザー入力（アウトライン）
   ↓
2. PlannerAgent: 構造化プラン作成
   ↓
3. CopywriterAgent: コピー洗練
   ↓
4. VisualAgent: 画像URL生成
   ↓
5. LayoutPlannerAgent: レイアウト選択
   ↓
6. LayoutAgent: Google Slides API形式JSON生成
   ↓
7. HTMLRenderer: プレビュー生成
   ↓
8. GoogleSlidesExporter: Google Slidesへ出力
```

### JSON形式（Google Slides API標準）
```json
{
  "objectId": "slide_1",
  "pageElements": [
    {
      "objectId": "element_1",
      "transform": {
        "translateX": 50,
        "translateY": 50
      },
      "size": {
        "width": {"magnitude": 300, "unit": "PT"},
        "height": {"magnitude": 100, "unit": "PT"}
      },
      "shape": {
        "shapeType": "TEXT_BOX",
        "text": {
          "textElements": [
            {"textRun": {"content": "タイトル"}}
          ]
        }
      }
    }
  ]
}
```

---

## セットアップ

### 前提条件
- Docker Desktop
- Python 3.14+
- Node.js 18+
- Google Cloud Platformアカウント

### 1. リポジトリクローン
```bash
git clone <repository-url>
cd slide-turbo
```

### 2. 環境変数設定
`.env`ファイルを作成：
```env
# Database
DATABASE_URL="postgresql://slide_turbo:slide_turbo@localhost:5432/slide_turbo?schema=public"

# Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Google OAuth
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/callback/google

# JWT
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

### 3. データベース起動
```bash
# Docker ComposeでPostgreSQLを起動
docker-compose up -d db

# データベーススキーマを適用
cd backend
python -m prisma db push
```

### 4. バックエンド起動
```bash
# 仮想環境のセットアップ（初回のみ）
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# または
.venv\Scripts\activate  # Windows

# 依存関係インストール
pip install -r requirements.txt
pip install prisma PyJWT

# Prisma Clientの生成
python -m prisma generate

# サーバー起動
cd backend
uvicorn app.main:app --reload --port 8000
```

### 5. フロントエンド起動
```bash
cd frontend
npm install
npm run dev
```

### 6. アクセス
- **フロントエンド**: http://localhost:3000
- **API ドキュメント**: http://localhost:8000/docs
- **ヘルスチェック**: http://localhost:8000/health

---

## 使用方法

### 1. 認証
1. http://localhost:3000 にアクセス
2. 「Googleでログイン」をクリック
3. Googleアカウントで認証

### 2. テンプレート作成
#### 方法A: Google Slidesからインポート
```bash
# API経由でインポート
curl -X POST http://localhost:8000/api/v1/templates/import \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "presentation_url": "https://docs.google.com/presentation/d/PRESENTATION_ID",
    "title": "My Template"
  }'
```

#### 方法B: 手動作成
```bash
curl -X POST http://localhost:8000/api/v1/templates \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Template",
    "contents": {
      "slides": [...],
      "slots": ["{{company_name}}", "{{product_name}}"]
    }
  }'
```

### 3. スライド生成（マルチエージェント）

#### ステップ1: アウトライン作成
```bash
curl -X POST http://localhost:8000/api/v1/outlines \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "slide_version_id": "version_id_here",
    "outline": {
      "title": "新製品発表",
      "sections": [
        {"heading": "背景", "content": "市場の課題..."},
        {"heading": "ソリューション", "content": "我々の製品..."},
        {"heading": "まとめ", "content": "期待される効果..."}
      ]
    }
  }'
```

#### ステップ2: スライド生成
```bash
curl -X POST http://localhost:8000/api/v1/outlines/generate-slide \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "outline_id": "outline_id_from_step1",
    "page_number": 1
  }'
```

**レスポンス例**:
```json
{
  "outline_id": "abc123",
  "slide": {
    "objectId": "slide_1",
    "pageElements": [
      {
        "objectId": "title_1",
        "transform": {"translateX": 50, "translateY": 50},
        "size": {
          "width": {"magnitude": 600, "unit": "PT"},
          "height": {"magnitude": 100, "unit": "PT"}
        },
        "shape": {
          "shapeType": "TEXT_BOX",
          "text": {
            "textElements": [
              {"textRun": {"content": "新製品発表"}}
            ]
          }
        }
      }
    ]
  }
}
```

### 4. プレビュー表示
```bash
# HTMLプレビューを生成
curl http://localhost:8000/api/v1/slides/{slide_id}/preview?version_num=1
```

ブラウザで表示すると、Google Slides API形式のJSONがHTMLにレンダリングされます。

### 5. Google Slidesへエクスポート
```bash
curl -X POST http://localhost:8000/api/v1/slides/{slide_id}/export \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d 'version_num=1&owner_email=user@example.com'
```

**レスポンス**:
```json
{
  "presentationId": "google_slides_id",
  "presentationUrl": "https://docs.google.com/presentation/d/...",
  "downloadUrl": "https://docs.google.com/presentation/d/.../export/pptx"
}
```

---

## API仕様

### 認証
全ての保護されたエンドポイントは、Authorizationヘッダーにトークンが必要です：
```
Authorization: Bearer YOUR_JWT_TOKEN
```

### エンドポイント一覧

#### ヘルスチェック
```
GET /health
```

#### ユーザー
```
GET  /api/v1/users/auth/google              # OAuth開始
POST /api/v1/users/auth/google/callback     # OAuthコールバック
GET  /api/v1/users/me                        # 自分の情報取得
PATCH /api/v1/users/me                       # プロフィール更新
```

#### テンプレート
```
POST   /api/v1/templates/import             # Google Slidesからインポート
POST   /api/v1/templates/import-preview     # インポートプレビュー
GET    /api/v1/templates                    # テンプレート一覧
GET    /api/v1/templates/{id}               # テンプレート詳細
PATCH  /api/v1/templates/{id}               # テンプレート更新
DELETE /api/v1/templates/{id}               # テンプレート削除
GET    /api/v1/templates/{id}/thumbnail     # サムネイル取得
GET    /api/v1/templates/{id}/thumbnails    # 全ページサムネイル
```

#### スライド
```
POST   /api/v1/slides                       # スライド作成
GET    /api/v1/slides                       # スライド一覧
GET    /api/v1/slides/{id}                  # スライド詳細
PATCH  /api/v1/slides/{id}                  # スライド更新
DELETE /api/v1/slides/{id}                  # スライド削除
GET    /api/v1/slides/{id}/preview          # HTMLプレビュー
POST   /api/v1/slides/{id}/export           # Google Slidesへエクスポート
```

#### バージョン管理
```
POST /api/v1/slides/{id}/versions           # 新バージョン作成
GET  /api/v1/slides/{id}/versions           # バージョン一覧
```

#### ページ操作
```
POST   /api/v1/slides/versions/{id}/pages   # ページ追加
GET    /api/v1/slides/versions/{id}/pages   # ページ一覧
PATCH  /api/v1/slides/pages/{id}            # ページ更新
DELETE /api/v1/slides/pages/{id}            # ページ削除
```

#### アウトライン
```
POST   /api/v1/outlines                     # アウトライン作成
GET    /api/v1/outlines/{id}                # アウトライン取得
PATCH  /api/v1/outlines/{id}                # アウトライン更新
DELETE /api/v1/outlines/{id}                # アウトライン削除
POST   /api/v1/outlines/refine              # アウトライン洗練
POST   /api/v1/outlines/generate-slide      # スライド生成（マルチエージェント）
```

---

## データフロー

### スライド生成フロー（詳細）

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant MultiAgent
    participant Gemini
    participant DB

    User->>Frontend: アウトライン入力
    Frontend->>Backend: POST /api/v1/outlines
    Backend->>DB: アウトライン保存
    Backend-->>Frontend: outline_id
    
    Frontend->>Backend: POST /api/v1/outlines/generate-slide
    Backend->>MultiAgent: generate_one_slide()
    
    MultiAgent->>Gemini: PlannerAgent.run()
    Gemini-->>MultiAgent: 構造化プラン
    
    MultiAgent->>Gemini: CopywriterAgent.run()
    Gemini-->>MultiAgent: 洗練されたコピー
    
    MultiAgent->>Gemini: VisualAgent.run()
    Gemini-->>MultiAgent: 画像URL
    
    MultiAgent->>Gemini: LayoutPlannerAgent.run()
    Gemini-->>MultiAgent: レイアウト選択
    
    MultiAgent->>MultiAgent: LayoutAgent.run()
    MultiAgent-->>Backend: Google Slides API形式JSON
    
    Backend->>DB: ページ保存
    Backend-->>Frontend: スライドJSON
    Frontend-->>User: プレビュー表示
```

### エクスポートフロー

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant GoogleSlides
    
    User->>Frontend: エクスポート要求
    Frontend->>Backend: POST /api/v1/slides/{id}/export
    Backend->>Backend: HTMLRenderer.render_presentation()
    Backend->>GoogleSlides: GoogleSlidesExporter.create_presentation()
    GoogleSlides-->>Backend: presentation_id
    Backend-->>Frontend: presentationUrl
    Frontend-->>User: リンク表示
    User->>GoogleSlides: ブラウザで開く
```

---

## トラブルシューティング

### バックエンドが起動しない

#### エラー: `ModuleNotFoundError: No module named 'app'`
**原因**: 間違ったディレクトリから起動している  
**解決策**:
```bash
cd /path/to/slide-turbo/backend
python -m uvicorn app.main:app --reload --port 8000
```

#### エラー: `Can't reach database server at localhost:5432`
**原因**: PostgreSQLが起動していない  
**解決策**:
```bash
docker-compose up -d db
# 起動確認
docker-compose logs db
```

#### エラー: `Environment variable not found: DATABASE_URL`
**原因**: .envファイルが存在しないか、内容が不正  
**解決策**:
```bash
# .envファイルの存在確認
ls -la backend/.env

# 内容確認
cat backend/.env
```

### Prisma関連エラー

#### エラー: `prisma-client-py: command not found`
**解決策**:
```bash
pip install prisma
export PATH="/path/to/.venv/bin:$PATH"
python -m prisma generate
```

### 認証エラー

#### エラー: `{"detail":"Not authenticated"}`
**原因**: JWTトークンが無効または期限切れ  
**解決策**:
1. `/api/v1/users/auth/google` で再認証
2. 新しいトークンを取得
3. Authorizationヘッダーに設定

### スライド生成エラー

#### エラー: マルチエージェントが500エラー
**原因**: GEMINI_API_KEYが無効または未設定  
**解決策**:
```bash
# .envファイルを確認
grep GEMINI_API_KEY .env

# 有効なAPIキーを設定
# https://makersuite.google.com/app/apikey
```

### Docker関連

#### エラー: `Cannot connect to the Docker daemon`
**解決策**:
1. Docker Desktopを起動
2. メニューバーでDockerアイコンを確認
3. `docker --version` で確認

#### エラー: `port is already allocated`
**解決策**:
```bash
# 使用中のプロセスを確認
lsof -i :5432  # または :8000, :3000

# プロセスをkill
kill -9 <PID>

# docker-composeを再起動
docker-compose down
docker-compose up -d
```

---

## パフォーマンス最適化

### マルチエージェント生成の高速化
- **並列処理**: 将来的に複数スライドの並列生成を検討
- **キャッシング**: 類似アウトラインの結果をキャッシュ
- **バッチ処理**: 複数スライドをまとめて生成

### データベース最適化
- **インデックス**: 頻繁に検索されるカラムにインデックス追加
- **コネクションプール**: Prismaのコネクションプール設定を最適化

---

## セキュリティ考慮事項

### 本番環境での設定変更
```env
# JWT秘密鍵を強力なものに変更
JWT_SECRET=<128文字以上のランダム文字列>

# 本番用データベース
DATABASE_URL="postgresql://secure_user:strong_password@db.prod:5432/slideturbo"

# CORS設定を本番ドメインに限定
ALLOWED_ORIGINS=https://yourdomain.com
```

### 推奨事項
- Google OAuth認証情報を環境変数で管理
- データベース接続文字列を暗号化
- HTTPS/TLSを必ず使用
- APIレート制限の実装
- ログの適切な管理

---

## ライセンス
[プロジェクトのライセンス情報]

## サポート
- **Issue**: [GitHub Issues URL]
- **ドキュメント**: [Documentation URL]
- **コミュニティ**: [Community URL]
