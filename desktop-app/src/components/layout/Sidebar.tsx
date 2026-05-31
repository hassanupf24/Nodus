/* ============================================================
   SIDEBAR — Main Navigation
   Premium glassmorphism sidebar with icon + label nav items,
   conversation list, and user status
   ============================================================ */

import { useState, useMemo } from "react";
import { useAppStore, useChatStore, useHealthStore } from "@/stores";
import type { ViewId } from "@/types";
import {
  MessageSquare,
  Search,
  LayoutDashboard,
  BookOpen,
  Clock,
  GitBranch,
  FolderOpen,
  Settings,
  Cpu,
  ChevronLeft,
  ChevronRight,
  Plus,
  Trash2,
  Zap,
  Shield,
} from "lucide-react";
import clsx from "clsx";

interface NavEntry {
  id: ViewId;
  label: string;
  icon: React.ReactNode;
  section: "main" | "tools" | "system";
}

const NAV_ITEMS: NavEntry[] = [
  { id: "chat", label: "AI Chat", icon: <MessageSquare size={18} />, section: "main" },
  { id: "search", label: "Search", icon: <Search size={18} />, section: "main" },
  { id: "dashboard", label: "Dashboard", icon: <LayoutDashboard size={18} />, section: "main" },
  { id: "knowledge", label: "Knowledge", icon: <BookOpen size={18} />, section: "tools" },
  { id: "timeline", label: "Timeline", icon: <Clock size={18} />, section: "tools" },
  { id: "graph", label: "Graph", icon: <GitBranch size={18} />, section: "tools" },
  { id: "files", label: "Files", icon: <FolderOpen size={18} />, section: "tools" },
  { id: "models", label: "Models", icon: <Cpu size={18} />, section: "system" },
  { id: "settings", label: "Settings", icon: <Settings size={18} />, section: "system" },
];

