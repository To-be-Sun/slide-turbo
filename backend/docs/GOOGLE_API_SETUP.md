# Google API セットアップガイド

このプロジェクトで使用するGoogle APIの有効化と認証設定の詳細手順です。

## 必要なAPI一覧

以下の2つのAPIを有効化する必要があります：

1. **Google Slides API** - スライドデータの取得と読み取り
2. **Google Drive API** - プレゼンテーションファイルへのアクセス

## セットアップ手順

### ステップ1: Google Cloud Console プロジェクトの作成

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 右上のプロジェクト選択ドロップダウンをクリック
3. 「新しいプロジェクト」をクリック
4. プロジェクト名を入力（例: `slide-gen-project`）
5. 「作成」をクリック
6. プロジェクトが作成されたら、そのプロジェクトを選択

### ステップ2: APIの有効化

#### 2-1. Google Slides API の有効化

1. 左側のメニューから「APIとサービス」→「ライブラリ」を選択
2. 検索バーに「Google Slides API」と入力
3. 「Google Slides API」をクリック
4. 「有効にする」ボタンをクリック
5. 有効化が完了するまで数秒待機

#### 2-2. Google Drive API の有効化

1. 「APIとサービス」→「ライブラリ」に戻る
2. 検索バーに「Google Drive API」と入力
3. 「Google Drive API」をクリック
4. 「有効にする」ボタンをクリック
5. 有効化が完了するまで数秒待機

**確認方法:**
- 「APIとサービス」→「有効なAPI」に移動
- 以下の2つが表示されていることを確認：
  - ✅ Google Slides API
  - ✅ Google Drive API

### ステップ3: OAuth 2.0 認証情報の作成

#### 3-1. OAuth同意画面の設定

1. 「APIとサービス」→「OAuth同意画面」を選択
2. ユーザータイプを選択：
   - **外部**（一般ユーザー向け）または
   - **内部**（Google Workspace組織内のみ）
3. 「作成」をクリック

4. OAuth同意画面の設定：
   - **アプリ名**: `Slide Gen`（任意の名前）
   - **ユーザーサポートメール**: あなたのメールアドレス
   - **デベロッパーの連絡先情報**: あなたのメールアドレス
   - 「保存して次へ」をクリック

5. スコープの設定：
   - 「スコープを追加または削除」をクリック
   - 以下のスコープを追加：
     - `https://www.googleapis.com/auth/presentations.readonly`
     - `https://www.googleapis.com/auth/drive.readonly`
   - 「更新」→「保存して次へ」をクリック

6. テストユーザーの追加（外部の場合）：
   - テストユーザーとして使用するGoogleアカウントのメールアドレスを追加
   - 「保存して次へ」をクリック

7. 概要を確認して「ダッシュボードに戻る」をクリック

#### 3-2. OAuth 2.0 クライアントIDの作成

1. 「APIとサービス」→「認証情報」を選択
2. 上部の「+ 認証情報を作成」→「OAuth クライアント ID」を選択

3. アプリケーションの種類を選択：
   - **「ウェブアプリケーション」**を選択

4. 名前を入力：
   - **名前**: `Slide Gen Backend`（任意の名前）

5. 承認済みのリダイレクト URI を追加：
   - 「URIを追加」をクリック
   - 以下のURIを追加：
     ```
     http://localhost:3000/login
     ```
   - 本番環境用のURIも追加する場合：
     ```
     https://yourdomain.com/login
     ```

6. 「作成」をクリック

7. **重要**: 表示されたダイアログから以下をコピーして保存：
   - **クライアントID**（例: `123456789-abcdefghijklmnop.apps.googleusercontent.com`）
   - **クライアントシークレット**（例: `GOCSPX-abcdefghijklmnopqrstuvwxyz`）

   ⚠️ **この情報は後で表示できないため、必ずコピーして保存してください**

### ステップ4: 環境変数の設定

バックエンドの`.env`ファイルに認証情報を設定：

```env
# Google API Configuration
GOOGLE_CLIENT_ID=ここにクライアントIDを貼り付け
GOOGLE_CLIENT_SECRET=ここにクライアントシークレットを貼り付け
GOOGLE_REDIRECT_URI=http://localhost:3000/login
```

### ステップ5: 認証フローの実行

1. バックエンドサーバーを起動：
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 3001
   ```

2. フロントエンドを起動：
   ```bash
   cd frontend
   pnpm dev
   ```

3. ブラウザでログイン画面にアクセス：
   ```
   http://localhost:3000/login
   ```

4. 「Google でログイン」をクリック

5. アクセス許可を確認：
   - 「Slide Gen が次の権限をリクエストしています」と表示
   - 権限を確認して「許可」をクリック

6. Google Slides 取り込みで利用する場合、`.env` に `GOOGLE_REFRESH_TOKEN` を設定：
   ```env
   GOOGLE_REFRESH_TOKEN=ここにリフレッシュトークンを貼り付け
   ```

7. 設定後にバックエンドを再起動

### ステップ6: 動作確認

1. フロントエンドを起動：
   ```bash
   cd frontend
   pnpm dev
   ```

2. ログインページにアクセスして Google 認証：
   ```
   http://localhost:3000/login
   ```

3. テンプレートページにアクセス：
   ```
   http://localhost:3000/templates
   ```

4. 「テンプレート追加」をクリック

5. Google SlidesのURLを入力（例）：
   ```
   https://docs.google.com/presentation/d/YOUR_PRESENTATION_ID/edit
   ```

6. 「読み込み」をクリックして動作確認

## トラブルシューティング

### エラー: "Access blocked: This app's request is invalid"

- OAuth同意画面の設定が完了していない可能性があります
- ステップ3-1のOAuth同意画面の設定を完了してください

### エラー: "redirect_uri_mismatch"

- `.env`の`GOOGLE_REDIRECT_URI`と、Google Cloud Consoleで設定したリダイレクトURIが一致しているか確認
- 完全一致が必要です（末尾のスラッシュも含めて）

### エラー: "invalid_grant"

- リフレッシュトークンが無効になっている可能性があります
- 新しいリフレッシュトークンを発行し、`.env` の `GOOGLE_REFRESH_TOKEN` を更新してください

### エラー: "API not enabled"

- Google Slides APIまたはGoogle Drive APIが有効化されていない可能性があります
- ステップ2を確認して、両方のAPIが有効になっているか確認してください

### テストユーザーが追加できない

- 外部アプリケーションの場合、テストユーザーを追加する必要があります
- OAuth同意画面の「テストユーザー」セクションで追加してください

## 本番環境への移行

本番環境では以下を変更してください：

1. OAuth同意画面を公開（「公開」ボタンをクリック）
2. 本番環境のリダイレクトURIを追加
3. `.env`の`GOOGLE_REDIRECT_URI`を本番環境のURLに変更

## 参考リンク

- [Google Cloud Console](https://console.cloud.google.com/)
- [Google Slides API ドキュメント](https://developers.google.com/slides/api)
- [Google Drive API ドキュメント](https://developers.google.com/drive/api)
- [OAuth 2.0 設定ガイド](https://developers.google.com/identity/protocols/oauth2)

