/* ============================================================
   NODUS TYPE DEFINITIONS
   Core types shared across the application
   ============================================================ */

// ---- Navigation & Views ----
export type ViewId =
  | "chat"
  | "search"
  | "knowledge"
  | "timeline"
  | "graph"
  | "files"
  | "dashboard"
  | "settings"
  | "models";

export interface NavItem {
  id: ViewId;
  label: string;
  icon: string;
  shortcut?: string;
}

// ---- Chat ----
export type MessageRole = "user" | "assistant" | "system";

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: number;
  model?: string;
  attachments?: FileAttachment[];
  isStreaming?: boolean;
  tokenCount?: number;
  latencyMs?: number;
}

export interface ChatConversation {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: number;
  updatedAt: number;
  model: string;
  summary?: string;
}

export interface FileAttachment {
  id: string;
  name: string;
  type: string;
  size: number;
  path?: string;
  thumbnailUrl?: string;
}

// ---- AI Models ----
export type ModelStatus = "available" | "downloading" | "loaded" | "error";

export interface AIModel {
  name: string;
  displayName: string;
  size: number;
  quantization: string;
  family: string;
  parameterCount: string;
  status: ModelStatus;
  downloadProgress?: number;
  vramUsage?: number;
  ramUsage?: number;
  lastUsed?: number;
}

// ---- Search ----
export type SearchMode = "semantic" | "keyword" | "hybrid";

export interface SearchQuery {
  query: string;
  mode: SearchMode;
  filters?: SearchFilters;
  limit?: number;
  offset?: number;
}

export interface SearchFilters {
  fileTypes?: string[];
  dateRange?: { start: number; end: number };
  tags?: string[];
  sources?: string[];
}

export interface SearchResult {
  id: string;
  content: string;
  score: number;
  source: string;
  sourceType: string;
  metadata: Record<string, unknown>;
  highlights: string[];
  timestamp: number;
}

// ---- Knowledge Graph ----
export interface GraphNode {
  id: string;
  label: string;
  type: EntityType;
  properties: Record<string, unknown>;
  x?: number;
  y?: number;
  size?: number;
  color?: string;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label: string;
  weight: number;
  properties?: Record<string, unknown>;
}

export type EntityType =
  | "person"
  | "organization"
  | "concept"
  | "document"
  | "event"
  | "location"
  | "topic"
  | "project";

// ---- Timeline ----
export interface TimelineEvent {
  id: string;
  title: string;
  description: string;
  timestamp: number;
  type: TimelineEventType;
  source: string;
  entities: string[];
  metadata?: Record<string, unknown>;
}

export type TimelineEventType =
  | "document_added"
  | "conversation"
  | "entity_created"
  | "relationship_formed"
  | "search_query"
  | "agent_action"
  | "insight_generated";

// ---- Ingestion ----
export type IngestionStatus = "pending" | "processing" | "completed" | "failed";

export interface IngestionJob {
  id: string;
  fileName: string;
  fileType: string;
  fileSize: number;
  status: IngestionStatus;
  progress: number;
  startedAt: number;
  completedAt?: number;
  error?: string;
  chunks?: number;
  entities?: number;
}

// ---- System ----
export interface SystemHealth {
  status: "healthy" | "degraded" | "unhealthy";
  services: ServiceHealth[];
  resources: ResourceUsage;
}

export interface ServiceHealth {
  name: string;
  status: "up" | "down" | "degraded";
  latencyMs: number;
  lastCheck: number;
}

export interface ResourceUsage {
  cpuPercent: number;
  ramUsedMb: number;
  ramTotalMb: number;
  gpuPercent?: number;
  gpuVramUsedMb?: number;
  gpuVramTotalMb?: number;
  diskUsedGb: number;
  diskTotalGb: number;
}

// ---- Settings ----
export interface AppSettings {
  general: GeneralSettings;
  ai: AISettings;
  privacy: PrivacySettings;
  appearance: AppearanceSettings;
}

export interface GeneralSettings {
  dataDirectory: string;
  language: string;
  autoStartup: boolean;
  minimizeToTray: boolean;
}

export interface AISettings {
  defaultModel: string;
  ollamaEndpoint: string;
  maxContextLength: number;
  temperature: number;
  streamingEnabled: boolean;
  gpuEnabled: boolean;
}

export interface PrivacySettings {
  localOnlyMode: boolean;
  cloudEscalationEnabled: boolean;
  telemetryEnabled: boolean;
  encryptionEnabled: boolean;
}

export interface AppearanceSettings {
  theme: "dark" | "light" | "system";
  fontSize: "small" | "medium" | "large";
  sidebarCollapsed: boolean;
  animationsEnabled: boolean;
}
