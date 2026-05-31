/* ============================================================
   NODUS APP STORE
   Global application state management with Zustand
   ============================================================ */

import { create } from "zustand";
import { immer } from "zustand/middleware/immer";
import { Store } from "@tauri-apps/plugin-store";
import type {
  ViewId,
  ChatMessage,
  ChatConversation,
  AIModel,
  SearchResult,
  SearchMode,
  AppSettings,
  IngestionJob,
  SystemHealth,
  GraphNode,
  GraphEdge,
  TimelineEvent,
} from "@/types";

// Initialize Tauri Store for settings
export const tauriStore = new Store("nodus_settings.json");

// ---- App State ----

interface AppState {
  currentView: ViewId;
  sidebarCollapsed: boolean;
  commandPaletteOpen: boolean;

  setCurrentView: (view: ViewId) => void;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setCommandPaletteOpen: (open: boolean) => void;
}

export const useAppStore = create<AppState>()(
  immer((set) => ({
    currentView: "chat",
    sidebarCollapsed: false,
    commandPaletteOpen: false,

    setCurrentView: (view) =>
      set((state) => {
        state.currentView = view;
      }),

    toggleSidebar: () =>
      set((state) => {
        state.sidebarCollapsed = !state.sidebarCollapsed;
      }),

    setSidebarCollapsed: (collapsed) =>
      set((state) => {
        state.sidebarCollapsed = collapsed;
      }),

    setCommandPaletteOpen: (open) =>
      set((state) => {
        state.commandPaletteOpen = open;
      }),
  })),
);

// ---- Chat Store ----

interface ChatState {
  conversations: ChatConversation[];
  activeConversationId: string | null;
  isGenerating: boolean;
  selectedModel: string;

  // Actions
  createConversation: () => string;
  setActiveConversation: (id: string) => void;
  addMessage: (conversationId: string, message: ChatMessage) => void;
  updateMessage: (conversationId: string, messageId: string, updates: Partial<ChatMessage>) => void;
  appendToMessage: (conversationId: string, messageId: string, content: string) => void;
  deleteConversation: (id: string) => void;
  setIsGenerating: (generating: boolean) => void;
  setSelectedModel: (model: string) => void;
  clearConversations: () => void;
}

export const useChatStore = create<ChatState>()(
  immer((set, get) => ({
    conversations: [],
    activeConversationId: null,
    isGenerating: false,
    selectedModel: "llama3.2:3b",

    createConversation: () => {
      const id = crypto.randomUUID();
      const conversation: ChatConversation = {
        id,
        title: "New Conversation",
        messages: [],
        createdAt: Date.now(),
        updatedAt: Date.now(),
        model: get().selectedModel,
      };
      set((state) => {
        state.conversations.unshift(conversation);
        state.activeConversationId = id;
      });
      return id;
    },

    setActiveConversation: (id) =>
      set((state) => {
        state.activeConversationId = id;
      }),

    addMessage: (conversationId, message) =>
      set((state) => {
        const conv = state.conversations.find((c) => c.id === conversationId);
        if (conv) {
          conv.messages.push(message);
          conv.updatedAt = Date.now();
          // Auto-title from first user message
          if (conv.messages.length === 1 && message.role === "user") {
            conv.title = message.content.slice(0, 60) + (message.content.length > 60 ? "…" : "");
          }
        }
      }),

    updateMessage: (conversationId, messageId, updates) =>
      set((state) => {
        const conv = state.conversations.find((c) => c.id === conversationId);
        if (conv) {
          const msg = conv.messages.find((m) => m.id === messageId);
          if (msg) {
            Object.assign(msg, updates);
          }
        }
      }),

    appendToMessage: (conversationId, messageId, content) =>
      set((state) => {
        const conv = state.conversations.find((c) => c.id === conversationId);
        if (conv) {
          const msg = conv.messages.find((m) => m.id === messageId);
          if (msg) {
            msg.content += content;
          }
        }
      }),

    deleteConversation: (id) =>
      set((state) => {
        state.conversations = state.conversations.filter((c) => c.id !== id);
        if (state.activeConversationId === id) {
          state.activeConversationId = state.conversations[0]?.id ?? null;
        }
      }),

    setIsGenerating: (generating) =>
      set((state) => {
        state.isGenerating = generating;
      }),

    setSelectedModel: (model) =>
      set((state) => {
        state.selectedModel = model;
      }),

    clearConversations: () =>
      set((state) => {
        state.conversations = [];
        state.activeConversationId = null;
      }),
  })),
);

