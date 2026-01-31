"use client"

import { useState, useEffect } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { Sidebar } from "@/components/sidebar"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { cn } from "@/lib/utils"
import { ArrowLeft, Check, Layers, Loader2 } from "lucide-react"
import Link from "next/link"
import { getTemplates, createProject } from "@/lib/api"
import type { Template } from "@/lib/types"
import { useToast } from "@/hooks/use-toast"

export default function NewProjectPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [name, setName] = useState("")
  const [description, setDescription] = useState("")
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null)
  const [templates, setTemplates] = useState<Template[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isCreating, setIsCreating] = useState(false)
  const { toast } = useToast()

  // URLパラメータからテンプレートIDを取得
  useEffect(() => {
    const templateId = searchParams.get("template")
    if (templateId) {
      setSelectedTemplate(templateId)
    }
  }, [searchParams])

  // テンプレートを読み込む
  useEffect(() => {
    loadTemplates()
  }, [])

  const loadTemplates = async () => {
    try {
      setIsLoading(true)
      const result = await getTemplates()
      if (result.success && result.data) {
        setTemplates(result.data.map((t: any) => ({
          ...t,
          createdAt: new Date(t.createdAt),
        })))
      }
    } catch (error) {
      console.error("Error loading templates:", error)
      toast({
        title: "エラー",
        description: "テンプレートの読み込みに失敗しました",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreate = async () => {
    if (!name || !selectedTemplate) return

    const template = templates.find((t) => t.id === selectedTemplate)
    if (!template) {
      toast({
        title: "エラー",
        description: "テンプレートが見つかりません",
        variant: "destructive",
      })
      return
    }

    setIsCreating(true)
    try {
      const result = await createProject({
        name,
        description,
        templateId: selectedTemplate,
        templateName: template.name,
      })

      if (result.success && result.data) {
        toast({
          title: "成功",
          description: "プロジェクトを作成しました",
        })
        router.push(`/projects/${result.data.id}`)
      }
    } catch (error) {
      console.error("Error creating project:", error)
      toast({
        title: "エラー",
        description: error instanceof Error ? error.message : "プロジェクトの作成に失敗しました",
        variant: "destructive",
      })
    } finally {
      setIsCreating(false)
    }
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 md:ml-64">
        <div className="container mx-auto max-w-4xl px-4 py-8 md:px-8">
          <div className="mb-8">
            <Link
              href="/"
              className="mb-4 inline-flex items-center text-sm text-muted-foreground hover:text-foreground"
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              プロジェクト一覧に戻る
            </Link>
            <h1 className="text-3xl font-bold">新規プロジェクト</h1>
            <p className="mt-2 text-muted-foreground">テンプレートを選んで新しいプロジェクトを開始</p>
          </div>

          <div className="space-y-8">
            {/* Project info */}
            <Card>
              <CardHeader>
                <CardTitle>プロジェクト情報</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">プロジェクト名</Label>
                  <Input
                    id="name"
                    placeholder="例: 2024年度事業計画"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">説明（任意）</Label>
                  <Textarea
                    id="description"
                    placeholder="プロジェクトの概要を入力"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    rows={3}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Template selection */}
            <Card>
              <CardHeader>
                <CardTitle>テンプレート選択</CardTitle>
                <CardDescription>ベースとなるテンプレートを選択してください</CardDescription>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="flex items-center justify-center py-12">
                    <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                  </div>
                ) : templates.length === 0 ? (
                  <div className="py-8 text-center text-sm text-muted-foreground">
                    テンプレートがありません。まずテンプレートページでテンプレートを作成してください。
                  </div>
                ) : (
                  <div className="grid gap-4 sm:grid-cols-2">
                    {templates.map((template) => (
                    <button
                      key={template.id}
                      onClick={() => setSelectedTemplate(template.id)}
                      className={cn(
                        "relative rounded-lg border-2 p-4 text-left transition-all hover:bg-secondary/50",
                        selectedTemplate === template.id ? "border-primary bg-primary/5" : "border-border",
                      )}
                    >
                      {selectedTemplate === template.id && (
                        <div className="absolute right-3 top-3 flex h-5 w-5 items-center justify-center rounded-full bg-primary">
                          <Check className="h-3 w-3 text-primary-foreground" />
                        </div>
                      )}
                      <div className="mb-3 aspect-video overflow-hidden rounded-md bg-muted">
                        <img
                          src={template.thumbnail || "/placeholder.svg"}
                          alt={template.name}
                          className="h-full w-full object-cover"
                        />
                      </div>
                      <h3 className="font-medium">{template.name}</h3>
                      <p className="mt-1 text-sm text-muted-foreground">{template.description}</p>
                      <div className="mt-2 flex items-center gap-2 text-xs text-muted-foreground">
                        <Layers className="h-3 w-3" />
                        {template.slideCount}スライド・{template.slots.length}スロット
                      </div>
                    </button>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            <div className="flex justify-end gap-3">
              <Button variant="outline" asChild>
                <Link href="/">キャンセル</Link>
              </Button>
              <Button onClick={handleCreate} disabled={!name || !selectedTemplate || isCreating}>
                {isCreating ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    作成中...
                  </>
                ) : (
                  "プロジェクトを作成"
                )}
              </Button>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
