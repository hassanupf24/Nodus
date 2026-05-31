/* ============================================================
   NODUS API SERVICE
   HTTP client for communicating with the Python AI backend
   ============================================================ */

const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

interface ApiOptions {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
  signal?: AbortSignal;
}

interface ApiError {
  status: number;
  message: string;
  detail?: unknown;
}

class NodusApiError extends Error {
  status: number;
  detail?: unknown;

  constructor(error: ApiError) {
    super(error.message);
    this.name = "NodusApiError";
    this.status = error.status;
    this.detail = error.detail;
  }
}

async function apiRequest<T>(endpoint: string, options: ApiOptions = {}): Promise<T> {
  const { method = "GET", body, headers = {}, signal } = options;

  const config: RequestInit = {
    method,
    headers: {
      "Content-Type": "application/json",
      ...headers,
    },
    signal,
  };

  if (body !== undefined) {
    config.body = JSON.stringify(body);
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

  if (!response.ok) {
    let detail: unknown;
    try {
      detail = await response.json();
    } catch {
      detail = await response.text();
    }
    throw new NodusApiError({
      status: response.status,
      message: `API request failed: ${response.statusText}`,
      detail,
    });
  }

  const contentType = response.headers.get("content-type");
  if (contentType?.includes("application/json")) {
    return response.json() as Promise<T>;
  }

  return response.text() as unknown as T;
}

// ---- Chat API ----

export interface ChatCompletionRequest {
  model: string;
  messages: Array<{ role: string; content: string }>;
  temperature?: number;
  max_tokens?: number;
  stream?: boolean;
}

export interface ChatCompletionChunk {
  id: string;
  choices: Array<{
    delta: { content?: string; role?: string };
    finish_reason: string | null;
    index: number;
  }>;
  model: string;
  created: number;
}

export async function* streamChatCompletion(
  request: ChatCompletionRequest,
  signal?: AbortSignal,
): AsyncGenerator<ChatCompletionChunk> {
  const response = await fetch(`${API_BASE_URL}/chat/completions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...request, stream: true }),
    signal,
  });

  if (!response.ok) {
    throw new NodusApiError({
      status: response.status,
      message: `Chat request failed: ${response.statusText}`,
    });
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error("No response body reader available");

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || !trimmed.startsWith("data: ")) continue;

      const data = trimmed.slice(6);
      if (data === "[DONE]") return;

      try {
        const chunk = JSON.parse(data) as ChatCompletionChunk;
        yield chunk;
      } catch {
        // Skip malformed chunks
      }
    }
  }
}

export async function chatCompletion(request: ChatCompletionRequest): Promise<ChatCompletionChunk> {
  return apiRequest<ChatCompletionChunk>("/chat/completions", {
    method: "POST",
    body: { ...request, stream: false },
  });
}

// ---- Models API ----

export interface ModelInfo {
  name: string;
  display_name: string;
  size: number;
  quantization: string;
  family: string;
  parameter_count: string;
  modified_at: string;
}

export async function listModels(): Promise<ModelInfo[]> {
  const result = await apiRequest<{ models: ModelInfo[] }>("/models");
  return result.models;
}

export async function pullModel(name: string): Promise<void> {
  await apiRequest("/models/pull", {
    method: "POST",
    body: { name },
  });
}

export async function deleteModel(name: string): Promise<void> {
  await apiRequest(`/models/${encodeURIComponent(name)}`, {
    method: "DELETE",
  });
}

// ---- Search API ----

export interface SearchRequest {
  query: string;
  mode?: "semantic" | "keyword" | "hybrid";
  limit?: number;
  offset?: number;
  filters?: {
    file_types?: string[];
    date_range?: { start: string; end: string };
    tags?: string[];
  };
}

export interface SearchResponse {
  results: Array<{
    id: string;
    content: string;
    score: number;
    source: string;
    source_type: string;
    metadata: Record<string, unknown>;
    highlights: string[];
    timestamp: string;
  }>;
  total: number;
  query_time_ms: number;
}

export async function search(request: SearchRequest): Promise<SearchResponse> {
  return apiRequest<SearchResponse>("/search", {
    method: "POST",
    body: request,
  });
}

// ---- Ingestion API ----

export interface IngestionResponse {
  job_id: string;
  status: string;
  message: string;
}

export async function ingestFile(filePath: string, collectionName: string = "documents"): Promise<IngestionResponse> {
  return apiRequest<IngestionResponse>("/ingest", {
    method: "POST",
    body: { file_path: filePath, collection_name: collectionName },
  });
}

export async function getIngestionStatus(jobId: string): Promise<IngestionResponse> {
  return apiRequest<IngestionResponse>(`/ingest/status/${jobId}`);
}

// ---- Knowledge Graph API ----

export interface GraphEntity {
  id: string;
  label: string;
  type: string;
  properties: Record<string, unknown>;
}

export interface GraphRelationship {
  id: string;
  source: string;
  target: string;
  label: string;
  weight: number;
}

export interface GraphData {
  nodes: GraphEntity[];
  edges: GraphRelationship[];
}

export async function getGraph(
  query?: string,
  limit?: number,
): Promise<GraphData> {
  const params = new URLSearchParams();
  if (query) params.set("query", query);
  if (limit) params.set("limit", limit.toString());
  const qs = params.toString();
  return apiRequest<GraphData>(`/graph${qs ? `?${qs}` : ""}`);
}

export async function getGraphNeighbors(entityId: string, depth?: number): Promise<GraphData> {
  const params = new URLSearchParams();
  if (depth) params.set("depth", depth.toString());
  const qs = params.toString();
  return apiRequest<GraphData>(`/graph/neighbors/${entityId}${qs ? `?${qs}` : ""}`);
}

// ---- Timeline API ----

export interface TimelineEntry {
  id: string;
  title: string;
  description: string;
  timestamp: string;
  type: string;
  source: string;
  entities: string[];
}

export async function getTimeline(
  limit?: number,
  offset?: number,
  startDate?: string,
  endDate?: string,
): Promise<{ events: TimelineEntry[]; total: number }> {
  const params = new URLSearchParams();
  if (limit) params.set("limit", limit.toString());
  if (offset) params.set("offset", offset.toString());
  if (startDate) params.set("start_date", startDate);
  if (endDate) params.set("end_date", endDate);
  const qs = params.toString();
  return apiRequest(`/timeline${qs ? `?${qs}` : ""}`);
}

// ---- Health API ----

export interface HealthResponse {
  status: string;
  services: Array<{
    name: string;
    status: string;
    latency_ms: number;
  }>;
  resources: {
    cpu_percent: number;
    ram_used_mb: number;
    ram_total_mb: number;
    gpu_percent?: number;
    gpu_vram_used_mb?: number;
    gpu_vram_total_mb?: number;
  };
}

export async function getHealth(): Promise<HealthResponse> {
  return apiRequest<HealthResponse>("/health");
}

// ---- Agents API ----

export interface AgentRequest {
  agent: string;
  input: string;
  context?: Record<string, unknown>;
}

export interface AgentResponse {
  agent: string;
  output: string;
  status: string;
  execution_time_ms: number;
  metadata?: Record<string, unknown>;
}

export async function invokeAgent(request: AgentRequest): Promise<AgentResponse> {
  return apiRequest<AgentResponse>("/agents/invoke", {
    method: "POST",
    body: request,
  });
}

export async function listAgents(): Promise<Array<{ name: string; description: string; status: string }>> {
  return apiRequest("/agents");
}

export { NodusApiError };
