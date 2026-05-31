/* ============================================================
   COMMAND PALETTE — Quick actions overlay (⌘K)
   ============================================================ */

import { useState, useEffect, useRef, useMemo } from "react";
import { useAppStore, useChatStore } from "@/stores";
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
  Plus,
  Zap,
} from "lucide-react";
import clsx from "clsx";

interface CommandItem {
  id: string;
  label: string;
  description: string;
  icon: React.ReactNode;
  action: () => void;
  category: string;
}

interface CommandPaletteProps {
  onClose: () => void;
}

export function CommandPalette({ onClose }: CommandPaletteProps) {
  const [query, setQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);

  const setCurrentView = useAppStore((s) => s.setCurrentView);
  const createConversation = useChatStore((s) => s.createConversation);

  const commands: CommandItem[] = useMemo(
    () => [
      {
        id: "new-chat",
        label: "New Conversation",
        description: "Start a new AI chat",
        icon: <Plus size={16} />,
        action: () => {
          createConversation();
          setCurrentView("chat");
        },
        category: "Actions",
      },
      {
        id: "nav-chat",
        label: "AI Chat",
        description: "Go to AI Chat",
        icon: <MessageSquare size={16} />,
        action: () => setCurrentView("chat"),
        category: "Navigation",
      },
      {
        id: "nav-search",
        label: "Semantic Search",
        description: "Search your knowledge base",
        icon: <Search size={16} />,
        action: () => setCurrentView("search"),
        category: "Navigation",
      },
      {
        id: "nav-dashboard",
        label: "Dashboard",
        description: "View system dashboard",
        icon: <LayoutDashboard size={16} />,
        action: () => setCurrentView("dashboard"),
        category: "Navigation",
      },
      {
        id: "nav-knowledge",
        label: "Knowledge Explorer",
        description: "Browse knowledge base",
        icon: <BookOpen size={16} />,
        action: () => setCurrentView("knowledge"),
        category: "Navigation",
      },
      {
        id: "nav-timeline",
        label: "Timeline",
        description: "View timeline of events",
        icon: <Clock size={16} />,
        action: () => setCurrentView("timeline"),
        category: "Navigation",
      },
      {
        id: "nav-graph",
        label: "Knowledge Graph",
        description: "Visual knowledge graph",
        icon: <GitBranch size={16} />,
        action: () => setCurrentView("graph"),
        category: "Navigation",
      },
      {
        id: "nav-files",
        label: "File Browser",
        description: "Browse ingested files",
        icon: <FolderOpen size={16} />,
        action: () => setCurrentView("files"),
        category: "Navigation",
      },
      {
        id: "nav-models",
        label: "Model Manager",
        description: "Manage AI models",
        icon: <Cpu size={16} />,
        action: () => setCurrentView("models"),
        category: "Navigation",
      },
      {
        id: "nav-settings",
        label: "Settings",
        description: "App settings",
        icon: <Settings size={16} />,
        action: () => setCurrentView("settings"),
        category: "Navigation",
      },
    ],
    [createConversation, setCurrentView],
  );

  const filtered = useMemo(() => {
    if (!query.trim()) return commands;
    const lowerQuery = query.toLowerCase();
    return commands.filter(
      (cmd) =>
        cmd.label.toLowerCase().includes(lowerQuery) ||
        cmd.description.toLowerCase().includes(lowerQuery),
    );
  }, [query, commands]);

  // Reset selection when filter changes
  useEffect(() => {
    setSelectedIndex(0);
  }, [filtered.length]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case "ArrowDown":
          e.preventDefault();
          setSelectedIndex((prev) => Math.min(prev + 1, filtered.length - 1));
          break;
        case "ArrowUp":
          e.preventDefault();
          setSelectedIndex((prev) => Math.max(prev - 1, 0));
          break;
        case "Enter":
          e.preventDefault();
          if (filtered[selectedIndex]) {
            filtered[selectedIndex].action();
            onClose();
          }
          break;
        case "Escape":
          e.preventDefault();
          onClose();
          break;
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [filtered, selectedIndex, onClose]);

  // Scroll selected item into view
  useEffect(() => {
    const list = listRef.current;
    if (!list) return;
    const items = list.querySelectorAll("[data-command-item]");
    const selected = items[selectedIndex];
    if (selected) {
      selected.scrollIntoView({ block: "nearest" });
    }
  }, [selectedIndex]);

  // Group by category
  const grouped = useMemo(() => {
    const groups: Record<string, CommandItem[]> = {};
    for (const item of filtered) {
      if (!groups[item.category]) groups[item.category] = [];
      groups[item.category]!.push(item);
    }
    return groups;
  }, [filtered]);

  let globalIndex = 0;

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center bg-black/50 backdrop-blur-sm pt-[15vh] animate-fade-in"
      onClick={onClose}
      id="command-palette-overlay"
    >
      <div
        className="w-full max-w-lg rounded-xl border border-border-default bg-surface-1 shadow-floating animate-scale-in overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Input */}
        <div className="flex items-center gap-3 border-b border-border-subtle px-4 py-3">
          <Zap size={16} className="text-accent-400 shrink-0" />
          <input
            ref={inputRef}
            type="text"
            placeholder="Search commands..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1 bg-transparent text-sm text-text-primary outline-none placeholder:text-text-tertiary"
            id="command-palette-input"
          />
          <kbd className="rounded bg-surface-3 px-1.5 py-0.5 text-[10px] font-mono text-text-tertiary">
            ESC
          </kbd>
        </div>

        {/* Results */}
        <div ref={listRef} className="max-h-80 overflow-y-auto p-2">
          {Object.entries(grouped).map(([category, items]) => (
            <div key={category}>
              <p className="px-2 py-1.5 text-[10px] font-semibold uppercase tracking-widest text-text-tertiary">
                {category}
              </p>
              {items.map((item) => {
                const idx = globalIndex++;
                return (
                  <button
                    key={item.id}
                    data-command-item
                    className={clsx(
                      "flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left transition-colors",
                      idx === selectedIndex
                        ? "bg-accent-500/15 text-accent-400"
                        : "text-text-secondary hover:bg-surface-3",
                    )}
                    onClick={() => {
                      item.action();
                      onClose();
                    }}
                    onMouseEnter={() => setSelectedIndex(idx)}
                    id={`command-${item.id}`}
                  >
                    <span className="shrink-0 opacity-70">{item.icon}</span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-text-primary">{item.label}</p>
                      <p className="text-xs text-text-tertiary truncate">{item.description}</p>
                    </div>
                  </button>
                );
              })}
            </div>
          ))}

          {filtered.length === 0 && (
            <div className="py-8 text-center text-sm text-text-tertiary">
              No matching commands
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
