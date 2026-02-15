# 📋 必要なファイル一覧と実装TODO

エージェントJSON → HTMLプレビュー → Google Slidesエクスポート機能の実装に必要なファイルとTODOリストです。

---

## 📂 ファイル構成

```
backend/app/infrastructure/rendering/
├── slide_page.json                      # ✅ 作成済み - JSONスキーマ定義と例
├── slide_page_example_google_api.json   # ✅ 作成済み - Google Slides API形式の参考例
├── __init__.py                          # ✅ 完了 - パッケージ初期化
├── schema.py                            # ✅ 完了 - Pydanticモデル定義（12クラス）
└── html_renderer.py                     # ✅ 完了 - HTMLレンダラー

backend/tests/infrastructure/rendering/
├── __init__.py                          # ✅ 完了 - テストパッケージ
├── test_schema.py                       # ✅ 完了 - schema.pyのテスト（31テスト）
└── test_html_renderer.py                # ✅ 完了 - html_renderer.pyのテスト（21テスト）

backend/app/infrastructure/google_slides/
└─ exporter.py                          # ✅ 完了 - エクスポート機能追加（既存ファイル更新）

backend/app/infrastructure/persistence/
└─ slide_repository.py                  # ✅ 完了 - find_version_by_num追加（Phase 2）

backend/app/application/slide/
└─ usecases.py                          # ✅ 完了 - render_preview, export_to_google_slides追加

backend/app/presentation/routers/
└─ slide_router.py                      # ✅ 完了 - プレビュー・エクスポートエンドポイント追加

frontend/lib/
└── slide-rendering.ts                   # ❌ TODO - API型定義とクライアント

frontend/components/
├── slide-preview.tsx                    # ❌ TODO - プレビューコンポーネント
└── export-to-google-slides-dialog.tsx   # ❌ TODO - エクスポートダイアログ
```

---

## 🔧 ファイル別TODOリスト

### 1. `backend/app/infrastructure/rendering/schema.py` ✅ 完了
**目的**: JSON構造のPydanticモデル定義

```python
# ✅ 実装完了 - 以下のクラスを実装済み

# - [ ] ElementPosition(BaseModel)
#       x: float, y: float, width: float, height: float

# - [ ] TextStyle(BaseModel)
#       font_family: str = "Arial"
#       font_size: float = 16
#       font_weight: Literal["normal", "bold"] = "normal"
#       color: str = "#000000"
#       align: Literal["left", "center", "right"] = "left"
#       line_height: float = 1.5

# - [ ] BackgroundStyle(BaseModel)
#       color: Optional[str] = None
#       image_url: Optional[str] = None

# - [ ] SlideElement(BaseModel) - 基底クラス
#       element_id: str
#       type: Literal["text", "image", "shape", "chart", "table"]
#       position: ElementPosition
#       z_index: int = 0

# - [ ] TextElement(SlideElement)
#       type: Literal["text"] = "text"
#       content: str
#       style: TextStyle = Field(default_factory=TextStyle)
#       placeholder: Optional[str] = None

# - [ ] ImageElement(SlideElement)
#       type: Literal["image"] = "image"
#       source_url: str
#       alt_text: str = ""
#       placeholder: Optional[str] = None

# - [ ] ShapeElement(SlideElement)
#       type: Literal["shape"] = "shape"
#       shape_type: Literal["rectangle", "circle", "triangle"]
#       fill_color: str = "#CCCCCC"
#       border_color: Optional[str] = None
#       border_width: float = 0

# - [ ] ChartElement(SlideElement)
#       type: Literal["chart"] = "chart"
#       chart_type: Literal["bar", "line", "pie"]
#       data: dict[str, Any]

# - [ ] TableElement(SlideElement)
#       type: Literal["table"] = "table"
#       rows: int
#       cols: int
#       cells: list[list[str]]

# - [ ] SlidePage(BaseModel)
#       page_num: int (>= 1)
#       layout: Literal["title_slide", "title_content", "two_column", "blank", "image_full"]
#       background: BackgroundStyle = Field(default_factory=BackgroundStyle)
#       elements: list[TextElement | ImageElement | ShapeElement | ChartElement | TableElement]
#       notes: Optional[str] = None

# - [ ] SlidePresentation(BaseModel)
#       title: str
#       pages: list[SlidePage] (min_items=1)
#       metadata: dict[str, Any] = Field(default_factory=dict)
```

