"use client"

import type React from "react"

import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"
import type { FilledSlot } from "@/lib/types"
import { CheckCircle2, Circle, AlertCircle } from "lucide-react"

interface SlidePreviewPanelProps {
  slots: FilledSlot[]
  slideCount: number
  activeSlideIndex: number
  selectedSlotId: string | null
  onSlideSelect: (index: number) => void
  onSlotClick: (slotId: string) => void
}

const statusConfig = {
  empty: { icon: Circle, color: "text-muted-foreground", bg: "bg-muted" },
  draft: { icon: AlertCircle, color: "text-yellow-500", bg: "bg-yellow-500/20" },
  filled: { icon: CheckCircle2, color: "text-primary", bg: "bg-primary/20" },
  approved: { icon: CheckCircle2, color: "text-accent", bg: "bg-accent/20" },
}

export function SlidePreviewPanel({
  slots,
  slideCount,
  activeSlideIndex,
  selectedSlotId,
  onSlideSelect,
  onSlotClick,
}: SlidePreviewPanelProps) {
  const getSlideSlots = (index: number) => slots.filter((s) => s.slideIndex === index)

  return (
    <div className="flex h-full flex-col">
      {/* Main preview */}
      <div className="flex flex-1 items-center justify-center bg-muted/30 p-8">
        <div className="aspect-video w-full max-w-2xl rounded-lg border border-border bg-card p-6 shadow-lg">
          <SlideContent
            slots={getSlideSlots(activeSlideIndex)}
            slideIndex={activeSlideIndex}
            selectedSlotId={selectedSlotId}
            onSlotClick={onSlotClick}
          />
        </div>
      </div>

      {/* Slide thumbnails */}
      <div className="border-t border-border p-4">
        <div className="flex gap-2 overflow-x-auto pb-2">
          {Array.from({ length: slideCount }).map((_, index) => {
            const slideSlots = getSlideSlots(index)
            const filledCount = slideSlots.filter((s) => s.status !== "empty").length
            const totalCount = slideSlots.length
            const isComplete = filledCount === totalCount && totalCount > 0

            return (
              <button
                key={index}
                onClick={() => onSlideSelect(index)}
                className={cn(
                  "relative flex-shrink-0 rounded-md border-2 p-1 transition-all",
                  activeSlideIndex === index ? "border-primary bg-primary/10" : "border-border hover:border-primary/50",
                )}
              >
                <div className="aspect-video w-24 rounded bg-card p-2">
                  <div className="text-[8px] font-medium text-muted-foreground">スライド {index + 1}</div>
                  <div className="mt-1 space-y-0.5">
                    {slideSlots.slice(0, 3).map((slot) => (
                      <div
                        key={slot.slotId}
                        className={cn("h-1 rounded-full", slot.status === "empty" ? "bg-muted" : "bg-primary")}
                      />
                    ))}
                  </div>
                </div>
                <Badge
                  variant="secondary"
                  className={cn(
                    "absolute -right-1 -top-1 h-5 min-w-5 px-1 text-[10px]",
                    isComplete ? "bg-accent text-accent-foreground" : "",
                  )}
                >
                  {filledCount}/{totalCount}
                </Badge>
              </button>
            )
          })}
        </div>
      </div>
    </div>
  )
}

function SlideContent({
  slots,
  slideIndex,
  selectedSlotId,
  onSlotClick,
}: {
  slots: FilledSlot[]
  slideIndex: number
  selectedSlotId: string | null
  onSlotClick: (slotId: string) => void
}) {
  if (slots.length === 0) {
    return (
      <div className="flex h-full items-center justify-center text-muted-foreground">スライド {slideIndex + 1}</div>
    )
  }

  const titleSlot = slots.find((s) => s.type === "title")
  const textSlots = slots.filter((s) => s.type === "text")
  const listSlot = slots.find((s) => s.type === "list")

  const SlotWrapper = ({
    slot,
    children,
  }: {
    slot: FilledSlot
    children: React.ReactNode
  }) => {
    const isSelected = selectedSlotId === slot.slotId
    const isEmpty = slot.status === "empty"

    return (
      <button
        onClick={() => onSlotClick(slot.slotId)}
        className={cn(
          "w-full rounded-md border-2 border-dashed p-3 text-left transition-all",
          isEmpty
            ? "border-muted-foreground/30 bg-muted/50 hover:border-primary/50 hover:bg-primary/5"
            : "border-transparent hover:border-primary/30",
          isSelected && "border-primary bg-primary/10 ring-2 ring-primary/20",
          slot.status === "approved" && "border-accent/30 bg-accent/5",
        )}
      >
        {children}
        {isSelected && (
          <Badge className="mt-2" variant="default">
            選択中 - AIに話しかけてください
          </Badge>
        )}
      </button>
    )
  }

  return (
    <div className="flex h-full flex-col gap-3">
      {/* Title */}
      {titleSlot && (
        <SlotWrapper slot={titleSlot}>
          {titleSlot.status === "empty" ? (
            <span className="text-sm text-muted-foreground">[{titleSlot.name}] クリックして編集</span>
          ) : (
            <h2 className="text-xl font-bold">{titleSlot.value}</h2>
          )}
          {titleSlot.status === "approved" && (
            <Badge variant="outline" className="ml-2 text-accent">
              <CheckCircle2 className="mr-1 h-3 w-3" />
              確定
            </Badge>
          )}
        </SlotWrapper>
      )}

      {/* Content */}
      <div className="flex-1 space-y-3">
        {textSlots.map((slot) => (
          <SlotWrapper key={slot.slotId} slot={slot}>
            {slot.status === "empty" ? (
              <span className="text-xs text-muted-foreground">[{slot.name}] クリックして編集</span>
            ) : (
              <p className="text-sm">{slot.value}</p>
            )}
          </SlotWrapper>
        ))}

        {listSlot && (
          <SlotWrapper slot={listSlot}>
            {listSlot.status === "empty" ? (
              <span className="text-xs text-muted-foreground">[{listSlot.name}] クリックして編集</span>
            ) : (
              <ul className="list-inside list-disc text-sm">
                {listSlot.value.split("\n").map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            )}
          </SlotWrapper>
        )}
      </div>
    </div>
  )
}
