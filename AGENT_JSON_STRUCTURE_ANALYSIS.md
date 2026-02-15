# エージェントJSON構造 vs. 設計Schema 差異分析レポート

## ⚠️ 重大な構造不一致を検出

**pr-11のマルチエージェント実装と、設計済みSlidePresentation schemaの間に重大な差異があります。**

---

## 📊 JSON構造の比較

### 1. **マルチエージェント出力構造** (multi_agent_slide_generator.py)

```json
{
  "objectId": "slide-mvp-001",
  "pageType": "SLIDE",
  "pageElements": [
    {
      "objectId": "slide-mvp-001-elem-1",
      "transform": {
        "scaleX": 1,
        "scaleY": 1,
        "translateX": 50,
        "translateY": 40
      },
      "size": {
        "width": {"magnitude": 860, "unit": "PT"},
        "height": {"magnitude": 80, "unit": "PT"}
      },
      "shape": {
        "shapeType": "TEXT_BOX",
        "text": {
          "textElements": [
            {
              "startIndex": 0,
              "endIndex": 10,
              "textRun": {
                "content": "タイトル",
                "style": {
                  "fontSize": {"magnitude": 48, "unit": "PT"},
                  "bold": true,
                  "foregroundColor": {...},
                  "fontFamily": "Arial"
                }
              }
            }
          ]
        }
      }
    },
    {
      "objectId": "slide-mvp-001-elem-2",
      "transform": {...},
      "size": {...},
      "shape": {
        "shapeType": "TEXT_BOX",
        "text": {
          "textElements": [
            {
              "startIndex": 0,
              "endIndex": 15,
              "textRun": {...}
            },
            {
              "startIndex": 14,
              "endIndex": 15,
              "paragraphMarker": {
                "style": {
                  "bullet": {"listId": "list-id-1", "nestingLevel": 0}
                }
              }
            }
          ]
        }
      }
    },
    {
      "objectId": "slide-mvp-001-elem-3",
      "transform": {...},
      "size": {...},
      "image": {
        "contentUrl": "https://placehold.co/600x400/png?text=..."
      }
    }
  ]
}
```

**特徴**:
- ✅ **Google Slides API生フォーマット**
- ✅ PT単位の座標系（transform.translateX/Y）
- ✅ textElements配列に細かいスタイル情報
- ✅ paragraphMarkerで箇条書き表現
- ❌ **1ページ分のみ**（プレゼンテーション全体の構造なし）

---

### 2. **設計済みSlidePresentation Schema** (rendering/schema.py)

```python
# Pydanticモデル定義
class SlidePresentation(BaseModel):
    title: str
    pages: list[SlidePage]
    metadata: dict[str, Any] = Field(default_factory=dict)

class SlidePage(BaseModel):
    page_num: int = Field(ge=1)
    layout: Literal["title_slide", "title_content", "two_column", "blank", "image_full"]
    background: BackgroundStyle = Field(default_factory=BackgroundStyle)
    elements: list[Union[TextElement, ImageElement, ShapeElement, ChartElement, TableElement]]
    notes: Optional[str] = None

class TextElement(SlideElement):
    type: Literal["text"] = "text"
    content: str
    style: TextStyle = Field(default_factory=TextStyle)
    position: ElementPosition
    placeholder: Optional[str] = None

class ElementPosition(BaseModel):
    x: float
    y: float
    width: float
    height: float

class TextStyle(BaseModel):
    font_family: str = "Arial"
    font_size: float = 16
    font_weight: Literal["normal", "bold"] = "normal"
    color: str = "#000000"
    align: Literal["left", "center", "right"] = "left"
    line_height: float = 1.5
```

**JSON例** (期待される形式):
```json
{
  "title": "プレゼンテーション全体のタイトル",
  "pages": [
    {
      "page_num": 1,
      "layout": "title_slide",
      "background": {
        "color": "#FFFFFF"
      },
      "elements": [
        {
          "element_id": "elem-1",
          "type": "text",
          "content": "タイトルテキスト",
          "position": {
            "x": 50,
            "y": 100,
            "width": 500,
            "height": 80
          },
          "style": {
            "font_family": "Arial",
            "font_size": 48,
            "font_weight": "bold",
            "color": "#000000",
            "align": "center"
          }
        },
        {
          "element_id": "elem-2",
          "type": "image",
          "source_url": "https://example.com/image.png",
          "position": {...}
        }
      ]
    },
    {
      "page_num": 2,
      "layout": "title_content",
      "elements": [...]
    }
  ],
  "metadata": {
    "author": "AI Agent",
    "version": "1.0"
  }
}
```

