# Slide Gen Backend (Python/FastAPI)

Google Slides APIとGemini 3を使用したスライド生成バックエンド

## 機能

- **Google Slides API統合**: Google Slidesプレゼンテーションをインポート
- **スライド→HTML変換**: スライドオブジェクトを詳細に解析してHTMLに変換
- **Geminiレビュー**: Gemini 3でHTMLをレビューしてタイトルとスロットを自動生成
- **テンプレート生成**: 既存のGoogle Slidesから編集可能なテンプレートを生成

## セットアップ

### 1. Conda環境のセットアップ（推奨）

```bash
cd backend

# セットアップスクリプトを実行（自動で環境作成と依存関係インストール）
# macOS/Linux:
chmod +x setup_conda.sh
./setup_conda.sh

# Windows:
# setup_conda.bat

# または手動で:
# conda環境を作成
conda create -n slide-gen-backend python=3.11 -y

# 環境をアクティベート
conda activate slide-gen-backend

# pipをアップグレード
pip install --upgrade pip

# 依存関係のインストール
pip install -r requirements.txt

# Playwrightブラウザのインストール（スライドレンダリング用）
playwright install chromium
```

### 1-2. 仮想環境を使用する場合（condaを使わない場合）

```bash
cd backend

# Python 3.11以上が必要
python --version

# 仮想環境を作成（推奨）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt

# Playwrightブラウザのインストール（スライドレンダリング用）
playwright install chromium
```

### 2. 環境変数の設定

`.env`ファイルを作成し、以下の変数を設定：

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/slide_gen?schema=public

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

### 3. データベースのセットアップ

```bash
# Alembicでマイグレーション（今後実装予定）
# 現在は自動でテーブルが作成されます

# データベースが存在することを確認
# PostgreSQLが起動していることを確認してください
```

### 4. Google API認証の設定

**詳細な手順は [Google API セットアップガイド](./docs/GOOGLE_API_SETUP.md) を参照してください。**

簡易手順：
1. [Google Cloud Console](https://console.cloud.google.com/)でプロジェクトを作成
2. **Google Slides API** と **Google Drive API** を有効化
3. OAuth 2.0認証情報を作成（ウェブアプリケーション）
4. リダイレクトURIに `http://localhost:3001/auth/callback` を追加
5. クライアントIDとシークレットを`.env`に設定、または`client_secret_*.json`ファイルを配置

### 5. 認証フローの実行

1. サーバーを起動：
```bash
python -m app.main
# または
uvicorn app.main:app --reload --port 3001
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
- `GET /api/slides/render/{slide_index}` - スライドを画像としてレンダリング

### プロジェクト

- `GET /api/projects` - プロジェクト一覧を取得
- `GET /api/projects/{id}` - プロジェクトを取得
- `POST /api/projects` - プロジェクトを作成
- `PATCH /api/projects/{id}` - プロジェクトを更新
- `DELETE /api/projects/{id}` - プロジェクトを削除
- `PATCH /api/projects/{id}/slots/{slot_id}` - スロットを更新
- `PATCH /api/projects/{id}/slots` - スロットを一括更新

### テンプレート

- `GET /api/templates` - テンプレート一覧を取得
- `GET /api/templates/{id}` - テンプレートを取得
- `POST /api/templates` - テンプレートを作成
- `PATCH /api/templates/{id}` - テンプレートを更新
- `DELETE /api/templates/{id}` - テンプレートを削除

## 開発

```bash
# conda環境をアクティベート（まだの場合）
conda activate slide-gen-backend

# 開発モード（ホットリロード）
uvicorn app.main:app --reload --port 3001

# 本番モード
uvicorn app.main:app --host 0.0.0.0 --port 3001

# 型チェック（mypyを使用する場合）
mypy app/
```

## Conda環境の管理

```bash
# 環境をアクティベート
conda activate slide-gen-backend

# 環境を非アクティブ化
conda deactivate

# 環境を削除
conda env remove -n slide-gen-backend

# インストール済みパッケージの確認
conda list

# 環境のエクスポート（依存関係のバックアップ）
conda env export > environment.yml

# 環境のインポート（依存関係の復元）
conda env create -f environment.yml
```

## パイプライン

1. **Google Slides取得**: プレゼンテーションIDからスライドデータを取得
2. **要素抽出**: テキスト、画像、図形などの要素を抽出
3. **HTML変換**: 要素を構造化されたHTMLに変換
4. **Geminiレビュー**: HTMLを分析してタイトルとスロットを生成
5. **テンプレート生成**: 編集可能なテンプレートとして保存

## 注意事項

- TypeScriptバックエンドからPythonバックエンドに移行しました
- データベーススキーマは同じですが、PrismaからSQLAlchemyに変更されています
- 古いTypeScriptファイルは`src/`ディレクトリに残っていますが、使用されていません

