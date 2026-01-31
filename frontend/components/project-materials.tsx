"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import type { ProjectMaterial } from "@/lib/types"
import { Plus, Search, ImageIcon, BarChart3, Type, Grip } from "lucide-react"

interface ProjectMaterialsProps {
  materials: ProjectMaterial[]
}

const typeIcons = {
  icon: ImageIcon,
  image: ImageIcon,
  text: Type,
  chart: BarChart3,
}

export function ProjectMaterials({ materials }: ProjectMaterialsProps) {
  const [search, setSearch] = useState("")

  const filteredMaterials = materials.filter(
    (m) =>
      m.name.toLowerCase().includes(search.toLowerCase()) ||
      m.tags.some((t) => t.toLowerCase().includes(search.toLowerCase())),
  )

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">マテリアル</h3>
        <Button size="sm" className="gap-2">
          <Plus className="h-3 w-3" />
          追加
        </Button>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="マテリアルを検索..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-9"
        />
      </div>

      <div className="grid gap-3">
        {filteredMaterials.map((material) => {
          const TypeIcon = typeIcons[material.type]

          return (
            <Card key={material.id} className="cursor-grab active:cursor-grabbing">
              <CardContent className="flex items-center gap-3 p-3">
                <Grip className="h-4 w-4 text-muted-foreground" />
                <div className="flex h-10 w-10 items-center justify-center rounded-md bg-muted">
                  {material.type === "image" || material.type === "icon" ? (
                    <img
                      src={material.content || "/placeholder.svg"}
                      alt={material.name}
                      className="h-full w-full rounded-md object-cover"
                    />
                  ) : (
                    <TypeIcon className="h-5 w-5 text-muted-foreground" />
                  )}
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium">{material.name}</p>
                  <div className="mt-1 flex gap-1">
                    {material.tags.map((tag) => (
                      <Badge key={tag} variant="secondary" className="text-[10px]">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {filteredMaterials.length === 0 && (
        <div className="py-8 text-center text-sm text-muted-foreground">マテリアルが見つかりません</div>
      )}
    </div>
  )
}
