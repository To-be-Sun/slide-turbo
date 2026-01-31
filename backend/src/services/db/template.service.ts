import { prisma } from "../../lib/prisma.js"
import type { Template, TemplateSlot } from "../../types.js"

/**
 * テンプレートを取得
 */
export async function getTemplate(id: string): Promise<Template | null> {
  const template = await prisma.template.findUnique({
    where: { id },
    include: {
      slots: {
        orderBy: [{ slideIndex: "asc" }, { createdAt: "asc" }],
      },
    },
  })

  if (!template) return null

  return {
    id: template.id,
    name: template.name,
    description: template.description,
    thumbnail: template.thumbnail,
    slideCount: template.slideCount,
    slots: template.slots.map((slot) => ({
      id: slot.id,
      slideIndex: slot.slideIndex,
      name: slot.name,
      type: slot.type as TemplateSlot["type"],
      placeholder: slot.placeholder,
      required: slot.required,
    })),
    createdAt: template.createdAt,
  }
}

/**
 * テンプレート一覧を取得
 */
export async function getTemplates(): Promise<Template[]> {
  const templates = await prisma.template.findMany({
    include: {
      slots: true,
    },
    orderBy: { createdAt: "desc" },
  })

  return templates.map((template) => ({
    id: template.id,
    name: template.name,
    description: template.description,
    thumbnail: template.thumbnail,
    slideCount: template.slideCount,
    slots: template.slots.map((slot) => ({
      id: slot.id,
      slideIndex: slot.slideIndex,
      name: slot.name,
      type: slot.type as TemplateSlot["type"],
      placeholder: slot.placeholder,
      required: slot.required,
    })),
    createdAt: template.createdAt,
  }))
}

/**
 * テンプレートを作成
 */
export async function createTemplate(data: {
  name: string
  description: string
  thumbnail: string
  slideCount: number
  html?: string
  slots: Array<{
    slideIndex: number
    name: string
    type: TemplateSlot["type"]
    placeholder: string
    required: boolean
  }>
}): Promise<Template> {
  const template = await prisma.template.create({
    data: {
      name: data.name,
      description: data.description,
      thumbnail: data.thumbnail,
      slideCount: data.slideCount,
      html: data.html,
      slots: {
        create: data.slots.map((slot) => ({
          slideIndex: slot.slideIndex,
          name: slot.name,
          type: slot.type,
          placeholder: slot.placeholder,
          required: slot.required,
        })),
      },
    },
    include: {
      slots: {
        orderBy: [{ slideIndex: "asc" }, { createdAt: "asc" }],
      },
    },
  })

  return {
    id: template.id,
    name: template.name,
    description: template.description,
    thumbnail: template.thumbnail,
    slideCount: template.slideCount,
    slots: template.slots.map((slot) => ({
      id: slot.id,
      slideIndex: slot.slideIndex,
      name: slot.name,
      type: slot.type as TemplateSlot["type"],
      placeholder: slot.placeholder,
      required: slot.required,
    })),
    createdAt: template.createdAt,
  }
}

/**
 * テンプレートを更新
 */
export async function updateTemplate(
  id: string,
  data: {
    name?: string
    description?: string
    thumbnail?: string
    slideCount?: number
    html?: string
  }
): Promise<Template> {
  const template = await prisma.template.update({
    where: { id },
    data,
    include: {
      slots: {
        orderBy: [{ slideIndex: "asc" }, { createdAt: "asc" }],
      },
    },
  })

  return {
    id: template.id,
    name: template.name,
    description: template.description,
    thumbnail: template.thumbnail,
    slideCount: template.slideCount,
    slots: template.slots.map((slot) => ({
      id: slot.id,
      slideIndex: slot.slideIndex,
      name: slot.name,
      type: slot.type as TemplateSlot["type"],
      placeholder: slot.placeholder,
      required: slot.required,
    })),
    createdAt: template.createdAt,
  }
}

/**
 * テンプレートを削除
 */
export async function deleteTemplate(id: string): Promise<void> {
  await prisma.template.delete({
    where: { id },
  })
}

