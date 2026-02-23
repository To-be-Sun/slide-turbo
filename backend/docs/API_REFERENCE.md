# Slide Turbo API リファレンス

## 目次
1. [認証](#認証)
2. [エンドポイント詳細](#エンドポイント詳細)
3. [データモデル](#データモデル)
4. [エラーハンドリング](#エラーハンドリング)
5. [レート制限](#レート制限)

---

## 認証

### JWT認証フロー

```mermaid
sequenceDiagram
    participant Client
    participant Backend
    participant Google
    
    Client->>Backend: GET /api/v1/users/auth/google
    Backend-->>Client: 302 Redirect to Google
    Client->>Google: OAuth consent
    Google-->>Backend: Callback with code
    Backend->>Google: Exchange code for tokens
    Google-->>Backend: User info
    Backend->>Backend: Create/Update user
    Backend-->>Client: Set JWT cookie
    Client->>Backend: API Request with JWT
    Backend-->>Client: Response
```

### 認証ヘッダー
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### JWTペイロード
```json
{
  "sub": "user_id_here",
  "email": "user@example.com",
  "exp": 1234567890
}
```

---

## エンドポイント詳細

### 1. ヘルスチェック

#### `GET /health`
システムの稼働状態をチェック

**認証**: 不要

**レスポンス**:
```json
{
  "status": "ok"
}
```

**ステータスコード**:
- `200`: システム正常

---

### 2. ユーザー認証

#### `GET /api/v1/users/auth/google`
Google OAuth認証を開始

**認証**: 不要

**レスポンス**: 302 Redirect to Google

---

#### `POST /api/v1/users/auth/google/callback`
Google OAuthのコールバック処理

**認証**: 不要

**クエリパラメータ**:
- `code` (string, required): Google認証コード

**レスポンス**:
```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer"
}
```

**ステータスコード**:
- `200`: 認証成功
- `401`: 認証失敗

---

#### `GET /api/v1/users/me`
現在のユーザー情報を取得

**認証**: 必要

**レスポンス**:
```json
{
  "id": "user_123",
  "email": "user@example.com",
  "name": "John Doe",
  "picture": "https://lh3.googleusercontent.com/...",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**ステータスコード**:
- `200`: 成功
- `401`: 認証エラー

---

#### `PATCH /api/v1/users/me`
ユーザープロフィールを更新

**認証**: 必要

**リクエストボディ**:
```json
{
  "name": "Updated Name"
}
```

**レスポンス**:
```json
{
  "id": "user_123",
  "email": "user@example.com",
  "name": "Updated Name",
  "picture": "https://lh3.googleusercontent.com/...",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**ステータスコード**:
- `200`: 更新成功
- `401`: 認証エラー
- `404`: ユーザー不存在

---

### 3. テンプレート管理

#### `POST /api/v1/templates/import`
Google Slidesからテンプレートをインポート

**認証**: 必要

**リクエストボディ**:
```json
{
  "presentation_url": "https://docs.google.com/presentation/d/PRESENTATION_ID",
  "title": "My Template"
}
```

**レスポンス**:
```json
{
  "id": "template_123",
  "title": "My Template",
  "contents": {
    "presentationId": "PRESENTATION_ID",
    "slides": [
      {
        "objectId": "slide_1",
        "pageElements": [...]
      }
    ],
    "slots": ["{{company_name}}", "{{product_name}}"]
  },
  "thumbnail_url": "https://...",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**ステータスコード**:
- `201`: インポート成功
- `400`: 無効なURL
- `401`: 認証エラー
- `500`: Google API エラー

---

#### `POST /api/v1/templates/import-preview`
インポート前にプレビュー

**認証**: 必要

**リクエストボディ**:
```json
{
  "presentation_url": "https://docs.google.com/presentation/d/PRESENTATION_ID"
}
```

**レスポンス**:
```json
{
  "presentation_id": "PRESENTATION_ID",
  "thumbnail_url": "https://...",
  "slide_count": 5,
  "detected_slots": ["{{company_name}}", "{{product_name}}"]
}
```

**ステータスコード**:
- `200`: プレビュー取得成功
- `400`: 無効なURL
- `401`: 認証エラー

---

#### `GET /api/v1/templates`
テンプレート一覧を取得

**認証**: 必要

**クエリパラメータ**:
- `skip` (integer, optional, default=0): スキップ件数
- `limit` (integer, optional, default=20): 取得件数

**レスポンス**:
```json
{
  "items": [
    {
      "id": "template_123",
      "title": "Template 1",
      "thumbnail_url": "https://...",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 10,
  "skip": 0,
  "limit": 20
}
```

**ステータスコード**:
- `200`: 成功
- `401`: 認証エラー

---

#### `GET /api/v1/templates/{id}`
テンプレート詳細を取得

**認証**: 必要

**パスパラメータ**:
- `id` (string, required): テンプレートID

**レスポンス**:
```json
{
  "id": "template_123",
  "title": "My Template",
  "contents": {
    "slides": [...],
    "slots": ["{{company_name}}"]
  },
  "thumbnail_url": "https://...",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**ステータスコード**:
- `200`: 成功
- `401`: 認証エラー
- `404`: テンプレート不存在

---

#### `PATCH /api/v1/templates/{id}`
テンプレートを更新

**認証**: 必要

**パスパラメータ**:
- `id` (string, required): テンプレートID

**リクエストボディ**:
```json
{
  "title": "Updated Template",
  "contents": {
    "slides": [...],
    "slots": ["{{new_slot}}"]
  }
}
```

**レスポンス**: 更新後のテンプレート情報

**ステータスコード**:
- `200`: 更新成功
- `401`: 認証エラー
- `404`: テンプレート不存在

---

#### `DELETE /api/v1/templates/{id}`
テンプレートを削除

**認証**: 必要

**パスパラメータ**:
- `id` (string, required): テンプレートID

**レスポンス**: なし

**ステータスコード**:
- `204`: 削除成功
- `401`: 認証エラー
- `404`: テンプレート不存在

---

#### `GET /api/v1/templates/{id}/thumbnail`
テンプレートのサムネイルを取得

**認証**: 必要

**パスパラメータ**:
- `id` (string, required): テンプレートID

**レスポンス**: 画像バイナリ (image/png)

**ステータスコード**:
- `200`: 成功
- `401`: 認証エラー
- `404`: サムネイル不存在

---

### 4. スライド管理

#### `POST /api/v1/slides`
新しいスライドプロジェクトを作成

**認証**: 必要

**リクエストボディ**:
```json
{
  "template_id": "template_123",
  "title": "My Presentation",
  "slot_values": {
    "company_name": "Acme Corp",
    "product_name": "Widget Pro"
  }
}
```

**レスポンス**:
```json
{
  "id": "slide_123",
  "template_id": "template_123",
  "title": "My Presentation",
  "latest_version": {
    "id": "version_1",
    "version_number": 1,
    "slot_values": {
      "company_name": "Acme Corp",
      "product_name": "Widget Pro"
    },
    "pages": []
  },
  "created_at": "2024-01-01T00:00:00Z"
}
```

**ステータスコード**:
- `201`: 作成成功
- `400`: バリデーションエラー
- `401`: 認証エラー
- `404`: テンプレート不存在

---

#### `GET /api/v1/slides`
スライド一覧を取得

**認証**: 必要

**クエリパラメータ**:
- `skip` (integer, optional, default=0)
- `limit` (integer, optional, default=20)

**レスポンス**:
```json
{
  "items": [
    {
      "id": "slide_123",
      "title": "My Presentation",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 5,
  "skip": 0,
  "limit": 20
}
```

**ステータスコード**:
- `200`: 成功
- `401`: 認証エラー

---

#### `GET /api/v1/slides/{id}`
スライド詳細を取得

**認証**: 必要

**パスパラメータ**:
- `id` (string, required): スライドID

**クエリパラメータ**:
- `version_num` (integer, optional): バージョン番号（指定しない場合は最新版）

**レスポンス**:
```json
{
  "id": "slide_123",
  "title": "My Presentation",
  "template_id": "template_123",
  "latest_version": {
    "id": "version_2",
    "version_number": 2,
    "slot_values": {...},
    "pages": [
      {
        "id": "page_1",
        "page_number": 1,
        "page_data": {
          "objectId": "slide_1",
          "pageElements": [...]
        }
      }
    ]
  },
  "created_at": "2024-01-01T00:00:00Z"
}
```

**ステータスコード**:
- `200`: 成功
- `401`: 認証エラー
- `404`: スライド不存在

---

#### `PATCH /api/v1/slides/{id}`
スライドを更新

**認証**: 必要

**パスパラメータ**:
- `id` (string, required): スライドID

**リクエストボディ**:
```json
{
  "title": "Updated Title"
}
```

**レスポンス**: 更新後のスライド情報

**ステータスコード**:
- `200`: 更新成功
- `401`: 認証エラー
- `404`: スライド不存在

---

#### `DELETE /api/v1/slides/{id}`
スライドを削除

**認証**: 必要

**パスパラメータ**:
- `id` (string, required): スライドID

**レスポンス**: なし

**ステータスコード**:
- `204`: 削除成功（idempotent）
- `401`: 認証エラー

---

#### `GET /api/v1/slides/{id}/preview`
スライドのHTMLプレビューを生成

**認証**: 不要（公開プレビューの場合）

**パスパラメータ**:
- `id` (string, required): スライドID

**クエリパラメータ**:
- `version_num` (integer, optional): バージョン番号

**レスポンス**: HTML (text/html)

**ステータスコード**:
- `200`: 成功
- `404`: スライド不存在

---

#### `POST /api/v1/slides/{id}/export`
Google Slidesへエクスポート

**認証**: 必要

**パスパラメータ**:
- `id` (string, required): スライドID

**フォームデータ**:
- `version_num` (integer, optional): バージョン番号
- `owner_email` (string, optional): 所有者メール

**レスポンス**:
```json
{
  "presentationId": "google_slides_id",
  "presentationUrl": "https://docs.google.com/presentation/d/...",
  "downloadUrl": "https://docs.google.com/presentation/d/.../export/pptx"
}
```

**ステータスコード**:
- `200`: エクスポート成功
- `401`: 認証エラー
- `404`: スライド不存在
- `500`: Google API エラー

---

### 5. バージョン管理

#### `POST /api/v1/slides/{id}/versions`
新しいバージョンを作成

**認証**: 必要

**パスパラメータ**:
- `id` (string, required): スライドID

**レスポンス**:
```json
{
  "id": "version_3",
  "slide_id": "slide_123",
  "version_number": 3,
  "slot_values": {...},
  "pages": [],
  "created_at": "2024-01-01T00:00:00Z"
}
```

**ステータスコード**:
- `201`: 作成成功
- `401`: 認証エラー
- `404`: スライド不存在

---

#### `GET /api/v1/slides/{id}/versions`
バージョン一覧を取得

**認証**: 必要

**パスパラメータ**:
- `id` (string, required): スライドID

**レスポンス**:
```json
{
  "versions": [
    {
      "id": "version_1",
      "version_number": 1,
      "created_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": "version_2",
      "version_number": 2,
      "created_at": "2024-01-02T00:00:00Z"
    }
  ]
}
```

**ステータスコード**:
- `200`: 成功
- `401`: 認証エラー
- `404`: スライド不存在

---

### 6. ページ管理

#### `POST /api/v1/slides/versions/{version_id}/pages`
バージョンにページを追加

**認証**: 必要

**パスパラメータ**:
- `version_id` (string, required): バージョンID

**リクエストボディ**:
```json
{
  "page_number": 1,
  "page_data": {
    "objectId": "slide_1",
    "pageElements": [
      {
        "objectId": "element_1",
        "transform": {
          "translateX": 50,
          "translateY": 50
        },
        "size": {
          "width": {"magnitude": 300, "unit": "PT"},
          "height": {"magnitude": 100, "unit": "PT"}
        },
        "shape": {
          "shapeType": "TEXT_BOX",
          "text": {
            "textElements": [
              {"textRun": {"content": "Hello"}}
            ]
          }
        }
      }
    ]
  }
}
```

**レスポンス**:
```json
{
  "id": "page_1",
  "version_id": "version_1",
  "page_number": 1,
  "page_data": {...},
  "created_at": "2024-01-01T00:00:00Z"
}
```

**ステータスコード**:
- `201`: 作成成功
- `400`: バリデーションエラー
- `401`: 認証エラー
- `404`: バージョン不存在

---

#### `PATCH /api/v1/slides/pages/{page_id}`
ページを更新

**認証**: 必要

**パスパラメータ**:
- `page_id` (string, required): ページID

**リクエストボディ**:
```json
{
  "page_data": {
    "objectId": "slide_1",
    "pageElements": [...]
  }
}
```

**レスポンス**: 更新後のページ情報

**ステータスコード**:
- `200`: 更新成功
- `401`: 認証エラー
- `404`: ページ不存在

---

#### `DELETE /api/v1/slides/pages/{page_id}`
ページを削除

**認証**: 必要

**パスパラメータ**:
- `page_id` (string, required): ページID

**レスポンス**: なし

**ステータスコード**:
- `204`: 削除成功
- `401`: 認証エラー
- `404`: ページ不存在

---

### 7. アウトライン管理

#### `POST /api/v1/outlines`
アウトラインを作成

**認証**: 必要

**リクエストボディ**:
```json
{
  "slide_version_id": "version_123",
  "outline": {
    "title": "新製品発表",
    "sections": [
      {
        "heading": "背景",
        "content": "市場の課題について..."
      },
      {
        "heading": "ソリューション",
        "content": "我々の製品が解決する..."
      }
    ]
  }
}
```

**レスポンス**:
```json
{
  "id": "outline_123",
  "slide_version_id": "version_123",
  "outline": {...},
  "created_at": "2024-01-01T00:00:00Z"
}
```

**ステータスコード**:
- `201`: 作成成功
- `400`: バリデーションエラー
- `401`: 認証エラー
- `404`: バージョン不存在

---

#### `GET /api/v1/outlines/{id}`
アウトライン詳細を取得

**認証**: 必要

**パスパラメータ**:
- `id` (string, required): アウトラインID

**レスポンス**:
```json
{
  "id": "outline_123",
  "slide_version_id": "version_123",
  "outline": {
    "title": "新製品発表",
    "sections": [...]
  },
  "created_at": "2024-01-01T00:00:00Z"
}
```

**ステータスコード**:
- `200`: 成功
- `401`: 認証エラー
- `404`: アウトライン不存在

---

#### `POST /api/v1/outlines/refine`
アウトラインをAIで洗練

**認証**: 必要

**リクエストボディ**:
```json
{
  "outline_id": "outline_123",
  "feedback": "もっと具体的な数字を入れてください"
}
```

**レスポンス**:
```json
{
  "outline_id": "outline_123",
  "refined_outline": {
    "title": "新製品発表",
    "sections": [
      {
        "heading": "背景",
        "content": "市場は年率15%で成長しており..."
      }
    ]
  }
}
```

**ステータスコード**:
- `200`: 洗練成功
- `400`: バリデーションエラー
- `401`: 認証エラー
- `404`: アウトライン不存在
- `500`: Gemini API エラー

---

#### `POST /api/v1/outlines/generate-slide`
マルチエージェントでスライドを生成

**認証**: 必要

**リクエストボディ**:
```json
{
  "outline_id": "outline_123",
  "page_number": 1
}
```

**レスポンス**:
```json
{
  "outline_id": "outline_123",
  "page_number": 1,
  "slide": {
    "objectId": "slide_1",
    "pageElements": [
      {
        "objectId": "title_1",
        "transform": {"translateX": 50, "translateY": 50},
        "size": {
          "width": {"magnitude": 600, "unit": "PT"},
          "height": {"magnitude": 100, "unit": "PT"}
        },
        "shape": {
          "shapeType": "TEXT_BOX",
          "text": {
            "textElements": [
              {
                "textRun": {
                  "content": "新製品発表",
                  "style": {
                    "fontSize": {"magnitude": 36, "unit": "PT"},
                    "bold": true
                  }
                }
              }
            ]
          }
        }
      }
    ]
  }
}
```

**ステータスコード**:
- `200`: 生成成功
- `400`: バリデーションエラー
- `401`: 認証エラー
- `404`: アウトライン不存在
- `500`: AIエージェントエラー

---

## データモデル

### User
```typescript
{
  id: string
  email: string
  name: string | null
  picture: string | null
  created_at: string (ISO 8601)
}
```

### Template
```typescript
{
  id: string
  title: string
  contents: GoogleSlidesPresentation
  thumbnail_url: string | null
  user_id: string
  created_at: string
}
```

### Slide
```typescript
{
  id: string
  title: string
  template_id: string
  user_id: string
  latest_version: SlideVersion
  created_at: string
}
```

### SlideVersion
```typescript
{
  id: string
  slide_id: string
  version_number: number
  slot_values: Record<string, string>
  pages: Page[]
  created_at: string
}
```

### Page
```typescript
{
  id: string
  version_id: string
  page_number: number
  page_data: GoogleSlidesSlide
  created_at: string
}
```

### Outline
```typescript
{
  id: string
  slide_version_id: string
  outline: {
    title: string
    sections: Array<{
      heading: string
      content: string
    }>
  }
  created_at: string
}
```

### GoogleSlidesSlide (Google Slides API形式)
```typescript
{
  objectId: string
  pageProperties?: {
    pageBackgroundFill?: {...}
  }
  pageElements: Array<{
    objectId: string
    transform: {
      translateX: number
      translateY: number
      scaleX?: number
      scaleY?: number
    }
    size: {
      width: {magnitude: number, unit: "PT"}
      height: {magnitude: number, unit: "PT"}
    }
    shape?: {
      shapeType: "TEXT_BOX" | "RECTANGLE" | "ELLIPSE" | ...
      text?: {
        textElements: Array<{
          textRun?: {
            content: string
            style?: TextStyle
          }
        }>
      }
    }
    image?: {
      contentUrl: string
      sourceUrl?: string
    }
  }>
}
```

---

## エラーハンドリング

### エラーレスポンス形式
```json
{
  "detail": "エラーメッセージ"
}
```

### ステータスコード一覧
- `200`: 成功
- `201`: 作成成功
- `204`: 削除成功（レスポンスボディなし）
- `400`: バリデーションエラー、リクエストエラー
- `401`: 認証エラー（トークン不正、期限切れ）
- `403`: 権限エラー（アクセス権限なし）
- `404`: リソース不存在
- `422`: バリデーションエラー（詳細）
- `500`: サーバー内部エラー
- `503`: サービス利用不可（外部API障害など）

### バリデーションエラーの詳細
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## レート制限

### 現在の制限
- **未実装**: 現在レート制限は実装されていません

### 推奨事項（本番環境）
- `/api/v1/outlines/generate-slide`: 10リクエスト/分（AIコストが高い）
- その他のエンドポイント: 100リクエスト/分

### 制限超過時のレスポンス（将来実装）
```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60

{
  "detail": "Rate limit exceeded. Please retry after 60 seconds."
}
```

---

## Webhook（将来実装予定）

### スライド生成完了通知
```json
{
  "event": "slide.generated",
  "data": {
    "outline_id": "outline_123",
    "page_number": 1,
    "slide_id": "slide_123",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

---

## バージョニング

現在のAPIバージョン: **v1**

APIのバージョンはURLのパスに含まれます: `/api/v1/...`

将来的な変更時は新しいバージョン（v2, v3...）を追加し、後方互換性を維持します。
