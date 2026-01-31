import express from "express"
import { z } from "zod"
import { getAuthUrl, setAuthToken } from "../config/google-slides.js"
import { fetchPresentation } from "../services/google-slides-parser.js"
import { convertPresentationToHTML, convertSlideToHTML } from "../services/slides-to-html.js"
import { extractSlideElements } from "../services/google-slides-parser.js"
import { reviewPresentation, reviewSlideHTML } from "../services/gemini-reviewer.js"

const router = express.Router()

/**
 * GET /api/google-slides/auth
 * Google認証URLを取得
 */
router.get("/auth", (req, res) => {
  try {
    const authUrl = getAuthUrl()
    res.json({
      success: true,
      data: {
        authUrl,
      },
    })
  } catch (error) {
    console.error("Error generating auth URL:", error)
    res.status(500).json({
      success: false,
      error: "Failed to generate auth URL",
      message: error instanceof Error ? error.message : "Unknown error",
    })
  }
})

/**
 * GET /api/google-slides/callback
 * OAuthコールバック
 */
router.get("/callback", async (req, res) => {
  try {
    const { code } = req.query

    if (!code || typeof code !== "string") {
      return res.status(400).json({
        success: false,
        error: "Authorization code is required",
      })
    }

    await setAuthToken(code)

    res.json({
      success: true,
      message: "Authentication successful. Please save the refresh token to your .env file.",
    })
  } catch (error) {
    console.error("Error in OAuth callback:", error)
    res.status(500).json({
      success: false,
      error: "Authentication failed",
      message: error instanceof Error ? error.message : "Unknown error",
    })
  }
})

/**
 * POST /api/google-slides/import
 * Google SlidesプレゼンテーションをインポートしてHTMLテンプレートを生成
 */
router.post("/import", async (req, res) => {
  try {
    const schema = z.object({
      presentationId: z.string(),
    })

    const { presentationId } = schema.parse(req.body)

    // プレゼンテーションを取得
    const presentation = await fetchPresentation(presentationId)

    if (!presentation.slides) {
      return res.status(400).json({
        success: false,
        error: "No slides found in presentation",
      })
    }

    // HTMLに変換
    const html = convertPresentationToHTML(presentation)

    // 各スライドのHTMLを抽出
    const slidesHTML: string[] = []
    for (let i = 0; i < (presentation.slides?.length || 0); i++) {
      const slide = presentation.slides[i]
      if (slide) {
        const elements = extractSlideElements(slide)
        const slideHTML = convertSlideToHTML(elements, i)
        slidesHTML.push(slideHTML)
      }
    }

    // Geminiでレビュー
    const review = await reviewPresentation(slidesHTML)

    // スロットを生成
    const slots = review.slideReviews.flatMap((slideReview, slideIndex) =>
      slideReview.suggestedSlots.map((slot) => ({
        ...slot,
        slideIndex,
      }))
    )

    // テンプレートをDBに保存
    const { createTemplate } = await import("../services/db/template.service.js")
    const savedTemplate = await createTemplate({
      name: review.title,
      description: review.description,
      thumbnail: presentation.thumbnail || "",
      slideCount: presentation.slides?.length || 0,
      html,
      slots: slots.map((slot) => ({
        slideIndex: slot.slideIndex,
        name: slot.name,
        type: slot.type,
        placeholder: slot.placeholder,
        required: slot.required,
      })),
    })

    res.json({
      success: true,
      data: {
        template: {
          id: savedTemplate.id,
          name: savedTemplate.name,
          description: savedTemplate.description,
          thumbnail: savedTemplate.thumbnail,
          slideCount: savedTemplate.slideCount,
          slots: savedTemplate.slots,
          createdAt: savedTemplate.createdAt,
        },
        html,
        review,
      },
    })
  } catch (error) {
    console.error("Error importing Google Slides:", error)
    res.status(500).json({
      success: false,
      error: "Failed to import Google Slides",
      message: error instanceof Error ? error.message : "Unknown error",
    })
  }
})

/**
 * POST /api/google-slides/parse-url
 * Google Slides URLからプレゼンテーションIDを抽出してインポート
 */
router.post("/parse-url", async (req, res) => {
  try {
    const schema = z.object({
      url: z.string().url(),
    })

    const { url } = schema.parse(req.body)

    // URLからプレゼンテーションIDを抽出
    // https://docs.google.com/presentation/d/{PRESENTATION_ID}/edit
    const match = url.match(/\/presentation\/d\/([a-zA-Z0-9-_]+)/)
    if (!match || !match[1]) {
      return res.status(400).json({
        success: false,
        error: "Invalid Google Slides URL",
      })
    }

    const presentationId = match[1]

    // インポート処理を実行
    const importResponse = await fetchPresentation(presentationId)
    const html = convertPresentationToHTML(importResponse)

    const slidesHTML: string[] = []
    if (importResponse.slides) {
      for (let i = 0; i < importResponse.slides.length; i++) {
        const slide = importResponse.slides[i]
        if (slide) {
          const elements = extractSlideElements(slide)
          const slideHTML = convertSlideToHTML(elements, i)
          slidesHTML.push(slideHTML)
        }
      }
    }

    const review = await reviewPresentation(slidesHTML)

    const slots = review.slideReviews.flatMap((slideReview, slideIndex) =>
      slideReview.suggestedSlots.map((slot) => ({
        ...slot,
        slideIndex,
      }))
    )

    // テンプレートをDBに保存
    const { createTemplate } = await import("../services/db/template.service.js")
    const savedTemplate = await createTemplate({
      name: review.title,
      description: review.description,
      thumbnail: importResponse.thumbnail || "",
      slideCount: importResponse.slides?.length || 0,
      html,
      slots: slots.map((slot) => ({
        slideIndex: slot.slideIndex,
        name: slot.name,
        type: slot.type,
        placeholder: slot.placeholder,
        required: slot.required,
      })),
    })

    res.json({
      success: true,
      data: {
        presentationId,
        template: {
          id: savedTemplate.id,
          name: savedTemplate.name,
          description: savedTemplate.description,
          thumbnail: savedTemplate.thumbnail,
          slideCount: savedTemplate.slideCount,
          slots: savedTemplate.slots,
          createdAt: savedTemplate.createdAt,
        },
        html,
        review,
      },
    })
  } catch (error) {
    console.error("Error parsing Google Slides URL:", error)
    res.status(500).json({
      success: false,
      error: "Failed to parse Google Slides URL",
      message: error instanceof Error ? error.message : "Unknown error",
    })
  }
})

/**
 * POST /api/google-slides/review-slide
 * 単一スライドのHTMLをレビュー
 */
router.post("/review-slide", async (req, res) => {
  try {
    const schema = z.object({
      html: z.string(),
      slideIndex: z.number().int().min(0),
    })

    const { html, slideIndex } = schema.parse(req.body)

    const review = await reviewSlideHTML(html, slideIndex)

    res.json({
      success: true,
      data: review,
    })
  } catch (error) {
    console.error("Error reviewing slide:", error)
    res.status(500).json({
      success: false,
      error: "Failed to review slide",
      message: error instanceof Error ? error.message : "Unknown error",
    })
  }
})

export default router