---

### 2. `backend/app/infrastructure/rendering/html_renderer.py` ✅ 完了
**目的**: JSON → HTML変換

```python
# ✅ 実装完了 - HTMLRenderer クラスの実装

class HTMLRenderer:
    # - [ ] render_presentation(presentation: SlidePresentation) -> str
    #       - プレゼンテーション全体のHTML生成
    #       - <html>, <head>, <body> 構造
    #       - CSSスタイルの埋め込み
    #       - JavaScriptナビゲーション

    # - [ ] render_page(page: SlidePage) -> str
    #       - 単一ページのHTML生成
    #       - 背景スタイル適用

    # - [ ] _render_element(element: ...) -> str
    #       - 要素タイプごとに分岐

    # - [ ] _render_text(element: TextElement) -> str
    #       - <div> タグ生成
    #       - インラインスタイル適用

    # - [ ] _render_image(element: ImageElement) -> str
    #       - <img> タグ生成

    # - [ ] _render_shape(element: ShapeElement) -> str
    #       - <div> で図形表現
    #       - circle の場合は border-radius: 50%

    # - [ ] _render_chart(element: ChartElement) -> str
    #       - <canvas> 要素生成
    #       - Chart.js用 data属性

    # - [ ] _render_table(element: TableElement) -> str
    #       - <table> タグ生成

    # - [ ] _render_background(background: BackgroundStyle) -> str
    #       - CSSスタイル文字列生成

    # - [ ] _escape_html(text: str) -> str
    #       - HTMLエスケープ処理

    # - [ ] _get_base_styles() -> str (static)
    #       - 基本CSSスタイルを返す
    #       - レスポンシブ対応
    #       - スライドホバーエフェクト

    # - [ ] _get_base_scripts() -> str (static)
    #       - キーボードナビゲーション (矢印キー)
    #       - Chart.js 初期化コード
```

---

### 3. `backend/app/infrastructure/google_slides/exporter.py` ✅ 完了
**目的**: JSON → Google Slides API

```python
# ✅ 実装完了 - GoogleSlidesExporter クラスに追加

    # - [x] export_presentation(presentation: SlidePresentation) -> dict[str, str]
    #       - 空のプレゼンテーション作成
    #       - 初期スライド削除
    #       - ページごとにバッチリクエスト生成
    #       - batchUpdate 実行
    #       - presentation_url, download_url を返す

    # - [x] _build_slide_requests(page: SlidePage) -> list[dict[str, Any]]
    #       - createSlide リクエスト
    #       - updatePageProperties (背景)
    #       - 要素リクエストを追加

    # - [x] _build_element_requests(element: ..., slide_id: str) -> list[dict]
    #       - TextElement → createShape + insertText + updateTextStyle
    #       - ImageElement → createImage
    #       - ShapeElement → createShape
    #       - TableElement → createTable
    #       - ChartElement → TODO コメント

    # - [x] _map_layout(layout: str) -> str (static)
    #       - レイアウト名マッピング (title_slide → TITLE)

    # - [x] _map_shape_type(shape_type: str) -> str (static)
    #       - 図形タイプマッピング (circle → ELLIPSE)

    # - [x] _hex_to_rgb(hex_color: str) -> dict[str, float] (static)
    #       - #FFFFFF → {"red": 1.0, "green": 1.0, "blue": 1.0}

    # - [x] px → PT 変換ロジック追加 (magnitude 計算時)
```

---

### 4. `backend/app/infrastructure/persistence/slide_repository.py` ✅ 完了 (Phase 2)
**目的**: バージョン取得機能追加

