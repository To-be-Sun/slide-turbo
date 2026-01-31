import express from "express"
import { z } from "zod"
import { getProjects, getProject, createProject, updateProject, deleteProject } from "../services/db/project.service.js"
import { updateSlot, updateSlots } from "../services/db/slot.service.js"

const router = express.Router()

/**
 * GET /api/projects
 * プロジェクト一覧を取得
 */
router.get("/", async (req, res) => {
  try {
    const projects = await getProjects()
    res.json({
      success: true,
      data: projects,
    })
  } catch (error) {
    console.error("Error fetching projects:", error)
    res.status(500).json({
      success: false,
      error: "Failed to fetch projects",
      message: error instanceof Error ? error.message : "Unknown error",
    })
  }
})

/**
 * GET /api/projects/:id
 * プロジェクトを取得
 */
router.get("/:id", async (req, res) => {
  try {
    const { id } = req.params
    const project = await getProject(id)

    if (!project) {
      return res.status(404).json({
        success: false,
        error: "Project not found",
      })
    }

    res.json({
      success: true,
      data: project,
    })
  } catch (error) {
    console.error("Error fetching project:", error)
    res.status(500).json({
      success: false,
      error: "Failed to fetch project",
      message: error instanceof Error ? error.message : "Unknown error",
    })
  }
})

/**
 * POST /api/projects
 * プロジェクトを作成
 */
router.post("/", async (req, res) => {
  try {
    const schema = z.object({
      name: z.string().min(1),
      description: z.string().optional().default(""),
      templateId: z.string().uuid(),
      templateName: z.string().min(1),
    })

    const data = schema.parse(req.body)
    const project = await createProject(data)

    res.json({
      success: true,
      data: project,
    })
  } catch (error) {
    console.error("Error creating project:", error)
    if (error instanceof z.ZodError) {
      res.status(400).json({
        success: false,
        error: "Invalid request data",
        details: error.errors,
      })
    } else {
      res.status(500).json({
        success: false,
        error: "Failed to create project",
        message: error instanceof Error ? error.message : "Unknown error",
      })
    }
  }
})

/**
 * PATCH /api/projects/:id
 * プロジェクトを更新
 */
router.patch("/:id", async (req, res) => {
  try {
    const { id } = req.params
    const schema = z.object({
      name: z.string().min(1).optional(),
      description: z.string().optional(),
      status: z.enum(["draft", "in-progress", "completed"]).optional(),
    })

    const data = schema.parse(req.body)
    const project = await updateProject(id, data)

    res.json({
      success: true,
      data: project,
    })
  } catch (error) {
    console.error("Error updating project:", error)
    if (error instanceof z.ZodError) {
      res.status(400).json({
        success: false,
        error: "Invalid request data",
        details: error.errors,
      })
    } else {
      res.status(500).json({
        success: false,
        error: "Failed to update project",
        message: error instanceof Error ? error.message : "Unknown error",
      })
    }
  }
})

/**
 * DELETE /api/projects/:id
 * プロジェクトを削除
 */
router.delete("/:id", async (req, res) => {
  try {
    const { id } = req.params
    await deleteProject(id)

    res.json({
      success: true,
      message: "Project deleted successfully",
    })
  } catch (error) {
    console.error("Error deleting project:", error)
    res.status(500).json({
      success: false,
      error: "Failed to delete project",
      message: error instanceof Error ? error.message : "Unknown error",
    })
  }
})

/**
 * PATCH /api/projects/:id/slots/:slotId
 * スロットを更新
 */
router.patch("/:id/slots/:slotId", async (req, res) => {
  try {
    const { id, slotId } = req.params
    const schema = z.object({
      value: z.string().optional(),
      status: z.enum(["empty", "draft", "filled", "approved"]).optional(),
      linkedStoryId: z.string().uuid().nullable().optional(),
    })

    const data = schema.parse(req.body)
    const slot = await updateSlot(id, slotId, data)

    res.json({
      success: true,
      data: slot,
    })
  } catch (error) {
    console.error("Error updating slot:", error)
    if (error instanceof z.ZodError) {
      res.status(400).json({
        success: false,
        error: "Invalid request data",
        details: error.errors,
      })
    } else {
      res.status(500).json({
        success: false,
        error: "Failed to update slot",
        message: error instanceof Error ? error.message : "Unknown error",
      })
    }
  }
})

/**
 * PATCH /api/projects/:id/slots
 * スロットを一括更新
 */
router.patch("/:id/slots", async (req, res) => {
  try {
    const { id } = req.params
    const schema = z.object({
      updates: z.array(
        z.object({
          slotId: z.string().uuid(),
          value: z.string().optional(),
          status: z.enum(["empty", "draft", "filled", "approved"]).optional(),
        })
      ),
    })

    const { updates } = schema.parse(req.body)
    const slots = await updateSlots(id, updates)

    res.json({
      success: true,
      data: slots,
    })
  } catch (error) {
    console.error("Error updating slots:", error)
    if (error instanceof z.ZodError) {
      res.status(400).json({
        success: false,
        error: "Invalid request data",
        details: error.errors,
      })
    } else {
      res.status(500).json({
        success: false,
        error: "Failed to update slots",
        message: error instanceof Error ? error.message : "Unknown error",
      })
    }
  }
})

export default router

