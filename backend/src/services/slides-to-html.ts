import type { slides_v1 } from "googleapis"
import type { SlideElement } from "./google-slides-parser.js"
import { extractSlideElements } from "./google-slides-parser.js"

/**
 * Google Slidesプレゼンテーション全体をHTMLに変換
 */
export function convertPresentationToHTML(
  presentation: slides_v1.Schema$Presentation
): string {
  if (!presentation.slides) {
    return ""
  }

  const slidesHTML = presentation.slides.map((slide, index) => {
    const elements = extractSlideElements(slide)
    return convertSlideToHTML(elements, index)
  })

  return generateFullPresentationHTML(slidesHTML, presentation.title || "Untitled")
}

/**
 * 単一スライドをHTMLに変換
 */
export function convertSlideToHTML(
  elements: SlideElement[],
  slideIndex: number
): string {
  // 要素を位置でソート（上から下、左から右）
  const sortedElements = [...elements].sort((a, b) => {
    const aY = a.position?.y || 0
    const bY = b.position?.y || 0
    if (Math.abs(aY - bY) > 50) {
      return aY - bY
    }
    return (a.position?.x || 0) - (b.position?.x || 0)
  })

  // タイトル要素を特定（通常は最初の大きなテキスト要素）
  const titleElement = sortedElements.find(
    (el) => el.type === "text" && (el.style?.fontSize || 0) > 24
  )

  // 本文要素
  const textElements = sortedElements.filter(
    (el) => el.type === "text" && el !== titleElement
  )

  // 画像要素
  const imageElements = sortedElements.filter((el) => el.type === "image")

  // その他の要素
  const otherElements = sortedElements.filter(
    (el) =>
      el.type !== "text" &&
      el.type !== "image" &&
      el.type !== "group" &&
      el !== titleElement
  )

  // グループ要素
  const groupElements = sortedElements.filter((el) => el.type === "group")

  return `
<div class="slide" data-slide-index="${slideIndex}">
  <div class="slide-content">
    ${titleElement ? renderElement(titleElement, "title") : ""}
    ${textElements.map((el) => renderElement(el, "text")).join("")}
    ${imageElements.map((el) => renderElement(el, "image")).join("")}
    ${otherElements.map((el) => renderElement(el, "other")).join("")}
    ${groupElements.map((el) => renderElement(el, "group")).join("")}
  </div>
</div>
`
}

/**
 * 要素をHTMLにレンダリング
 */
function renderElement(element: SlideElement, context: string): string {
  const positionStyle = element.position
    ? `position: absolute; left: ${element.position.x}px; top: ${element.position.y}px; width: ${element.position.width}px; height: ${element.position.height}px;`
    : ""

  const styleAttr = element.style
    ? `style="${positionStyle} ${buildStyleString(element.style)}"`
    : `style="${positionStyle}"`

  switch (element.type) {
    case "text":
      const tag = context === "title" ? "h1" : "p"
      const className = context === "title" ? "slide-title" : "slide-text"
      return `<${tag} class="${className}" data-element-id="${element.id}" ${styleAttr}>${escapeHtml(element.content || "")}</${tag}>`

    case "image":
      return `<div class="slide-image" data-element-id="${element.id}" ${styleAttr}>
        <img src="${element.imageUrl || "/placeholder.svg"}" alt="Slide image" />
      </div>`

    case "table":
      return `<div class="slide-table" data-element-id="${element.id}" ${styleAttr}>
        <pre>${escapeHtml(element.content || "")}</pre>
      </div>`

    case "group":
      const childrenHTML = element.children
        ?.map((child) => renderElement(child, "other"))
        .join("") || ""
      return `<div class="slide-group" data-element-id="${element.id}" ${styleAttr}>${childrenHTML}</div>`

    default:
      return `<div class="slide-element" data-element-id="${element.id}" data-type="${element.type}" ${styleAttr}></div>`
  }
}

/**
 * スタイルオブジェクトをCSS文字列に変換
 */
function buildStyleString(style: SlideElement["style"]): string {
  if (!style) return ""

  const styles: string[] = []

  if (style.fontSize) {
    styles.push(`font-size: ${style.fontSize}px`)
  }
  if (style.fontFamily) {
    styles.push(`font-family: ${style.fontFamily}`)
  }
  if (style.color) {
    styles.push(`color: ${style.color}`)
  }
  if (style.bold) {
    styles.push("font-weight: bold")
  }
  if (style.italic) {
    styles.push("font-style: italic")
  }
  if (style.alignment) {
    styles.push(`text-align: ${style.alignment}`)
  }

  return styles.join("; ")
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

/**
 * 完全なプレゼンテーションHTMLを生成
 */
function generateFullPresentationHTML(
  slidesHTML: string[],
  title: string
): string {
  return `
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${escapeHtml(title)}</title>
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
    .slide {
      width: 100%;
      max-width: 1920px;
      margin: 0 auto;
      aspect-ratio: 16 / 9;
      background: white;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
      position: relative;
    }
    .slide-content {
      width: 100%;
      height: 100%;
      padding: 60px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      position: relative;
    }
    .slide-title {
      font-size: 3rem;
      font-weight: bold;
      margin-bottom: 2rem;
      line-height: 1.2;
    }
    .slide-text {
      font-size: 1.5rem;
      line-height: 1.8;
      margin-bottom: 1.5rem;
    }
    .slide-image {
      margin: 2rem 0;
    }
    .slide-image img {
      width: 100%;
      height: auto;
      border-radius: 8px;
      max-width: 600px;
    }
    .slide-table {
      margin: 2rem 0;
    }
    .slide-table pre {
      background: rgba(255,255,255,0.1);
      padding: 1rem;
      border-radius: 8px;
      font-size: 1rem;
      white-space: pre-wrap;
    }
    .slide-group {
      position: relative;
    }
    .slide-element {
      background: rgba(255,255,255,0.1);
      border-radius: 4px;
    }
  </style>
</head>
<body>
  <div class="slides-container">
    ${slidesHTML.join("")}
  </div>
</body>
</html>
`
}