// ---- Search Store ----

interface SearchState {
  query: string;
  mode: SearchMode;
  results: SearchResult[];
  isSearching: boolean;
  totalResults: number;
  queryTimeMs: number;

  setQuery: (query: string) => void;
  setMode: (mode: SearchMode) => void;
  setResults: (results: SearchResult[], total: number, timeMs: number) => void;
  setIsSearching: (searching: boolean) => void;
  clearResults: () => void;
}

export const useSearchStore = create<SearchState>()(
  immer((set) => ({
    query: "",
    mode: "hybrid",
    results: [],
    isSearching: false,
    totalResults: 0,
    queryTimeMs: 0,

    setQuery: (query) =>
      set((state) => {
        state.query = query;
      }),

    setMode: (mode) =>
      set((state) => {
        state.mode = mode;
      }),

    setResults: (results, total, timeMs) =>
      set((state) => {
        state.results = results;
        state.totalResults = total;
        state.queryTimeMs = timeMs;
        state.isSearching = false;
      }),

    setIsSearching: (searching) =>
      set((state) => {
        state.isSearching = searching;
      }),

    clearResults: () =>
      set((state) => {
        state.results = [];
        state.totalResults = 0;
        state.queryTimeMs = 0;
      }),
  })),
);

// ---- Models Store ----

interface ModelsState {
  models: AIModel[];
  isLoading: boolean;

  setModels: (models: AIModel[]) => void;
  updateModel: (name: string, updates: Partial<AIModel>) => void;
  setIsLoading: (loading: boolean) => void;
}

export const useModelsStore = create<ModelsState>()(
  immer((set) => ({
    models: [],
    isLoading: false,

    setModels: (models) =>
      set((state) => {
        state.models = models;
      }),

    updateModel: (name, updates) =>
      set((state) => {
        const model = state.models.find((m) => m.name === name);
        if (model) {
          Object.assign(model, updates);
        }
      }),

    setIsLoading: (loading) =>
      set((state) => {
        state.isLoading = loading;
      }),
  })),
);

// ---- Graph Store ----

interface GraphState {
  nodes: GraphNode[];
  edges: GraphEdge[];
  selectedNodeId: string | null;
  isLoading: boolean;

  setGraphData: (nodes: GraphNode[], edges: GraphEdge[]) => void;
  setSelectedNode: (id: string | null) => void;
  setIsLoading: (loading: boolean) => void;
}

export const useGraphStore = create<GraphState>()(
  immer((set) => ({
    nodes: [],
    edges: [],
    selectedNodeId: null,
    isLoading: false,

    setGraphData: (nodes, edges) =>
      set((state) => {
        state.nodes = nodes;
        state.edges = edges;
      }),

    setSelectedNode: (id) =>
      set((state) => {
        state.selectedNodeId = id;
      }),

    setIsLoading: (loading) =>
      set((state) => {
        state.isLoading = loading;
      }),
  })),
);

// ---- Timeline Store ----

interface TimelineState {
  events: TimelineEvent[];
  isLoading: boolean;
  totalEvents: number;

  setEvents: (events: TimelineEvent[], total: number) => void;
  appendEvents: (events: TimelineEvent[]) => void;
  setIsLoading: (loading: boolean) => void;
}

