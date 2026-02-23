// ============================================
// Slide Turbo — API クライアント
// Backend /api/v1 へのリクエストを管理
// ============================================

import type {
  Outline,
  Page,
  Slide,
  SlideListItem,
  SlideOutput,
  SlideVersion,
  Template,
  TemplateListItem,
  TokenResponse,
  User,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001";
const DEV_TOKEN = "dev-token-slide-turbo";

// ── Dev Mode Helper ─────────────────────────

function isDevToken(): boolean {
  if (typeof window === "undefined") return false;
  return localStorage.getItem("token") === DEV_TOKEN;
}

// ── Helper ───────────────────────────────────

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `API error: ${res.status}`);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

// ── Auth ─────────────────────────────────────

export function getGoogleAuthUrl(): string {
  // 常にバックエンド経由で Google へリダイレクト（.env はバックエンドで一元管理）
  return `${API_BASE}/api/v1/users/auth/google`;
}

export async function googleCallback(code: string): Promise<TokenResponse> {
  return request<TokenResponse>("/api/v1/users/auth/google/callback", {
    method: "POST",
    body: JSON.stringify({ code }),
  });
}

export async function getMe(): Promise<User> {
  if (isDevToken()) {
    return { id: "dev-user-001", email: "dev@slide-turbo.local", name: "Dev User", icon: null, created_at: new Date().toISOString() };
  }
  return request<User>("/api/v1/users/me");
}

// ── Dev Mode In-Memory Store (+ localStorage 永続化) ─────

const DEV_STORE_KEY = "slide-turbo-dev-store";

const devStore = {
  slides: [] as Slide[],
  templates: [] as Template[],
  outlines: [] as Outline[],
  versions: [] as SlideVersion[],
  pages: [] as Page[],
};

let _devStoreLoaded = false;

function loadDevStore(): void {
  if (typeof window === "undefined" || _devStoreLoaded) return;
  try {
    const raw = localStorage.getItem(DEV_STORE_KEY);
    if (raw) {
      const data = JSON.parse(raw) as {
        slides?: Slide[];
        templates?: Template[];
        versions?: SlideVersion[];
        pages?: Page[];
        outlines?: Outline[];
      };
      if (Array.isArray(data.slides)) devStore.slides = data.slides;
      if (Array.isArray(data.templates)) devStore.templates = data.templates;
      if (Array.isArray(data.versions)) devStore.versions = data.versions;
      if (Array.isArray(data.pages)) devStore.pages = data.pages;
      if (Array.isArray(data.outlines)) devStore.outlines = data.outlines;
    }
  } catch {
    // ignore
  }
  _devStoreLoaded = true;
}

function saveDevStore(): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(
      DEV_STORE_KEY,
      JSON.stringify({
        slides: devStore.slides,
        templates: devStore.templates,
        versions: devStore.versions,
        pages: devStore.pages,
        outlines: devStore.outlines,
      })
    );
  } catch {
    // ignore
  }
}

