"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Plus, Trash2, Presentation } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { SlideListItem, TemplateListItem } from "@/lib/types";
import {
  getSlides,
  getTemplates,
  createSlide,
  deleteSlide,
} from "@/lib/api";

export default function DashboardPage() {
  const router = useRouter();
  const [slides, setSlides] = useState<SlideListItem[]>([]);
  const [templates, setTemplates] = useState<TemplateListItem[]>([]);
  const [loading, setLoading] = useState(true);

  // 新規作成ダイアログ
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newTemplateId, setNewTemplateId] = useState<string>("");
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    Promise.all([
      getSlides().catch(() => [] as SlideListItem[]),
      getTemplates().catch(() => [] as TemplateListItem[]),
    ])
      .then(([s, t]) => {
        setSlides(s);
        setTemplates(t);
      })
      .finally(() => setLoading(false));
  }, []);

  const handleCreate = async () => {
    if (!newTitle.trim()) return;
    setCreating(true);
    try {
      const slide = await createSlide({
        title: newTitle,
        template_id: newTemplateId || undefined,
      });
      setDialogOpen(false);
      setNewTitle("");
      setNewTemplateId("");
      router.push(`/slides/${slide.id}`);
    } catch (err) {
      console.error(err);
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("このスライドを削除しますか？")) return;
    try {
      await deleteSlide(id);
      setSlides((prev) => prev.filter((s) => s.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="animate-pulse text-muted-foreground">Loading...</div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">スライド</h1>
          <p className="text-sm text-muted-foreground">
            プレゼンテーションの作成・管理
          </p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button className="gap-2">
              <Plus className="h-4 w-4" />
              新規作成
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>新しいスライドを作成</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label>タイトル</Label>
                <Input
                  placeholder="プレゼンテーションのタイトル"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label>テンプレート (任意)</Label>
                <Select
                  value={newTemplateId}
                  onValueChange={(v) =>
                    setNewTemplateId(v === "__none__" ? "" : v)
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="テンプレートなし" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="__none__">テンプレートなし</SelectItem>
                    {templates.map((t) => (
                      <SelectItem key={t.id} value={t.id}>
                        {t.title}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button
                onClick={handleCreate}
                disabled={!newTitle.trim() || creating}
              >
                {creating ? "作成中..." : "作成"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Slide Grid */}
      {slides.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-lg border border-dashed py-16">
          <Presentation className="mb-3 h-10 w-10 text-muted-foreground/50" />
          <p className="mb-1 font-medium text-muted-foreground">
            スライドがありません
          </p>
          <p className="mb-4 text-sm text-muted-foreground/70">
            「新規作成」からプレゼンテーションを始めましょう
          </p>
          <Button
            variant="outline"
            className="gap-2"
            onClick={() => setDialogOpen(true)}
          >
            <Plus className="h-4 w-4" />
            作成する
          </Button>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {slides.map((slide) => (
            <Card
              key={slide.id}
              className="group cursor-pointer transition-colors hover:border-primary/50"
              onClick={() => router.push(`/slides/${slide.id}`)}
            >
              {/* Thumbnail */}
              <div className="relative aspect-video w-full overflow-hidden rounded-t-lg bg-muted">
                {slide.images[0] ? (
                  <img
                    src={slide.images[0]}
                    alt={slide.title}
                    className="h-full w-full object-cover"
                  />
                ) : (
                  <div className="flex h-full items-center justify-center">
                    <Presentation className="h-8 w-8 text-muted-foreground/30" />
                  </div>
                )}
                <Button
                  variant="destructive"
                  size="icon"
                  className="absolute right-2 top-2 h-7 w-7 opacity-0 transition-opacity group-hover:opacity-100"
                  onClick={(e) => handleDelete(slide.id, e)}
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </Button>
              </div>
              <CardHeader className="p-4">
                <CardTitle className="text-base">{slide.title}</CardTitle>
                <CardDescription className="text-xs">
                  更新:{" "}
                  {new Date(slide.updated_at).toLocaleDateString("ja-JP")}
                </CardDescription>
              </CardHeader>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
