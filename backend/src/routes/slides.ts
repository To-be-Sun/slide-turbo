import express from "express"
import { z } from "zod"
import { generateHTMLFromTemplate } from "../services/template-to-html.js"
import { renderSlidesFromHTML, renderSingleSlide } from "../services/slide-renderer.js"
import { fillSlotWithAI, replaceSlotInHTML } from "../services/slot-replacer.js"
import { getTemplate } from "../services/db/template.service.js"
import type { GenerateSlideRequest, FillSlotRequest } from "../types.js"

const router = express.Router()

// スライド生成リクエストのバリデーション
const generateSlideSchema = z.object({
  templateId: z.string(),
  slots: z.array(
    z.object({
      slotId: z.string(),
      slideIndex: z.number(),
      name: z.string(),
      type: z.enum(["title", "text", "image", "chart", "list", "icon"]),
      value: z.string(),
      status: z.enum(["empty", "draft", "filled", "approved"]),
      linkedStoryId: z.string().optional(),
    })
  ),
  story: z
    .array(
      z.object({
        id: z.string(),
        title: z.string(),
        content: z.string(),
        slideIndices: z.array(z.number()),
        status: z.enum(["draft", "approved"]),
        order: z.number(),
      })
    )
    .optional(),
})

/**
 * POST /api/slides/generate
 * テンプレートとスロットからスライドを生成
 */
router.post("/generate", async (req, res) => {
  try {
    const body = generateSlideSchema.parse(req.body)

    // データベースからテンプレートを取得
    const template = await getTemplate(body.templateId)
    if (!template) {
      return res.status(404).json({
        success: false,
        error: "Template not found",
      })
    }

    // HTML生成
    const html = await generateHTMLFromTemplate(template, body.slots, body.story)

    // スライドを画像として描画
    const slides = await renderSlidesFromHTML(html)

    res.json({
      success: true,
      data: {
        html,
        slides,
      },
    })
  } catch (error) {
    console.error("Error generating slides:", error)
    if (error instanceof z.ZodError) {
      res.status(400).json({
        success: false,
        error: "Invalid request data",
        details: error.errors,
      })
    } else {
      res.status(500).json({
        success: false,
        error: "Failed to generate slides",
        message: error instanceof Error ? error.message : "Unknown error",
      })
    }
  }
})

/**
 * POST /api/slides/fill-slot
 * AIを使ってスロットを埋める
 */
router.post("/fill-slot", async (req, res) => {
  try {
    const body: FillSlotRequest = req.body

    if (!body.slotId || body.value === undefined) {
      return res.status(400).json({
        success: false,
        error: "slotId and value are required",
      })
    }

    // AIでスロットを埋める
    const filledValue = await fillSlotWithAI(body)

    // HTMLを生成（簡易実装）
    const html = `<div data-slot-id="${body.slotId}">${filledValue}</div>`

    res.json({
      success: true,
      data: {
        value: filledValue,
        html,
      },
    })
  } catch (error) {
    console.error("Error filling slot:", error)
    res.status(500).json({
      success: false,
      error: "Failed to fill slot",
      message: error instanceof Error ? error.message : "Unknown error",
    })
  }
})

/**
 * POST /api/slides/replace-slot
 * HTML内のスロットを置き換え
 */
router.post("/replace-slot", async (req, res) => {
  try {
    const { html, slotId, value, slotType } = req.body

    if (!html || !slotId || !value || !slotType) {
      return res.status(400).json({
        success: false,
        error: "html, slotId, value, and slotType are required",
      })
    }

    const updatedHTML = replaceSlotInHTML(html, slotId, value, slotType)

    res.json({
      success: true,
      data: {
        html: updatedHTML,
      },
    })
  } catch (error) {
    console.error("Error replacing slot:", error)
    res.status(500).json({
      success: false,
      error: "Failed to replace slot",
      message: error instanceof Error ? error.message : "Unknown error",
    })
  }
})

/**
 * GET /api/slides/render/:slideIndex
 * 特定のスライドを画像としてレンダリング
 */
router.get("/render/:slideIndex", async (req, res) => {
  try {
    const slideIndex = parseInt(req.params.slideIndex)
    const { html } = req.query

    if (!html || typeof html !== "string") {
      return res.status(400).json({
        success: false,
        error: "html query parameter is required",
      })
    }

    const imageBase64 = await renderSingleSlide(html, slideIndex)

    res.setHeader("Content-Type", "image/png")
    res.send(Buffer.from(imageBase64, "base64"))
  } catch (error) {
    console.error("Error rendering slide:", error)
    res.status(500).json({
      success: false,
      error: "Failed to render slide",
      message: error instanceof Error ? error.message : "Unknown error",
    })
  }
})

export default router

