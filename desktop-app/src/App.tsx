/* ============================================================
   NODUS APP — Root Application Component
   ============================================================ */

import { useEffect, useCallback } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { StatusBar } from "@/components/layout/StatusBar";
import { ChatView } from "@/views/ChatView";
import { SearchView } from "@/views/SearchView";
import { DashboardView } from "@/views/DashboardView";
import { KnowledgeView } from "@/views/KnowledgeView";
import { TimelineView } from "@/views/TimelineView";
import { GraphView } from "@/views/GraphView";
import { FilesView } from "@/views/FilesView";
import { SettingsView } from "@/views/SettingsView";
import { ModelsView } from "@/views/ModelsView";
import { CommandPalette } from "@/components/shared/CommandPalette";
import { useAppStore, loadPersistedSettings, useHealthStore } from "@/stores";
import { getHealth } from "@/services/api";
import type { ViewId } from "@/types";

const VIEW_COMPONENTS: Record<ViewId, React.ComponentType> = {
  chat: ChatView,
  search: SearchView,
  dashboard: DashboardView,
  knowledge: KnowledgeView,
  timeline: TimelineView,
  graph: GraphView,
  files: FilesView,
  settings: SettingsView,
  models: ModelsView,
};

export function App() {
  const currentView = useAppStore((s) => s.currentView);
  const sidebarCollapsed = useAppStore((s) => s.sidebarCollapsed);
  const commandPaletteOpen = useAppStore((s) => s.commandPaletteOpen);
  const setCommandPaletteOpen = useAppStore((s) => s.setCommandPaletteOpen);

  const ViewComponent = VIEW_COMPONENTS[currentView];

  // Global keyboard shortcuts
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      // Ctrl/Cmd + K = Command Palette
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        setCommandPaletteOpen(!commandPaletteOpen);
      }
    },
    [commandPaletteOpen, setCommandPaletteOpen],
  );

  useEffect(() => {
    loadPersistedSettings();
    document.addEventListener("keydown", handleKeyDown);

    const fetchHealth = async () => {
      try {
        const data = await getHealth();
        useHealthStore.getState().setHealth({
          status: data.status as any,
          services: data.services.map((s) => ({
            name: s.name,
            status: s.status as any,
            latencyMs: s.latency_ms,
            lastCheck: Date.now(),
          })),
          resources: {
            cpuPercent: data.resources.cpu_percent,
            ramUsedMb: data.resources.ram_used_mb,
            ramTotalMb: data.resources.ram_total_mb,
            gpuPercent: data.resources.gpu_percent,
            gpuVramUsedMb: data.resources.gpu_vram_used_mb,
            gpuVramTotalMb: data.resources.gpu_vram_total_mb,
            diskUsedGb: 128,
            diskTotalGb: 512,
          },
        });
      } catch (e) {
        useHealthStore.getState().setIsConnected(false);
      }
    };

    fetchHealth();
    const interval = setInterval(fetchHealth, 5000);

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      clearInterval(interval);
    };
  }, [handleKeyDown]);

  return (
    <div className="flex h-screen overflow-hidden bg-surface-0">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <main
        className="flex flex-1 flex-col overflow-hidden transition-all"
        style={{
          marginLeft: sidebarCollapsed ? "64px" : "var(--spacing-sidebar)",
        }}
      >
        {/* Title Bar / Drag Region */}
        <div
          data-tauri-drag-region
          className="flex h-10 shrink-0 items-center justify-between border-b border-border-subtle bg-surface-1/50 px-4"
        >
          <span className="text-xs font-medium text-text-tertiary">
            {currentView.charAt(0).toUpperCase() + currentView.slice(1)}
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setCommandPaletteOpen(true)}
              className="btn-ghost text-xs"
              aria-label="Open command palette"
              id="command-palette-trigger"
            >
              <kbd className="rounded bg-surface-3 px-1.5 py-0.5 text-[10px] font-mono text-text-tertiary">
                ⌘K
              </kbd>
            </button>
          </div>
        </div>

        {/* View Content */}
        <div className="flex-1 overflow-hidden">
          <ViewComponent />
        </div>

        {/* Status Bar */}
        <StatusBar />
      </main>

      {/* Command Palette Overlay */}
      {commandPaletteOpen && (
        <CommandPalette onClose={() => setCommandPaletteOpen(false)} />
      )}
    </div>
  );
}
