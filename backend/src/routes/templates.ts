import express from "express"
import { z } from "zod"
import {
  getTemplates,
  getTemplate,
  createTemplate,
  updateTemplate,
  deleteTemplate,
} from "../services/db/template.service.js"

const router = express.Router()

/**
 * GET /api/templates
 * テンプレート一覧を取得
 */
router.get("/", async (req, res) => {
  try {
    const templates = await getTemplates()
    res.json({
      success: true,
      data: templates,
    })
  } catch (error) {
    console.error("Error fetching templates:", error)
    res.status(500).json({
      success: false,
      error: "Failed to fetch templates",
      message: error instanceof Error ? error.message : "Unknown error",
    })
  }
})

/**
 * GET /api/templates/:id
 * テンプレートを取得
 */
router.get("/:id", async (req, res) => {
  try {
    const { id } = req.params
    const template = await getTemplate(id)

    if (!template) {
      return res.status(404).json({
        success: false,
        error: "Template not found",
      })
    }

    res.json({
      success: true,
      data: template,
    })
  } catch (error) {
    console.error("Error fetching template:", error)
    res.status(500).json({
      success: false,
      error: "Failed to fetch template",
      message: error instanceof Error ? error.message : "Unknown error",
    })
  }
})

/**
 * POST /api/templates
 * テンプレートを作成
 */
router.post("/", async (req, res) => {
  try {
    const schema = z.object({
      name: z.string().min(1),
      description: z.string().default(""),
      thumbnail: z.string().default(""),
      slideCount: z.number().int().min(1),
      html: z.string().optional(),
      slots: z.array(
        z.object({
          slideIndex: z.number().int().min(0),
          name: z.string().min(1),
          type: z.enum(["title", "text", "image", "chart", "list", "icon"]),
          placeholder: z.string().default(""),
          required: z.boolean().default(false),
        })
      ),
    })

    const data = schema.parse(req.body)
    const template = await createTemplate(data)

    res.json({
      success: true,
      data: template,
    })
  } catch (error) {
    console.error("Error creating template:", error)
    if (error instanceof z.ZodError) {
      res.status(400).json({
        success: false,
        error: "Invalid request data",
        details: error.errors,
      })
    } else {
      res.status(500).json({
        success: false,
        error: "Failed to create template",
        message: error instanceof Error ? error.message : "Unknown error",
      })
    }
  }
})

/**
 * PATCH /api/templates/:id
 * テンプレートを更新
 */
router.patch("/:id", async (req, res) => {
  try {
    const { id } = req.params
    const schema = z.object({
      name: z.string().min(1).optional(),
      description: z.string().optional(),
      thumbnail: z.string().optional(),
      slideCount: z.number().int().min(1).optional(),
      html: z.string().optional(),
    })

    const data = schema.parse(req.body)
    const template = await updateTemplate(id, data)

    res.json({
      success: true,
      data: template,
    })
  } catch (error) {
    console.error("Error updating template:", error)
    if (error instanceof z.ZodError) {
      res.status(400).json({
        success: false,
        error: "Invalid request data",
        details: error.errors,
      })
    } else {
      res.status(500).json({
        success: false,
        error: "Failed to update template",
        message: error instanceof Error ? error.message : "Unknown error",
      })
    }
  }
})

/**
 * DELETE /api/templates/:id
 * テンプレートを削除
 */
router.delete("/:id", async (req, res) => {
  try {
    const { id } = req.params
    await deleteTemplate(id)

    res.json({
      success: true,
      message: "Template deleted successfully",
    })
  } catch (error) {
    console.error("Error deleting template:", error)
    res.status(500).json({
      success: false,
      error: "Failed to delete template",
      message: error instanceof Error ? error.message : "Unknown error",
    })
  }
})

export default router

