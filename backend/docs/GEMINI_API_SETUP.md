# Gemini API キーの設定方法

このプロジェクトでは、Google Gemini APIを使用してスライドのレビューやコンテンツ生成を行います。

## APIキーの取得方法

### 1. Google AI Studioにアクセス

1. [Google AI Studio](https://aistudio.google.com/app/apikey) にアクセス
2. Googleアカウントでログイン

### 2. APIキーを作成

1. 「Create API Key」ボタンをクリック
2. 既存のGoogle Cloudプロジェクトを選択するか、新しいプロジェクトを作成
3. APIキーが生成されます
4. **重要**: 生成されたAPIキーをコピーして保存してください（後で表示できません）

### 3. 環境変数に設定

バックエンドの `.env` ファイルを作成または編集：

```bash
cd backend
```

`.env` ファイルを作成（`.env.example`をコピー）：

```bash
cp .env.example .env
```

`.env` ファイルを編集して、取得したAPIキーを設定：

```env
GEMINI_API_KEY=あなたのAPIキーをここに貼り付け
```

例：
```env
GEMINI_API_KEY=AIzaSyAbCdEfGhIjKlMnOpQrStUvWxYz1234567
```

### 4. 動作確認

バックエンドサーバーを起動：

```bash
pnpm dev
```

エラーが表示されなければ、APIキーが正しく設定されています。

## 使用される機能

Gemini APIは以下の機能で使用されます：

1. **スライドレビュー** (`src/services/gemini-reviewer.ts`)
   - Google SlidesからインポートしたHTMLをレビュー
   - タイトルと説明を自動生成
   - スロットを提案

2. **スロット埋め** (`src/services/slot-replacer.ts`)
   - AIを使ってスロットの内容を生成
   - コンテキストに基づいた内容生成

3. **HTML生成** (`src/services/template-to-html.ts`)
   - スライドのHTMLを生成
   - デザインの提案

## トラブルシューティング

### エラー: "GEMINI_API_KEY environment variable is required"

- `.env` ファイルが `backend/` ディレクトリに存在するか確認
- `GEMINI_API_KEY` が正しく設定されているか確認
- サーバーを再起動

### エラー: "API key not valid"

- APIキーが正しくコピーされているか確認
- Google AI StudioでAPIキーが有効か確認
- APIキーに制限がかかっていないか確認

### エラー: "Quota exceeded"

- APIの使用量制限に達している可能性があります
- Google Cloud Consoleでクォータを確認
- 有料プランにアップグレードする必要がある場合があります

## セキュリティ注意事項

⚠️ **重要**: APIキーは絶対にGitにコミットしないでください

- `.env` ファイルは `.gitignore` に含まれています
- 本番環境では環境変数やシークレット管理サービスを使用してください
- APIキーを他人と共有しないでください

## 参考リンク

- [Google AI Studio](https://aistudio.google.com/app/apikey)
- [Gemini API ドキュメント](https://ai.google.dev/docs)
- [APIキーの管理](https://aistudio.google.com/app/apikey)

