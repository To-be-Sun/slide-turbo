"use client"

import { Button } from "@/components/ui/button"
import { X, Sparkles, ArrowRight } from "lucide-react"
import type { Suggestion } from "@/lib/types"

interface SuggestionBannerProps {
  suggestions: Suggestion[]
  onDismiss: (id: string) => void
}

export function SuggestionBanner({ suggestions, onDismiss }: SuggestionBannerProps) {
  const latestSuggestion = suggestions[suggestions.length - 1]

  if (!latestSuggestion) return null

  return (
    <div className="border-b border-primary/20 bg-primary/5 px-4 py-3">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/20">
            <Sparkles className="h-4 w-4 text-primary" />
          </div>
          <div>
            <p className="text-sm font-medium">{latestSuggestion.message}</p>
            {latestSuggestion.type === "slot-update" && (
              <p className="text-xs text-muted-foreground">
                影響を受けるスロット: {latestSuggestion.targetSlotIds?.length || 0}件
              </p>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button size="sm" variant="outline" className="gap-1 bg-transparent">
            適用する
            <ArrowRight className="h-3 w-3" />
          </Button>
          <Button size="icon" variant="ghost" className="h-8 w-8" onClick={() => onDismiss(latestSuggestion.id)}>
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}
