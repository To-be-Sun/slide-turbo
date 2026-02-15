# エージェントJSON受け口実装ガイド

## 🎯 目的
AI エージェントが生成した `SlidePresentation` 形式のJSONを一括で受け取り、データベースに保存する

---

## 📋 必要な実装

### 1. DTO追加 (`app/application/slide/dto.py`)

```python
from app.infrastructure.rendering.schema import SlidePresentation

class ImportAgentOutputDTO(BaseModel):
    """エージェント出力JSON"""
    presentation: SlidePresentation
```

### 2. Usecase追加 (`app/application/slide/usecases.py`)

```python
async def import_agent_output(
    self,
    slide_id: str,
    version_num: int,
    dto: ImportAgentOutputDTO,
) -> SlideVersionResponseDTO:
    """
    エージェント出力を一括保存
    
    1. SlideVersionを取得 or 作成
    2. presentation.pages をループ
    3. 各SlidePage を Page テーブルに保存 (contents = page.model_dump())
    """
    # バージョン取得/作成
    version = await self.repo.find_version_by_num(slide_id, version_num)
    if not version:
        version = await self.repo.create_version(slide_id, version_num)
    
    # 既存ページを削除 (上書き)
    await self.repo.delete_pages_by_version(version.id)
    
    # 新しいページを一括保存
    for page in dto.presentation.pages:
        await self.repo.create_page(
            slide_version_id=version.id,
            page_num=page.page_num,
            contents=page.model_dump(mode="json"),  # Pydantic → dict → JSON
        )
    
    return SlideVersionResponseDTO(...)
```

### 3. Router追加 (`app/presentation/routers/slide_router.py`)

```python
@router.post(
    "/{slide_id}/versions/{version_num}/import-agent-output",
    response_model=SlideVersionResponseDTO,
    status_code=201,
)
async def import_agent_output(
    slide_id: str,
    version_num: int,
    body: ImportAgentOutputDTO,
    uc: SlideUseCases = Depends(_get_usecases),
):
    """
    エージェント出力JSONを一括インポート
    
    Request Body:
    {
      "presentation": {
        "title": "...",
        "pages": [
          {
            "page_num": 1,
            "layout": "title_slide",
            "elements": [...],
            "background": {...},
            "notes": "..."
          },
          ...
        ],
        "author": "...",
        "version": 1
      }
    }
    """
    return await uc.import_agent_output(slide_id, version_num, body)
```

### 4. Repository拡張 (`app/infrastructure/persistence/slide_repository.py`)

```python
async def delete_pages_by_version(self, version_id: str) -> int:
    """バージョン内の全ページを削除 (上書き用)"""
    result = await self.db.page.delete_many(
        where={"slide_version_id": version_id}
    )
    return result
```

---

## 🔄 エージェント → データベース フロー

```
エージェント
  ↓ 
  SlidePresentation JSON
  {
    "title": "...",
    "pages": [
      {
        "page_num": 1,
        "layout": "title_slide",
        "elements": [
          {
            "element_id": "title_1",
            "type": "text",
            "position": {...},
            "content": "タイトル",
            "style": {...}
          },
          ...
        ],
        "background": {"color": "#667eea"},
        "notes": "ノート"
      },
      ...
    ],
    "author": "AI Agent",
    "version": 1
  }
  ↓
POST /api/slides/{slide_id}/versions/{version_num}/import-agent-output
  ↓
SlideUseCases.import_agent_output()
  ↓
Database (Prisma)
  - Slide (既存/新規)
  - SlideVersion (指定version_num)
  - Page[] (各SlidePage → Page.contents に JSON保存)
```

---

## 📊 データベース保存形式

### Page.contents に保存されるJSON

