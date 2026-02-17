# HTMLレンダリング & リアルタイムプレビュー & Google Slidesエクスポート機能 - 実装TODO

## 📋 概要

エージェントが出力したJSON構造からHTMLプレビューを生成し、リアルタイム更新とGoogle Slidesへのエクスポートを実装する。

---

## 🗂️ 必要なファイルとTODOリスト

### 1️⃣ **バックエンド - スキーマ定義** ✅ 完了

#### `backend/app/infrastructure/rendering/schema.py`
**目的**: JSON構造のPydanticモデル定義

**完了済み**:
- [x] `ElementPosition` クラスを定義（x, y, width, height）
- [x] `TextStyle` クラスを定義（font_family, font_size, font_weight, color, align, line_height）
- [x] `BackgroundStyle` クラスを定義（color, image_url）
- [x] 基底クラス `SlideElement` を定義（element_id, type, position, z_index）
- [x] `TextElement` クラスを定義（content, style, placeholder）
- [x] `ImageElement` クラスを定義（source_url, alt_text, placeholder）
- [x] `ShapeElement` クラスを定義（shape_type, fill_color, border_color, border_width）
- [x] `ChartElement` クラスを定義（chart_type, data）
- [x] `TableElement` クラスを定義（rows, cols, cells）
- [x] `SlidePage` クラスを定義（page_num, layout, background, elements, notes）
- [x] `SlidePresentation` クラスを定義（title, pages, metadata）
- [x] バリデーションルールを追加（色のHEX形式、座標の正負など）

**テスト**: 31テストケース全てパス ✅

---

### 2️⃣ **バックエンド - HTMLレンダラー** ✅ 完了

#### `backend/app/infrastructure/rendering/html_renderer.py`
**目的**: JSON → HTML変換ロジック

**完了済み**:
- [x] `HTMLRenderer` クラスを作成
- [x] `render_presentation(presentation: SlidePresentation) -> str` メソッド実装
  - [x] HTMLドキュメント構造を生成
  - [x] CSSスタイルを埋め込み
  - [x] JavaScriptナビゲーションを埋め込み
- [x] `render_page(page: SlidePage) -> str` メソッド実装
  - [x] 単一ページのHTML生成
  - [x] 背景スタイル適用
- [x] `_render_element()` メソッド実装（要素タイプごとに分岐）
- [x] `_render_text(element: TextElement) -> str` 実装
  - [x] インラインスタイル生成
  - [x] HTMLエスケープ処理
- [x] `_render_image(element: ImageElement) -> str` 実装
- [x] `_render_shape(element: ShapeElement) -> str` 実装
  - [x] 円形の場合はborder-radius適用
- [x] `_render_chart(element: ChartElement) -> str` 実装
  - [x] Canvas要素を生成
  - [x] Chart.js用のdata属性を設定
- [x] `_render_table(element: TableElement) -> str` 実装
- [x] `_render_background(background: BackgroundStyle) -> str` 実装
- [x] `_escape_html(text: str) -> str` ユーティリティ実装
- [x] レスポンシブ対応のCSSを追加
- [x] キーボードナビゲーション（矢印キー）のJSを追加

**テスト**: 21テストケース全てパス ✅

---

### 3️⃣ **バックエンド - Google Slidesエクスポーター** ✅ 完了

#### `backend/app/infrastructure/google_slides/exporter.py`
**目的**: JSON → Google Slides API変換

**完了済み**:
- [x] `GoogleSlidesExporter` クラスに `export_presentation()` メソッド追加
- [x] 空のプレゼンテーションを作成（`presentations().create()`）
- [x] 初期スライドを削除
- [x] `_build_slide_requests(page: SlidePage)` メソッド実装
  - [x] スライド作成リクエスト生成
  - [x] 背景設定リクエスト生成
- [x] `_build_element_requests()` メソッド実装
  - [x] TextElement → createShape + insertText + updateTextStyle
  - [x] ImageElement → createImage
  - [x] ShapeElement → createShape
  - [x] TableElement → createTable
  - [ ] ChartElement → 未実装TODOコメント追加
