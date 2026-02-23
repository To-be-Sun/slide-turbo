# PR #12 変更報告書

## 概要

pr-11, pr-9 マージ後のバグ修正および機能追加を行いました。

---

## 🚨 Breaking Changes（破壊的変更）

### 1. Gemini APIモデル名の変更【必須対応】

| 項目 | 内容 |
|------|------|
| ファイル | `backend/.env` |
| 変更前 | `GEMINI_MODEL=gemini-1.5-flash-latest` |
| 変更後 | `GEMINI_MODEL=gemini-2.5-flash` |

**理由**: Google が gemini-1.5 モデルを廃止し、APIから削除されました。

**影響**: この変更がないとスライド生成が**完全に動作しません**（404エラー）。

```bash
# 確認コマンド
grep GEMINI_MODEL backend/.env
# 期待される出力: GEMINI_MODEL=gemini-2.5-flash
```

---

## ⚠️ 重要な仕様変更

### 2. フロントエンドAPI関数のモックデータ廃止

| 項目 | 内容 |
|------|------|
| ファイル | `frontend/lib/api.ts` |
| 変更対象 | 24個のAPI関数 |

**変更内容**: 
開発モード（`dev-token-slide-turbo`）でも全てのAPI関数が実際のバックエンドAPIを呼び出すように変更しました。

**影響**:
- バックエンドが起動していないと開発できなくなりました
- データはすべてPostgreSQLに保存されます
- localStorageへのモックデータ保存は廃止

**変更した関数一覧**:

| カテゴリ | 関数名 |
|---------|--------|
| Templates | `getTemplates`, `getTemplate`, `createTemplate`, `importTemplate`, `updateTemplate`, `deleteTemplate` |
| Slides | `getSlides`, `getSlide`, `createSlide`, `updateSlide`, `deleteSlide` |
| Versions | `getVersions`, `createVersion` |
| Pages | `getPages`, `addPage`, `updatePage`, `deletePage` |
| Outlines | `getOutlines`, `getOutline`, `createOutline`, `updateOutline`, `deleteOutline` |
| AI Operations | `refineOutline`, `generateSlideFromOutline` |

---

## ✨ 新機能

### 3. スライド生成中のローディングUI

| 項目 | 内容 |
|------|------|
| ファイル | `frontend/app/slides/[id]/page.tsx` |

**機能**:
- 画面中央にスピナー（ぐるぐる回転アイコン）を表示
- 「スライド生成中...」メッセージ
- 「AIが5つのエージェントでスライドを作成しています」の説明文
- 生成中はボタンが無効化され、二重クリック防止

### 4. Google Slidesエクスポートボタン

| 項目 | 内容 |
|------|------|
| ファイル | `frontend/app/slides/[id]/page.tsx`, `frontend/lib/api.ts` |

**機能**:
- プレビューエリアのヘッダーに「Google Slidesへ」ボタンを追加
- クリックすると現在のスライドをGoogle Slidesにエクスポート
- エクスポート成功時は新しいタブでGoogle Slidesを開く
- エクスポート中はローディングオーバーレイを表示

**注意**: `GOOGLE_REFRESH_TOKEN` が未設定の場合はエラーになります。

---

## 📝 新規ファイル

| ファイル | 用途 |
|---------|------|
| `backend/docs/USER_GUIDE.md` | ユーザーガイド |
| `backend/docs/API_REFERENCE.md` | API仕様書 |
| `backend/docs/TECHNICAL_SPECIFICATION.md` | 技術仕様書 |
| `backend/scripts/get_google_refresh_token.py` | Google OAuth トークン取得スクリプト |
| `frontend/.env.local` | フロントエンド環境変数設定 |

---

## 🔧 環境設定の追加

### backend/.env

```env
# 必須変更
GEMINI_MODEL=gemini-2.5-flash
```

### frontend/.env.local（新規作成）

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🐛 修正したバグ

1. **Gemini API 404エラー**: 廃止されたモデル名を使用していた
2. **モックデータの不整合**: フロントエンドがlocalStorageのデータを返し、データベースと不整合が発生
3. **スライド生成のフィードバック不足**: 生成中であることがユーザーに伝わらなかった

---

## 📋 チェックリスト

マージ前に以下を確認してください：

- [ ] `backend/.env` の `GEMINI_MODEL` が `gemini-2.5-flash` になっている
- [ ] `frontend/.env.local` に `NEXT_PUBLIC_API_URL=http://localhost:8000` が設定されている
- [ ] バックエンドサーバーが起動している状態でフロントエンドをテスト
- [ ] スライド生成が正常に動作する（ローディング表示 → スライド表示）

---

## 関連Issue/PR

- マージ元: pr-11, pr-9
- 関連: Google Slides API統合、マルチエージェントスライド生成
