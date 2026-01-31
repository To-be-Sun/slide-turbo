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
GOOGLE_REDIRECT_URI=http://localhost:3001/auth/callback
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
4. リダイレクトURIに `http://localhost:3001/auth/callback` を追加
5. クライアントIDとシークレットを`.env`に設定

### 4. 認証フローの実行

1. サーバーを起動：
```bash
pnpm dev
```

2. ブラウザで認証URLにアクセス：
```
http://localhost:3001/api/google-slides/auth
```

3. Googleアカウントで認証
4. リフレッシュトークンを`.env`の`GOOGLE_REFRESH_TOKEN`に設定

## API エンドポイント

### Google Slides

- `GET /api/google-slides/auth` - 認証URLを取得
- `GET /api/google-slides/callback` - OAuthコールバック
- `POST /api/google-slides/import` - プレゼンテーションIDからインポート
- `POST /api/google-slides/parse-url` - URLからインポート
- `POST /api/google-slides/review-slide` - 単一スライドをレビュー

### スライド生成

- `POST /api/slides/generate` - テンプレートからスライドを生成
- `POST /api/slides/fill-slot` - AIでスロットを埋める
- `POST /api/slides/replace-slot` - HTML内のスロットを置き換え
- `GET /api/slides/render/:slideIndex` - スライドを画像としてレンダリング

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