export function Sidebar() {
  const currentView = useAppStore((s) => s.currentView);
  const setCurrentView = useAppStore((s) => s.setCurrentView);
  const sidebarCollapsed = useAppStore((s) => s.sidebarCollapsed);
  const toggleSidebar = useAppStore((s) => s.toggleSidebar);
  const isConnected = useHealthStore((s) => s.isConnected);

  const conversations = useChatStore((s) => s.conversations);
  const activeConversationId = useChatStore((s) => s.activeConversationId);
  const createConversation = useChatStore((s) => s.createConversation);
  const setActiveConversation = useChatStore((s) => s.setActiveConversation);
  const deleteConversation = useChatStore((s) => s.deleteConversation);

  const [hoveredConvId, setHoveredConvId] = useState<string | null>(null);

  const sections = useMemo(() => {
    const main = NAV_ITEMS.filter((n) => n.section === "main");
    const tools = NAV_ITEMS.filter((n) => n.section === "tools");
    const system = NAV_ITEMS.filter((n) => n.section === "system");
    return { main, tools, system };
  }, []);

  const recentConversations = conversations.slice(0, 8);

  return (
    <aside
      className={clsx(
        "fixed left-0 top-0 z-30 flex h-full flex-col border-r border-border-subtle bg-surface-1 transition-all duration-200",
        sidebarCollapsed ? "w-16" : "w-[var(--spacing-sidebar)]",
      )}
    >
      {/* Logo / Brand */}
      <div
        data-tauri-drag-region
        className="flex h-14 shrink-0 items-center justify-between border-b border-border-subtle px-4"
      >
        {!sidebarCollapsed && (
          <div className="flex items-center gap-2.5 animate-fade-in">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-accent-600 to-accent-400 shadow-glow">
              <Zap size={16} className="text-white" />
            </div>
            <div>
              <h1 className="text-sm font-bold gradient-text tracking-tight">NODUS</h1>
              <p className="text-[10px] text-text-tertiary leading-none">Private AI Memory</p>
            </div>
          </div>
        )}
        {sidebarCollapsed && (
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-accent-600 to-accent-400 shadow-glow mx-auto">
            <Zap size={16} className="text-white" />
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-2.5 py-3">
        {/* Main Section */}
        <div className="mb-4">
          {!sidebarCollapsed && (
            <p className="mb-1.5 px-2 text-[10px] font-semibold uppercase tracking-widest text-text-tertiary">
              Main
            </p>
          )}
          <div className="space-y-0.5">
            {sections.main.map((item) => (
              <button
                key={item.id}
                id={`nav-${item.id}`}
                onClick={() => setCurrentView(item.id)}
                className={clsx("nav-item w-full", currentView === item.id && "active")}
                title={sidebarCollapsed ? item.label : undefined}
              >
                {item.icon}
                {!sidebarCollapsed && <span>{item.label}</span>}
              </button>
            ))}
          </div>
        </div>

        {/* Recent Conversations (only in Chat view context) */}
        {!sidebarCollapsed && currentView === "chat" && (
          <div className="mb-4 animate-fade-in">
            <div className="mb-1.5 flex items-center justify-between px-2">
              <p className="text-[10px] font-semibold uppercase tracking-widest text-text-tertiary">
                Conversations
              </p>
              <button
                onClick={() => {
                  createConversation();
                  setCurrentView("chat");
                }}
                className="btn-ghost p-1"
                aria-label="New conversation"
                id="new-conversation-btn"
              >
                <Plus size={14} />
              </button>
            </div>
            <div className="space-y-0.5 stagger-children">
              {recentConversations.map((conv) => (
                <div
                  key={conv.id}
                  className={clsx(
                    "group flex items-center gap-2 rounded-md px-2 py-1.5 text-xs cursor-pointer transition-all",
                    activeConversationId === conv.id
                      ? "bg-accent-500/10 text-accent-400"
                      : "text-text-secondary hover:bg-surface-3 hover:text-text-primary",
                  )}
                  onClick={() => setActiveConversation(conv.id)}
                  onMouseEnter={() => setHoveredConvId(conv.id)}
                  onMouseLeave={() => setHoveredConvId(null)}
                >
                  <MessageSquare size={12} className="shrink-0 opacity-50" />
                  <span className="flex-1 truncate">{conv.title}</span>
                  {hoveredConvId === conv.id && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteConversation(conv.id);
                      }}
                      className="shrink-0 p-0.5 text-text-tertiary hover:text-error transition-colors"
                      aria-label={`Delete conversation: ${conv.title}`}
                    >
                      <Trash2 size={12} />
                    </button>
                  )}
                </div>
              ))}
              {recentConversations.length === 0 && (
                <p className="px-2 py-2 text-[11px] text-text-tertiary italic">
                  No conversations yet
                </p>
              )}
            </div>
          </div>
        )}

        {/* Tools Section */}
        <div className="mb-4">
          {!sidebarCollapsed && (
            <p className="mb-1.5 px-2 text-[10px] font-semibold uppercase tracking-widest text-text-tertiary">
              Tools
            </p>
          )}
          <div className="space-y-0.5">
            {sections.tools.map((item) => (
              <button
                key={item.id}
                id={`nav-${item.id}`}
                onClick={() => setCurrentView(item.id)}
                className={clsx("nav-item w-full", currentView === item.id && "active")}
                title={sidebarCollapsed ? item.label : undefined}
              >
                {item.icon}
                {!sidebarCollapsed && <span>{item.label}</span>}
              </button>
            ))}
          </div>
        </div>

        {/* System Section */}
        <div>
          {!sidebarCollapsed && (
            <p className="mb-1.5 px-2 text-[10px] font-semibold uppercase tracking-widest text-text-tertiary">
              System
            </p>
          )}
          <div className="space-y-0.5">
            {sections.system.map((item) => (
              <button
                key={item.id}
                id={`nav-${item.id}`}
                onClick={() => setCurrentView(item.id)}
                className={clsx("nav-item w-full", currentView === item.id && "active")}
                title={sidebarCollapsed ? item.label : undefined}
              >
                {item.icon}
                {!sidebarCollapsed && <span>{item.label}</span>}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Bottom — Status & Collapse */}
      <div className="shrink-0 border-t border-border-subtle p-2.5">
        {/* Connection Status */}
        {!sidebarCollapsed && (
          <div className="mb-2 flex items-center gap-2 rounded-md bg-surface-2 px-3 py-2 animate-fade-in">
            <div
              className={clsx(
                "h-2 w-2 rounded-full",
                isConnected
                  ? "bg-success animate-pulse"
                  : "bg-error",
              )}
            />
            <span className="text-[11px] text-text-secondary">
              {isConnected ? "AI Services Connected" : "Services Offline"}
            </span>
            <Shield size={12} className="ml-auto text-success opacity-60" />
          </div>
        )}

        {/* Collapse Toggle */}
        <button
          onClick={toggleSidebar}
          className="nav-item w-full justify-center"
          aria-label={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          id="sidebar-toggle"
        >
          {sidebarCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
          {!sidebarCollapsed && <span>Collapse</span>}
        </button>
      </div>
    </aside>
  );
}
