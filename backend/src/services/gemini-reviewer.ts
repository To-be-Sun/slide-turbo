import { getAvailableModel } from "../config/gemini.js"

/**
 * HTMLスライドをGeminiでレビューしてタイトルを生成
 */
export interface SlideReview {
  title: string
  description: string
  suggestedSlots: Array<{
    id: string
    name: string
    type: "title" | "text" | "image" | "chart" | "list" | "icon"
    placeholder: string
    required: boolean
  }>
  improvements?: string[]
}

/**
 * スライドHTMLをレビューしてメタデータを生成
 */
export async function reviewSlideHTML(
  html: string,
  slideIndex: number
): Promise<SlideReview> {
  const model = await getAvailableModel()

  const prompt = `
以下のHTMLスライドを分析して、以下の情報をJSON形式で返してください：

1. title: スライドのタイトル（簡潔に、30文字以内）
2. description: スライドの説明（50文字以内）
3. suggestedSlots: このスライドから抽出できる編集可能なスロットの配列
   - id: スロットID（例: "s${slideIndex}-title"）
   - name: スロット名（例: "タイトル"）
   - type: スロットタイプ（"title" | "text" | "image" | "chart" | "list" | "icon"）
   - placeholder: プレースホルダーテキスト
   - required: 必須かどうか
4. improvements: 改善提案（任意、配列）

HTML:
${html.substring(0, 5000)} ${html.length > 5000 ? "...(truncated)" : ""}

JSON形式のみを返してください。説明や余計なテキストは不要です。
`

  try {
    const result = await model.generateContent(prompt)
    const response = await result.response
    const text = response.text().trim()

    // JSONを抽出（```json```ブロックがある場合）
    let jsonText = text
    const jsonMatch = text.match(/```(?:json)?\s*([\s\S]*?)\s*```/)
    if (jsonMatch) {
      jsonText = jsonMatch[1]
    }

    const review = JSON.parse(jsonText) as SlideReview

    // バリデーション
    if (!review.title || !review.description) {
      throw new Error("Invalid review response: missing title or description")
    }

    return review
  } catch (error) {
    console.error("Error reviewing slide HTML:", error)
    
    // フォールバック: 基本的なレビューを返す
    return {
      title: `スライド ${slideIndex + 1}`,
      description: "スライドコンテンツ",
      suggestedSlots: [
        {
          id: `s${slideIndex}-title`,
          name: "タイトル",
          type: "title",
          placeholder: "スライドのタイトル",
          required: true,
        },
      ],
    }
  }
}

/**
 * プレゼンテーション全体をレビュー
 */
export async function reviewPresentation(
  slidesHTML: string[]
): Promise<{
  title: string
  description: string
  slideReviews: SlideReview[]
}> {
  const model = await getAvailableModel()

  // 各スライドをレビュー
  const slideReviews = await Promise.all(
    slidesHTML.map((html, index) => reviewSlideHTML(html, index))
  )

  // 全体のタイトルと説明を生成
  const allTitles = slideReviews.map((r) => r.title).join(", ")
  const prompt = `
以下のスライドタイトルから、プレゼンテーション全体のタイトルと説明を生成してください：

スライドタイトル:
${allTitles}

以下のJSON形式で返してください：
{
  "title": "プレゼンテーション全体のタイトル",
  "description": "プレゼンテーションの説明（100文字以内）"
}

JSON形式のみを返してください。
`

  try {
    const result = await model.generateContent(prompt)
    const response = await result.response
    const text = response.text().trim()

    let jsonText = text
    const jsonMatch = text.match(/```(?:json)?\s*([\s\S]*?)\s*```/)
    if (jsonMatch) {
      jsonText = jsonMatch[1]
    }

    const presentationInfo = JSON.parse(jsonText) as {
      title: string
      description: string
    }

    return {
      title: presentationInfo.title || "Untitled Presentation",
      description: presentationInfo.description || "",
      slideReviews,
    }
  } catch (error) {
    console.error("Error reviewing presentation:", error)
    return {
      title: "Untitled Presentation",
      description: "",
      slideReviews,
    }
  }
}

