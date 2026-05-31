/* ============================================================
   TIMELINE VIEW — Temporal Intelligence Interface
   ============================================================ */

import { useState, useMemo } from "react";
import { 
  Clock, 
  Calendar, 
  Search, 
  PlusCircle, 
  MessageSquare, 
  Eye, 
  BrainCircuit, 
  GitBranch, 
  Filter 
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import type { TimelineEvent, TimelineEventType } from "@/types";

const MOCK_TIMELINE_EVENTS: TimelineEvent[] = [
  {
    id: "evt-1",
    title: "Document Ingested: Nodus System Architecture Spec.pdf",
    description: "Successfully processed PDF file, generated 48 vector chunks, and pushed them to Qdrant vector store. Extracted 4 graph entities.",
    timestamp: Date.now() - 3600000 * 2, // 2 hours ago
    type: "document_added",
    source: "local-fs",
    entities: ["Nodus", "Qdrant", "SQLite", "AES-256"]
  },
  {
    id: "evt-2",
    title: "Entity Extracted: Qdrant Vector Store",
    description: "Identified 'Qdrant' as an organization entity inside the Nodus architecture document. Bound relationships: [Nodus] -> (uses) -> [Qdrant].",
    timestamp: Date.now() - 3600000 * 2.1,
    type: "entity_created",
    source: "graph-extractor",
    entities: ["Qdrant", "Nodus"]
  },
  {
    id: "evt-3",
    title: "AI Session: Local-First Setup Questions",
    description: "User initiated a session about offline configurations. Assistant proposed Ollama llama3.2 running locally to secure private logs.",
    timestamp: Date.now() - 3600000 * 24, // 1 day ago
    type: "conversation",
    source: "chat-system",
    entities: ["Ollama", "llama3.2"]
  },
  {
    id: "evt-4",
    title: "Insight Generated: Context Window Bottlenecks",
    description: "Timeline Intelligence detected recurrent queries regarding VRAM depletion during large file parsing. Suggested GGUF Q4 quantization.",
    timestamp: Date.now() - 3600000 * 24 * 3, // 3 days ago
    type: "insight_generated",
    source: "timeline-agent",
    entities: ["VRAM", "GGUF", "Q4_K_M"]
  },
  {
    id: "evt-5",
    title: "Agent Action: Schema Sync Task",
    description: "Research agent completed analysis on conflict resolution rules. Formed SQLite backup replica in local data directory.",
    timestamp: Date.now() - 3600000 * 24 * 6, // 6 days ago
    type: "agent_action",
    source: "research-agent",
    entities: ["SQLite", "Conflict Resolution"]
  }
];

export function TimelineView() {
  const [events] = useState<TimelineEvent[]>(MOCK_TIMELINE_EVENTS);
  const [filterType, setFilterType] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");

  const filteredEvents = useMemo(() => {
    return events.filter((evt) => {
      const matchesSearch = evt.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
                            evt.description.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesType = filterType === "all" || evt.type === filterType;
      return matchesSearch && matchesType;
    });
  }, [events, filterType, searchQuery]);

  const getEventIcon = (type: TimelineEventType) => {
    switch (type) {
      case "document_added":
        return <PlusCircle className="text-emerald-400" size={16} />;
      case "conversation":
        return <MessageSquare className="text-sky-400" size={16} />;
      case "entity_created":
        return <GitBranch className="text-purple-400" size={16} />;
      case "relationship_formed":
        return <GitBranch className="text-indigo-400" size={16} />;
      case "agent_action":
        return <BrainCircuit className="text-yellow-400" size={16} />;
      case "insight_generated":
        return <BrainCircuit className="text-rose-400" size={16} />;
      default:
        return <Clock className="text-text-secondary" size={16} />;
    }
  };

  const getEventBadgeColor = (type: TimelineEventType) => {
    switch (type) {
      case "document_added": return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
      case "conversation": return "bg-sky-500/10 text-sky-400 border-sky-500/20";
      case "entity_created": return "bg-purple-500/10 text-purple-400 border-purple-500/20";
      case "agent_action": return "bg-yellow-500/10 text-yellow-400 border-yellow-500/20";
      case "insight_generated": return "bg-rose-500/10 text-rose-400 border-rose-500/20";
      default: return "bg-surface-3 text-text-secondary border-border-subtle";
    }
  };

  return (
    <div className="h-full flex flex-col bg-surface-0 overflow-hidden">
      {/* Top Filter Bar */}
      <div className="flex flex-col gap-3 border-b border-border-subtle bg-surface-1/50 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Clock size={18} className="text-accent-400" />
            <h1 className="text-sm font-semibold uppercase tracking-wider text-text-primary">
              Timeline Intelligence
            </h1>
          </div>
          <span className="text-xs text-text-tertiary">
            Organizing memories sequentially
          </span>
        </div>

        <div className="flex gap-3">
          {/* Search */}
          <div className="relative flex-1">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-text-tertiary" />
            <input
              type="text"
              placeholder="Search historical events..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input-field pl-9 py-1.5"
            />
          </div>

          {/* Type Filter */}
          <div className="flex items-center gap-2 bg-surface-2 border border-border-subtle rounded-lg px-2 text-xs text-text-secondary">
            <Filter size={14} className="text-text-tertiary" />
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="bg-transparent border-none py-1.5 outline-none text-text-secondary focus:ring-0"
            >
              <option value="all">All Events</option>
              <option value="document_added">Document Ingests</option>
              <option value="entity_created">Entity Extractions</option>
              <option value="conversation">AI Chats</option>
              <option value="agent_action">Agent Actions</option>
              <option value="insight_generated">Timeline Insights</option>
            </select>
          </div>
        </div>
      </div>

      {/* Main Timeline Stream */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-3xl mx-auto relative pl-6 border-l-2 border-border-subtle space-y-8 py-2">
          {filteredEvents.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-20 text-center text-text-tertiary">
              <Calendar size={48} className="mb-3 stroke-1 text-text-tertiary" />
              <p className="text-sm font-medium">No events found in this timeframe.</p>
              <p className="text-xs text-text-tertiary mt-1">Refine your filters or index more local files.</p>
            </div>
          ) : (
            filteredEvents.map((evt) => (
              <div key={evt.id} className="relative group animate-fade-in">
                {/* Timeline dot marker */}
                <div className="absolute -left-[32px] top-1 flex h-6 w-6 items-center justify-center rounded-full bg-surface-0 border-2 border-border-strong group-hover:border-accent-500 transition-colors">
                  {getEventIcon(evt.type)}
                </div>

                {/* Event Card */}
                <div className="card bg-surface-1/50 border border-border-subtle p-5 group-hover:border-border-default hover:bg-surface-1 transition-all">
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-border-subtle/50 pb-3">
                    <div className="flex flex-wrap items-center gap-2.5">
                      <span className={`text-[9px] font-mono font-bold border rounded px-1.5 py-0.5 ${getEventBadgeColor(evt.type)}`}>
                        {evt.type.replace("_", " ").toUpperCase()}
                      </span>
                      <h2 className="text-xs font-bold text-text-primary">
                        {evt.title}
                      </h2>
                    </div>
                    <span className="text-[10px] text-text-tertiary font-mono shrink-0">
                      {formatDistanceToNow(evt.timestamp)} ago
                    </span>
                  </div>

                  <p className="text-xs text-text-secondary mt-3 leading-relaxed">
                    {evt.description}
                  </p>

                  {/* Entities Linked */}
                  {evt.entities.length > 0 && (
                    <div className="mt-4 flex flex-wrap items-center gap-1.5 border-t border-border-subtle/40 pt-3">
                      <span className="text-[9px] text-text-tertiary font-mono uppercase tracking-wider mr-1">
                        Entities:
                      </span>
                      {evt.entities.map((ent, idx) => (
                        <span 
                          key={idx} 
                          className="bg-surface-2 border border-border-subtle hover:border-accent-500/30 text-[10px] text-text-secondary rounded px-2 py-0.5 transition-colors cursor-pointer"
                        >
                          {ent}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Footer metadata */}
                  <div className="mt-3 flex items-center justify-between text-[10px] text-text-tertiary font-mono">
                    <span>Source: {evt.source}</span>
                    <button className="flex items-center gap-1 hover:text-accent-400 transition-colors">
                      <Eye size={12} /> Inspect Context
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