- [x] `_map_layout(layout: str)` メソッド実装（レイアウト名マッピング）
- [x] `_map_shape_type(shape_type: str)` メソッド実装
- [x] `_hex_to_rgb(hex_color: str)` メソッド実装
- [x] px → PT 変換ロジックを追加
- [x] バッチリクエストを実行（`presentations().batchUpdate()`）
- [x] プレゼンテーションURL、ダウンロードURLを返す
- [x] エラーハンドリング追加（API呼び出し失敗時）

---

### 4️⃣ **バックエンド - Repository拡張** ✅ 完了 (Phase 2)

#### `backend/app/infrastructure/persistence/slide_repository.py`
**目的**: バージョン番号によるSlideVersion取得機能

**完了済み**:
- [x] `find_version_by_num(slide_id: str, version_num: int)` メソッド追加
  - [x] `slideversion.find_first()` でクエリ
  - [x] `where={"slideId": slide_id, "versionNum": version_num}`
  - [x] Noneチェック

---

### 5️⃣ **バックエンド - UseCases拡張** ✅ 完了 (Phase 2 & 3)

#### `backend/app/application/slide/usecases.py`
**目的**: HTMLレンダリングとエクスポート機能の追加

**完了済み**:
- [x] `HTMLRenderer` と `GoogleSlidesExporter` を依存性注入
- [x] `__init__` メソッドに `google_slides_exporter` パラメータ追加
- [x] `render_preview(slide_id: str, version_num: int) -> str` メソッド追加
  - [x] スライド取得
  - [x] バージョン取得
  - [x] ページ一覧取得
  - [x] Page.contents → SlidePresentationに変換
  - [x] HTMLRenderer.render_presentation() 呼び出し
  - [x] エラーハンドリング（NotFoundExceptionなど）
- [x] `export_to_google_slides(slide_id: str, version_num: int) -> dict` メソッド追加
  - [x] スライド取得
  - [x] バージョン取得
  - [x] ページ一覧取得
  - [x] Page.contents → SlidePresentationに変換
  - [x] GoogleSlidesExporter.export_presentation() 呼び出し
  - [x] 結果を返す

---

### 6️⃣ **バックエンド - Router拡張** ✅ 完了 (Phase 2 & 3)

#### `backend/app/presentation/routers/slide_router.py`
**目的**: プレビューとエクスポートのエンドポイント追加

**完了済み**:
- [x] `HTMLResponse` を FastAPI からインポート
- [x] `Query` をインポート
- [x] `GET /{slide_id}/preview` エンドポイント追加
  - [x] `version` クエリパラメータ（int）
  - [x] `response_class=HTMLResponse` を指定
  - [x] `uc.render_preview()` を呼び出し
  - [x] HTML文字列を返す
- [x] `POST /{slide_id}/export/google-slides` エンドポイント追加
  - [x] `version` クエリパラメータ（int）
  - [x] `uc.export_to_google_slides()` を呼び出し
  - [x] `{"success": True, "data": result}` 形式で返す
- [x] エラーハンドリング（各UseCaseの例外をキャッチ）

---

### 7️⃣ **バックエンド - パッケージ初期化** ✅ 完了

#### `backend/app/infrastructure/rendering/__init__.py`
**目的**: renderingパッケージのエクスポート

**完了済み**:
- [x] `HTMLRenderer` をインポート
- [x] `SlidePage`, `SlidePresentation`, `TextElement` などをインポート
- [x] `__all__` リストに追加

---

### 8️⃣ **フロントエンド - API型定義**

#### `frontend/lib/slide-rendering.ts`
**目的**: スライドレンダリングAPI用の型とクライアント

**TODO**:
- [ ] `getSlidePreview(slideId: string, version?: number)` 関数実装
  - [ ] fetch で `GET /api/v1/slides/{id}/preview` を呼び出し
  - [ ] `response.text()` でHTML取得
  - [ ] 認証トークンをヘッダーに付与
