# 認証情報の設定方法

Google APIの認証情報を設定する方法は2つあります。

## 方法1: JSONファイルを使用（推奨）

Google Cloud ConsoleからダウンロードしたJSONファイルを使用する方法です。

### 手順

1. Google Cloud ConsoleでOAuth 2.0認証情報を作成
2. 「JSONをダウンロード」をクリックしてファイルをダウンロード
3. ダウンロードしたJSONファイルを `backend/` ディレクトリに配置
   - ファイル名は `client_secret_*.json` の形式（例: `client_secret_927850856578-7akadrh5n4jeahnd3qup48mrinp9scrp.apps.googleusercontent.com.json`）
   - または `client_secret.json` にリネーム

4. 環境変数でJSONファイルのパスを指定する場合（オプション）:
   ```env
   GOOGLE_CREDENTIALS_PATH=/path/to/client_secret.json
   ```

### JSONファイルの構造

```json
{
  "web": {
    "client_id": "your-client-id.apps.googleusercontent.com",
    "client_secret": "GOCSPX-your-client-secret",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
  }
}
```

### 優先順位

1. `GOOGLE_CREDENTIALS_PATH` 環境変数で指定されたパス
2. `backend/client_secret.json`
3. `backend/client_secret_*.json`（ワイルドカード検索）

---

## 方法2: 環境変数を使用

`.env`ファイルに直接認証情報を設定する方法です。

### 手順

1. `backend/.env` ファイルを作成または編集
2. 以下の環境変数を設定：

```env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:3001/auth/callback
GOOGLE_REFRESH_TOKEN=your-refresh-token
```

### 環境変数の取得方法

- **CLIENT_ID**: Google Cloud Console → 認証情報 → OAuth 2.0 クライアントID → クライアントID
- **CLIENT_SECRET**: 同じ画面のクライアントシークレット
- **REFRESH_TOKEN**: 認証フロー実行後に取得（[GOOGLE_API_SETUP.md](./GOOGLE_API_SETUP.md) を参照）

---

## どちらの方法を使うべきか

- **JSONファイル（推奨）**: 
  - Google Cloud Consoleから直接ダウンロードできる
  - 設定が簡単
  - 複数のプロジェクトで使い回しやすい

- **環境変数**:
  - CI/CD環境で使いやすい
  - 環境ごとに異なる認証情報を設定できる
  - シークレット管理ツールと統合しやすい

---

## セキュリティ注意事項

⚠️ **重要**: 認証情報ファイルは絶対にGitにコミットしないでください

- `.gitignore` に `client_secret*.json` が含まれていることを確認
- 環境変数も `.env` ファイルは `.gitignore` に含まれています
- 本番環境では環境変数やシークレット管理サービスを使用してください

