"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import Link from "next/link"
import { Sidebar } from "@/components/sidebar"
import { Button } from "@/components/ui/button"
import { SlidePreviewPanel } from "@/components/slide-preview-panel"
import { SuggestionBanner } from "@/components/suggestion-banner"
import { ArrowLeft, History, Download, Loader2 } from "lucide-react"
import type { FilledSlot, StorySection, Suggestion, Project, Template } from "@/lib/types"
import { AIChatPanel } from "@/components/ai-chat-panel"
import { getProject, getTemplate, generateSlides } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"

export default function ProjectPage() {
  const params = useParams()
  const router = useRouter()
  const id = params.id as string
  const [project, setProject] = useState<Project | null>(null)
  const [template, setTemplate] = useState<Template | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const { toast } = useToast()

  const [slots, setSlots] = useState<FilledSlot[]>([])
  const [story, setStory] = useState<StorySection[]>([])
  const [suggestions, setSuggestions] = useState<Suggestion[]>([])
  const [activeSlideIndex, setActiveSlideIndex] = useState(0)
  const [selectedSlotId, setSelectedSlotId] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)

  useEffect(() => {
    loadProject()
  }, [id])

  const loadProject = async () => {
    try {
      setIsLoading(true)
      const projectResult = await getProject(id)
      if (projectResult.success && projectResult.data) {
        const projectData = projectResult.data
        setProject(projectData)
        setSlots(projectData.slots)
        setStory(projectData.story)
        setSuggestions(projectData.suggestions)

        // テンプレートも読み込む
        const templateResult = await getTemplate(projectData.templateId)
        if (templateResult.success && templateResult.data) {
          setTemplate(templateResult.data)
        }
      } else {
        toast({
          title: "エラー",
          description: "プロジェクトが見つかりません",
          variant: "destructive",
        })
        router.push("/")
      }
    } catch (error) {
      console.error("Error loading project:", error)
      toast({
        title: "エラー",
        description: "プロジェクトの読み込みに失敗しました",
        variant: "destructive",
      })
      router.push("/")
    } finally {
      setIsLoading(false)
    }
  }

  const slideCount = template?.slideCount || 5

  if (isLoading || !project) {
    return (
      <div className="flex min-h-screen">
        <Sidebar />
        <main className="flex-1 md:ml-64 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </main>
      </div>
    )
  }

  const handleSlotUpdate = (slotId: string, value: string) => {
    setSlots((prev) => prev.map((s) => (s.slotId === slotId ? { ...s, value, status: value ? "filled" : "empty" } : s)))

    // Generate suggestion when slot changes
    const slot = slots.find((s) => s.slotId === slotId)
    if (slot?.linkedStoryId) {
      const newSuggestion: Suggestion = {
        id: `sug-${Date.now()}`,
        type: "story-sync",
        message: `「${slot.name}」が更新されました。関連するストーリーセクションも更新しますか？`,
        sourceSlotId: slotId,
        targetSlotIds: [],
        dismissed: false,
        createdAt: new Date(),
      }
      setSuggestions((prev) => [...prev, newSuggestion])
    }
  }

  const handleSlotApprove = (slotId: string) => {
    setSlots((prev) => prev.map((s) => (s.slotId === slotId ? { ...s, status: "approved" } : s)))
  }

  const handleStoryUpdate = (storyId: string, content: string) => {
    setStory((prev) => prev.map((s) => (s.id === storyId ? { ...s, content } : s)))

    // Find related slots and suggest updates
    const storySection = story.find((s) => s.id === storyId)
    if (storySection) {
      const relatedSlots = slots.filter((s) => s.linkedStoryId === storyId)
      if (relatedSlots.length > 0) {
        const newSuggestion: Suggestion = {
          id: `sug-${Date.now()}`,
          type: "slot-update",
          message: `ストーリー「${storySection.title}」が変更されました。関連スロットの更新を提案します。`,
          targetSlotIds: relatedSlots.map((s) => s.slotId),
          dismissed: false,
          createdAt: new Date(),
        }
        setSuggestions((prev) => [...prev, newSuggestion])
      }
    }
  }

  const handleDismissSuggestion = (suggestionId: string) => {
    setSuggestions((prev) => prev.map((s) => (s.id === suggestionId ? { ...s, dismissed: true } : s)))
  }

  const handleSlotClick = (slotId: string) => {
    setSelectedSlotId(slotId)
  }

  const handleGenerateSlides = async () => {
    if (!project || !template) return

    setIsGenerating(true)
    try {
      const result = await generateSlides({
        templateId: project.templateId,
        slots: slots,
        story: story,
      })

      if (result.success && result.data) {
        toast({
          title: "成功",
          description: "スライドを生成しました",
        })
        // 生成されたHTMLや画像を表示する処理を追加可能
        console.log("Generated slides:", result.data)
      }
    } catch (error) {
      console.error("Error generating slides:", error)
      toast({
        title: "エラー",
        description: error instanceof Error ? error.message : "スライドの生成に失敗しました",
        variant: "destructive",
      })
    } finally {
      setIsGenerating(false)
    }
  }

  const activeSuggestions = suggestions.filter((s) => !s.dismissed)
  const currentSlideSlots = slots.filter((s) => s.slideIndex === activeSlideIndex)

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 md:ml-64">
        <div className="flex h-screen flex-col">
          {/* Header */}
          <header className="border-b border-border px-4 py-4 md:px-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Link href="/" className="text-muted-foreground hover:text-foreground">
                  <ArrowLeft className="h-5 w-5" />
                </Link>
                <div>
                  <h1 className="text-xl font-bold">{project.name}</h1>
                  <p className="text-sm text-muted-foreground">{project.templateName}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleGenerateSlides}
                  disabled={isGenerating}
                >
                  {isGenerating ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      生成中...
                    </>
                  ) : (
                    <>
                      <Download className="mr-2 h-4 w-4" />
                      スライド生成
                    </>
                  )}
                </Button>
                <Button variant="outline" size="sm">
                  <History className="mr-2 h-4 w-4" />
                  バージョン保存
                </Button>
              </div>
            </div>
          </header>

          {/* Suggestions */}
          {activeSuggestions.length > 0 && (
            <SuggestionBanner suggestions={activeSuggestions} onDismiss={handleDismissSuggestion} />
          )}

          {/* Main content */}
          <div className="flex flex-1 overflow-hidden">
            {/* Left: Slide preview */}
            <div className="w-1/2 border-r border-border">
              <SlidePreviewPanel
                slots={slots}
                slideCount={slideCount}
                activeSlideIndex={activeSlideIndex}
                selectedSlotId={selectedSlotId}
                onSlideSelect={setActiveSlideIndex}
                onSlotClick={handleSlotClick}
              />
            </div>

            {/* Right: Editor panels */}
            <div className="flex w-1/2 flex-col">
              <AIChatPanel
                slots={slots}
                story={story}
                activeSlideIndex={activeSlideIndex}
                selectedSlotId={selectedSlotId}
                onSlotUpdate={handleSlotUpdate}
                onStoryUpdate={handleStoryUpdate}
                onSlotApprove={handleSlotApprove}
              />
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
