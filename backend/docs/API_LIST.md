# 有効化が必要なGoogle API一覧

このプロジェクトで使用するGoogle Cloud APIの一覧です。

## 必須API（2つ）

### 1. Google Slides API

**用途**: Google Slidesプレゼンテーションのデータを取得

**必要な権限（スコープ）**:
- `https://www.googleapis.com/auth/presentations.readonly` - プレゼンテーションの読み取り専用アクセス

**有効化手順**:
1. Google Cloud Console → 「APIとサービス」→ 「ライブラリ」
2. 「Google Slides API」を検索
3. 「有効にする」をクリック

**API名**: `slides.googleapis.com`

---

### 2. Google Drive API

**用途**: Google Drive上のプレゼンテーションファイルへのアクセス

**必要な権限（スコープ）**:
- `https://www.googleapis.com/auth/drive.readonly` - Google Driveの読み取り専用アクセス

**有効化手順**:
1. Google Cloud Console → 「APIとサービス」→ 「ライブラリ」
2. 「Google Drive API」を検索
3. 「有効にする」をクリック

**API名**: `drive.googleapis.com`

---

## 確認方法

有効化されたAPIを確認するには：

1. Google Cloud Console → 「APIとサービス」→ 「有効なAPI」
2. 以下の2つが表示されていることを確認：
   - ✅ **Google Slides API**
   - ✅ **Google Drive API**

## 注意事項

- 両方のAPIを有効化する必要があります
- APIの有効化は無料ですが、使用量に応じて課金される場合があります（通常の読み取り操作は無料枠内）
- OAuth 2.0認証情報の作成も必要です（詳細は [GOOGLE_API_SETUP.md](./GOOGLE_API_SETUP.md) を参照）

