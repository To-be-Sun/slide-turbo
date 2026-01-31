import type { Template, FilledSlot, StorySection } from "../types.js"
import { getAvailableModel } from "../config/gemini.js"

/**
 * テンプレートとスロットデータからHTMLを生成
 */
export async function generateHTMLFromTemplate(
  template: Template,
  slots: FilledSlot[],
  story?: StorySection[]
): Promise<string> {
  const model = await getAvailableModel()

  // スライドごとにスロットをグループ化
  const slidesData = template.slots.reduce((acc, slot) => {
    if (!acc[slot.slideIndex]) {
      acc[slot.slideIndex] = []
    }
    const filledSlot = slots.find((s) => s.slotId === slot.id)
    acc[slot.slideIndex].push({
      ...slot,
      value: filledSlot?.value || "",
      status: filledSlot?.status || "empty",
    })
    return acc
  }, {} as Record<number, Array<TemplateSlot & { value: string; status: string }>>)

  // 各スライドのHTMLを生成
  const slidesHTML = await Promise.all(
    Object.entries(slidesData).map(async ([slideIndex, slideSlots]) => {
      return generateSlideHTML(parseInt(slideIndex), slideSlots, story)
    })
  )

  // 全体のHTML構造を生成
  return generateFullHTML(slidesHTML, template)
}

/**
 * 単一スライドのHTMLを生成
 */
async function generateSlideHTML(
  slideIndex: number,
  slots: Array<TemplateSlot & { value: string; status: string }>,
  story?: StorySection[]
): Promise<string> {
  const model = await getAvailableModel()

  const storyContext = story?.find((s) => s.slideIndices.includes(slideIndex))

  const prompt = `
以下の情報から、プレゼンテーションスライドのHTMLを生成してください。

スライド番号: ${slideIndex + 1}

ストーリーコンテキスト:
${storyContext ? `タイトル: ${storyContext.title}\n内容: ${storyContext.content}` : "なし"}

スロット情報:
${slots
  .map(
    (slot) => `
- ${slot.name} (${slot.type}): ${slot.value || slot.placeholder}
  状態: ${slot.status}
`
  )
  .join("\n")}

要件:
1. モダンでプロフェッショナルなデザイン
2. レスポンシブ対応（16:9のアスペクト比）
3. タイトルスロットは大きく目立つように
4. テキストスロットは読みやすく配置
5. リストスロットは箇条書きで表示
6. 画像/アイコンスロットはプレースホルダーを表示
7. チャートスロットはデータ可視化の準備を
8. 空のスロットは点線の枠で表示

HTMLのみを返してください（<style>タグを含む完全なHTML）。
`

  try {
    const result = await model.generateContent(prompt)
    const response = await result.response
    let html = response.text()

    // HTMLの開始・終了タグを確認
    if (!html.includes("<html")) {
      html = `<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>スライド ${slideIndex + 1}</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
  </style>
</head>
<body>
${html}
</body>
</html>`
    }

    return html
  } catch (error) {
    console.error("Error generating slide HTML:", error)
    // フォールバック: シンプルなHTMLを生成
    return generateFallbackSlideHTML(slideIndex, slots)
  }
}

/**
 * フォールバック: シンプルなHTMLを生成
 */
function generateFallbackSlideHTML(
  slideIndex: number,
  slots: Array<TemplateSlot & { value: string; status: string }>
): string {
  const titleSlot = slots.find((s) => s.type === "title")
  const textSlots = slots.filter((s) => s.type === "text")
  const listSlot = slots.find((s) => s.type === "list")
  const imageSlot = slots.find((s) => s.type === "image" || s.type === "icon")

  return `
<div class="slide" data-slide-index="${slideIndex}">
  <div class="slide-content">
    ${titleSlot ? `<h1 class="slide-title ${titleSlot.status === "empty" ? "empty" : ""}">${titleSlot.value || titleSlot.placeholder}</h1>` : ""}
    ${textSlots.map((slot) => `<p class="slide-text ${slot.status === "empty" ? "empty" : ""}">${slot.value || slot.placeholder}</p>`).join("")}
    ${listSlot ? `<ul class="slide-list ${listSlot.status === "empty" ? "empty" : ""}">${listSlot.value ? listSlot.value.split("\n").map((item) => `<li>${item}</li>`).join("") : `<li>${listSlot.placeholder}</li>`}</ul>` : ""}
    ${imageSlot ? `<div class="slide-image ${imageSlot.status === "empty" ? "empty" : ""}">${imageSlot.value ? `<img src="${imageSlot.value}" alt="${imageSlot.name}" />` : `<div class="placeholder">${imageSlot.placeholder}</div>`}</div>` : ""}
  </div>
</div>
<style>
  .slide { width: 100%; height: 100vh; display: flex; align-items: center; justify-content: center; padding: 60px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
  .slide-content { max-width: 1200px; width: 100%; }
  .slide-title { font-size: 3rem; font-weight: bold; margin-bottom: 2rem; }
  .slide-title.empty { border: 2px dashed rgba(255,255,255,0.5); padding: 1rem; border-radius: 8px; color: rgba(255,255,255,0.7); }
  .slide-text { font-size: 1.5rem; line-height: 1.8; margin-bottom: 1.5rem; }
  .slide-text.empty { border: 2px dashed rgba(255,255,255,0.5); padding: 1rem; border-radius: 8px; color: rgba(255,255,255,0.7); min-height: 60px; }
  .slide-list { font-size: 1.3rem; line-height: 2; margin-left: 2rem; }
  .slide-list.empty { border: 2px dashed rgba(255,255,255,0.5); padding: 1rem; border-radius: 8px; color: rgba(255,255,255,0.7); }
  .slide-image { width: 100%; max-width: 600px; margin: 2rem auto; }
  .slide-image.empty { border: 2px dashed rgba(255,255,255,0.5); padding: 2rem; border-radius: 8px; text-align: center; color: rgba(255,255,255,0.7); }
  .slide-image img { width: 100%; height: auto; border-radius: 8px; }
</style>
`
}

/**
 * 全スライドを含む完全なHTMLを生成
 */
function generateFullHTML(slidesHTML: string[], template: Template): string {
  return `
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${template.name}</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { 
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: #0a0a0a;
      color: #ffffff;
    }
    .slides-container {
      display: flex;
      flex-direction: column;
      gap: 40px;
      padding: 40px;
    }
    .slide-wrapper {
      width: 100%;
      max-width: 1920px;
      margin: 0 auto;
      aspect-ratio: 16 / 9;
      background: white;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    .slide-wrapper iframe {
      width: 100%;
      height: 100%;
      border: none;
    }
  </style>
</head>
<body>
  <div class="slides-container">
    ${slidesHTML
      .map(
        (html, index) => `
    <div class="slide-wrapper" data-slide="${index}">
      ${html}
    </div>
    `
      )
      .join("")}
  </div>
</body>
</html>
`
}