function uid(): string {
  return `dev-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

const now = () => new Date().toISOString();

// ── Templates ────────────────────────────────

export async function getTemplates(): Promise<TemplateListItem[]> {
  // 実際のAPIを呼び出す（開発モードでもバックエンドから取得）
  // if (isDevToken()) {
  //   loadDevStore();
  //   return devStore.templates.map((t) => ({ id: t.id, title: t.title, created_at: t.created_at }));
  // }
  return request<TemplateListItem[]>("/api/v1/templates");
}

export async function getTemplate(id: string): Promise<Template> {
  // 実際のAPIを呼び出す（開発モードでもバックエンドから取得）
  // if (isDevToken()) {
  //   loadDevStore();
  //   const t = devStore.templates.find((t) => t.id === id);
  //   if (t) return t;
  //   throw new Error("Template not found");
  // }
  return request<Template>(`/api/v1/templates/${id}`);
}

/** テンプレート 1 ページ目のサムネイル URL（Google Slides インポートのみ） */
export async function getTemplateThumbnail(
  templateId: string
): Promise<{ url: string }> {
  return request<{ url: string }>(`/api/v1/templates/${templateId}/thumbnail`);
}

/** テンプレート全ページのサムネイル URL（Google Slides インポートのみ） */
export async function getTemplateThumbnails(
  templateId: string
): Promise<{ urls: string[] }> {
  return request<{ urls: string[] }>(`/api/v1/templates/${templateId}/thumbnails`);
}

export async function createTemplate(data: {
  title: string;
  contents: unknown;
}): Promise<Template> {
  // 実際のAPIを呼び出す（開発モードでもバックエンドで作成）
  // if (isDevToken()) {
  //   loadDevStore();
  //   const t: Template = { id: uid(), owner_id: "dev-user-001", title: data.title, contents: data.contents, created_at: now(), updated_at: now() };
  //   devStore.templates.push(t);
  //   saveDevStore();
  //   return t;
  // }
  return request<Template>("/api/v1/templates", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/** 開発モード用: elements から表示用 HTML を生成（バックエンドと同じ形式） */
function elementsToHtml(elements: { type?: string; text?: string; sourceUrl?: string }[]): string {
  const parts: string[] = [];
  for (const el of elements) {
    if (el.type === "shape" && el.text?.trim()) {
      parts.push(`<p>${el.text.trim().replace(/</g, "&lt;").replace(/>/g, "&gt;")}</p>`);
    } else if (el.type === "image" && el.sourceUrl) {
      parts.push(`<img src="${el.sourceUrl.replace(/"/g, "&quot;")}" alt="" class="max-w-full h-auto" />`);
    }
  }
  if (parts.length === 0) return "<div class='slide'><p class='text-muted-foreground'>（空のスライド）</p></div>";
  return "<div class='slide'>" + parts.join("") + "</div>";
}

/** 開発モードでテンプレートインポート時に作る仮のスライド枚数（複数ページをシミュレート） */
const DEV_TEMPLATE_PLACEHOLDER_PAGE_COUNT = 10;

export async function importTemplatePreview(
  presentationUrl: string
): Promise<{ title: string; contents: unknown }> {
  return request<{ title: string; contents: unknown }>(
    "/api/v1/templates/import-preview",
    {
      method: "POST",
      body: JSON.stringify({ presentation_url: presentationUrl }),
    }
  );
}

export async function importTemplate(
  presentationUrl: string
): Promise<Template> {
  // 実際のAPIを呼び出す（開発モードでもバックエンドでインポート）
  // if (isDevToken()) {
  //   loadDevStore();
  //   const label = presentationUrl.length > 30 ? presentationUrl.slice(-25) : presentationUrl;
  //   const pages: { pageNum: number; elements: { type: "shape"; text: string }[]; html: string }[] = [];
  //   for (let i = 1; i <= DEV_TEMPLATE_PLACEHOLDER_PAGE_COUNT; i++) {
  //     const text = i === 1 ? `インポート: ${label} (1/${DEV_TEMPLATE_PLACEHOLDER_PAGE_COUNT})` : `スライド ${i}`;
  //     const elements = [{ type: "shape" as const, text }];
  //     pages.push({ pageNum: i, elements, html: elementsToHtml(elements) });
  //   }
  //   const contents = { pages };
  //   const t: Template = { id: uid(), owner_id: "dev-user-001", title: `Imported: ${label}`, contents, created_at: now(), updated_at: now() };
  //   devStore.templates.push(t);
  //   saveDevStore();
  //   return t;
  // }
  return request<Template>("/api/v1/templates/import", {
    method: "POST",
    body: JSON.stringify({ presentation_url: presentationUrl }),
  });
}