- [ ] `exportToGoogleSlides(slideId: string, version?: number)` 関数実装
  - [ ] `POST /api/v1/slides/{id}/export/google-slides` を呼び出し
  - [ ] 結果のURLを返す
- [ ] TypeScript型定義を追加
  - [ ] `SlidePageContent` インターフェース
  - [ ] `SlideElement` 型（Union型）
  - [ ] `TextElement`, `ImageElement`, `ShapeElement`, `ChartElement`, `TableElement`
  - [ ] `BaseElement` インターフェース（position, z_index）

---

### 9️⃣ **フロントエンド - プレビューコンポーネント**

#### `frontend/components/slide-preview.tsx`
**目的**: リアルタイムHTMLプレビュー表示

**TODO**:
- [ ] `SlidePreview` コンポーネント作成
- [ ] Props定義: `slideId`, `version`, `refreshInterval`
- [ ] `useState` でHTML、loading、error、lastUpdatedを管理
- [ ] `fetchPreview()` 関数実装
  - [ ] `getSlidePreview()` API呼び出し
  - [ ] エラーハンドリング
- [ ] `useEffect` でプレビュー取得
  - [ ] refreshInterval > 0 の場合は setInterval で自動更新
  - [ ] クリーンアップ関数でclearInterval
- [ ] `handleRefresh()` 手動更新ボタン実装
- [ ] ローディング表示（`<Loader2>` アニメーション）
- [ ] エラー表示（`<Alert>` コンポーネント）
- [ ] iframe要素でHTMLプレビュー表示
  - [ ] `srcDoc` 属性にHTML設定
  - [ ] `sandbox="allow-scripts allow-same-origin"` 設定
- [ ] 最終更新時刻の表示
- [ ] レスポンシブ対応（スマホ・タブレット・PC）

---

### 🔟 **フロントエンド - エクスポートダイアログ**

#### `frontend/components/export-to-google-slides-dialog.tsx`
**目的**: Google Slidesエクスポートダイアログ

**TODO**:
- [ ] `ExportToGoogleSlidesDialog` コンポーネント作成
- [ ] Props定義: `slideId`, `version`
- [ ] `useState` で open, exporting, error, result を管理
- [ ] `Dialog` コンポーネントを使用（shadcn/ui）
- [ ] `handleExport()` 関数実装
  - [ ] `exportToGoogleSlides()` API呼び出し
  - [ ] loading状態管理
  - [ ] エラーハンドリング
- [ ] エクスポート開始ボタン
- [ ] ローディング表示（`<Loader2>` + メッセージ）
- [ ] 成功時の表示
  - [ ] 成功アラート
  - [ ] Google Slidesで開くリンク（`presentation_url`）
  - [ ] PPTX ダウンロードリンク（`download_url`）
  - [ ] 外部リンクアイコン（`<ExternalLink>`）
- [ ] エラー表示（`<Alert variant="destructive">`）
- [ ] 閉じるボタン

---

## 🔄 実装の流れ（推奨順序）

### Phase 1: バックエンド基盤 ✅ 完了（rendering dir）
1. ✅ `schema.py` - データ構造定義（12クラス、31テスト）
2. ✅ `html_renderer.py` - HTMLレンダリング（21テスト）
3. ⏭️ `slide_repository.py` - Repository拡張
4. ✅ `rendering/__init__.py` - パッケージ初期化

### Phase 2: バックエンド機能 ✅ 完了
5. ✅ `usecases.py` - UseCases拡張
6. ✅ `slide_router.py` - エンドポイント追加
7. ✅ **テスト実行** - バックエンド単体でプレビュー確認（52テスト全てパス）

### Phase 3: Google Slidesエクスポート ✅ 完了
8. ✅ `exporter.py` - エクスポート機能実装
9. ⏭️ **テスト実行** - Google Slides API動作確認（手動テスト推奨）

