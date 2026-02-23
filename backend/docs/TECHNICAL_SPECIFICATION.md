# Slide Turbo - 技術仕様書

## 目次
1. [システムアーキテクチャ](#システムアーキテクチャ)
2. [マルチエージェントシステム](#マルチエージェントシステム)
3. [Google Slides API形式](#google-slides-api形式)
4. [データベーススキーマ](#データベーススキーマ)
5. [コンポーネント設計](#コンポーネント設計)
6. [セキュリティ](#セキュリティ)
7. [パフォーマンス](#パフォーマンス)
8. [テスト戦略](#テスト戦略)

---

## システムアーキテクチャ

### レイヤードアーキテクチャ

```
┌─────────────────────────────────────────────────┐
│          Presentation Layer (API)               │
│  - FastAPI routers                              │
│  - HTTP request/response handling               │
│  - Authentication middleware                    │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│          Application Layer (Use Cases)          │
│  - Business logic orchestration                 │
│  - Multi-agent coordination                     │
│  - Transaction management                       │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│          Domain Layer (Entities)                │
│  - Slide, Template, User entities               │
│  - Business rules                               │
│  - Domain events                                │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│       Infrastructure Layer                      │
│  - Prisma repositories                          │
│  - Google Slides API client                     │
│  - Gemini AI client                             │
│  - HTML renderer                                │
└─────────────────────────────────────────────────┘
```

### ディレクトリ構造

```
backend/app/
├── main.py                      # FastAPI application entry point
├── presentation/                # 表現層
│   ├── api.py                   # APIルーター集約
│   └── routers/                 # HTTPエンドポイント
│       ├── user_router.py       # ユーザー認証
│       ├── template_router.py   # テンプレート管理
│       ├── slide_router.py      # スライド管理
│       └── outline_router.py    # アウトライン・生成
├── application/                 # アプリケーション層
│   ├── user/                    # ユーザーユースケース
│   │   └── usecases.py
│   ├── template/                # テンプレートユースケース
│   │   └── usecases.py
│   ├── slide/                   # スライドユースケース
│   │   └── usecases.py
│   └── outline/                 # アウトラインユースケース
│       └── usecases.py
├── domain/                      # ドメイン層
│   ├── user/                    # ユーザーエンティティ
│   │   ├── entity.py
│   │   └── repository.py
│   ├── template/                # テンプレートエンティティ
│   │   ├── entity.py
│   │   └── repository.py
│   ├── slide/                   # スライドエンティティ
│   │   ├── entity.py
│   │   └── repository.py
│   └── outline/                 # アウトラインエンティティ
│       ├── entity.py
│       └── repository.py
├── infrastructure/              # インフラストラクチャ層
│   ├── persistence/             # データ永続化
│   │   ├── prisma_user_repo.py
│   │   ├── prisma_template_repo.py
│   │   ├── prisma_slide_repo.py
│   │   └── prisma_outline_repo.py
│   ├── ai/                      # AI統合
│   │   ├── gemini_client.py
│   │   └── multi_agent/         # マルチエージェント
│   │       ├── agents.py        # 5つのエージェント定義
│   │       ├── coordinator.py   # エージェント協調
│   │       └── prompts.py       # プロンプトテンプレート
│   ├── google_slides/           # Google Slides統合
│   │   ├── client.py            # Google API client
│   │   ├── parser.py            # JSON解析
│   │   └── exporter.py          # エクスポート
│   └── rendering/               # HTMLレンダリング
│       └── html_renderer.py     # JSON to HTML変換
├── core/                        # コア機能
│   ├── config.py                # 設定管理
│   ├── db.py                    # データベース接続
│   ├── auth.py                  # 認証
│   └── security.py              # セキュリティユーティリティ
└── shared/                      # 共有機能
    └── exceptions.py            # カスタム例外
```

---

## マルチエージェントシステム

### エージェント構成

システムは5つの専門エージェントで構成されます：

```
Outline Input
     ↓
┌────────────────────┐
│  PlannerAgent      │  役割: 構造化プラン作成
│  - 論理構造        │  入力: ユーザーのアウトライン
│  - フロー設計      │  出力: 詳細な構造化プラン
└─────────┬──────────┘
          ↓
┌────────────────────┐
│ CopywriterAgent    │  役割: コピー洗練
│  - 表現改善        │  入力: PlannerAgentの出力
│  - トーン調整      │  出力: 洗練されたコピー
└─────────┬──────────┘
          ↓
┌────────────────────┐
│  VisualAgent       │  役割: ビジュアル要素提案
│  - 画像URL生成     │  入力: CopywriterAgentの出力
│  - アイコン選択    │  出力: 画像URL、ビジュアル指示
└─────────┬──────────┘
          ↓
┌────────────────────┐
│ LayoutPlannerAgent │  役割: レイアウト選択
│  - テンプレート選択│  入力: VisualAgentの出力
│  - スタイル決定    │  出力: 選択されたレイアウトID
└─────────┬──────────┘
          ↓
┌────────────────────┐
│  LayoutAgent       │  役割: 最終JSON生成
│  - JSON生成        │  入力: LayoutPlannerAgentの出力
│  - 配置計算        │  出力: Google Slides API形式JSON
└─────────┬──────────┘
          ↓
   Slide JSON Output
```

### エージェント詳細

#### 1. PlannerAgent
**責任**: 論理構造とフローの設計

**入力例**:
```json
{
  "outline": {
    "title": "新製品発表",
    "sections": [
      {"heading": "背景", "content": "市場の課題..."}
    ]
  },
  "page_number": 1
}
```

**出力例**:
```json
{
  "page_type": "title_slide",
  "main_message": "新製品で市場の課題を解決",
  "key_points": ["課題1", "課題2"],
  "structure": {
    "title": "背景",
    "subtitle": "市場の課題",
    "body": "..."
  }
}
```

#### 2. CopywriterAgent
**責任**: コピーの洗練とトーン調整

**入力**: PlannerAgentの出力

**出力例**:
```json
{
  "refined_copy": {
    "title": "市場を変える新しいソリューション",
    "subtitle": "年率15%成長する市場の3つの課題",
    "body": "業界には3つの重要な課題が存在します..."
  },
  "tone": "professional",
  "style": "persuasive"
}
```

#### 3. VisualAgent
**責任**: ビジュアル要素の提案

**入力**: CopywriterAgentの出力

**出力例**:
```json
{
  "images": [
    {
      "type": "hero",
      "url": "https://images.unsplash.com/photo-...",
      "position": "background"
    }
  ],
  "icons": [
    {"type": "chart", "color": "#2563eb"}
  ],
  "color_scheme": {
    "primary": "#2563eb",
    "secondary": "#64748b"
  }
}
```

#### 4. LayoutPlannerAgent
**責任**: レイアウトテンプレートの選択

**入力**: VisualAgentの出力

**出力例**:
```json
{
  "layout_id": "hero_with_text",
  "layout_style": "modern",
  "grid": {
    "columns": 2,
    "rows": 3
  },
  "spacing": "comfortable"
}
```

#### 5. LayoutAgent
**責任**: 最終的なGoogle Slides API形式JSONの生成

**入力**: LayoutPlannerAgentの出力 + 全エージェントの累積データ

**出力**: Google Slides API形式の完全なJSON（後述）

### エージェント協調フロー

```python
class MultiAgentCoordinator:
    """複数のエージェントを協調させるコーディネーター"""
    
    async def generate_one_slide(
        self, 
        outline: dict, 
        page_number: int
    ) -> dict:
        # 1. プラン作成
        plan = await self.planner_agent.run(outline, page_number)
        
        # 2. コピー洗練
        refined = await self.copywriter_agent.run(plan)
        
        # 3. ビジュアル提案
        visual = await self.visual_agent.run(refined)
        
        # 4. レイアウト選択
        layout_plan = await self.layout_planner_agent.run(visual)
        
        # 5. 最終JSON生成
        slide_json = await self.layout_agent.run(
            plan=plan,
            refined=refined,
            visual=visual,
            layout_plan=layout_plan
        )
        
        return slide_json
```

### プロンプトエンジニアリング

各エージェントは専門化されたプロンプトを使用：

```python
PLANNER_PROMPT = """
あなたはプレゼンテーションの構造設計の専門家です。
与えられたアウトラインから、論理的で説得力のある構造を設計してください。

入力:
{outline}

ページ番号: {page_number}

以下の点を考慮してください:
1. ページの役割（タイトル、説明、まとめなど）
2. 情報の優先順位
3. 論理的なフロー

JSON形式で出力してください。
"""

```

---

## Google Slides API形式

### 標準JSON構造

システム内部では、全てのスライドデータをGoogle Slides API形式で扱います：

```json
{
  "objectId": "slide_page_1",
  "pageProperties": {
    "pageBackgroundFill": {
      "solidFill": {
        "color": {"rgbColor": {"red": 1, "green": 1, "blue": 1}}
      }
    }
  },
  "pageElements": [
    {
      "objectId": "element_title_1",
      "transform": {
        "scaleX": 1,
        "scaleY": 1,
        "translateX": 50,
        "translateY": 50,
        "unit": "PT"
      },
      "size": {
        "width": {"magnitude": 600, "unit": "PT"},
        "height": {"magnitude": 100, "unit": "PT"}
      },
      "shape": {
        "shapeType": "TEXT_BOX",
        "text": {
          "textElements": [
            {
              "endIndex": 10,
              "textRun": {
                "content": "タイトル",
                "style": {
                  "bold": true,
                  "fontSize": {"magnitude": 36, "unit": "PT"},
                  "foregroundColor": {
                    "opaqueColor": {
                      "rgbColor": {"red": 0, "green": 0, "blue": 0}
                    }
                  }
                }
              }
            }
          ]
        }
      }
    },
    {
      "objectId": "element_image_1",
      "transform": {
        "translateX": 100,
        "translateY": 200
      },
      "size": {
        "width": {"magnitude": 400, "unit": "PT"},
        "height": {"magnitude": 300, "unit": "PT"}
      },
      "image": {
        "contentUrl": "https://images.unsplash.com/photo-...",
        "sourceUrl": "https://images.unsplash.com/photo-..."
      }
    }
  ]
}
```

### 座標系

- **単位**: PT (ポイント、1pt = 1/72 inch)
- **原点**: 左上 (0, 0)
- **X軸**: 左から右（正の方向）
- **Y軸**: 上から下（正の方向）

```
(0,0) ──────────────────────→ X
  │
  │   ┌──────────────┐
  │   │  Element     │
  │   │  (x, y)      │
  │   └──────────────┘
  │
  ↓
  Y
```

### 標準スライドサイズ

- **幅**: 720 PT (10 inches)
- **高さ**: 540 PT (7.5 inches)
- **アスペクト比**: 4:3

---

## データベーススキーマ

### Prismaスキーマ

```prisma
model User {
  id         String   @id @default(cuid())
  email      String   @unique
  name       String?
  picture    String?
  createdAt  DateTime @default(now())
  
  templates  Template[]
  slides     Slide[]
}

model Template {
  id           String   @id @default(cuid())
  title        String
  contents     Json     // Google Slides API形式JSON
  thumbnailUrl String?
  userId       String
  createdAt    DateTime @default(now())
  
  user         User     @relation(fields: [userId], references: [id])
  slides       Slide[]
}

model Slide {
  id         String   @id @default(cuid())
  title      String
  templateId String
  userId     String
  createdAt  DateTime @default(now())
  
  template   Template       @relation(fields: [templateId], references: [id])
  user       User           @relation(fields: [userId], references: [id])
  versions   SlideVersion[]
}

model SlideVersion {
  id            String   @id @default(cuid())
  slideId       String
  versionNumber Int
  slotValues    Json     // {slot_name: value}
  createdAt     DateTime @default(now())
  
  slide         Slide    @relation(fields: [slideId], references: [id])
  pages         Page[]
  outlines      Outline[]
  
  @@unique([slideId, versionNumber])
}

model Page {
  id        String   @id @default(cuid())
  versionId String
  pageNumber Int
  pageData  Json     // Google Slides API形式JSON
  createdAt DateTime @default(now())
  
  version   SlideVersion @relation(fields: [versionId], references: [id])
  
  @@unique([versionId, pageNumber])
}

model Outline {
  id        String   @id @default(cuid())
  versionId String
  outline   Json     // {title, sections: [{heading, content}]}
  createdAt DateTime @default(now())
  
  version   SlideVersion @relation(fields: [versionId], references: [id])
}
```

### インデックス戦略

```sql
-- 頻繁にアクセスされるカラムにインデックス
CREATE INDEX idx_slide_user_id ON Slide(userId);
CREATE INDEX idx_template_user_id ON Template(userId);
CREATE INDEX idx_slideversion_slide_id ON SlideVersion(slideId);
CREATE INDEX idx_page_version_id ON Page(versionId);

-- 複合インデックス（バージョン番号による検索最適化）
CREATE INDEX idx_slideversion_slide_version ON SlideVersion(slideId, versionNumber DESC);
```

---

## コンポーネント設計

### HTMLRenderer

**責任**: Google Slides API形式JSONをHTMLに変換

```python
class HTMLRenderer:
    """Google Slides API形式JSONをHTMLに変換"""
    
    def render_presentation(self, slides: List[dict]) -> str:
        """プレゼンテーション全体をHTMLに変換"""
        html_pages = []
        for i, slide in enumerate(slides):
            html = self._render_slide(slide, i)
            html_pages.append(html)
        
        return self._wrap_in_html_document(html_pages)
    
    def _render_slide(self, slide: dict, page_num: int) -> str:
        """単一スライドをHTMLに変換"""
        elements_html = []
        
        for element in slide.get("pageElements", []):
            html = self._render_element(element)
            elements_html.append(html)
        
        return f"""
        <div class="slide" id="page-{page_num}" 
             style="width: 720pt; height: 540pt; position: relative;">
            {''.join(elements_html)}
        </div>
        """
    
    def _render_element(self, element: dict) -> str:
        """単一要素をHTMLに変換"""
        if "shape" in element:
            return self._render_shape(element)
        elif "image" in element:
            return self._render_image(element)
        # ... その他の要素タイプ
    
    def _render_shape(self, element: dict) -> str:
        """シェイプ（テキストボックスなど）をHTMLに変換"""
        transform = element.get("transform", {})
        size = element.get("size", {})
        shape = element.get("shape", {})
        
        # テキスト抽出
        text_content = ""
        text_data = shape.get("text", {})
        for text_elem in text_data.get("textElements", []):
            if "textRun" in text_elem:
                text_content += text_elem["textRun"]["content"]
        
        # スタイル適用
        style = self._build_style(transform, size, shape)
        
        return f'<div style="{style}">{text_content}</div>'
    
    def _build_style(self, transform: dict, size: dict, shape: dict) -> str:
        """CSS styleを構築"""
        styles = []
        
        # 位置
        x = transform.get("translateX", 0)
        y = transform.get("translateY", 0)
        styles.append(f"position: absolute")
        styles.append(f"left: {x}pt")
        styles.append(f"top: {y}pt")
        
        # サイズ
        width = size.get("width", {}).get("magnitude", 100)
        height = size.get("height", {}).get("magnitude", 100)
        styles.append(f"width: {width}pt")
        styles.append(f"height: {height}pt")
        
        # テキストスタイル
        text_data = shape.get("text", {})
        if text_data:
            text_elem = text_data.get("textElements", [{}])[0]
            if "textRun" in text_elem:
                style_data = text_elem["textRun"].get("style", {})
                
                if style_data.get("bold"):
                    styles.append("font-weight: bold")
                
                font_size = style_data.get("fontSize", {}).get("magnitude")
                if font_size:
                    styles.append(f"font-size: {font_size}pt")
        
        return "; ".join(styles)
```

### GoogleSlidesExporter

**責任**: JSONをGoogle Slidesプレゼンテーションとしてエクスポート

```python
class GoogleSlidesExporter:
    """Google Slides APIを使ってプレゼンテーションを作成"""
    
    def __init__(self, credentials):
        self.service = build('slides', 'v1', credentials=credentials)
    
    async def create_presentation(
        self, 
        title: str, 
        slides: List[dict],
        owner_email: str = None
    ) -> dict:
        """プレゼンテーションを作成"""
        
        # 1. 空のプレゼンテーション作成
        presentation = self.service.presentations().create(
            body={"title": title}
        ).execute()
        
        presentation_id = presentation["presentationId"]
        
        # 2. 各スライドを追加
        for i, slide_data in enumerate(slides):
            await self._add_slide(presentation_id, slide_data, i)
        
        # 3. 所有者設定（オプション）
        if owner_email:
            self._transfer_ownership(presentation_id, owner_email)
        
        return {
            "presentationId": presentation_id,
            "presentationUrl": f"https://docs.google.com/presentation/d/{presentation_id}",
            "downloadUrl": f"https://docs.google.com/presentation/d/{presentation_id}/export/pptx"
        }
    
    async def _add_slide(
        self, 
        presentation_id: str, 
        slide_data: dict, 
        position: int
    ):
        """スライドを追加"""
        
        # Google Slides API batchUpdate形式に変換
        requests = []
        
        # スライド作成リクエスト
        slide_id = slide_data.get("objectId", f"slide_{position}")
        requests.append({
            "createSlide": {
                "objectId": slide_id,
                "insertionIndex": position
            }
        })
        
        # 要素追加リクエスト
        for element in slide_data.get("pageElements", []):
            request = self._create_element_request(slide_id, element)
            if request:
                requests.append(request)
        
        # バッチ実行
        body = {"requests": requests}
        self.service.presentations().batchUpdate(
            presentationId=presentation_id,
            body=body
        ).execute()
```

---

## セキュリティ

### 認証フロー

1. **Google OAuth 2.0**による認証
2. **JWT**トークンによるセッション管理
3. **HTTPOnly Cookie**でトークン保存（オプション）

```python
# JWT生成
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

# JWT検証
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await user_repository.find_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user
```

### CORS設定

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### データ保護

- **暗号化**: データベースパスワード、API キーは環境変数で管理
- **スコープ制限**: Google API アクセスは最小限のスコープに制限
- **入力検証**: Pydantic モデルによる厳格な検証

---

## パフォーマンス

### キャッシング戦略

```python
from functools import lru_cache
from cachetools import TTLCache

# テンプレートキャッシュ（1時間）
template_cache = TTLCache(maxsize=100, ttl=3600)

@lru_cache(maxsize=128)
def get_google_slides_client(credentials_path: str):
    """Google Slides クライアントをキャッシュ"""
    return build('slides', 'v1', credentials=load_credentials(credentials_path))
```

### 非同期処理

```python
import asyncio

async def generate_multiple_slides(outlines: List[dict]) -> List[dict]:
    """複数スライドを並列生成"""
    tasks = [
        coordinator.generate_one_slide(outline, i)
        for i, outline in enumerate(outlines)
    ]
    return await asyncio.gather(*tasks)
```

### データベース最適化

```python
# N+1問題の回避（Prisma includeを使用）
slide = await prisma.slide.find_unique(
    where={"id": slide_id},
    include={
        "versions": {
            "include": {
                "pages": True
            },
            "order_by": {"versionNumber": "desc"},
            "take": 1
        }
    }
)
```

---

## テスト戦略

### ユニットテスト

```python
import pytest
from app.infrastructure.rendering.html_renderer import HTMLRenderer

def test_render_text_element():
    """テキスト要素のレンダリングテスト"""
    renderer = HTMLRenderer()
    
    element = {
        "objectId": "text_1",
        "transform": {"translateX": 50, "translateY": 100},
        "size": {
            "width": {"magnitude": 300, "unit": "PT"},
            "height": {"magnitude": 100, "unit": "PT"}
        },
        "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
                "textElements": [
                    {"textRun": {"content": "Hello World"}}
                ]
            }
        }
    }
    
    html = renderer._render_element(element)
    
    assert "Hello World" in html
    assert "left: 50pt" in html
    assert "top: 100pt" in html
```

### 統合テスト

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_slide():
    """スライド作成APIの統合テスト"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/slides",
            json={
                "template_id": "test_template",
                "title": "Test Slide"
            },
            headers={"Authorization": "Bearer test_token"}
        )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Slide"
```

### E2Eテスト

```python
from playwright.async_api import async_playwright

async def test_full_slide_generation_flow():
    """フルフローE2Eテスト"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # 1. ログイン
        await page.goto("http://localhost:3000/login")
        await page.click("text=Googleでログイン")
        # ... OAuth flow
        
        # 2. アウトライン作成
        await page.goto("http://localhost:3000/outline/new")
        await page.fill("#title", "Test Presentation")
        await page.click("button:text('生成')")
        
        # 3. プレビュー確認
        await page.wait_for_selector(".slide-preview")
        assert await page.locator(".slide-preview").count() > 0
        
        await browser.close()
```

---

## デプロイメント

### Docker構成

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: slide_turbo
      POSTGRES_PASSWORD: slide_turbo
      POSTGRES_DB: slide_turbo
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://slide_turbo:slide_turbo@db:5432/slide_turbo
      GEMINI_API_KEY: ${GEMINI_API_KEY}
    depends_on:
      - db
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://backend:8000

volumes:
  postgres_data:
```

### CI/CD（GitHub Actions例）

```yaml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.14'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          cd backend
          pytest
      
      - name: Run linting
        run: |
          cd backend
          flake8 app/
```

---

## ログとモニタリング

### ログ設定

```python
import logging
from logging.handlers import RotatingFileHandler

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('app.log', maxBytes=10485760, backupCount=5),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### メトリクス収集（Prometheus例）

```python
from prometheus_client import Counter, Histogram

# メトリクス定義
slide_generation_counter = Counter(
    'slide_generations_total',
    'Total number of slide generations'
)

slide_generation_duration = Histogram(
    'slide_generation_duration_seconds',
    'Time spent generating slides'
)

# 使用例
@slide_generation_duration.time()
async def generate_slide(...):
    slide_generation_counter.inc()
    # ... generation logic
```

---

## まとめ

このシステムは以下の原則に基づいて設計されています：

1. **関心の分離**: レイヤードアーキテクチャによる明確な責任分担
2. **拡張性**: マルチエージェントシステムによる柔軟な機能拡張
3. **標準準拠**: Google Slides API形式を内部標準として採用
4. **型安全性**: Pydantic、TypeScriptによる厳格な型チェック
5. **テスト可能性**: 依存性注入とモックによるテストの容易性

今後の拡張ポイント：
- **リアルタイム協調編集**: WebSocketによる複数ユーザー同時編集
- **AIフィードバックループ**: ユーザーフィードバックを学習に活用
- **テンプレートマーケットプレイス**: コミュニティテンプレート共有
- **詳細分析**: プレゼンテーションパフォーマンス分析
