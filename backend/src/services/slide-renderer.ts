import puppeteer from "puppeteer"
import type { SlideData } from "../types.js"

/**
 * HTMLからスライドを画像として描画
 */
export async function renderSlidesFromHTML(html: string): Promise<SlideData[]> {
  const browser = await puppeteer.launch({
    headless: true,
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
  })

  try {
    const page = await browser.newPage()
    
    // 16:9のアスペクト比で設定
    await page.setViewport({
      width: 1920,
      height: 1080,
      deviceScaleFactor: 2, // 高解像度
    })

    // HTMLを読み込み
    await page.setContent(html, { waitUntil: "networkidle0" })

    // 各スライドを抽出して画像化
    const slides: SlideData[] = []
    const slideWrappers = await page.$$(".slide-wrapper")

    for (let i = 0; i < slideWrappers.length; i++) {
      const slideElement = slideWrappers[i]
      
      // スライドのHTMLを取得
      const slideHTML = await page.evaluate((el) => el.innerHTML, slideElement)
      
      // スライドを画像としてキャプチャ
      const screenshot = await slideElement.screenshot({
        type: "png",
        omitBackground: false,
      })

      // Base64エンコード
      const imageBase64 = screenshot.toString("base64")
      const imageUrl = `data:image/png;base64,${imageBase64}`

      slides.push({
        slideIndex: i,
        html: slideHTML,
        imageUrl,
      })
    }

    return slides
  } finally {
    await browser.close()
  }
}

/**
 * 単一スライドを画像として描画
 */
export async function renderSingleSlide(html: string, slideIndex: number): Promise<string> {
  const browser = await puppeteer.launch({
    headless: true,
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
  })

  try {
    const page = await browser.newPage()
    
    await page.setViewport({
      width: 1920,
      height: 1080,
      deviceScaleFactor: 2,
    })

    await page.setContent(html, { waitUntil: "networkidle0" })

    const slideElement = await page.$(`.slide-wrapper[data-slide="${slideIndex}"]`)
    if (!slideElement) {
      throw new Error(`Slide ${slideIndex} not found`)
    }

    const screenshot = await slideElement.screenshot({
      type: "png",
      omitBackground: false,
    })

    return screenshot.toString("base64")
  } finally {
    await browser.close()
  }
}

/**
 * HTMLをPDFとして出力
 */
export async function renderSlidesToPDF(html: string, outputPath: string): Promise<void> {
  const browser = await puppeteer.launch({
    headless: true,
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
  })

  try {
    const page = await browser.newPage()
    
    await page.setViewport({
      width: 1920,
      height: 1080,
    })

    await page.setContent(html, { waitUntil: "networkidle0" })

    await page.pdf({
      path: outputPath,
      format: "A4",
      landscape: true,
      printBackground: true,
    })
  } finally {
    await browser.close()
  }
}

