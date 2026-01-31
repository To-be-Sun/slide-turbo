import { prisma } from "../../lib/prisma.js"
import type { FilledSlot } from "../../types.js"

/**
 * スロットを更新
 */
export async function updateSlot(
  projectId: string,
  slotId: string,
  data: {
    value?: string
    status?: FilledSlot["status"]
    linkedStoryId?: string | null
  }
): Promise<FilledSlot> {
  const updateData: any = {}
  if (data.value !== undefined) updateData.value = data.value
  if (data.status) updateData.status = data.status.toUpperCase()
  if (data.linkedStoryId !== undefined) updateData.linkedStoryId = data.linkedStoryId

  const slot = await prisma.filledSlot.update({
    where: {
      id: slotId,
      projectId: projectId,
    },
    data: updateData,
  })

  return {
    slotId: slot.slotId,
    slideIndex: slot.slideIndex,
    name: slot.name,
    type: slot.type as FilledSlot["type"],
    value: slot.value,
    status: slot.status.toLowerCase() as FilledSlot["status"],
    linkedStoryId: slot.linkedStoryId || undefined,
  }
}

/**
 * スロットを一括更新
 */
export async function updateSlots(
  projectId: string,
  updates: Array<{
    slotId: string
    value?: string
    status?: FilledSlot["status"]
  }>
): Promise<FilledSlot[]> {
  const results = await Promise.all(
    updates.map((update) =>
      updateSlot(projectId, update.slotId, {
        value: update.value,
        status: update.status,
      })
    )
  )

  return results
}