```json
{
  "page_num": 1,
  "layout": "title_slide",
  "elements": [
    {
      "element_id": "title_1",
      "type": "text",
      "position": {"x": 100, "y": 150, "width": 600, "height": 100},
      "content": "スライドタイトル",
      "z_index": 0,
      "style": {
        "font_size": 48,
        "font_weight": "bold",
        "color": "#ffffff",
        "align": "center",
        "line_height": 1.5
      }
    }
  ],
  "background": {
    "color": "#667eea",
    "image_url": null
  },
  "notes": "ノート内容"
}
```

---

## ✅ 実装後の動作確認

### テストケース

```python
# tests/application/slide/test_import_agent_output.py

async def test_import_agent_output_success():
    """エージェントJSON一括保存成功"""
    presentation = SlidePresentation(
        title="テストプレゼン",
        pages=[
            SlidePage(
                page_num=1,
                layout="title_slide",
                elements=[
                    TextElement(
                        element_id="test_1",
                        type="text",
                        position=ElementPosition(x=100, y=100, width=600, height=100),
                        content="タイトル",
                    )
                ],
            ),
            SlidePage(page_num=2, layout="blank", elements=[]),
        ],
    )
    
    dto = ImportAgentOutputDTO(presentation=presentation)
    result = await usecases.import_agent_output("slide_1", 1, dto)
    
    # 検証
    assert result.version_num == 1
    pages = await repo.find_pages_by_version(result.id)
    assert len(pages) == 2
    assert pages[0].page_num == 1
    assert pages[0].contents["layout"] == "title_slide"
```

### curlテスト

```bash
curl -X POST http://localhost:8000/api/slides/{slide_id}/versions/1/import-agent-output \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "presentation": {
      "title": "エージェント生成プレゼン",
      "pages": [
        {
          "page_num": 1,
          "layout": "title_slide",
          "elements": [
            {
              "element_id": "title_1",
              "type": "text",
              "position": {"x": 100, "y": 150, "width": 600, "height": 100},
              "content": "タイトル",
              "style": {"font_size": 48, "color": "#ffffff"}
            }
          ],
          "background": {"color": "#667eea"}
        }
      ],
      "author": "AI Agent",
      "version": 1
    }
  }'
```

---

## 🎯 実装優先度

### Phase 1: 最小実装 (1-2時間)
1. ✅ DTO追加
2. ✅ Usecase実装
3. ✅ Router追加
4. ✅ 基本テスト

### Phase 2: 拡張機能 (1-2時間)
5. ✅ エラーハンドリング (ページ番号重複、バリデーション)
6. ✅ トランザクション処理
7. ✅ ロギング
8. ✅ 既存ページ上書き/マージ選択

### Phase 3: 統合テスト (30分)
9. ✅ E2Eテスト (エージェント → 保存 → プレビュー → エクスポート)
10. ✅ パフォーマンステスト (100ページ一括保存)

---

## 🚨 現状の回避策

エージェント側で以下を実装すれば、既存APIで保存可能:

```python
# エージェント側の実装
async def save_presentation_to_backend(presentation: SlidePresentation, slide_id: str):
    # 1. Slide作成
    slide = await create_slide({"title": presentation.title})
    
    # 2. Version作成
    version = await create_version(slide.id)
    
    # 3. ページを1つずつPOST (N回のAPI呼び出し)
    for page in presentation.pages:
        await add_page(
            version_id=version.id,
            data={
                "page_num": page.page_num,
                "contents": page.model_dump(mode="json")
            }
        )
```

**デメリット**:
- N回のAPI呼び出し (ネットワークオーバーヘッド)
- トランザクション保証なし
- エラー時の部分保存リスク

---

## 📌 まとめ

**現状**: ❌ エージェントJSON一括受信エンドポイント未実装

**必要実装**:
1. ImportAgentOutputDTO (DTO)
2. import_agent_output() (Usecase)
3. POST /{slide_id}/versions/{version_num}/import-agent-output (Router)
4. delete_pages_by_version() (Repository)

**実装時間**: 約2-3時間 (テスト含む)

**優先度**: 🔴 **HIGH** (エージェント連携の必須機能)
