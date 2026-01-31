# データベースセットアップガイド

PostgreSQLとPrismaを使用したデータベースのセットアップ手順です。

## 前提条件

- PostgreSQLがインストールされていること
- Node.jsとpnpmがインストールされていること

## セットアップ手順

### 1. PostgreSQLのインストール

#### macOS (Homebrew)
```bash
brew install postgresql@15
brew services start postgresql@15
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

#### Windows
[PostgreSQL公式サイト](https://www.postgresql.org/download/windows/)からインストーラーをダウンロード

### 2. データベースの作成

```bash
# PostgreSQLに接続
psql postgres

# データベースを作成
CREATE DATABASE slide_gen;

# ユーザーを作成（オプション）
CREATE USER slide_gen_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE slide_gen TO slide_gen_user;

# 終了
\q
```

### 3. 環境変数の設定

`.env`ファイルを作成または編集：

```env
DATABASE_URL="postgresql://user:password@localhost:5432/slide_gen?schema=public"
```

接続文字列の形式：
- `postgresql://ユーザー名:パスワード@ホスト:ポート/データベース名?schema=スキーマ名`

例：
```env
# デフォルトユーザー（postgres）を使用
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/slide_gen?schema=public"

# カスタムユーザーを使用
DATABASE_URL="postgresql://slide_gen_user:your_password@localhost:5432/slide_gen?schema=public"
```

### 4. Prismaのセットアップ

```bash
cd backend

# 依存関係をインストール
pnpm install

# Prismaクライアントを生成
pnpm db:generate

# データベースにスキーマを適用
pnpm db:push

# または、マイグレーションを使用（推奨）
pnpm db:migrate
```

### 5. シードデータの投入（オプション）

```bash
pnpm db:seed
```

## コマンド一覧

### データベース操作

```bash
# Prismaクライアントを生成
pnpm db:generate

# スキーマをデータベースに適用（開発用）
pnpm db:push

# マイグレーションを作成・適用（本番用）
pnpm db:migrate

# Prisma Studioを起動（GUIでデータベースを確認）
pnpm db:studio

# シードデータを投入
pnpm db:seed
```

### マイグレーション

```bash
# 新しいマイグレーションを作成
pnpm db:migrate --name migration_name

# マイグレーションを適用
pnpm db:migrate deploy

# マイグレーションをリセット（注意：データが削除されます）
pnpm db:migrate reset
```

## データベーススキーマ

主要なテーブル：

- **templates** - スライドテンプレート
- **template_slots** - テンプレートのスロット定義
- **projects** - プロジェクト
- **filled_slots** - 埋められたスロット
- **story_sections** - ストーリーセクション
- **project_materials** - プロジェクトマテリアル
- **project_versions** - プロジェクトバージョン
- **suggestions** - AI提案
- **chat_messages** - チャットメッセージ
- **history_items** - 履歴

詳細は `prisma/schema.prisma` を参照してください。

## トラブルシューティング

### エラー: "Can't reach database server"

- PostgreSQLが起動しているか確認
- 接続文字列が正しいか確認
- ファイアウォール設定を確認

### エラー: "relation does not exist"

- マイグレーションが適用されていない可能性
- `pnpm db:push` または `pnpm db:migrate` を実行

### エラー: "password authentication failed"

- データベースのパスワードが正しいか確認
- `.env`の`DATABASE_URL`を確認

## Prisma Studio

データベースの内容をGUIで確認・編集できます：

```bash
pnpm db:studio
```

ブラウザで `http://localhost:5555` が開きます。

