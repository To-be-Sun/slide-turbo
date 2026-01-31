"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { Sidebar } from "@/components/sidebar"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { PlusCircle, FolderOpen, Clock, CheckCircle2, Circle, Loader2 } from "lucide-react"
import { getProjects } from "@/lib/api"
import type { Project } from "@/lib/types"
import { useToast } from "@/hooks/use-toast"

const statusConfig = {
  draft: { label: "下書き", color: "bg-muted text-muted-foreground", icon: Circle },
  "in-progress": { label: "作成中", color: "bg-primary/20 text-primary", icon: Clock },
  completed: { label: "完了", color: "bg-accent/20 text-accent", icon: CheckCircle2 },
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const { toast } = useToast()

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    try {
      setIsLoading(true)
      const result = await getProjects()
      if (result.success && result.data) {
        setProjects(result.data.map((p: any) => ({
          ...p,
          createdAt: new Date(p.createdAt),
          updatedAt: new Date(p.updatedAt),
        })))
      }
    } catch (error) {
      console.error("Error loading projects:", error)
      toast({
        title: "エラー",
        description: "プロジェクトの読み込みに失敗しました",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const getProgress = (project: Project) => {
    if (project.slots.length === 0) return 0
    const filled = project.slots.filter((s) => s.status !== "empty").length
    return Math.round((filled / project.slots.length) * 100)
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 md:ml-64">
        <div className="container mx-auto max-w-5xl px-4 py-8 md:px-8">
          <div className="mb-8 flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">プロジェクト</h1>
              <p className="mt-2 text-muted-foreground">スライドプロジェクトを管理</p>
            </div>
            <Button asChild>
              <Link href="/projects/new">
                <PlusCircle className="mr-2 h-4 w-4" />
                新規作成
              </Link>
            </Button>
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : projects.length === 0 ? (
            <Card className="border-dashed">
              <CardContent className="flex flex-col items-center justify-center py-16">
                <FolderOpen className="mb-4 h-12 w-12 text-muted-foreground" />
                <h3 className="mb-2 text-lg font-medium">プロジェクトがありません</h3>
                <p className="mb-4 text-sm text-muted-foreground">新しいプロジェクトを作成して始めましょう</p>
                <Button asChild>
                  <Link href="/projects/new">
                    <PlusCircle className="mr-2 h-4 w-4" />
                    新規作成
                  </Link>
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4">
              {projects.map((project) => {
                const status = statusConfig[project.status]
                const StatusIcon = status.icon
                const progress = getProgress(project)

                return (
                  <Link key={project.id} href={`/projects/${project.id}`}>
                    <Card className="transition-colors hover:bg-secondary/50">
                      <CardHeader className="pb-3">
                        <div className="flex items-start justify-between">
                          <div>
                            <CardTitle className="text-lg">{project.name}</CardTitle>
                            <CardDescription className="mt-1">{project.description}</CardDescription>
                          </div>
                          <Badge variant="secondary" className={status.color}>
                            <StatusIcon className="mr-1 h-3 w-3" />
                            {status.label}
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="flex items-center gap-4">
                          <div className="flex-1">
                            <div className="mb-1 flex justify-between text-sm">
                              <span className="text-muted-foreground">スロット完了</span>
                              <span className="font-medium">{progress}%</span>
                            </div>
                            <Progress value={progress} className="h-2" />
                          </div>
                          <div className="text-sm text-muted-foreground">
                            <span className="font-medium text-foreground">{project.templateName}</span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </Link>
                )
              })}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