export async function updateTemplate(
  id: string,
  data: { title?: string; contents?: unknown }
): Promise<Template> {
  // 実際のAPIを呼び出す（開発モードでもバックエンドで更新）
  // if (isDevToken()) {
  //   loadDevStore();
  //   const idx = devStore.templates.findIndex((t) => t.id === id);
  //   if (idx >= 0) {
  //     if (data.title) devStore.templates[idx].title = data.title;
  //     if (data.contents !== undefined) devStore.templates[idx].contents = data.contents;
  //     devStore.templates[idx].updated_at = now();
  //     saveDevStore();
  //     return devStore.templates[idx];
  //   }
  //   throw new Error("Template not found");
  // }
  return request<Template>(`/api/v1/templates/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function deleteTemplate(id: string): Promise<void> {
  // 実際のAPIを呼び出す（開発モードでもバックエンドで削除）
  // if (isDevToken()) {
  //   loadDevStore();
  //   devStore.templates = devStore.templates.filter((t) => t.id !== id);
  //   saveDevStore();
  //   return;
  // }
  return request<void>(`/api/v1/templates/${id}`, { method: "DELETE" });
}

// ── Slides ───────────────────────────────────

export async function getSlides(): Promise<SlideListItem[]> {
  // 実際のAPIを呼び出す（開発モードでもバックエンドから取得）
  // if (isDevToken()) {
  //   loadDevStore();
  //   return devStore.slides.map((s) => ({ id: s.id, title: s.title, template_id: s.template_id, images: s.images, updated_at: s.updated_at }));
  // }
  return request<SlideListItem[]>("/api/v1/slides");
}

export async function getSlide(id: string): Promise<Slide> {
  // 実際のAPIを呼び出す（開発モードでもバックエンドから取得）
  // if (isDevToken()) {
  //   loadDevStore();
  //   const s = devStore.slides.find((s) => s.id === id);
  //   if (s) return s;
  //   throw new Error("Slide not found");
  // }
  return request<Slide>(`/api/v1/slides/${id}`);
}

export async function createSlide(data: {
  title: string;
  template_id?: string;
}): Promise<Slide> {
  // 実際のAPIを呼び出す（開発モードでもバックエンドで作成）
  // if (isDevToken()) {
  //   loadDevStore();
  //   const s: Slide = { id: uid(), owner_id: "dev-user-001", template_id: data.template_id || null, title: data.title, images: [], created_at: now(), updated_at: now() };
  //   devStore.slides.push(s);
  //   const v: SlideVersion = { id: uid(), slide_id: s.id, version_num: 1, created_at: now() };
  //   devStore.versions.push(v);
  //   // テンプレートのページはコピーせず、1ページのプレースホルダーのみ追加
  //   const placeholderContents = data.template_id
  //     ? { html: "<div class='slide'><p class='text-muted-foreground'>新しいスライド。左パネルの + からページを追加してください。</p></div>", elements: [] }
  //     : { html: "<div class='slide'><p class='text-muted-foreground'>新しいスライド</p></div>", elements: [] };
  //   devStore.pages.push({ id: uid(), slide_version_id: v.id, page_num: 1, contents: placeholderContents, created_at: now(), updated_at: now() });
  //   saveDevStore();
  //   return s;
  // }
  return request<Slide>("/api/v1/slides", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateSlide(
  id: string,
  data: { title?: string }
): Promise<Slide> {
  // 実際のAPIを呼び出す（開発モードでもバックエンドで更新）
  // if (isDevToken()) {
  //   loadDevStore();
  //   const idx = devStore.slides.findIndex((s) => s.id === id);
  //   if (idx >= 0) {
  //     if (data.title) devStore.slides[idx].title = data.title;
  //     devStore.slides[idx].updated_at = now();
  //     saveDevStore();
  //     return devStore.slides[idx];
  //   }
  //   throw new Error("Slide not found");
  // }
  return request<Slide>(`/api/v1/slides/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function deleteSlide(id: string): Promise<void> {
  // 実際のAPIを呼び出す（開発モードでもバックエンドで削除）
  // if (isDevToken()) {
  //   loadDevStore();
  //   devStore.slides = devStore.slides.filter((s) => s.id !== id);
  //   devStore.versions = devStore.versions.filter((v) => v.slide_id !== id);
  //   devStore.pages = devStore.pages.filter((p) =>
  //     devStore.versions.some((v) => v.id === p.slide_version_id)
  //   );
  //   devStore.outlines = devStore.outlines.filter((o) =>
  //     devStore.versions.some((v) => v.id === o.slide_version_id)
  //   );
  //   saveDevStore();
  //   return;
  // }
  return request<void>(`/api/v1/slides/${id}`, { method: "DELETE" });
}

// ── Versions ─────────────────────────────────

export async function getVersions(slideId: string): Promise<SlideVersion[]> {
  // 実際のAPIを呼び出す（開発モードでもバックエンドから取得）
  // if (isDevToken()) {
  //   loadDevStore();
  //   return devStore.versions.filter((v) => v.slide_id === slideId);
  // }
  return request<SlideVersion[]>(`/api/v1/slides/${slideId}/versions`);
}

export async function createVersion(
  slideId: string
): Promise<SlideVersion> {
  // 実際のAPIを呼び出す（開発モードでもバックエンドで作成）
  // if (isDevToken()) {
  //   loadDevStore();
  //   const existing = devStore.versions.filter((v) => v.slide_id === slideId);
  //   const v: SlideVersion = { id: uid(), slide_id: slideId, version_num: existing.length + 1, created_at: now() };
  //   devStore.versions.push(v);
  //   saveDevStore();
  //   return v;
  // }
  return request<SlideVersion>(`/api/v1/slides/${slideId}/versions`, {
    method: "POST",
  });
}

// ── Pages ────────────────────────────────────

export async function getPages(versionId: string): Promise<Page[]> {
  // 実際のAPIを呼び出す（開発モードでもバックエンドから取得）
  // if (isDevToken()) {
  //   loadDevStore();
  //   return devStore.pages.filter((p) => p.slide_version_id === versionId);
  // }
  return request<Page[]>(`/api/v1/slides/versions/${versionId}/pages`);
}

export async function addPage(
  versionId: string,
  data: { page_num: number; contents: unknown }
): Promise<Page> {
  // 実際のAPIを呼び出す（開発モードでもバックエンドで作成）
  // if (isDevToken()) {
  //   loadDevStore();
  //   const p: Page = { id: uid(), slide_version_id: versionId, page_num: data.page_num, contents: data.contents, created_at: now(), updated_at: now() };
  //   devStore.pages.push(p);
  //   saveDevStore();
  //   return p;
  // }
  return request<Page>(`/api/v1/slides/versions/${versionId}/pages`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updatePage(
  pageId: string,
  data: { contents: unknown }
): Promise<Page> {
  // 実際のAPIを呼び出す（開発モードでもバックエンドで更新）
  // if (isDevToken()) {
  //   loadDevStore();
  //   const idx = devStore.pages.findIndex((p) => p.id === pageId);
  //   if (idx >= 0) {
  //     devStore.pages[idx].contents = data.contents;
  //     devStore.pages[idx].updated_at = now();
  //     saveDevStore();
  //     return devStore.pages[idx];
  //   }
  //   throw new Error("Page not found");
  // }
  return request<Page>(`/api/v1/slides/pages/${pageId}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function deletePage(pageId: string): Promise<void> {
  // 実際のAPIを呼び出す（開発モードでもバックエンドで削除）
  // if (isDevToken()) {
  //   devStore.pages = devStore.pages.filter((p) => p.id !== pageId);
  //   return;
  // }
  return request<void>(`/api/v1/slides/pages/${pageId}`, {
    method: "DELETE",
  });
}

// ── Outlines ─────────────────────────────────

export async function getOutlines(versionId: string): Promise<Outline[]> {
  // 実際のAPIを呼び出す（開発モードでもバックエンドから取得）
  // if (isDevToken()) {
  //   loadDevStore();
  //   return devStore.outlines.filter((o) => o.slide_version_id === versionId);
  // }
  return request<Outline[]>(
    `/api/v1/outlines/by-version/${versionId}`
  );
}

export async function getOutline(id: string): Promise<Outline> {
  // 実際のAPIを呼び出す（開発モードでもバックエンドから取得）
  // if (isDevToken()) {
  //   loadDevStore();
  //   const o = devStore.outlines.find((o) => o.id === id);
  //   if (o) return o;
  //   throw new Error("Outline not found");
  // }
  return request<Outline>(`/api/v1/outlines/${id}`);
}

export async function createOutline(data: {
  slide_version_id: string;
  title: string;
  description: string;
}): Promise<Outline> {
  // 実際のAPIを呼び出す（開発モードでもバックエンドで作成）
  // if (isDevToken()) {
  //   loadDevStore();
  //   const o: Outline = { id: uid(), slide_version_id: data.slide_version_id, title: data.title, description: data.description, created_at: now(), updated_at: now() };
  //   devStore.outlines.push(o);
  //   saveDevStore();
  //   return o;
  // }
  return request<Outline>("/api/v1/outlines", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateOutline(
  id: string,
  data: { title?: string; description?: string }
): Promise<Outline> {
  // 実際のAPIを呼び出す（開発モードでもバックエンドで更新）
  // if (isDevToken()) {
  //   loadDevStore();
  //   const idx = devStore.outlines.findIndex((o) => o.id === id);
  //   if (idx >= 0) {
  //     if (data.title) devStore.outlines[idx].title = data.title;
  //     if (data.description !== undefined) devStore.outlines[idx].description = data.description;
  //     devStore.outlines[idx].updated_at = now();
  //     saveDevStore();
  //     return devStore.outlines[idx];
  //   }
  //   throw new Error("Outline not found");
  // }
  return request<Outline>(`/api/v1/outlines/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function deleteOutline(id: string): Promise<void> {
  // 実際のAPIを呼び出す（開発モードでもバックエンドで削除）
  // if (isDevToken()) {
  //   loadDevStore();
  //   devStore.outlines = devStore.outlines.filter((o) => o.id !== id);
  //   saveDevStore();
  //   return;
  // }
  return request<void>(`/api/v1/outlines/${id}`, { method: "DELETE" });
}

export async function refineOutline(data: {
  outline_id: string;
  instructions: string;
}): Promise<Outline> {
  // 実際のAPIを呼び出す（開発モードでもGemini APIでブラッシュアップ）
  // if (isDevToken()) {
  //   loadDevStore();
  //   const idx = devStore.outlines.findIndex((o) => o.id === data.outline_id);
  //   if (idx >= 0) {
  //     devStore.outlines[idx].description += `\n[AI refined: ${data.instructions}]`;
  //     devStore.outlines[idx].updated_at = now();
  //     saveDevStore();
  //     return devStore.outlines[idx];
  //   }
  //   throw new Error("Outline not found");
  // }
  return request<Outline>("/api/v1/outlines/refine", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function generateSlideFromOutline(data: {
  outline_id: string;
  slide_object_id?: string;
  image_url?: string;
  page_num?: number;
  total_pages?: number;
  previous_slide_summary?: string;
}): Promise<SlideOutput> {
  // スライド生成は開発モードでも実際のAPIを呼ぶ（Gemini API使用）
  // if (isDevToken()) {
  //   return {
  //     outline_id: data.outline_id,
  //     slide: {
  //       objectId: data.slide_object_id || "slide-mvp-001",
  //       pageType: "SLIDE",
  //       pageElements: [],
  //     },
  //   };
  // }
  return request<SlideOutput>("/api/v1/outlines/generate-slide", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// Export
// ─────────────────────────────────────────────────────────────────────────────

export async function exportSlideToGoogleSlides(
  slideId: string,
  versionNum?: number,
  ownerEmail?: string
): Promise<{
  presentationId: string;
  presentationUrl: string;
  downloadUrl: string;
}> {
  const params = new URLSearchParams();
  if (versionNum !== undefined) {
    params.append("version_num", String(versionNum));
  }
  if (ownerEmail) {
    params.append("owner_email", ownerEmail);
  }
  const query = params.toString();
  const url = `/api/v1/slides/${slideId}/export${query ? `?${query}` : ""}`;
  
  return request(url, {
    method: "POST",
  });
}
