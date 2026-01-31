import { getGoogleSlidesClient } from "../config/google-slides.js"
import type { slides_v1 } from "googleapis"

/**
 * Google SlidesのプレゼンテーションIDからスライドデータを取得
 */
export async function fetchPresentation(presentationId: string): Promise<slides_v1.Schema$Presentation> {
  const slides = getGoogleSlidesClient()
  
  try {
    const presentation = await slides.presentations.get({
      presentationId,
    })
    
    if (!presentation.data) {
      throw new Error("Presentation data is null")
    }
    
    return presentation.data
  } catch (error) {
    console.error("Error fetching presentation:", error)
    throw new Error(`Failed to fetch presentation: ${error instanceof Error ? error.message : "Unknown error"}`)
  }
}

/**
 * スライドオブジェクトから詳細な構造を抽出
 */
export interface SlideElement {
  id: string
  type: "text" | "image" | "shape" | "table" | "video" | "line" | "group"
  content?: string
  position?: {
    x: number
    y: number
    width: number
    height: number
  }
  style?: {
    fontSize?: number
    fontFamily?: string
    color?: string
    bold?: boolean
    italic?: boolean
    alignment?: string
  }
  imageUrl?: string
  children?: SlideElement[]
}

/**
 * スライドページから要素を抽出
 */
export function extractSlideElements(
  page: slides_v1.Schema$Page
): SlideElement[] {
  const elements: SlideElement[] = []

  if (!page.pageElements) {
    return elements
  }

  for (const element of page.pageElements) {
    const extracted = extractElement(element)
    if (extracted) {
      elements.push(extracted)
    }
  }

  return elements
}

/**
 * 単一要素を抽出
 */
function extractElement(
  element: slides_v1.Schema$PageElement
): SlideElement | null {
  if (!element.objectId) {
    return null
  }

  const baseElement: SlideElement = {
    id: element.objectId,
    type: "shape",
    position: element.transform
      ? {
          x: (element.transform.translateX?.magnitude || 0) / 9525, // EMU to pixels (1 EMU = 1/9525 cm)
          y: (element.transform.translateY?.magnitude || 0) / 9525,
          width: (element.transform.width?.magnitude || 0) / 9525,
          height: (element.transform.height?.magnitude || 0) / 9525,
        }
      : undefined,
  }

  // テキスト要素
  if (element.shape?.shapeType === "TEXT_BOX" || element.shape?.text) {
    const textContent = extractTextContent(element.shape.text)
    return {
      ...baseElement,
      type: "text",
      content: textContent.text,
      style: textContent.style,
    }
  }

  // 画像要素
  if (element.image) {
    return {
      ...baseElement,
      type: "image",
      imageUrl: element.image.contentUrl || element.image.sourceUrl || undefined,
    }
  }

  // 図形要素
  if (element.shape) {
    const shapeType = element.shape.shapeType
    if (shapeType && shapeType !== "TEXT_BOX") {
      return {
        ...baseElement,
        type: "shape",
        content: shapeType,
      }
    }
  }

  // テーブル要素
  if (element.table) {
    return {
      ...baseElement,
      type: "table",
      content: extractTableContent(element.table),
    }
  }

  // グループ要素
  if (element.elementGroup) {
    const children = element.elementGroup.children
      ?.map((child) => extractElement(child))
      .filter((e): e is SlideElement => e !== null) || []

    return {
      ...baseElement,
      type: "group",
      children,
    }
  }

  return baseElement
}

/**
 * テキストコンテンツを抽出
 */
function extractTextContent(
  textElement?: slides_v1.Schema$TextContent
): { text: string; style?: SlideElement["style"] } {
  if (!textElement?.textElements) {
    return { text: "" }
  }

  let fullText = ""
  let style: SlideElement["style"] | undefined

  for (const textEl of textElement.textElements) {
    if (textEl.textRun) {
      fullText += textEl.textRun.content || ""
      
      if (textEl.textRun.textStyle) {
        const ts = textEl.textRun.textStyle
        style = {
          fontSize: ts.fontSize?.magnitude ? ts.fontSize.magnitude / 100 : undefined, // ポイントからピクセルに変換
          fontFamily: ts.fontFamily || undefined,
          color: ts.foregroundColor?.opaqueColor?.rgbColor
            ? rgbToHex(ts.foregroundColor.opaqueColor.rgbColor)
            : undefined,
          bold: ts.bold || undefined,
          italic: ts.italic || undefined,
        }
      }
    }
  }

  return { text: fullText.trim(), style }
}

/**
 * テーブルコンテンツを抽出
 */
function extractTableContent(table: slides_v1.Schema$Table): string {
  if (!table.tableRows) {
    return ""
  }

  const rows = table.tableRows.map((row) => {
    if (!row.tableCells) return ""
    return row.tableCells
      .map((cell) => {
        const text = extractTextContent(cell.text?.textContent).text
        return text || ""
      })
      .join(" | ")
  })

  return rows.join("\n")
}

/**
 * RGBカラーをHEXに変換
 */
function rgbToHex(
  rgb: slides_v1.Schema$RgbColor | undefined
): string | undefined {
  if (!rgb) return undefined

  const r = Math.round((rgb.red || 0) * 255)
  const g = Math.round((rgb.green || 0) * 255)
  const b = Math.round((rgb.blue || 0) * 255)

  return `#${[r, g, b].map((x) => x.toString(16).padStart(2, "0")).join("")}`
}
