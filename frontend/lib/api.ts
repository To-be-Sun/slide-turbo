// ============================================
// Slide Turbo — API クライアント
// Backend /api/v1 へのリクエストを管理
// ============================================

import type {
  Outline,
  Page,
  Slide,
  SlideListItem,
  SlideVersion,
  Template,
  TemplateListItem,
  TokenResponse,
  User,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001";
const DEV_TOKEN = "dev-token-slide-turbo";
const GOOGLE_TOKEN_EXPIRED_DETAIL =
  "Google access token is invalid or expired. Please sign in again.";

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

function getGoogleAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("google_access_token");
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const googleAccessToken = getGoogleAccessToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  if (googleAccessToken) {
    headers["X-Google-Access-Token"] = googleAccessToken;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    if (
      res.status === 401 &&
      body.detail === GOOGLE_TOKEN_EXPIRED_DETAIL &&
      typeof window !== "undefined"
    ) {
      localStorage.removeItem("token");
      localStorage.removeItem("google_access_token");
      localStorage.removeItem("dev_user");
      if (window.location.pathname !== "/login") {
        window.location.href = "/login?reason=google_token_expired";
      }
    }
    throw new Error(body.detail || `API error: ${res.status}`);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

// ── Auth ─────────────────────────────────────

export function getGoogleAuthUrl(): string {
  const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;
  if (!clientId) {
    // フォールバック: バックエンド経由
    return `${API_BASE}/api/v1/users/auth/google`;
  }
  const redirectUri = encodeURIComponent(`${window.location.origin}/login`);
  const scope = encodeURIComponent(
    "openid email profile https://www.googleapis.com/auth/presentations.readonly https://www.googleapis.com/auth/drive.readonly"
  );
  return (
    `https://accounts.google.com/o/oauth2/v2/auth` +
    `?client_id=${clientId}` +
    `&redirect_uri=${redirectUri}` +
    `&response_type=code` +
    `&scope=${scope}` +
    `&access_type=offline` +
    `&prompt=consent` +
    `&include_granted_scopes=true`
  );
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

// ── Dev Mode In-Memory Store ─────────────────

const devStore = {
  slides: [] as Slide[],
  templates: [] as Template[],
  outlines: [] as Outline[],
  versions: [] as SlideVersion[],
  pages: [] as Page[],
};

function uid(): string {
  return `dev-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

const now = () => new Date().toISOString();

// ── Templates ────────────────────────────────

export async function getTemplates(): Promise<TemplateListItem[]> {
  if (isDevToken()) return devStore.templates.map((t) => ({ id: t.id, title: t.title, created_at: t.created_at }));
  return request<TemplateListItem[]>("/api/v1/templates");
}

export async function getTemplate(id: string): Promise<Template> {
  if (isDevToken()) {
    const t = devStore.templates.find((t) => t.id === id);
    if (t) return t;
    throw new Error("Template not found");
  }
  return request<Template>(`/api/v1/templates/${id}`);
}

export async function createTemplate(data: {
  title: string;
  contents: unknown;
}): Promise<Template> {
  if (isDevToken()) {
    const t: Template = { id: uid(), owner_id: "dev-user-001", title: data.title, contents: data.contents, created_at: now(), updated_at: now() };
    devStore.templates.push(t);
    return t;
  }
  return request<Template>("/api/v1/templates", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function importTemplate(
  presentationUrl: string
): Promise<Template> {
  if (isDevToken()) {
    const t: Template = { id: uid(), owner_id: "dev-user-001", title: `Imported: ${presentationUrl.slice(-10)}`, contents: {}, created_at: now(), updated_at: now() };
    devStore.templates.push(t);
    return t;
  }
  return request<Template>("/api/v1/templates/import", {
    method: "POST",
    body: JSON.stringify({ presentation_url: presentationUrl }),
  });
}

export async function updateTemplate(
  id: string,
  data: { title?: string; contents?: unknown }
): Promise<Template> {
  if (isDevToken()) {
    const idx = devStore.templates.findIndex((t) => t.id === id);
    if (idx >= 0) {
      if (data.title) devStore.templates[idx].title = data.title;
      if (data.contents !== undefined) devStore.templates[idx].contents = data.contents;
      devStore.templates[idx].updated_at = now();
      return devStore.templates[idx];
    }
    throw new Error("Template not found");
  }
  return request<Template>(`/api/v1/templates/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function deleteTemplate(id: string): Promise<void> {
  if (isDevToken()) {
    devStore.templates = devStore.templates.filter((t) => t.id !== id);
    return;
  }
  return request<void>(`/api/v1/templates/${id}`, { method: "DELETE" });
}

// ── Slides ───────────────────────────────────

export async function getSlides(): Promise<SlideListItem[]> {
  if (isDevToken()) return devStore.slides.map((s) => ({ id: s.id, title: s.title, template_id: s.template_id, images: s.images, updated_at: s.updated_at }));
  return request<SlideListItem[]>("/api/v1/slides");
}

export async function getSlide(id: string): Promise<Slide> {
  if (isDevToken()) {
    const s = devStore.slides.find((s) => s.id === id);
    if (s) return s;
    throw new Error("Slide not found");
  }
  return request<Slide>(`/api/v1/slides/${id}`);
}

export async function createSlide(data: {
  title: string;
  template_id?: string;
}): Promise<Slide> {
  if (isDevToken()) {
    const s: Slide = { id: uid(), owner_id: "dev-user-001", template_id: data.template_id || null, title: data.title, images: [], created_at: now(), updated_at: now() };
    devStore.slides.push(s);
    // 初期バージョンも自動作成
    const v: SlideVersion = { id: uid(), slide_id: s.id, version_num: 1, created_at: now() };
    devStore.versions.push(v);
    return s;
  }
  return request<Slide>("/api/v1/slides", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateSlide(
  id: string,
  data: { title?: string }
): Promise<Slide> {
  if (isDevToken()) {
    const idx = devStore.slides.findIndex((s) => s.id === id);
    if (idx >= 0) {
      if (data.title) devStore.slides[idx].title = data.title;
      devStore.slides[idx].updated_at = now();
      return devStore.slides[idx];
    }
    throw new Error("Slide not found");
  }
  return request<Slide>(`/api/v1/slides/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function deleteSlide(id: string): Promise<void> {
  if (isDevToken()) {
    devStore.slides = devStore.slides.filter((s) => s.id !== id);
    return;
  }
  return request<void>(`/api/v1/slides/${id}`, { method: "DELETE" });
}

// ── Versions ─────────────────────────────────

export async function getVersions(slideId: string): Promise<SlideVersion[]> {
  if (isDevToken()) return devStore.versions.filter((v) => v.slide_id === slideId);
  return request<SlideVersion[]>(`/api/v1/slides/${slideId}/versions`);
}

export async function createVersion(
  slideId: string
): Promise<SlideVersion> {
  if (isDevToken()) {
    const existing = devStore.versions.filter((v) => v.slide_id === slideId);
    const v: SlideVersion = { id: uid(), slide_id: slideId, version_num: existing.length + 1, created_at: now() };
    devStore.versions.push(v);
    return v;
  }
  return request<SlideVersion>(`/api/v1/slides/${slideId}/versions`, {
    method: "POST",
  });
}

// ── Pages ────────────────────────────────────

export async function getPages(versionId: string): Promise<Page[]> {
  if (isDevToken()) return devStore.pages.filter((p) => p.slide_version_id === versionId);
  return request<Page[]>(`/api/v1/slides/versions/${versionId}/pages`);
}

export async function addPage(
  versionId: string,
  data: { page_num: number; contents: unknown }
): Promise<Page> {
  if (isDevToken()) {
    const p: Page = { id: uid(), slide_version_id: versionId, page_num: data.page_num, contents: data.contents, created_at: now(), updated_at: now() };
    devStore.pages.push(p);
    return p;
  }
  return request<Page>(`/api/v1/slides/versions/${versionId}/pages`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updatePage(
  pageId: string,
  data: { contents: unknown }
): Promise<Page> {
  if (isDevToken()) {
    const idx = devStore.pages.findIndex((p) => p.id === pageId);
    if (idx >= 0) {
      devStore.pages[idx].contents = data.contents;
      devStore.pages[idx].updated_at = now();
      return devStore.pages[idx];
    }
    throw new Error("Page not found");
  }
  return request<Page>(`/api/v1/slides/pages/${pageId}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

// ── Outlines ─────────────────────────────────

export async function getOutlines(versionId: string): Promise<Outline[]> {
  if (isDevToken()) return devStore.outlines.filter((o) => o.slide_version_id === versionId);
  return request<Outline[]>(
    `/api/v1/outlines/by-version/${versionId}`
  );
}

export async function getOutline(id: string): Promise<Outline> {
  if (isDevToken()) {
    const o = devStore.outlines.find((o) => o.id === id);
    if (o) return o;
    throw new Error("Outline not found");
  }
  return request<Outline>(`/api/v1/outlines/${id}`);
}

export async function createOutline(data: {
  slide_version_id: string;
  title: string;
  description: string;
}): Promise<Outline> {
  if (isDevToken()) {
    const o: Outline = { id: uid(), slide_version_id: data.slide_version_id, title: data.title, description: data.description, created_at: now(), updated_at: now() };
    devStore.outlines.push(o);
    return o;
  }
  return request<Outline>("/api/v1/outlines", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateOutline(
  id: string,
  data: { title?: string; description?: string }
): Promise<Outline> {
  if (isDevToken()) {
    const idx = devStore.outlines.findIndex((o) => o.id === id);
    if (idx >= 0) {
      if (data.title) devStore.outlines[idx].title = data.title;
      if (data.description !== undefined) devStore.outlines[idx].description = data.description;
      devStore.outlines[idx].updated_at = now();
      return devStore.outlines[idx];
    }
    throw new Error("Outline not found");
  }
  return request<Outline>(`/api/v1/outlines/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function deleteOutline(id: string): Promise<void> {
  if (isDevToken()) {
    devStore.outlines = devStore.outlines.filter((o) => o.id !== id);
    return;
  }
  return request<void>(`/api/v1/outlines/${id}`, { method: "DELETE" });
}

export async function refineOutline(data: {
  outline_id: string;
  instructions: string;
}): Promise<Outline> {
  if (isDevToken()) {
    const idx = devStore.outlines.findIndex((o) => o.id === data.outline_id);
    if (idx >= 0) {
      devStore.outlines[idx].description += `\n[AI refined: ${data.instructions}]`;
      devStore.outlines[idx].updated_at = now();
      return devStore.outlines[idx];
    }
    throw new Error("Outline not found");
  }
  return request<Outline>("/api/v1/outlines/refine", {
    method: "POST",
    body: JSON.stringify(data),
  });
}
