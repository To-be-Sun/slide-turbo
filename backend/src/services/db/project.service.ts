import { prisma } from "../../lib/prisma.js"
import type { Project, FilledSlot, StorySection, ProjectMaterial, ProjectVersion, Suggestion } from "../../types.js"

/**
 * プロジェクトを取得
 */
export async function getProject(id: string): Promise<Project | null> {
  const project = await prisma.project.findUnique({
    where: { id },
    include: {
      slots: {
        orderBy: [{ slideIndex: "asc" }, { createdAt: "asc" }],
      },
      storySections: {
        orderBy: { order: "asc" },
      },
      materials: {
        orderBy: { createdAt: "desc" },
      },
      versions: {
        orderBy: { createdAt: "desc" },
      },
      suggestions: {
        where: { dismissed: false },
        orderBy: { createdAt: "desc" },
      },
    },
  })

  if (!project) return null

  return {
    id: project.id,
    name: project.name,
    description: project.description,
    templateId: project.templateId,
    templateName: project.templateName,
    status: project.status.toLowerCase() as Project["status"],
    slots: project.slots.map((slot) => ({
      slotId: slot.slotId,
      slideIndex: slot.slideIndex,
      name: slot.name,
      type: slot.type as FilledSlot["type"],
      value: slot.value,
      status: slot.status.toLowerCase() as FilledSlot["status"],
      linkedStoryId: slot.linkedStoryId || undefined,
    })),
    story: project.storySections.map((story) => ({
      id: story.id,
      title: story.title,
      content: story.content,
      slideIndices: story.slideIndices,
      status: story.status.toLowerCase() as StorySection["status"],
      order: story.order,
    })),
    materials: project.materials.map((material) => ({
      id: material.id,
      name: material.name,
      type: material.type as ProjectMaterial["type"],
      content: material.content,
      tags: material.tags,
      usedInSlots: [], // TODO: 実装
    })),
    versions: project.versions.map((version) => ({
      id: version.id,
      name: version.name,
      description: version.description,
      slots: [], // TODO: 実装
      story: [], // TODO: 実装
      createdAt: version.createdAt,
    })),
    suggestions: project.suggestions.map((suggestion) => ({
      id: suggestion.id,
      type: suggestion.type.replace("_", "-") as Suggestion["type"],
      message: suggestion.message,
      sourceSlotId: suggestion.sourceSlotId || undefined,
      targetSlotIds: suggestion.targetSlotIds || [],
      suggestedValue: suggestion.suggestedValue || undefined,
      dismissed: suggestion.dismissed,
      createdAt: suggestion.createdAt,
    })),
    createdAt: project.createdAt,
    updatedAt: project.updatedAt,
  }
}

/**
 * プロジェクト一覧を取得
 */
export async function getProjects(): Promise<Project[]> {
  const projects = await prisma.project.findMany({
    include: {
      slots: true,
      _count: {
        select: {
          slots: true,
        },
      },
    },
    orderBy: { updatedAt: "desc" },
  })

  return projects.map((project) => {
    const filledSlots = project.slots.filter((s) => s.status !== "EMPTY").length
    const totalSlots = project._count.slots

    return {
      id: project.id,
      name: project.name,
      description: project.description,
      templateId: project.templateId,
      templateName: project.templateName,
      status: project.status.toLowerCase() as Project["status"],
      slots: project.slots.map((slot) => ({
        slotId: slot.slotId,
        slideIndex: slot.slideIndex,
        name: slot.name,
        type: slot.type as FilledSlot["type"],
        value: slot.value,
        status: slot.status.toLowerCase() as FilledSlot["status"],
        linkedStoryId: slot.linkedStoryId || undefined,
      })),
      story: [],
      materials: [],
      versions: [],
      suggestions: [],
      createdAt: project.createdAt,
      updatedAt: project.updatedAt,
    }
  })
}

/**
 * プロジェクトを作成
 */
export async function createProject(data: {
  name: string
  description: string
  templateId: string
  templateName: string
}): Promise<Project> {
  // テンプレートのスロットを取得
  const template = await prisma.template.findUnique({
    where: { id: data.templateId },
    include: { slots: true },
  })

  if (!template) {
    throw new Error("Template not found")
  }

  // プロジェクトを作成し、初期スロットも作成
  const project = await prisma.project.create({
    data: {
      name: data.name,
      description: data.description,
      templateId: data.templateId,
      templateName: data.templateName,
      status: "DRAFT",
      slots: {
        create: template.slots.map((slot) => ({
          slotId: slot.id,
          slideIndex: slot.slideIndex,
          name: slot.name,
          type: slot.type,
          value: "",
          status: "EMPTY",
        })),
      },
    },
    include: {
      slots: true,
    },
  })

  return getProject(project.id) as Promise<Project>
}

/**
 * プロジェクトを更新
 */
export async function updateProject(
  id: string,
  data: {
    name?: string
    description?: string
    status?: Project["status"]
  }
): Promise<Project> {
  const updateData: any = {}
  if (data.name) updateData.name = data.name
  if (data.description) updateData.description = data.description
  if (data.status) updateData.status = data.status.toUpperCase()

  await prisma.project.update({
    where: { id },
    data: updateData,
  })

  return getProject(id) as Promise<Project>
}

/**
 * プロジェクトを削除
 */
export async function deleteProject(id: string): Promise<void> {
  await prisma.project.delete({
    where: { id },
  })
}

