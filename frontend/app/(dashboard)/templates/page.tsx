"use client";

import { useEffect, useState } from "react";
import {
  Import,
  Layers,
  MoreHorizontal,
  Pencil,
  Plus,
  Trash2,
} from "lucide-react";
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
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { TemplateListItem } from "@/lib/types";
import {
  getTemplates,
  createTemplate,
  importTemplate,
  deleteTemplate,
  updateTemplate,
} from "@/lib/api";

export default function TemplatesPage() {
  const [templates, setTemplates] = useState<TemplateListItem[]>([]);
  const [loading, setLoading] = useState(true);

  // 新規作成
  const [createOpen, setCreateOpen] = useState(false);
  const [newTitle, setNewTitle] = useState("");

  // インポート
  const [importOpen, setImportOpen] = useState(false);
  const [importUrl, setImportUrl] = useState("");
  const [importing, setImporting] = useState(false);

  // 編集
  const [editOpen, setEditOpen] = useState(false);
  const [editId, setEditId] = useState("");
  const [editTitle, setEditTitle] = useState("");

  useEffect(() => {
    getTemplates()
      .then(setTemplates)
      .catch(() => setTemplates([]))
      .finally(() => setLoading(false));
  }, []);

  const handleCreate = async () => {
    if (!newTitle.trim()) return;
    try {
      const t = await createTemplate({ title: newTitle, contents: {} });
      setTemplates((prev) => [
        { id: t.id, title: t.title, created_at: t.created_at },
        ...prev,
      ]);
      setCreateOpen(false);
      setNewTitle("");
    } catch (err) {
      console.error(err);
    }
  };

  const handleImport = async () => {
    if (!importUrl.trim()) return;
    setImporting(true);
    try {
      const t = await importTemplate(importUrl);
      setTemplates((prev) => [
        { id: t.id, title: t.title, created_at: t.created_at },
        ...prev,
      ]);
      setImportOpen(false);
      setImportUrl("");
    } catch (err) {
      console.error(err);
    } finally {
      setImporting(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("このテンプレートを削除しますか？")) return;
    try {
      await deleteTemplate(id);
      setTemplates((prev) => prev.filter((t) => t.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  const handleEdit = async () => {
    if (!editTitle.trim()) return;
    try {
      await updateTemplate(editId, { title: editTitle });
      setTemplates((prev) =>
        prev.map((t) =>
          t.id === editId ? { ...t, title: editTitle } : t
        )
      );
      setEditOpen(false);
    } catch (err) {
      console.error(err);
    }
  };

  const openEdit = (id: string, title: string) => {
    setEditId(id);
    setEditTitle(title);
    setEditOpen(true);
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
          <h1 className="text-2xl font-bold">テンプレート</h1>
          <p className="text-sm text-muted-foreground">
            スライドテンプレートの管理・インポート
          </p>
        </div>
        <div className="flex gap-2">
          {/* Import */}
          <Dialog open={importOpen} onOpenChange={setImportOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" className="gap-2">
                <Import className="h-4 w-4" />
                インポート
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Google Slides からインポート</DialogTitle>
              </DialogHeader>
              <div className="space-y-2 py-4">
                <Label>プレゼンテーション URL</Label>
                <Input
                  placeholder="https://docs.google.com/presentation/d/..."
                  value={importUrl}
                  onChange={(e) => setImportUrl(e.target.value)}
                />
              </div>
              <DialogFooter>
                <Button
                  onClick={handleImport}
                  disabled={!importUrl.trim() || importing}
                >
                  {importing ? "インポート中..." : "インポート"}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          {/* Create */}
          <Dialog open={createOpen} onOpenChange={setCreateOpen}>
            <DialogTrigger asChild>
              <Button className="gap-2">
                <Plus className="h-4 w-4" />
                新規作成
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>テンプレートを作成</DialogTitle>
              </DialogHeader>
              <div className="space-y-2 py-4">
                <Label>タイトル</Label>
                <Input
                  placeholder="テンプレート名"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                />
              </div>
              <DialogFooter>
                <Button
                  onClick={handleCreate}
                  disabled={!newTitle.trim()}
                >
                  作成
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Edit Dialog */}
      <Dialog open={editOpen} onOpenChange={setEditOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>テンプレートを編集</DialogTitle>
          </DialogHeader>
          <div className="space-y-2 py-4">
            <Label>タイトル</Label>
            <Input
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
            />
          </div>
          <DialogFooter>
            <Button onClick={handleEdit} disabled={!editTitle.trim()}>
              保存
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Template Grid */}
      {templates.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-lg border border-dashed py-16">
          <Layers className="mb-3 h-10 w-10 text-muted-foreground/50" />
          <p className="mb-1 font-medium text-muted-foreground">
            テンプレートがありません
          </p>
          <p className="mb-4 text-sm text-muted-foreground/70">
            Google Slides からインポートするか、新規作成しましょう
          </p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {templates.map((t) => (
            <Card key={t.id} className="group">
              <div className="flex aspect-video items-center justify-center rounded-t-lg bg-muted">
                <Layers className="h-8 w-8 text-muted-foreground/30" />
              </div>
              <CardHeader className="flex-row items-start justify-between p-4">
                <div className="min-w-0 flex-1">
                  <CardTitle className="truncate text-base">
                    {t.title}
                  </CardTitle>
                  <CardDescription className="text-xs">
                    作成:{" "}
                    {new Date(t.created_at).toLocaleDateString("ja-JP")}
                  </CardDescription>
                </div>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon" className="h-8 w-8">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem
                      onClick={() => openEdit(t.id, t.title)}
                    >
                      <Pencil className="mr-2 h-4 w-4" />
                      編集
                    </DropdownMenuItem>
                    <DropdownMenuItem
                      className="text-destructive"
                      onClick={() => handleDelete(t.id)}
                    >
                      <Trash2 className="mr-2 h-4 w-4" />
                      削除
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </CardHeader>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
