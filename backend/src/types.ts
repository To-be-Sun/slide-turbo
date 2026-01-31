// フロントエンドと共通の型定義
export interface Template {
  id: string
  name: string
  description: string
  thumbnail: string
  slideCount: number
  slots: TemplateSlot[]
  createdAt: Date
}

export interface TemplateSlot {
  id: string
  slideIndex: number
  name: string
  type: "title" | "text" | "image" | "chart" | "list" | "icon"
  placeholder: string
  required: boolean
}

export interface FilledSlot {
  slotId: string
  slideIndex: number
  name: string
  type: "title" | "text" | "image" | "chart" | "list" | "icon"
  value: string
  status: "empty" | "draft" | "filled" | "approved"
  linkedStoryId?: string
}

export interface StorySection {
  id: string
  title: string
  content: string
  slideIndices: number[]
  status: "draft" | "approved"
  order: number
}

// API Request/Response types
export interface GenerateSlideRequest {
  templateId: string
  slots: FilledSlot[]
  story?: StorySection[]
}

export interface GenerateSlideResponse {
  html: string
  slides: SlideData[]
}

export interface SlideData {
  slideIndex: number
  html: string
  imageUrl?: string
}

export interface FillSlotRequest {
  slotId: string
  value: string
  context?: {
    story?: StorySection[]
    otherSlots?: FilledSlot[]
  }
}

export interface FillSlotResponse {
  value: string
  html: string
}