export const useTimelineStore = create<TimelineState>()(
  immer((set) => ({
    events: [],
    isLoading: false,
    totalEvents: 0,

    setEvents: (events, total) =>
      set((state) => {
        state.events = events;
        state.totalEvents = total;
      }),

    appendEvents: (events) =>
      set((state) => {
        state.events.push(...events);
      }),

    setIsLoading: (loading) =>
      set((state) => {
        state.isLoading = loading;
      }),
  })),
);

// ---- Ingestion Store ----

interface IngestionState {
  jobs: IngestionJob[];
  addJob: (job: IngestionJob) => void;
  updateJob: (id: string, updates: Partial<IngestionJob>) => void;
  removeJob: (id: string) => void;
}

export const useIngestionStore = create<IngestionState>()(
  immer((set) => ({
    jobs: [],

    addJob: (job) =>
      set((state) => {
        state.jobs.unshift(job);
      }),

    updateJob: (id, updates) =>
      set((state) => {
        const job = state.jobs.find((j) => j.id === id);
        if (job) {
          Object.assign(job, updates);
        }
      }),

    removeJob: (id) =>
      set((state) => {
        state.jobs = state.jobs.filter((j) => j.id !== id);
      }),
  })),
);

// ---- Settings Store ----

interface SettingsState {
  settings: AppSettings;
  updateGeneralSettings: (updates: Partial<AppSettings["general"]>) => void;
  updateAISettings: (updates: Partial<AppSettings["ai"]>) => void;
  updatePrivacySettings: (updates: Partial<AppSettings["privacy"]>) => void;
  updateAppearanceSettings: (updates: Partial<AppSettings["appearance"]>) => void;
}

const DEFAULT_SETTINGS: AppSettings = {
  general: {
    dataDirectory: "",
    language: "en",
    autoStartup: false,
    minimizeToTray: true,
  },
  ai: {
    defaultModel: "llama3.2:3b",
    ollamaEndpoint: "http://localhost:11434",
    maxContextLength: 4096,
    temperature: 0.7,
    streamingEnabled: true,
    gpuEnabled: true,
  },
  privacy: {
    localOnlyMode: true,
    cloudEscalationEnabled: false,
    telemetryEnabled: false,
    encryptionEnabled: true,
  },
  appearance: {
    theme: "dark",
    fontSize: "medium",
    sidebarCollapsed: false,
    animationsEnabled: true,
  },
};

export const useSettingsStore = create<SettingsState>()(
  immer((set) => ({
    settings: DEFAULT_SETTINGS,

    updateGeneralSettings: (updates) =>
      set((state) => {
        Object.assign(state.settings.general, updates);
      }),

    updateAISettings: (updates) =>
      set((state) => {
        Object.assign(state.settings.ai, updates);
      }),

    updatePrivacySettings: (updates) =>
      set((state) => {
        Object.assign(state.settings.privacy, updates);
      }),

    updateAppearanceSettings: (updates) =>
      set((state) => {
        Object.assign(state.settings.appearance, updates);
      }),
  })),
);

// Persist settings to Tauri Store
useSettingsStore.subscribe((state) => {
  tauriStore.set("settings", state.settings).then(() => tauriStore.save()).catch(console.error);
});

export const loadPersistedSettings = async () => {
  try {
    const saved = await tauriStore.get<AppSettings>("settings");
    if (saved) {
      useSettingsStore.setState((state) => ({ settings: { ...state.settings, ...saved } }));
    }
  } catch (error) {
    console.error("Failed to load persisted settings:", error);
  }
};


// ---- System Health Store ----

interface HealthState {
  health: SystemHealth | null;
  isConnected: boolean;

  setHealth: (health: SystemHealth) => void;
  setIsConnected: (connected: boolean) => void;
}

export const useHealthStore = create<HealthState>()(
  immer((set) => ({
    health: null,
    isConnected: false,

    setHealth: (health) =>
      set((state) => {
        state.health = health;
        state.isConnected = health.status !== "unhealthy";
      }),

    setIsConnected: (connected) =>
      set((state) => {
        state.isConnected = connected;
      }),
  })),
);
