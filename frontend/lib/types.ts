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

export interface Project {
  id: string
  name: string
  description: string
  templateId: string
  templateName: string
  status: "draft" | "in-progress" | "completed"
  slots: FilledSlot[]
  story: StorySection[]
  materials: ProjectMaterial[]
  versions: ProjectVersion[]
  suggestions: Suggestion[]
  createdAt: Date
  updatedAt: Date
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

export interface ProjectMaterial {
  id: string
  name: string
  type: "icon" | "image" | "text" | "chart"
  content: string
  tags: string[]
  usedInSlots: string[]
}

export interface ProjectVersion {
  id: string
  name: string
  description: string
  slots: FilledSlot[]
  story: StorySection[]
  createdAt: Date
}

export interface Suggestion {
  id: string
  type: "slot-update" | "story-sync" | "material-add"
  message: string
  sourceSlotId?: string
  targetSlotIds?: string[]
  suggestedValue?: string
  dismissed: boolean
  createdAt: Date
}

export interface ChatMessage {
  id: string
  role: "user" | "assistant" | "system"
  content: string
  timestamp: Date
  // Context about what the message is referencing
  context?: {
    type: "slot" | "story" | "slide" | "general"
    slotId?: string
    slideIndex?: number
    storyId?: string
  }
  // Actions suggested by AI
  actions?: ChatAction[]
}

export interface ChatAction {
  id: string
  type: "fill-slot" | "update-story" | "approve" | "suggest-change"
  label: string
  targetId: string
  value?: string
  applied?: boolean
}

export interface HistoryItem {
  id: string
  projectId?: string
  type: "project" | "template" | "slot" | "story" | "version"
  action: string
  description: string
  timestamp: Date
}
