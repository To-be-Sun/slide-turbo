"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { cn } from "@/lib/utils"
import type { ChatMessage, ChatAction, FilledSlot, StorySection } from "@/lib/types"
import {
  Send,
  Sparkles,
  Check,
  Loader2,
  Type,
  ImageIcon,
  List,
  BarChart3,
  BookOpen,
  Layers,
  RefreshCw,
} from "lucide-react"

interface AIChatPanelProps {
  slots: FilledSlot[]
  story: StorySection[]
  activeSlideIndex: number
  selectedSlotId: string | null
  onSlotUpdate: (slotId: string, value: string) => void
  onStoryUpdate: (storyId: string, content: string) => void
  onSlotApprove: (slotId: string) => void
}

const typeIcons = {
  title: Type,
  text: Type,
  image: ImageIcon,
  chart: BarChart3,
  list: List,
  icon: ImageIcon,
}

export function AIChatPanel({
  slots,
  story,
  activeSlideIndex,
  selectedSlotId,
  onSlotUpdate,
  onStoryUpdate,
  onSlotApprove,
}: AIChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "こんにちは！スライド作成をお手伝いします。\n\n左のプレビューでスロット（点線の枠）をクリックするか、「タイトルを考えて」「ストーリーを作って」などと話しかけてください。",
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  // Handle slot selection from preview
  useEffect(() => {
    if (selectedSlotId) {
      const slot = slots.find((s) => s.slotId === selectedSlotId)
      if (slot) {
        const contextMessage: ChatMessage = {
          id: `ctx-${Date.now()}`,
          role: "system",
          content: `「${slot.name}」が選択されました`,
          timestamp: new Date(),
          context: { type: "slot", slotId: slot.slotId, slideIndex: slot.slideIndex },
        }
        setMessages((prev) => [...prev, contextMessage])

        // Auto-generate suggestion for empty slots
        if (slot.status === "empty") {
          generateSlotSuggestion(slot)
        }
      }
    }
  }, [selectedSlotId])

  const generateSlotSuggestion = async (slot: FilledSlot) => {
    setIsLoading(true)

    // Simulate AI thinking
    await new Promise((resolve) => setTimeout(resolve, 1500))

    const suggestions: Record<string, string> = {
      title: "プロジェクト概要と成果報告",
      text: "本プロジェクトでは、ユーザー体験の向上と業務効率化を両立するソリューションを開発しました。",
      list: "• 開発期間：3ヶ月\n• チーム：5名\n• 主要技術：React, Node.js\n• 成果：処理速度40%向上",
    }

    const suggestedValue = suggestions[slot.type] || `${slot.name}の内容をここに入力`

    const aiMessage: ChatMessage = {
      id: `ai-${Date.now()}`,
      role: "assistant",
      content: `「${slot.name}」の提案です：\n\n**${suggestedValue}**\n\nこの内容でよければ「適用」を押してください。変更したい場合は、どのように変えたいか教えてください。`,
      timestamp: new Date(),
      context: { type: "slot", slotId: slot.slotId },
      actions: [
        {
          id: `action-${Date.now()}`,
          type: "fill-slot",
          label: "適用する",
          targetId: slot.slotId,
          value: suggestedValue,
        },
      ],
    }

    setMessages((prev) => [...prev, aiMessage])
    setIsLoading(false)
  }

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: input,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    // Simulate AI response
    await new Promise((resolve) => setTimeout(resolve, 2000))

    const currentSlideSlots = slots.filter((s) => s.slideIndex === activeSlideIndex)
    const emptySlots = currentSlideSlots.filter((s) => s.status === "empty")
    const inputLower = input.toLowerCase()

    let aiResponse: ChatMessage

    if (inputLower.includes("ストーリー") || inputLower.includes("構成") || inputLower.includes("流れ")) {
      // Story generation request
      aiResponse = {
        id: `ai-${Date.now()}`,
        role: "assistant",
        content: `プレゼンテーションのストーリー構成を提案します：\n\n**1. 導入** (スライド1)\n課題提起と目的の明確化\n\n**2. 現状分析** (スライド2)\n現在の問題点と背景\n\n**3. 解決策** (スライド3-4)\n提案するソリューションの詳細\n\n**4. まとめ** (スライド5)\n期待される効果と次のステップ\n\nこの構成でストーリーを作成しますか？`,
        timestamp: new Date(),
        context: { type: "story" },
        actions: [
          {
            id: `action-story-${Date.now()}`,
            type: "update-story",
            label: "ストーリーを作成",
            targetId: "all",
          },
        ],
      }
    } else if (inputLower.includes("全部") || inputLower.includes("まとめて") || inputLower.includes("一括")) {
      // Batch fill request
      const actions: ChatAction[] = emptySlots.map((slot) => ({
        id: `action-${slot.slotId}`,
        type: "fill-slot" as const,
        label: slot.name,
        targetId: slot.slotId,
        value: `AIが生成した「${slot.name}」の内容`,
      }))

      aiResponse = {
        id: `ai-${Date.now()}`,
        role: "assistant",
        content: `スライド${activeSlideIndex + 1}の空きスロット${emptySlots.length}件を一括で埋めました：\n\n${emptySlots.map((s) => `• **${s.name}**`).join("\n")}\n\n内容を確認して、調整が必要な箇所があれば教えてください。`,
        timestamp: new Date(),
        context: { type: "slide", slideIndex: activeSlideIndex },
        actions,
      }

      // Auto-apply all
      emptySlots.forEach((slot) => {
        onSlotUpdate(slot.slotId, `AIが生成した「${slot.name}」の内容`)
      })
    } else if (selectedSlotId) {
      // Response for selected slot
      const slot = slots.find((s) => s.slotId === selectedSlotId)
      if (slot) {
        const generatedContent = `${input}に基づいて生成された内容`
        aiResponse = {
          id: `ai-${Date.now()}`,
          role: "assistant",
          content: `「${slot.name}」を更新しました：\n\n**${generatedContent}**\n\nこれでよろしいですか？`,
          timestamp: new Date(),
          context: { type: "slot", slotId: slot.slotId },
          actions: [
            {
              id: `action-${Date.now()}`,
              type: "fill-slot",
              label: "確定する",
              targetId: slot.slotId,
              value: generatedContent,
            },
          ],
        }
      } else {
        aiResponse = {
          id: `ai-${Date.now()}`,
          role: "assistant",
          content: "スロットが見つかりませんでした。プレビューからスロットを選択してください。",
          timestamp: new Date(),
        }
      }
    } else {
      // General response
      aiResponse = {
        id: `ai-${Date.now()}`,
        role: "assistant",
        content: `了解しました！\n\nスライド${activeSlideIndex + 1}には以下のスロットがあります：\n${currentSlideSlots.map((s) => `• ${s.name} ${s.status === "empty" ? "(未入力)" : "(入力済)"}`).join("\n")}\n\n埋めたいスロットをプレビューでクリックするか、「全部埋めて」と言ってください。`,
        timestamp: new Date(),
        context: { type: "slide", slideIndex: activeSlideIndex },
      }
    }

    setMessages((prev) => [...prev, aiResponse])
    setIsLoading(false)
  }

  const handleAction = (action: ChatAction) => {
    if (action.type === "fill-slot" && action.value) {
      onSlotUpdate(action.targetId, action.value)

      // Mark action as applied
      setMessages((prev) =>
        prev.map((msg) => ({
          ...msg,
          actions: msg.actions?.map((a) => (a.id === action.id ? { ...a, applied: true } : a)),
        })),
      )

      // Add confirmation message
      const slot = slots.find((s) => s.slotId === action.targetId)
      const confirmMessage: ChatMessage = {
        id: `confirm-${Date.now()}`,
        role: "system",
        content: `「${slot?.name || "スロット"}」に適用しました`,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, confirmMessage])
    } else if (action.type === "approve") {
      onSlotApprove(action.targetId)
    }
  }

  const handleQuickAction = (prompt: string) => {
    setInput(prompt)
    inputRef.current?.focus()
  }

  const currentSlideSlots = slots.filter((s) => s.slideIndex === activeSlideIndex)
  const emptyCount = currentSlideSlots.filter((s) => s.status === "empty").length

  return (
    <div className="flex h-full flex-col">
      {/* Header with context */}
      <div className="border-b border-border p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            <h3 className="font-semibold">AI アシスタント</h3>
          </div>
          <Badge variant="outline">
            スライド {activeSlideIndex + 1}: {emptyCount}件未入力
          </Badge>
        </div>

        {/* Quick actions */}
        <div className="mt-3 flex flex-wrap gap-2">
          <Button
            variant="outline"
            size="sm"
            className="h-7 gap-1 bg-transparent text-xs"
            onClick={() => handleQuickAction("このスライドを全部埋めて")}
          >
            <Layers className="h-3 w-3" />
            全スロット埋める
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="h-7 gap-1 bg-transparent text-xs"
            onClick={() => handleQuickAction("ストーリーを考えて")}
          >
            <BookOpen className="h-3 w-3" />
            ストーリー作成
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="h-7 gap-1 bg-transparent text-xs"
            onClick={() => handleQuickAction("全体を見直して改善点を教えて")}
          >
            <RefreshCw className="h-3 w-3" />
            改善提案
          </Button>
        </div>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1" ref={scrollRef}>
        <div className="space-y-4 p-4">
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} slots={slots} onAction={handleAction} />
          ))}

          {isLoading && (
            <div className="flex items-center gap-2 text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span className="text-sm">考え中...</span>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="border-t border-border p-4">
        <form
          onSubmit={(e) => {
            e.preventDefault()
            handleSend()
          }}
          className="flex gap-2"
        >
          <Input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="メッセージを入力... 例: タイトルを考えて"
            disabled={isLoading}
            className="flex-1"
          />
          <Button type="submit" size="icon" disabled={isLoading || !input.trim()}>
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </div>
    </div>
  )
}

