// ============================================
// Slide Turbo — TypeScript 型定義
// Backend の DTO / Entity に対応
// ============================================

// ── User ─────────────────────────────────────

export interface User {
  id: string;
  email: string;
  name: string;
  icon: string | null;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  google_access_token?: string | null;
  user: User;
}

// ── Template ─────────────────────────────────

export interface Template {
  id: string;
  owner_id: string;
  title: string;
  contents: unknown; // JSON
  created_at: string;
  updated_at: string;
}

export interface TemplateListItem {
  id: string;
  title: string;
  created_at: string;
}

// ── Slide (Project) ──────────────────────────

export interface Slide {
  id: string;
  owner_id: string;
  template_id: string | null;
  title: string;
  images: string[];
  created_at: string;
  updated_at: string;
}

export interface SlideListItem {
  id: string;
  title: string;
  template_id: string | null;
  images: string[];
  updated_at: string;
}

// ── SlideVersion ─────────────────────────────

export interface SlideVersion {
  id: string;
  slide_id: string;
  version_num: number;
  created_at: string;
}

// ── Page ─────────────────────────────────────

export interface Page {
  id: string;
  slide_version_id: string;
  page_num: number;
  contents: unknown; // JSON
  created_at: string;
  updated_at: string;
}

// ── Outline (骨子) ───────────────────────────

export interface Outline {
  id: string;
  slide_version_id: string;
  title: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface SlideOutput {
  outline_id: string;
  slide: unknown;
}
