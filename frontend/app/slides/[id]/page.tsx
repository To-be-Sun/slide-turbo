"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft,
  ChevronDown,
  ChevronRight,
  FilePlus,
  Pencil,
  Plus,
  Sparkles,
  Trash2,
} from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { SlideJsonCanvas } from "@/components/slide-json-canvas";
import type { Outline, Page, Slide, SlideVersion } from "@/lib/types";
import {
  getSlide,
  getVersions,
  getPages,
  getOutlines,
  createOutline,
  updateOutline,
  deleteOutline,
  refineOutline,
  addPage,
  deletePage,
  updatePage,
  generateSlideFromOutline,
} from "@/lib/api";

export default function SlideEditorPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();

  // Data
  const [slide, setSlide] = useState<Slide | null>(null);
  const [versions, setVersions] = useState<SlideVersion[]>([]);
  const [currentVersion, setCurrentVersion] = useState<SlideVersion | null>(null);
  const [pages, setPages] = useState<Page[]>([]);
  const [outlines, setOutlines] = useState<Outline[]>([]);
  const [loading, setLoading] = useState(true);

  // UI state
  const [outlinesOpen, setOutlinesOpen] = useState(true);
  const [selectedPage, setSelectedPage] = useState<number>(0);
  const [editingOutline, setEditingOutline] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [editDesc, setEditDesc] = useState("");

  // New outline dialog
  const [newOutlineOpen, setNewOutlineOpen] = useState(false);
  const [newOutlineTitle, setNewOutlineTitle] = useState("");
  const [newOutlineDesc, setNewOutlineDesc] = useState("");

  // AI refine
  const [refineId, setRefineId] = useState<string | null>(null);
  const [refineInstructions, setRefineInstructions] = useState("");
  const [refining, setRefining] = useState(false);

  // Load data
  useEffect(() => {
    async function load() {
      try {
        const s = await getSlide(id);
        setSlide(s);
        const v = await getVersions(id);
        setVersions(v);
        if (v.length > 0) {
          const latest = v[v.length - 1];
          setCurrentVersion(latest);
          const [p, o] = await Promise.all([
            getPages(latest.id),
            getOutlines(latest.id),
          ]);
          setPages(p);
          setOutlines(o);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  // Outline CRUD
  const handleCreateOutline = async () => {
    if (!currentVersion || !newOutlineTitle.trim()) return;
    try {
      const o = await createOutline({
        slide_version_id: currentVersion.id,
        title: newOutlineTitle,
        description: newOutlineDesc,
      });
      setOutlines((prev) => [...prev, o]);
      setNewOutlineOpen(false);
      setNewOutlineTitle("");
      setNewOutlineDesc("");
    } catch (err) {
      console.error(err);
    }
  };

  const handleUpdateOutline = async (outlineId: string) => {
    try {
      const o = await updateOutline(outlineId, {
        title: editTitle,
        description: editDesc,
      });
      setOutlines((prev) => prev.map((x) => (x.id === o.id ? o : x)));
      setEditingOutline(null);
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteOutline = async (outlineId: string) => {
    if (!confirm("この骨子を削除しますか？")) return;
    try {
      await deleteOutline(outlineId);
      setOutlines((prev) => prev.filter((x) => x.id !== outlineId));
    } catch (err) {
      console.error(err);
    }
  };

  const handleRefine = async () => {
    if (!refineId || !refineInstructions.trim()) return;
    setRefining(true);
    try {
      const o = await refineOutline({
        outline_id: refineId,
        instructions: refineInstructions,
      });
      setOutlines((prev) => prev.map((x) => (x.id === o.id ? o : x)));
      setRefineId(null);
      setRefineInstructions("");
    } catch (err) {
      console.error(err);
    } finally {
      setRefining(false);
    }
  };

  const startEdit = (o: Outline) => {
    setEditingOutline(o.id);
    setEditTitle(o.title);
    setEditDesc(o.description);
  };

  const nextPageNum = (): number => {
    if (pages.length === 0) return 1;
    return Math.max(...pages.map((p) => p.page_num)) + 1;
  };

  const getPreviousSlideSummary = (currentPageNum: number): string | undefined => {
    const prev = [...pages]
      .filter((p) => p.page_num < currentPageNum)
      .sort((a, b) => b.page_num - a.page_num)[0];
    if (!prev || typeof prev.contents !== "object" || prev.contents === null) {
      return undefined;
    }

    const c = prev.contents as { html?: string; slide_json?: unknown };
    if (typeof c.html === "string" && c.html.trim()) {
      return `Previous page ${prev.page_num}: HTML slide`;
    }

    const json = c.slide_json as
      | { pageElements?: Array<{ shape?: { text?: { textElements?: Array<{ textRun?: { content?: string } }> } } }> }
      | undefined;
    const firstText = json?.pageElements
      ?.flatMap((e) => e.shape?.text?.textElements ?? [])
      .map((te) => te.textRun?.content ?? "")
      .join("")
      .replace(/\s+/g, " ")
      .trim();
    if (firstText) {
      return `Previous page ${prev.page_num}: ${firstText.slice(0, 120)}`;
    }
    return `Previous page ${prev.page_num}`;
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="animate-pulse text-muted-foreground">Loading...</div>
      </div>
    );
  }

  if (!slide) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-muted-foreground">スライドが見つかりません</p>
      </div>
    );
  }

  return (
    <div className="flex h-screen flex-col">
      {/* ── Top Bar ────────────────────────────── */}
      <header className="flex h-12 items-center gap-3 border-b bg-card px-4">
        <Link href="/">
          <Button variant="ghost" size="icon" className="h-8 w-8">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <h1 className="text-sm font-semibold">{slide.title}</h1>
        {currentVersion && (
          <Badge variant="secondary" className="text-xs">
            v{currentVersion.version_num}
          </Badge>
        )}
      </header>

      {/* ── Main Content ───────────────────────── */}
      <div className="flex flex-1 overflow-hidden">
        {/* ── Left Panel: Outline ─────────────── */}
        <div className="flex w-96 flex-col border-r bg-card">
          <Collapsible open={outlinesOpen} onOpenChange={setOutlinesOpen}>
            <div className="flex w-full items-center gap-2 border-b px-4 py-3 text-sm font-semibold">
              <CollapsibleTrigger asChild>
                <button className="flex items-center gap-2 text-left hover:text-primary transition-colors">
                  {outlinesOpen ? (
                    <ChevronDown className="h-4 w-4" />
                  ) : (
                    <ChevronRight className="h-4 w-4" />
                  )}
                  骨子 ({outlines.length})
                </button>
              </CollapsibleTrigger>
              <Button
                variant="ghost"
                size="icon"
                className="ml-auto h-7 w-7"
                onClick={() => setNewOutlineOpen(true)}
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            <CollapsibleContent>
              <ScrollArea className="max-h-[50vh]">
                <div className="space-y-1 p-2">
                  {outlines.length === 0 ? (
                    <p className="px-2 py-4 text-center text-xs text-muted-foreground">
                      骨子を追加してプレゼンの構成を決めましょう
                    </p>
                  ) : (
                    outlines.map((o) => (
                      <div
                        key={o.id}
                        className="group rounded-lg border bg-background p-3"
                      >
                        {editingOutline === o.id ? (
                          <div className="space-y-2">
                            <Input
                              value={editTitle}
                              onChange={(e) => setEditTitle(e.target.value)}
                              className="h-8 text-sm"
                            />
                            <Textarea
                              value={editDesc}
                              onChange={(e) => setEditDesc(e.target.value)}
                              rows={3}
                              className="text-sm"
                            />
                            <div className="flex gap-1">
                              <Button
                                size="sm"
                                className="h-7 text-xs"
                                onClick={() => handleUpdateOutline(o.id)}
                              >
                                保存
                              </Button>
                              <Button
                                size="sm"
                                variant="ghost"
                                className="h-7 text-xs"
                                onClick={() => setEditingOutline(null)}
                              >
                                キャンセル
                              </Button>
                            </div>
                          </div>
                        ) : (
                          <>
                            <div className="flex items-start justify-between">
                              <h3 className="text-sm font-medium">
                                {o.title}
                              </h3>
                              <div className="flex gap-0.5 opacity-0 transition-opacity group-hover:opacity-100">
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-6 w-6"
                                  onClick={() => {
                                    setRefineId(o.id);
                                  }}
                                >
                                  <Sparkles className="h-3 w-3 text-amber-500" />
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-6 w-6"
                                  onClick={() => startEdit(o)}
                                >
                                  <Pencil className="h-3 w-3" />
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-6 w-6"
                                  onClick={() => handleDeleteOutline(o.id)}
                                >
                                  <Trash2 className="h-3 w-3 text-destructive" />
                                </Button>
                              </div>
                            </div>
                            <p className="mt-1 text-xs text-muted-foreground line-clamp-3">
                              {o.description}
                            </p>
                          </>
                        )}
                      </div>
                    ))
                  )}
                </div>
              </ScrollArea>
            </CollapsibleContent>
          </Collapsible>

          <Separator />

          {/* ── AI Refine Section ──────────────── */}
          {refineId && (
            <div className="border-b p-4">
              <div className="mb-2 flex items-center gap-2 text-sm font-medium">
                <Sparkles className="h-4 w-4 text-amber-500" />
                AI で骨子をブラッシュアップ
              </div>
              <Textarea
                placeholder="例: もっと具体的な数値を入れて / ストーリー性を持たせて"
                value={refineInstructions}
                onChange={(e) => setRefineInstructions(e.target.value)}
                rows={3}
                className="mb-2 text-sm"
              />
              <div className="flex gap-2">
                <Button
                  size="sm"
                  className="gap-1"
                  onClick={handleRefine}
                  disabled={refining || !refineInstructions.trim()}
                >
                  <Sparkles className="h-3 w-3" />
                  {refining ? "生成中..." : "AI で改善"}
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => {
                    setRefineId(null);
                    setRefineInstructions("");
                  }}
                >
                  閉じる
                </Button>
              </div>
            </div>
          )}

          {/* ── Page List (Thumbnails) ────────── */}
          <div className="flex-1 overflow-auto p-3">
            <div className="mb-2 flex items-center justify-between">
              <span className="text-xs font-medium text-muted-foreground">
                ページ ({pages.length})
              </span>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6"
                onClick={async () => {
                  if (!currentVersion) return;
                  const pageNum = nextPageNum();
                  const p = await addPage(currentVersion.id, {
                    page_num: pageNum,
                    contents: { html: "<div class='slide'>新しいスライド</div>" },
                  });
                  setPages((prev) => [...prev, p]);
                }}
              >
                <FilePlus className="h-3.5 w-3.5" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6"
                title="骨子からAIで1枚生成"
                onClick={async () => {
                  if (!currentVersion || outlines.length === 0) return;
                  const pageNum = nextPageNum();
                  const outlineIndex = Math.min(
                    Math.max(pageNum - 1, 0),
                    outlines.length - 1
                  );
                  const targetOutline = outlines[outlineIndex];
                  const output = await generateSlideFromOutline({
                    outline_id: targetOutline.id,
                    slide_object_id: `slide-mvp-${String(pageNum).padStart(3, "0")}`,
                    page_num: pageNum,
                    total_pages: Math.max(outlines.length, pageNum),
                    previous_slide_summary: getPreviousSlideSummary(pageNum),
                  });
                  const p = await addPage(currentVersion.id, {
                    page_num: pageNum,
                    contents: { slide_json: output.slide },
                  });
                  setPages((prev) => [...prev, p]);
                  setSelectedPage(pages.length);
                }}
              >
                <Sparkles className="h-3.5 w-3.5 text-amber-500" />
              </Button>
            </div>
            <div className="space-y-2">
              {pages.map((p, i) => (
                <div
                  key={p.id}
                  role="button"
                  tabIndex={0}
                  className={`w-full rounded-lg border p-2 text-left transition-colors ${
                    selectedPage === i
                      ? "border-primary bg-primary/5"
                      : "hover:border-muted-foreground/30"
                  }`}
                  onClick={() => setSelectedPage(i)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      setSelectedPage(i);
                    }
                  }}
                >
                  <div className="mb-1 flex items-center gap-2">
                    <span className="text-xs font-mono text-muted-foreground">
                      {p.page_num}
                    </span>
                    <span className="truncate text-xs">ページ {p.page_num}</span>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="ml-auto h-5 w-5"
                      onClick={async (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        if (!confirm(`ページ ${p.page_num} を削除しますか？`)) return;
                        await deletePage(p.id);
                        if (currentVersion) {
                          const refreshed = await getPages(currentVersion.id);
                          setPages(refreshed);
                          setSelectedPage((prev) =>
                            Math.min(prev, Math.max(0, refreshed.length - 1))
                          );
                        }
                      }}
                    >
                      <Trash2 className="h-3 w-3 text-destructive" />
                    </Button>
                  </div>
                  <div className="aspect-video rounded bg-muted" />
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ── Right Panel: Slide Preview ──────── */}
        <div className="flex flex-1 flex-col bg-muted/30">
          <div className="flex items-center justify-between border-b bg-card px-4 py-2">
            <span className="text-sm font-medium">
              プレビュー
              {pages[selectedPage] && ` — ページ ${pages[selectedPage].page_num}`}
            </span>
          </div>
          <div className="flex flex-1 items-center justify-center p-8">
            {pages[selectedPage] ? (
              <div className="w-full max-w-4xl">
                <div className="aspect-video w-full rounded-lg border bg-white shadow-lg">
                  {(() => {
                    const contents = pages[selectedPage].contents;
                    const html =
                      typeof contents === "object" && contents !== null
                        ? (contents as { html?: string }).html
                        : undefined;
                    const slideJson =
                      typeof contents === "object" && contents !== null
                        ? (contents as { slide_json?: unknown }).slide_json
                        : undefined;

                    if (html) {
                      return (
                        <div
                          className="flex h-full items-center justify-center p-8 text-black"
                          dangerouslySetInnerHTML={{ __html: html }}
                        />
                      );
                    }

                    if (slideJson) {
                      return <SlideJsonCanvas slide={slideJson} />;
                    }

                    return (
                      <div className="flex h-full items-center justify-center p-8 text-black">
                        コンテンツなし
                      </div>
                    );
                  })()}
                </div>
                <p className="mt-3 text-center text-xs text-muted-foreground">
                  {selectedPage + 1} / {pages.length}
                </p>
              </div>
            ) : (
              <div className="text-center text-muted-foreground">
                <p className="mb-2 text-sm">ページがありません</p>
                <p className="text-xs">左パネルの + からページを追加してください</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ── New Outline Dialog ─────────────────── */}
      <Dialog open={newOutlineOpen} onOpenChange={setNewOutlineOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>骨子を追加</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>タイトル</Label>
              <Input
                placeholder="例: 課題の提示"
                value={newOutlineTitle}
                onChange={(e) => setNewOutlineTitle(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>説明</Label>
              <Textarea
                placeholder="このセクションで伝えたいこと"
                value={newOutlineDesc}
                onChange={(e) => setNewOutlineDesc(e.target.value)}
                rows={4}
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              onClick={handleCreateOutline}
              disabled={!newOutlineTitle.trim() || !newOutlineDesc.trim()}
            >
              追加
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