**特徴**:
- ✅ **プレゼンテーション全体を表現**（複数ページ）
- ✅ Pydanticモデルによる型安全性
- ✅ シンプルな座標系（x, y, width, height）
- ✅ レイアウトタイプ明示（title_slide, title_content等）
- ✅ HTMLRenderer、GoogleSlidesExporterで処理可能

---

## 🔴 重大な差異

### 1. **構造の不一致**

| 項目 | エージェント出力 | 設計Schema |
|------|------------------|------------|
| **形式** | Google Slides API生フォーマット | Pydanticモデル |
| **スコープ** | 1ページのみ | プレゼンテーション全体 |
| **座標系** | PT単位、transform | ピクセル単位、position |
| **テキスト表現** | textElements配列（細かい） | content文字列（シンプル） |
| **スタイル** | fontSize.magnitude.unit | font_size: float |
| **箇条書き** | paragraphMarker | content内で表現 |
| **画像** | image.contentUrl | ImageElement.source_url |
| **レイアウト** | 暗黙的（レイアウト名埋め込み） | layout: Literal[...] |
| **型安全性** | dict[str, Any] (型なし) | Pydantic BaseModel |

### 2. **APIレスポンス形式の問題**

**現在の実装** (outline_router.py):
```python
POST /api/v1/outlines/generate-slide
→ SlideOutputResponseDTO(outline_id, slide: Any)
→ Google Slides API生フォーマットを返す
```

**問題点**:
- ❌ `slide: Any`で型安全性なし
- ❌ フロントエンドが Google Slides API の複雑な構造を理解する必要
- ❌ HTMLRenderer, GoogleSlidesExporterと互換性なし

### 3. **保存形式の問題**

**現在の実装**:
```python
# multi_agent_slide_generator.py が生成
slide_json = {...}  # Google Slides API生フォーマット

# Page.contents に直接保存
await repo.create_page(
    slide_version_id=version_id,
    page_num=1,
    contents=slide_json  # ← Google Slides API生フォーマット
)
```

**問題点**:
- ❌ `render_preview()`が期待する形式（SlidePresentation schema）と不一致
- ❌ `export_to_google_slides()`が処理できない
- ❌ ページ間の統一性がない（各ページが独立したGoogle Slides構造）

---

## 💥 pr-11による機能喪失の問題

### **削除される機能** (pr-11のdiff確認結果)

#### ❌ `backend/app/application/slide/usecases.py`から削除:
```python
# 削除されるインポート
from app.infrastructure.rendering import HTMLRenderer, SlidePresentation
from app.infrastructure.google_slides.exporter import GoogleSlidesExporter

# 削除される関数
def _template_elements_to_html(elements: list[dict[str, Any]]) -> str
def _template_contents_to_pages(contents: Any) -> list[tuple[int, dict[str, Any]]]

# 削除されるメソッド
async def render_preview(self, slide_id: str, version_num: int) -> str
async def export_to_google_slides(self, slide_id: str, version_num: int) -> dict[str, str]
```

#### ❌ `backend/app/infrastructure/persistence/slide_repository.py`から削除:
```python
async def find_version_by_num(self, slide_id: str, version_num: int) -> SlideVersion | None
async def find_page_by_id(self, page_id: str) -> Page | None
```

#### ❌ 影響を受けるエンドポイント:
- `GET /api/v1/slides/{slide_id}/preview` → **動作不能**
- `POST /api/v1/slides/{slide_id}/export/google-slides` → **動作不能**

### **pr-9で実装済みの資産**:
- ✅ `backend/app/infrastructure/rendering/schema.py`: 12クラス、31テスト
- ✅ `backend/app/infrastructure/rendering/html_renderer.py`: HTMLRenderer、21テスト
- ✅ `backend/app/infrastructure/google_slides/exporter.py`: GoogleSlidesExporter（345行）、15テスト
- ✅ 合計67テスト全てパス済み

**これらが全て無効化される！**

---

## 🎯 推奨される統合アプローチ

### **Option A: エージェント出力を変換 (推奨)**

```python
# multi_agent_slide_generator.py の最終出力を変換
class MultiAgentSlideGenerator:
    async def generate_one_slide_as_schema(
        self, **kwargs
    ) -> SlidePage:
        """エージェント出力 → SlidePresentation schema変換"""
        raw_slide = await self.generate_one_slide(**kwargs)
        return self._convert_to_schema(raw_slide)
    
    def _convert_to_schema(self, raw_slide: dict) -> SlidePage:
        """Google Slides API生フォーマット → SlidePage変換"""
        elements = []
        for elem in raw_slide.get("pageElements", []):
            if "shape" in elem:
                # TEXT_BOX → TextElement変換
                text_content = self._extract_text_from_shape(elem["shape"])
                position = self._extract_position(elem)
                style = self._extract_text_style(elem["shape"])
                elements.append(TextElement(
                    element_id=elem["objectId"],
                    content=text_content,
                    position=position,
                    style=style
                ))
            elif "image" in elem:
                # image → ImageElement変換
                position = self._extract_position(elem)
                elements.append(ImageElement(
                    element_id=elem["objectId"],
                    source_url=elem["image"]["contentUrl"],
                    position=position
                ))
        
        return SlidePage(
            page_num=kwargs.get("page_num", 1),
            layout=self._infer_layout(raw_slide),
            elements=elements
        )
```

