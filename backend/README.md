# Slide Gen Backend

Google Slides APIとGemini 3を使用したスライド生成バックエンド

## 機能

- **Google Slides API統合**: Google Slidesプレゼンテーションをインポート
- **スライド→HTML変換**: スライドオブジェクトを詳細に解析してHTMLに変換
- **Geminiレビュー**: Gemini 3でHTMLをレビューしてタイトルとスロットを自動生成
- **テンプレート生成**: 既存のGoogle Slidesから編集可能なテンプレートを生成

## セットアップ

### 1. 依存関係のインストール

```bash
cd backend
pnpm install
# または
npm install
```

### 2. 環境変数の設定

`.env`ファイルを作成し、以下の変数を設定：

```bash
cd backend
cp .env.example .env
```

`.env`ファイルを編集：

```env
# Database
DATABASE_URL="postgresql://user:password@localhost:5432/slide_gen?schema=public"

# Gemini API Configuration（必須）
# Google AI Studio (https://aistudio.google.com/app/apikey) でAPIキーを取得
GEMINI_API_KEY=your_gemini_api_key_here

# Google API Configuration
# JSONファイルを使う場合は以下は不要
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:3000/login
GOOGLE_REFRESH_TOKEN=your_refresh_token_here

# Server Configuration
PORT=3001
NODE_ENV=development

# CORS Configuration
FRONTEND_URL=http://localhost:3000
```

**詳細な設定方法:**
- Gemini APIキー: [Gemini API セットアップガイド](./docs/GEMINI_API_SETUP.md)
- Google認証情報: [認証情報設定ガイド](./docs/CREDENTIALS_SETUP.md)

### 3. Google API認証の設定

**詳細な手順は [Google API セットアップガイド](./docs/GOOGLE_API_SETUP.md) を参照してください。**

簡易手順：
1. [Google Cloud Console](https://console.cloud.google.com/)でプロジェクトを作成
2. **Google Slides API** と **Google Drive API** を有効化
3. OAuth 2.0認証情報を作成（ウェブアプリケーション）
4. リダイレクトURIに `http://localhost:3000/login` を追加
5. クライアントIDとシークレットを`.env`に設定

### 4. 認証フローの実行

1. サーバーを起動：
```bash
pnpm dev
```

2. ブラウザでフロントエンドのログイン画面にアクセス：
```
http://localhost:3000/login
```

3. 「Google でログイン」をクリックして認証
4. リフレッシュトークンを`.env`の`GOOGLE_REFRESH_TOKEN`に設定

## API エンドポイント

### 認証・ユーザー

- `GET /api/v1/users/auth/google` - Google OAuth へリダイレクト
- `POST /api/v1/users/auth/google/callback` - 認可コードを受け取りJWTを発行
- `GET /api/v1/users/me` - ログイン中ユーザー取得
- `PATCH /api/v1/users/me` - ユーザー更新

### テンプレート

- `POST /api/v1/templates` - テンプレート作成
- `POST /api/v1/templates/import` - Google Slides URLからテンプレートをインポート
- `GET /api/v1/templates` - テンプレート一覧
- `GET /api/v1/templates/{template_id}` - テンプレート詳細
- `PATCH /api/v1/templates/{template_id}` - テンプレート更新
- `DELETE /api/v1/templates/{template_id}` - テンプレート削除

### スライド

- `POST /api/v1/slides` - スライド作成
- `GET /api/v1/slides` - スライド一覧
- `GET /api/v1/slides/{slide_id}` - スライド詳細
- `PATCH /api/v1/slides/{slide_id}` - スライド更新
- `DELETE /api/v1/slides/{slide_id}` - スライド削除

## パイプライン

1. **Google Slides取得**: プレゼンテーションIDからスライドデータを取得
2. **要素抽出**: テキスト、画像、図形などの要素を抽出
3. **HTML変換**: 要素を構造化されたHTMLに変換
4. **Geminiレビュー**: HTMLを分析してタイトルとスロットを生成
5. **テンプレート生成**: 編集可能なテンプレートとして保存

## 開発

```bash
# 開発モード（ホットリロード）
pnpm dev

# ビルド
pnpm build

# 本番モード
pnpm start

# 型チェック
pnpm type-check
```
