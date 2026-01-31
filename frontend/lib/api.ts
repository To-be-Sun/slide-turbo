/**
 * APIクライアント
 * Next.jsのAPI Routes経由でバックエンドAPIを呼び出します
 */

// フロントエンドからは相対パスでAPIを呼び出す
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || ""

/**
 * Google Slidesをインポート
 */
export async function importGoogleSlides(url: string) {
  const response = await fetch("/api/google-slides/parse-url", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ url }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || error.message || "Failed to import Google Slides")
  }

  return response.json()
}

/**
 * Google認証URLを取得
 */
export async function getGoogleAuthUrl() {
  const response = await fetch("/api/google-slides/auth")
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || "Failed to get auth URL")
  }

  return response.json()
}

/**
 * スライドを生成
 */
export async function generateSlides(data: {
  templateId: string
  slots: Array<{
    slotId: string
    slideIndex: number
    name: string
    type: "title" | "text" | "image" | "chart" | "list" | "icon"
    value: string
    status: "empty" | "draft" | "filled" | "approved"
    linkedStoryId?: string
  }>
  story?: Array<{
    id: string
    title: string
    content: string
    slideIndices: number[]
    status: "draft" | "approved"
    order: number
  }>
}) {
  const response = await fetch("/api/slides/generate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || error.message || "Failed to generate slides")
  }

  return response.json()
}

/**
 * スロットをAIで埋める
 */
export async function fillSlot(data: {
  slotId: string
  value: string
  context?: {
    story?: Array<{
      id: string
      title: string
      content: string
      slideIndices: number[]
      status: "draft" | "approved"
      order: number
    }>
    otherSlots?: Array<{
      slotId: string
      slideIndex: number
      name: string
      type: "title" | "text" | "image" | "chart" | "list" | "icon"
      value: string
      status: "empty" | "draft" | "filled" | "approved"
      linkedStoryId?: string
    }>
  }
}) {
  const response = await fetch("/api/slides/fill-slot", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || error.message || "Failed to fill slot")
  }

  return response.json()
}

/**
 * スロットを置き換え
 */
export async function replaceSlot(data: {
  html: string
  slotId: string
  value: string
  slotType: "title" | "text" | "image" | "chart" | "list" | "icon"
}) {
  const response = await fetch("/api/slides/replace-slot", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || error.message || "Failed to replace slot")
  }

  return response.json()
}

/**
 * スライドを画像としてレンダリング
 */
export async function renderSlide(slideIndex: number, html: string): Promise<string> {
  const response = await fetch(
    `/api/slides/render/${slideIndex}?html=${encodeURIComponent(html)}`
  )

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || error.message || "Failed to render slide")
  }

  const blob = await response.blob()
  return URL.createObjectURL(blob)
}

/**
 * テンプレート一覧を取得
 */
export async function getTemplates() {
  const response = await fetch("/api/templates")

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || "Failed to fetch templates")
  }

  return response.json()
}

/**
 * テンプレートを取得
 */
export async function getTemplate(id: string) {
  const response = await fetch(`/api/templates/${id}`)

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || "Failed to fetch template")
  }

  return response.json()
}

/**
 * プロジェクトを作成
 */
export async function createProject(data: {
  name: string
  description?: string
  templateId: string
  templateName: string
}) {
  const response = await fetch("/api/projects", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || error.message || "Failed to create project")
  }

  return response.json()
}

/**
 * プロジェクトを取得
 */
export async function getProject(id: string) {
  const response = await fetch(`/api/projects/${id}`)

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || "Failed to fetch project")
  }

  return response.json()
}

/**
 * プロジェクト一覧を取得
 */
export async function getProjects() {
  const response = await fetch("/api/projects")

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || "Failed to fetch projects")
  }

  return response.json()
}