**メリット**:
- ✅ 既存のHTMLRenderer、GoogleSlidesExporterが使える
- ✅ 型安全性が保たれる
- ✅ pr-9の実装資産を活用
- ✅ フロントエンドがシンプルな構造を受け取れる

**実装工数**: 半日〜1日

---

### **Option B: 二重サポート (互換性重視)**

```python
class SlideUseCases:
    async def save_agent_output(
        self, 
        slide_id: str, 
        version_num: int,
        agent_slides: list[dict]  # Google Slides API生フォーマット
    ) -> None:
        """エージェント出力を保存（変換あり）"""
        # 変換してから保存
        presentation = self._convert_agent_output_to_schema(agent_slides)
        
        # SlidePresentation schemaとして保存
        version = await self.repo.find_version_by_num(slide_id, version_num)
        for page_data in presentation.pages:
            await self.repo.create_page(
                slide_version_id=version.id,
                page_num=page_data.page_num,
                contents=page_data.model_dump()  # Pydantic → dict
            )
    
    async def render_preview(self, slide_id: str, version_num: int) -> str:
        """HTMLプレビュー生成（既存機能維持）"""
        # ページ取得 → SlidePresentation復元 → HTMLRenderer
        ...
```

**メリット**:
- ✅ pr-9の機能を完全に維持
- ✅ エージェント出力も扱える
- ✅ テストが全て通る

**実装工数**: 1〜2日

---

### **Option C: 完全置き換え (非推奨)**

pr-9の実装を全て削除し、Google Slides API生フォーマットのみサポート。

**デメリット**:
- ❌ HTMLプレビュー機能喪失
- ❌ Google Slidesエクスポート機能喪失
- ❌ 67個のテストが無駄になる
- ❌ フロントエンドが複雑な構造を扱う必要

**推奨しません。**

---

## 🚨 即座に対処すべき競合

### **現在の競合ファイル** (git status):
```
both modified:   backend/app/application/slide/usecases.py
both modified:   backend/app/infrastructure/persistence/slide_repository.py
both modified:   backend/app/presentation/routers/slide_router.py
both modified:   frontend/app/slides/[id]/page.tsx
```

### **推奨解決策**:

1. **usecases.py**: 
   - HEADの内容を維持（HTMLRenderer, GoogleSlidesExporter込み）
   - pr-11の削除を拒否
   
2. **slide_repository.py**:
   - `find_version_by_num`, `find_page_by_id`を維持
   - pr-11の削除を拒否

3. **slide_router.py**:
   - `GET /{slide_id}/preview`を維持
   - `POST /{slide_id}/export/google-slides`を維持

4. **新規追加**:
   - エージェント出力 → SlidePresentation変換ロジック

---

## 📋 アクションアイテム

### **緊急（今すぐ）**:
- [ ] pr-11マージを一旦中止
- [ ] 構造変換ロジックの設計確定
- [ ] テスト戦略の策定

### **短期（1-2日）**:
- [ ] `_convert_to_schema()`実装
- [ ] `generate_one_slide_as_schema()`追加
- [ ] 変換ロジックのテスト追加（10-15テスト）
- [ ] pr-9とpr-11の統合マージ

### **中長期**:
- [ ] エージェント出力の直接保存パス廃止
- [ ] SlidePresentation schemaを唯一の保存形式に統一
- [ ] フロントエンドAPI型定義の整理

---

## 🎓 結論

**マルチエージェントが出力するJSON構造と、設計済みSlidePresentation schemaの間に重大な不一致があります。**

**推奨アクション**:
1. ✅ **Option Aを採用**: エージェント出力を変換してSlidePresentation schemaに統一
2. ✅ **pr-9の機能を維持**: HTMLRenderer, GoogleSlidesExporterは資産
3. ✅ **型安全性を優先**: Pydanticモデルを活用
4. ❌ **pr-11の機能削除を拒否**: `render_preview`, `export_to_google_slides`は必須

**実装優先度**: 🔴 **最優先** - 構造変換なしではシステム全体が破綻します。
