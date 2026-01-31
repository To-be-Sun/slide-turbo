"use client"

import { useState, useEffect } from "react"
import Image from "next/image"
import Link from "next/link"
import { Sidebar } from "@/components/sidebar"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Plus, Search, MoreVertical, Pencil, Trash2, Upload, Layers, Play, Loader2 } from "lucide-react"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import type { Template } from "@/lib/types"
import { importGoogleSlides, getTemplates } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"

export default function TemplatesPage() {
  const [templates, setTemplates] = useState<Template[]>([])
  const [search, setSearch] = useState("")
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [googleSlidesUrl, setGoogleSlidesUrl] = useState("")
  const [isImporting, setIsImporting] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const { toast } = useToast()

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

  const filteredTemplates = templates.filter(
    (t) =>
      t.name.toLowerCase().includes(search.toLowerCase()) || t.description.toLowerCase().includes(search.toLowerCase()),
  )

  const handleDelete = (id: string) => {
    setTemplates((prev) => prev.filter((t) => t.id !== id))
  }

  const handleImportGoogleSlides = async () => {
    if (!googleSlidesUrl.trim()) {
      toast({
        title: "エラー",
        description: "Google SlidesのURLを入力してください",
        variant: "destructive",
      })
      return
    }

    setIsImporting(true)
    try {
      const result = await importGoogleSlides(googleSlidesUrl)
      
      if (result.success && result.data.template) {
        const newTemplate: Template = {
          ...result.data.template,
          createdAt: new Date(result.data.template.createdAt),
        }
        
        // テンプレート一覧を再読み込み
        await loadTemplates()
        setGoogleSlidesUrl("")
        setIsDialogOpen(false)
        
        toast({
          title: "成功",
          description: `「${newTemplate.name}」をインポートしました`,
        })
      }
    } catch (error) {
      console.error("Error importing Google Slides:", error)
      toast({
        title: "エラー",
        description: error instanceof Error ? error.message : "Google Slidesのインポートに失敗しました",
        variant: "destructive",
      })
    } finally {
      setIsImporting(false)
    }
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 md:ml-64">
        <div className="container mx-auto max-w-5xl px-4 py-8 md:px-8">
          <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-3xl font-bold">テンプレート</h1>
              <p className="mt-2 text-muted-foreground">スライドテンプレートを管理</p>
            </div>
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button className="gap-2">
                  <Plus className="h-4 w-4" />
                  テンプレート追加
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>テンプレートを追加</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label>テンプレート名</Label>
                    <Input placeholder="例: 営業提案書" />
                  </div>
                  <div className="space-y-2">
                    <Label>説明</Label>
                    <Textarea placeholder="テンプレートの説明を入力" />
                  </div>
                  <div className="space-y-2">
                    <Label>Google Slidesから読み込み</Label>
                    <div className="flex gap-2">
                      <Input
                        placeholder="https://docs.google.com/presentation/d/..."
                        className="flex-1"
                        value={googleSlidesUrl}
                        onChange={(e) => setGoogleSlidesUrl(e.target.value)}
                        disabled={isImporting}
                      />
                      <Button
                        variant="outline"
                        className="gap-2 bg-transparent"
                        onClick={handleImportGoogleSlides}
                        disabled={isImporting || !googleSlidesUrl.trim()}
                      >
                        {isImporting ? (
                          <>
                            <Loader2 className="h-4 w-4 animate-spin" />
                            読み込み中...
                          </>
                        ) : (
                          <>
                            <Upload className="h-4 w-4" />
                            読み込み
                          </>
                        )}
                      </Button>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Google SlidesのURLを入力すると、スライド構造とスロットを自動解析します
                    </p>
                  </div>
                  <Button
                    className="w-full"
                    onClick={() => setIsDialogOpen(false)}
                    disabled={isImporting}
                  >
                    閉じる
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>

          {/* Search */}
          <div className="relative mb-6">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="テンプレートを検索..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* Templates grid */}
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : filteredTemplates.length === 0 ? (
            <Card className="border-dashed">
              <div className="flex flex-col items-center justify-center py-16">
                <Layers className="mb-4 h-12 w-12 text-muted-foreground" />
                <h3 className="mb-2 text-lg font-medium">テンプレートがありません</h3>
                <p className="mb-4 text-sm text-muted-foreground">Google Slidesからインポートして始めましょう</p>
              </div>
            </Card>
          ) : (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {filteredTemplates.map((template) => (
              <Card key={template.id} className="overflow-hidden border-border bg-card">
                <div className="aspect-video relative bg-secondary">
                  <Image
                    src={template.thumbnail || "/placeholder.svg"}
                    alt={template.name}
                    fill
                    className="object-cover"
                  />
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="absolute right-2 top-2 bg-background/80 hover:bg-background"
                      >
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem className="gap-2">
                        <Pencil className="h-4 w-4" />
                        編集
                      </DropdownMenuItem>
                      <DropdownMenuItem className="gap-2 text-destructive" onClick={() => handleDelete(template.id)}>
                        <Trash2 className="h-4 w-4" />
                        削除
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
                <div className="p-4">
                  <h3 className="font-semibold">{template.name}</h3>
                  <p className="mt-1 text-sm text-muted-foreground line-clamp-2">{template.description}</p>
                  <div className="mt-3 flex items-center gap-2">
                    <Badge variant="secondary" className="gap-1">
                      <Layers className="h-3 w-3" />
                      {template.slideCount}スライド
                    </Badge>
                    <Badge variant="outline">{template.slots.length}スロット</Badge>
                  </div>
                  <Button asChild variant="outline" size="sm" className="mt-3 w-full gap-2 bg-transparent">
                    <Link href={`/projects/new?template=${template.id}`}>
                      <Play className="h-3 w-3" />
                      このテンプレートで開始
                    </Link>
                  </Button>
                </div>
              </Card>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