function MessageBubble({
  message,
  slots,
  onAction,
}: {
  message: ChatMessage
  slots: FilledSlot[]
  onAction: (action: ChatAction) => void
}) {
  if (message.role === "system") {
    return (
      <div className="flex justify-center">
        <Badge variant="secondary" className="text-xs font-normal">
          {message.content}
        </Badge>
      </div>
    )
  }

  const isUser = message.role === "user"

  return (
    <div className={cn("flex", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn("max-w-[85%] rounded-lg px-4 py-2", isUser ? "bg-primary text-primary-foreground" : "bg-muted")}
      >
        <div className="whitespace-pre-wrap text-sm">{message.content}</div>

        {/* Context badge */}
        {message.context && (
          <div className="mt-2">
            <Badge variant="outline" className="text-xs">
              {message.context.type === "slot" && (
                <>
                  <Type className="mr-1 h-3 w-3" />
                  {slots.find((s) => s.slotId === message.context?.slotId)?.name || "スロット"}
                </>
              )}
              {message.context.type === "slide" && (
                <>
                  <Layers className="mr-1 h-3 w-3" />
                  スライド {(message.context.slideIndex || 0) + 1}
                </>
              )}
              {message.context.type === "story" && (
                <>
                  <BookOpen className="mr-1 h-3 w-3" />
                  ストーリー
                </>
              )}
            </Badge>
          </div>
        )}

        {/* Actions */}
        {message.actions && message.actions.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {message.actions.map((action) => (
              <Button
                key={action.id}
                variant={action.applied ? "secondary" : "default"}
                size="sm"
                className="h-7 gap-1 text-xs"
                onClick={() => onAction(action)}
                disabled={action.applied}
              >
                {action.applied ? (
                  <>
                    <Check className="h-3 w-3" />
                    適用済み
                  </>
                ) : (
                  action.label
                )}
              </Button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