```python
# ✅ 実装完了 - SlideRepository クラスに追加

    # - [x] async def find_version_by_num(
    #           self, slide_id: str, version_num: int
    #       ) -> SlideVersion | None:
    #       - db.slideversion.find_first() で検索
    #       - where={"slideId": slide_id, "versionNum": version_num}
    #       - _to_version() で変換して返す
```

---

### 5. `backend/app/application/slide/usecases.py` ✅ 完了 (Phase 2 & 3)
**目的**: プレビュー・エクスポート機能追加

```python
# ✅ 実装完了 - SlideUseCases クラスに追加

    # - [x] __init__ に依存性追加
    #       html_renderer: Optional[HTMLRenderer] = None
    #       google_slides_exporter: Optional[GoogleSlidesExporter] = None

    # - [x] async def render_preview(
    #           self, slide_id: str, version_num: Optional[int] = None
    #       ) -> str:
    #       - スライド取得 (find_slide_by_id)
    #       - バージョン取得 (find_version_by_num or find_latest_version)
    #       - ページ一覧取得 (find_pages_by_version)
    #       - Page.contents → SlidePresentation に変換
    #       - html_renderer.render_presentation() 呼び出し
    #       - NotFoundException 処理

    # - [x] async def export_to_google_slides(
    #           self, slide_id: str, version_num: Optional[int] = None
    #       ) -> dict[str, str]:
    #       - 上記と同様にスライド・バージョン・ページ取得
    #       - SlidePresentation に変換
    #       - google_slides_exporter.export_presentation() 呼び出し
    #       - 結果を返す
```

---

### 6. `backend/app/presentation/routers/slide_router.py` ✅ 完了 (Phase 2 & 3)
**目的**: エンドポイント追加

```python
# ✅ 実装完了 - インポート追加
# from typing import Optional
# from fastapi import Query
# from fastapi.responses import HTMLResponse

# - [x] GET /{slide_id}/preview エンドポイント追加
#       async def render_slide_preview(
#           slide_id: str,
#           version: Optional[int] = Query(None, description="バージョン番号"),
#           uc: SlideUseCases = Depends(_get_usecases),
#       ):
#       - response_class=HTMLResponse 指定
#       - uc.render_preview(slide_id, version_num=version)
#       - HTMLResponse で返す

# - [x] POST /{slide_id}/export/google-slides エンドポイント追加
#       async def export_to_google_slides(
#           slide_id: str,
#           version: Optional[int] = Query(None),
#           uc: SlideUseCases = Depends(_get_usecases),
#       ):
#       - uc.export_to_google_slides(slide_id, version_num=version)
#       - {"success": True, "data": result} で返す
```

---

### 7. `backend/app/infrastructure/rendering/__init__.py` ✅ 完了
**目的**: パッケージエクスポート

```python
# ✅ 実装完了 - 以下をインポート済み

# from app.infrastructure.rendering.html_renderer import HTMLRenderer
# from app.infrastructure.rendering.schema import (
#     SlidePage,
#     SlidePresentation,
#     TextElement,
#     ImageElement,
#     ShapeElement,
#     ChartElement,
#     TableElement,
# )

# __all__ = [
#     "HTMLRenderer",
#     "SlidePage",
#     "SlidePresentation",
#     "TextElement",
#     "ImageElement",
#     "ShapeElement",
#     "ChartElement",
#     "TableElement",
# ]
```

---

### 8. `frontend/lib/slide-rendering.ts`
**目的**: API型定義とクライアント

```typescript
// TODO: 以下の実装

// - [ ] getSlidePreview(slideId: string, version?: number): Promise<string>
//       - GET /api/v1/slides/{id}/preview?version={version}
//       - response.text() で HTML取得
//       - 認証トークン付与

// - [ ] exportToGoogleSlides(slideId: string, version?: number): Promise<{...}>
//       - POST /api/v1/slides/{id}/export/google-slides
//       - presentation_id, presentation_url, download_url を返す

// - [ ] 型定義
//       - SlidePageContent interface
//       - SlideElement type (Union)
//       - TextElement, ImageElement, ShapeElement, ChartElement, TableElement
//       - BaseElement interface
```

