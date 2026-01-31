import { getAvailableModel } from "../config/gemini.js"
import type { FilledSlot, StorySection, FillSlotRequest } from "../types.js"

/**
 * AIを使ってスロットの内容を生成・置き換え
 */
export async function fillSlotWithAI(request: FillSlotRequest): Promise<string> {
  const model = await getAvailableModel()

  const { slotId, value, context } = request

  // コンテキスト情報を構築
  const contextPrompt = context
    ? `
関連ストーリー:
${context.story?.map((s) => `- ${s.title}: ${s.content}`).join("\n") || "なし"}

関連スロット:
${context.otherSlots?.map((s) => `- ${s.name}: ${s.value}`).join("\n") || "なし"}
`
    : ""

  const prompt = `
以下のスロットに適切な内容を生成してください。

スロットID: ${slotId}
ユーザー入力: ${value || "なし"}

${contextPrompt}

要件:
1. ユーザー入力がある場合は、それを基に適切な内容を生成
2. ユーザー入力がない場合は、コンテキストから適切な内容を推測
3. 関連するストーリーや他のスロットと一貫性を保つ
4. 簡潔で明確な内容にする

生成した内容のみを返してください（説明や余計なテキストは不要）。
`

  try {
    const result = await model.generateContent(prompt)
    const response = await result.response
    return response.text().trim()
  } catch (error) {
    console.error("Error filling slot with AI:", error)
    // フォールバック: ユーザー入力をそのまま返す
    return value || ""
  }
}

/**
 * HTML内の特定スロットを置き換え
 */
export function replaceSlotInHTML(
  html: string,
  slotId: string,
  newValue: string,
  slotType: FilledSlot["type"]
): string {
  // スロットIDに基づいてHTML内の該当箇所を置き換え
  // これは簡易実装。実際にはより堅牢なHTMLパーサーを使用することを推奨

  // データ属性でスロットを識別
  const slotSelector = `[data-slot-id="${slotId}"]`
  
  // タイプに応じた置き換え
  let replacementHTML = ""
  
  switch (slotType) {
    case "title":
      replacementHTML = `<h1 class="slide-title" data-slot-id="${slotId}">${escapeHtml(newValue)}</h1>`
      break
    case "text":
      replacementHTML = `<p class="slide-text" data-slot-id="${slotId}">${escapeHtml(newValue)}</p>`
      break
    case "list":
      const listItems = newValue.split("\n").filter((item) => item.trim())
      replacementHTML = `<ul class="slide-list" data-slot-id="${slotId}">${listItems.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`
      break
    case "image":
    case "icon":
      replacementHTML = `<div class="slide-image" data-slot-id="${slotId}"><img src="${escapeHtml(newValue)}" alt="${slotId}" /></div>`
      break
    case "chart":
      replacementHTML = `<div class="slide-chart" data-slot-id="${slotId}">${escapeHtml(newValue)}</div>`
      break
    default:
      replacementHTML = `<div data-slot-id="${slotId}">${escapeHtml(newValue)}</div>`
  }

  // HTML内の該当スロットを置き換え
  // 正規表現で置き換え（簡易実装）
  const regex = new RegExp(
    `<[^>]*data-slot-id="${slotId}"[^>]*>.*?</[^>]*>`,
    "gs"
  )
  
  if (regex.test(html)) {
    return html.replace(regex, replacementHTML)
  }

  // 見つからない場合は、適切な場所に挿入
  // これは簡易実装。実際にはDOMパーサーを使用することを推奨
  return html
}

/**
 * HTMLエスケープ
 */
function escapeHtml(text: string): string {
  const map: Record<string, string> = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  }
  return text.replace(/[&<>"']/g, (m) => map[m])
}