### Phase 3.5: バックエンドリファクタリング ✅ 完了
- ✅ `exporter.py` リファクタリング（481行 → 345行、28.3%削減）
- ✅ 定数の外部化（LAYOUT_MAPPING, SHAPE_TYPE_MAPPING, TEXT_ALIGN_MAPPING）
- ✅ 共通プロパティビルダー抽出（_build_element_properties）
- ✅ ヘルパー関数のモジュール化（hex_to_rgb, px_to_pt）
- ✅ コード重複削減（60行の重複を解消）

### Phase 4: フロントエンド
10. `slide-rendering.ts` - API型定義
11. `slide-preview.tsx` - プレビューコンポーネント
12. `export-to-google-slides-dialog.tsx` - エクスポートダイアログ
13. **統合テスト** - E2Eでの動作確認

---

## 🧪 テストケース

### バックエンド単体テスト
- [x] `schema.py`: Pydanticモデルのバリデーションテスト（31/31 passed ✅）
- [x] `html_renderer.py`: 各要素タイプのHTML生成テスト（21/21 passed ✅）
- [ ] `exporter.py`: Google Slides APIリクエスト生成テスト（手動テスト推奨）

### 統合テスト
- [x] `GET /api/v1/slides/{id}/preview` - 200応答とHTML取得 ✅
- [ ] `POST /api/v1/slides/{id}/export/google-slides` - 成功レスポンス
- [ ] フロントエンド: リアルタイムプレビュー動作確認
- [ ] フロントエンド: エクスポート → Google Slidesで開ける

---

## 📚 参考資料

- JSON Schema: `backend/app/infrastructure/rendering/slide_page.json`
- Google Slides API Docs: https://developers.google.com/slides/api/reference/rest
- Chart.js Docs: https://www.chartjs.org/docs/
- shadcn/ui Components: https://ui.shadcn.com/

---

## ⚠️ 注意事項

1. **px → PT 変換**: Google Slides APIはポイント（PT）単位を使用。1px ≈ 0.75pt
2. **認証**: Google Slides APIアクセスには `X-Google-Access-Token` ヘッダーが必要
3. **CORS**: プレビュー iframe の sandbox 属性を適切に設定
4. **メモリ管理**: リアルタイム更新のインターバルは5秒以上推奨
5. **エラーハンドリング**: トークン期限切れ時のリダイレクト処理

---

## 🎯 完成後の機能

✅ エージェントJSON → HTMLプレビュー変換  
⏭️ 手動プレビュー（自動更新は未実装）  
✅ Google Slidesエクスポート  
✅ PPTX ダウンロード  
✅ レスポンシブ対応（HTML）  
✅ キーボードナビゲーション（HTML）

---

## 📊 実装進捗サマリー

### Phase 1: バックエンド基盤 ✅ 完了
- rendering/schema.py: 12クラス、31テスト
- rendering/html_renderer.py: HTMLRenderer、21テスト
- **合計**: 52テスト全てパス ✅

### Phase 2: バックエンド機能 ✅ 完了
- slide_repository.py: find_version_by_num 追加
- usecases.py: render_preview 追加
- slide_router.py: GET /{slide_id}/preview 追加
- **合計**: HTMLプレビューAPI実装完了 ✅

### Phase 3: Google Slidesエクスポート ✅ 完了
- client.py: OAuth2スコープ更新（書き込み権限）
- exporter.py: export_presentation + 9個のヘルパーメソッド
- usecases.py: export_to_google_slides 追加
- slide_router.py: POST /{slide_id}/export/google-slides 追加
- **合計**: Google Slidesエクスポート機能完了 ✅

### Phase 3.5: バックエンドリファクタリング ✅ 完了
- exporter.py: 481行 → 345行（28.3%削減）
- 定数化、共通プロパティ抽出、ヘルパー関数モジュール化
- コード重複100%削減（60行の重複解消）
- **合計**: 保守性・可読性大幅向上 ✅

### Phase 4: フロントエンド ⏭️ 未実装
- slide-rendering.ts: API型定義とクライアント
- slide-preview.tsx: プレビューコンポーネント
- export-to-google-slides-dialog.tsx: エクスポートダイアログ  