---

### 9. `frontend/components/slide-preview.tsx`
**目的**: 手動プレビューコンポーネント

```typescript
// TODO: SlidePreview コンポーネント実装

// - [ ] Props: slideId, version?

// - [ ] useState で状態管理
//       - html: string
//       - loading: boolean
//       - error: string | null
//       - lastUpdated: Date | null

// - [ ] fetchPreview() 関数
//       - getSlidePreview() API呼び出し
//       - エラーハンドリング
//       - lastUpdated 更新

// - [ ] useEffect でプレビュー取得（初回のみ）
//       - マウント時に1回だけ fetchPreview() を呼び出し

// - [ ] handleRefresh() 手動更新ボタン
//       - ユーザーがボタンクリックで fetchPreview() を再実行

// - [ ] UI実装
//       - ローディング表示 (Loader2)
//       - エラー表示 (Alert)
//       - iframe で srcDoc={html}
//       - sandbox="allow-scripts allow-same-origin"
//       - 最終更新時刻表示
//       - 手動更新ボタン（RefreshCwアイコン）
```

---

### 10. `frontend/components/export-to-google-slides-dialog.tsx`
**目的**: エクスポートダイアログ

```typescript
// TODO: ExportToGoogleSlidesDialog コンポーネント実装

// - [ ] Props: slideId, version?

// - [ ] useState で状態管理
//       - open: boolean
//       - exporting: boolean
//       - error: string | null
//       - result: { presentation_url, download_url } | null

// - [ ] handleExport() 関数
//       - exportToGoogleSlides() API呼び出し
//       - loading 管理
//       - エラーハンドリング

// - [ ] UI実装
//       - Dialog コンポーネント (shadcn/ui)
//       - エクスポート開始ボタン
//       - ローディング (Loader2 + テキスト)
//       - 成功時:
//         - 成功アラート
//         - Google Slidesリンク (ExternalLink アイコン)
//         - PPTX ダウンロードリンク (Download アイコン)
//       - エラー表示 (Alert destructive)
//       - 閉じるボタン
```

---

## 🎯 実装順序（推奨）

### Phase 1: バックエンド基盤 (1-4) ✅ 完了
1. ✅ `schema.py`
2. ✅ `html_renderer.py`
3. ✅ `slide_repository.py`
4. ✅ `rendering/__init__.py`

### Phase 2: バックエンド機能 (5-6) ✅ 完了
5. ✅ `usecases.py`
6. ✅ `slide_router.py`
7. ✅ **テスト**: curl でプレビュー取得確認

### Phase 3: Google Slides (7) ✅ 完了
8. ✅ `exporter.py`
9. ⏭️ **テスト**: エクスポート → Google Slidesで開く（手動テスト推奨）

### Phase 4: フロントエンド (8-10)
10. `slide-rendering.ts`
11. `slide-preview.tsx`
12. `export-to-google-slides-dialog.tsx`
13. **統合テスト**: E2E確認

---

## 🧪 テストポイント

- [x] schema.py: Pydantic バリデーション（31テスト完了）
- [x] html_renderer.py: 各要素タイプのHTML生成（21テスト完了）
- [ ] exporter.py: Google Slides API リクエスト形式（手動テスト推奨）
- [x] GET /preview: 200レスポンスとHTML取得
- [ ] POST /export/google-slides: 成功レスポンス（手動テスト推奨）
- [ ] フロントエンド: 手動更新ボタン動作
- [ ] フロントエンド: エクスポート → Slidesで開ける

---

## 📚 参考資料

- JSON例: [slide_page.json](backend/app/infrastructure/rendering/slide_page.json)
- Google API例: [slide_page_example_google_api.json](backend/app/infrastructure/rendering/slide_page_example_google_api.json)
- Google Slides API: https://developers.google.com/slides/api/reference/rest
- Chart.js: https://www.chartjs.org/docs/
- shadcn/ui: https://ui.shadcn.com/
