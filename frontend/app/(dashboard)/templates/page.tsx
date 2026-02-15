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
  getTemplate,
  createTemplate,
  importTemplate,
  importTemplatePreview,
  getTemplateThumbnail,
  getTemplateThumbnails,
  deleteTemplate,
  updateTemplate,
} from "@/lib/api";

const DEV_TOKEN = "dev-token-slide-turbo";
function isDevUser(): boolean {
  if (typeof window === "undefined") return false;
  return localStorage.getItem("token") === DEV_TOKEN;
}

function isCanvaUrl(url: string): boolean {
  return /canva\.com/i.test(url);
}

function isGoogleSlidesUrl(url: string): boolean {
  return /docs\.google\.com\/presentation/i.test(url);
}

function TemplateCard({
  template,
  onEdit,
  onDelete,
  onPreview,
}: {
  template: TemplateListItem;
  onEdit: () => void;
  onDelete: () => void;
  onPreview: () => void;
}) {
  const [thumbnailUrl, setThumbnailUrl] = useState<string | null>(null);

  useEffect(() => {
    if (isDevUser()) return;
    let cancelled = false;
    getTemplateThumbnail(template.id)
      .then((res) => {
        if (!cancelled && res.url) setThumbnailUrl(res.url);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [template.id]);

  return (
    <Card
      className="group cursor-pointer transition-colors hover:bg-muted/50"
      onClick={onPreview}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onPreview();
        }
      }}
    >
      <div className="flex aspect-video items-center justify-center overflow-hidden rounded-t-lg bg-muted">
        {thumbnailUrl ? (
          <img
            src={thumbnailUrl}
            alt=""
            className="h-full w-full object-contain"
          />
        ) : (
          <Layers className="h-8 w-8 text-muted-foreground/30" />
        )}
      </div>
      <CardHeader className="flex-row items-start justify-between p-4">
        <div className="min-w-0 flex-1">
          <CardTitle className="truncate text-base">{template.title}</CardTitle>
          <CardDescription className="text-xs">
            作成: {new Date(template.created_at).toLocaleDateString("ja-JP")}
          </CardDescription>
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="h-8 w-8" onClick={(e) => e.stopPropagation()}>
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={onEdit}>
              <Pencil className="mr-2 h-4 w-4" />
              編集
            </DropdownMenuItem>
            <DropdownMenuItem className="text-destructive" onClick={onDelete}>
              <Trash2 className="mr-2 h-4 w-4" />
              削除
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </CardHeader>
    </Card>
  );
}

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
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewData, setPreviewData] = useState<{ title: string; contents: unknown } | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);

  // 編集
  const [editOpen, setEditOpen] = useState(false);
  const [editId, setEditId] = useState("");
  const [editTitle, setEditTitle] = useState("");

  // 全スライドプレビュー
  const [slidesPreviewOpen, setSlidesPreviewOpen] = useState(false);
  const [slidesPreviewTemplateId, setSlidesPreviewTemplateId] = useState<string | null>(null);
  const [slidesPreviewSlides, setSlidesPreviewSlides] = useState<
    Array<{ type: "image"; url: string } | { type: "html"; html: string }>
  >([]);
  const [slidesPreviewTitle, setSlidesPreviewTitle] = useState("");
  const [slidesPreviewLoading, setSlidesPreviewLoading] = useState(false);

  const openSlidesPreview = (templateId: string) => {
    setSlidesPreviewTemplateId(templateId);
    setSlidesPreviewOpen(true);
    setSlidesPreviewSlides([]);
    setSlidesPreviewTitle("");
    setSlidesPreviewLoading(true);
  };

  useEffect(() => {
    getTemplates()
      .then(setTemplates)
      .catch(() => setTemplates([]))
      .finally(() => setLoading(false));
  }, []);

  // プレビューダイアログ用: テンプレート詳細とサムネイルを取得
  useEffect(() => {
    if (!slidesPreviewOpen || !slidesPreviewTemplateId) return;
    let cancelled = false;
    setSlidesPreviewLoading(true);
    Promise.all([
      getTemplate(slidesPreviewTemplateId),
      getTemplateThumbnails(slidesPreviewTemplateId).catch(() => ({ urls: [] })),
    ])
      .then(([template, { urls }]) => {
        if (cancelled) return;
        setSlidesPreviewTitle(template.title);
        if (urls.length > 0) {
          setSlidesPreviewSlides(urls.map((url) => ({ type: "image" as const, url })));
        } else {
          const contents = template.contents as { pages?: Array<{ html?: string }> } | null;
          const pages = contents?.pages;
          if (Array.isArray(pages) && pages.length > 0) {
            setSlidesPreviewSlides(
              pages.map((p) => ({
                type: "html" as const,
                html: typeof p?.html === "string" ? p.html : "<p>（空のスライド）</p>",
              }))
            );
          } else {
            setSlidesPreviewSlides([]);
          }
        }
      })
      .catch(() => {
        if (!cancelled) setSlidesPreviewSlides([]);
      })
      .finally(() => {
        if (!cancelled) setSlidesPreviewLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [slidesPreviewOpen, slidesPreviewTemplateId]);

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

  const handlePreview = async () => {
    if (!importUrl.trim() || isCanvaUrl(importUrl)) return;
    setPreviewLoading(true);
    setPreviewData(null);
    try {
      const data = await importTemplatePreview(importUrl);
      setPreviewData(data);
      setPreviewOpen(true);
    } catch (err) {
      console.error(err);
      alert("プレビューの取得に失敗しました。ログイン状態とURLを確認してください。");
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleImport = async () => {
    if (!importUrl.trim()) return;
    if (isCanvaUrl(importUrl)) {
      alert("Canva のURLは未対応です。Google Slides のURL（https://docs.google.com/presentation/d/...）をご利用ください。");
      return;
    }
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
                {importUrl.trim() && isCanvaUrl(importUrl) && (
                  <p className="text-sm text-amber-600 dark:text-amber-400">
                    Canva のURLは未対応です。Google Slides のURLをご利用ください。
                  </p>
                )}
                {!isGoogleSlidesUrl(importUrl) && importUrl.trim().length > 10 && !isCanvaUrl(importUrl) && (
                  <p className="text-sm text-muted-foreground">
                    対応しているのは Google Slides のURL（docs.google.com/presentation/...）のみです。
                  </p>
                )}
                {isDevUser() && (
                  <p className="text-sm text-muted-foreground">
                    現在は開発モードのため、URLの内容は取得されずプレビュー用の仮データになります。実際のテンプレートを表示するには Google ログインで本番APIをご利用ください。
                  </p>
                )}
              </div>
              <DialogFooter>
                <Button
                  variant="outline"
                  onClick={handlePreview}
                  disabled={!importUrl.trim() || previewLoading || isCanvaUrl(importUrl)}
                >
                  {previewLoading ? "取得中..." : "プレビュー（保存しない）"}
                </Button>
                <Button
                  onClick={handleImport}
                  disabled={!importUrl.trim() || importing}
                >
                  {importing ? "インポート中..." : "インポート"}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          {/* プレビュー結果 */}
          <Dialog open={previewOpen} onOpenChange={setPreviewOpen}>
            <DialogContent className="max-h-[90vh] max-w-3xl">
              <DialogHeader>
                <DialogTitle>インポートで取得される情報</DialogTitle>
                {previewData && (
                  <p className="text-sm text-muted-foreground">
                    タイトル: {previewData.title}
                  </p>
                )}
              </DialogHeader>
              <div className="overflow-auto rounded border bg-muted/30 p-3">
                <pre className="text-xs">
                  {previewData
                    ? JSON.stringify(previewData.contents, null, 2)
                    : ""}
                </pre>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setPreviewOpen(false)}>
                  閉じる
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

      {/* 全スライドプレビュー */}
      <Dialog open={slidesPreviewOpen} onOpenChange={setSlidesPreviewOpen}>
        <DialogContent className="max-h-[90vh] max-w-4xl">
          <DialogHeader>
            <DialogTitle>{slidesPreviewTitle || "スライドプレビュー"}</DialogTitle>
          </DialogHeader>
          <div className="overflow-auto">
            {slidesPreviewLoading ? (
              <div className="flex items-center justify-center py-16 text-muted-foreground">
                読み込み中...
              </div>
            ) : slidesPreviewSlides.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
                <Layers className="mb-3 h-10 w-10 opacity-50" />
                <p>プレビューは利用できません</p>
              </div>
            ) : (
              <div className="flex max-h-[70vh] flex-col gap-4 overflow-y-auto pr-1">
                {slidesPreviewSlides.map((slide, i) => (
                  <div
                    key={i}
                    className="flex aspect-video shrink-0 items-center justify-center overflow-hidden rounded-lg border bg-muted"
                  >
                    {slide.type === "image" ? (
                      <img
                        src={slide.url}
                        alt={`スライド ${i + 1}`}
                        className="h-full w-full object-contain"
                      />
                    ) : (
                      <div
                        className="slide-preview h-full w-full overflow-hidden bg-white p-2 text-left text-black [&_.slide]:min-h-0 [&_.slide-canvas]:relative [&_.slide-canvas]:h-full [&_.slide-canvas]:w-full [&_.slide-canvas]:overflow-hidden [&_.slide-text]:overflow-hidden [&_.slide-text]:break-words [&_.slide-image]:max-w-full [&_.slide-image]:max-h-full [&_img]:max-w-full [&_img]:h-auto [&_p]:my-0"
                        dangerouslySetInnerHTML={{ __html: slide.html }}
                      />
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>

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
            <TemplateCard
              key={t.id}
              template={t}
              onEdit={() => openEdit(t.id, t.title)}
              onDelete={() => handleDelete(t.id)}
              onPreview={() => openSlidesPreview(t.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
