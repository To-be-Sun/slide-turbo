"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { ProjectVersion } from "@/lib/types"
import { RotateCcw, GitBranch, Clock } from "lucide-react"

interface VersionHistoryProps {
  versions: ProjectVersion[]
}

export function VersionHistory({ versions }: VersionHistoryProps) {
  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat("ja-JP", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date)
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">バージョン履歴</h3>
        <Button size="sm" variant="outline" className="gap-2 bg-transparent">
          <GitBranch className="h-3 w-3" />
          現在を保存
        </Button>
      </div>

      <div className="space-y-2">
        {/* Current version */}
        <Card className="border-primary">
          <CardContent className="flex items-center justify-between p-3">
            <div className="flex items-center gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/20">
                <Clock className="h-4 w-4 text-primary" />
              </div>
              <div>
                <p className="text-sm font-medium">現在の状態</p>
                <p className="text-xs text-muted-foreground">自動保存済み</p>
              </div>
            </div>
            <Badge>現在</Badge>
          </CardContent>
        </Card>

        {/* Past versions */}
        {versions.map((version) => (
          <Card key={version.id}>
            <CardContent className="flex items-center justify-between p-3">
              <div className="flex items-center gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted">
                  <GitBranch className="h-4 w-4 text-muted-foreground" />
                </div>
                <div>
                  <p className="text-sm font-medium">{version.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {version.description} • {formatDate(version.createdAt)}
                  </p>
                </div>
              </div>
              <Button size="sm" variant="ghost" className="gap-1">
                <RotateCcw className="h-3 w-3" />
                復元
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {versions.length === 0 && (
        <div className="py-8 text-center text-sm text-muted-foreground">保存されたバージョンはありません</div>
      )}
    </div>
  )
}
