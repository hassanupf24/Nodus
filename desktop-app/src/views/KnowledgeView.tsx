/* ============================================================
   KNOWLEDGE VIEW — Knowledge Explorer
   ============================================================ */

import { useState, useMemo } from "react";
import { 
  FileText, 
  Search, 
  Tag, 
  Info, 
  ExternalLink, 
  BookOpen, 
  FolderOpen,
  Trash2,
  Calendar
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";

interface DocumentItem {
  id: string;
  title: string;
  type: string;
  size: number;
  snippet: string;
  entities: { name: string; type: string }[];
  tags: string[];
  createdAt: number;
}

const MOCK_DOCUMENTS: DocumentItem[] = [
  {
    id: "doc-1",
    title: "Nodus System Architecture Spec.pdf",
    type: "pdf",
    size: 2450302,
    snippet: "This document describes the offline-first design of the Nodus personal knowledge operating system. Nodus integrates a local vector database (Qdrant) and a graph database (SQLite) to resolve user queries with contextual memory persistence.",
    entities: [
      { name: "Nodus", type: "project" },
      { name: "Qdrant", type: "organization" },
      { name: "SQLite", type: "organization" },
      { name: "AES-256", type: "concept" }
    ],
    tags: ["architecture", "spec", "offline-first"],
    createdAt: Date.now() - 3600000 * 2, // 2 hours ago
  },
  {
    id: "doc-2",
    title: "Meeting Notes - Knowledge Graph Design.md",
    type: "md",
    size: 14502,
    snippet: "We discussed the graph schema. Nodes will represent entities (person, project, concept) and edges will represent temporal relationships with weights indicating link strength based on co-occurrence in user sessions.",
    entities: [
      { name: "Knowledge Graph", type: "concept" },
      { name: "SQLite Schema", type: "concept" },
      { name: "Temporal Relationships", type: "concept" }
    ],
    tags: ["meeting", "design", "graph"],
    createdAt: Date.now() - 3600000 * 24, // 1 day ago
  },
  {
    id: "doc-3",
    title: "Research Paper - Retrieval Augmented Generation.pdf",
    type: "pdf",
    size: 4890322,
    snippet: "Abstract: We present a method to combine dense vector retrievals with sparse lexical retrievals over structural knowledge graphs. By ranking hybrid results, LLMs demonstrate lower rates of hallucination and more precise source attribution.",
    entities: [
      { name: "RAG", type: "concept" },
      { name: "Hybrid Search", type: "concept" },
      { name: "Dense Retrieval", type: "concept" }
    ],
    tags: ["research", "paper", "ai"],
    createdAt: Date.now() - 3600000 * 24 * 5, // 5 days ago
  },
  {
    id: "doc-4",
    title: "Personal Journal Entry.txt",
    type: "txt",
    size: 4096,
    snippet: "Thinking about building a personal memory assistant. It needs to automatically index documents I read, extract the key characters and technical terms, and let me search it in plain natural language.",
    entities: [
      { name: "Memory Assistant", type: "concept" },
      { name: "Local Vector Indexing", type: "concept" }
    ],
    tags: ["journal", "ideas", "personal"],
    createdAt: Date.now() - 3600000 * 24 * 12, // 12 days ago
  }
];

export function KnowledgeView() {
  const [documents, setDocuments] = useState<DocumentItem[]>(MOCK_DOCUMENTS);
  const [selectedDocId, setSelectedDocId] = useState<string | null>(MOCK_DOCUMENTS[0]?.id || null);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedType, setSelectedType] = useState<string>("all");
  const [selectedTag, setSelectedTag] = useState<string>("all");

  // Get all unique tags for filtering
  const allTags = useMemo(() => {
    const tags = new Set<string>();
    documents.forEach(doc => doc.tags.forEach(t => tags.add(t)));
    return Array.from(tags);
  }, [documents]);

  // Filter documents
  const filteredDocs = useMemo(() => {
    return documents.filter((doc) => {
      const matchesSearch = doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                            doc.snippet.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesType = selectedType === "all" || doc.type === selectedType;
      const matchesTag = selectedTag === "all" || doc.tags.includes(selectedTag);
      return matchesSearch && matchesType && matchesTag;
    });
  }, [documents, searchQuery, selectedType, selectedTag]);

  const selectedDoc = useMemo(() => {
    return documents.find(d => d.id === selectedDocId) || null;
  }, [documents, selectedDocId]);

  const handleDelete = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setDocuments(prev => prev.filter(d => d.id !== id));
    if (selectedDocId === id) {
      const remaining = documents.filter(d => d.id !== id);
      setSelectedDocId(remaining[0]?.id || null);
    }
  };

  const getFileIconColor = (type: string) => {
    switch (type) {
      case "pdf": return "text-red-400";
      case "md": return "text-emerald-400";
      case "txt": return "text-sky-400";
      default: return "text-text-secondary";
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes > 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    return `${(bytes / 1024).toFixed(1)} KB`;
  };

  return (
    <div className="flex h-full bg-surface-0 overflow-hidden">
      {/* Document Directory Column */}
      <div className="flex flex-1 flex-col border-r border-border-subtle h-full overflow-hidden">
        {/* Toolbar */}
        <div className="flex flex-col gap-3 border-b border-border-subtle bg-surface-1/50 p-4">
          <div className="flex items-center gap-2">
            <FolderOpen size={18} className="text-accent-400" />
            <h1 className="text-sm font-semibold uppercase tracking-wider text-text-primary">
              Knowledge Explorer
            </h1>
          </div>
          
          <div className="flex gap-2">
            {/* Search */}
            <div className="relative flex-1">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-text-tertiary" />
              <input
                type="text"
                placeholder="Search knowledge sources..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="input-field pl-9 py-1.5"
              />
            </div>
            
            {/* Type Filter */}
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="bg-surface-2 border border-border-subtle rounded-lg px-2 text-xs text-text-secondary outline-none focus:border-accent-500"
            >
              <option value="all">All Types</option>
              <option value="pdf">PDF</option>
              <option value="md">Markdown</option>
              <option value="txt">Text</option>
            </select>

            {/* Tag Filter */}
            <select
              value={selectedTag}
              onChange={(e) => setSelectedTag(e.target.value)}
              className="bg-surface-2 border border-border-subtle rounded-lg px-2 text-xs text-text-secondary outline-none focus:border-accent-500"
            >
              <option value="all">All Tags</option>
              {allTags.map(t => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Document List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          {filteredDocs.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-20 text-center text-text-tertiary">
              <FileText size={48} className="mb-3 stroke-1 text-text-tertiary" />
              <p className="text-sm font-medium">No files match your filter settings.</p>
              <p className="text-xs text-text-tertiary mt-1">Try resetting search query or metadata tags.</p>
            </div>
          ) : (
            filteredDocs.map((doc) => (
              <div
                key={doc.id}
                onClick={() => setSelectedDocId(doc.id)}
                className={`group flex items-start justify-between rounded-lg p-3.5 border transition-all cursor-pointer ${
                  selectedDocId === doc.id
                    ? "bg-accent-500/10 border-accent-500/30"
                    : "bg-surface-1/50 border-border-subtle hover:border-border-default"
                }`}
              >
                <div className="flex gap-3 min-w-0 flex-1">
                  <FileText className={`mt-0.5 shrink-0 ${getFileIconColor(doc.type)}`} size={18} />
                  <div className="min-w-0 flex-1">
                    <h2 className="text-xs font-semibold text-text-primary group-hover:text-accent-400 transition-colors truncate">
                      {doc.title}
                    </h2>
                    <p className="text-[10px] text-text-tertiary mt-1 truncate">
                      {doc.snippet}
                    </p>
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      <span className="text-[9px] text-text-tertiary font-mono">
                        {formatSize(doc.size)}
                      </span>
                      <span className="text-[9px] text-text-tertiary">•</span>
                      <span className="text-[9px] text-text-tertiary">
                        {formatDistanceToNow(doc.createdAt)} ago
                      </span>
                      {doc.tags.slice(0, 2).map((tag) => (
                        <span key={tag} className="badge badge-accent py-0 px-1 text-[8px]">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                <button 
                  onClick={(e) => handleDelete(doc.id, e)}
                  className="ml-2 p-1 text-text-tertiary hover:text-error rounded hover:bg-surface-3 opacity-0 group-hover:opacity-100 transition-all"
                  title="Remove from knowledge core"
                >
                  <Trash2 size={13} />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Document Detail Inspector */}
      {selectedDoc ? (
        <div className="w-[380px] bg-surface-1 border-l border-border-subtle h-full flex flex-col overflow-hidden animate-slide-in-right">
          {/* Header */}
          <div className="p-4 border-b border-border-subtle bg-surface-2/30">
            <span className="badge badge-accent mb-2 uppercase text-[9px] font-mono">
              Source Inspector
            </span>
            <h2 className="text-sm font-bold text-text-primary leading-tight break-all">
              {selectedDoc.title}
            </h2>
            <div className="flex gap-3 mt-2 text-xs text-text-secondary">
              <span className="flex items-center gap-1">
                <Calendar size={12} /> {new Date(selectedDoc.createdAt).toLocaleDateString()}
              </span>
              <span>•</span>
              <span>{formatSize(selectedDoc.size)}</span>
            </div>
          </div>

          {/* Details Scroll Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-6">
            {/* Snippet Card */}
            <div className="space-y-2">
              <span className="text-[10px] font-semibold uppercase tracking-wider text-text-tertiary flex items-center gap-1">
                <BookOpen size={12} /> Content Preview
              </span>
              <div className="rounded-lg bg-surface-0 border border-border-subtle p-3 text-xs text-text-secondary leading-relaxed font-mono whitespace-pre-wrap">
                {selectedDoc.snippet}
              </div>
            </div>

            {/* Extracted Entities */}
            <div className="space-y-2.5">
              <span className="text-[10px] font-semibold uppercase tracking-wider text-text-tertiary flex items-center gap-1">
                <Info size={12} /> Graph Entities ({selectedDoc.entities.length})
              </span>
              <div className="flex flex-wrap gap-2">
                {selectedDoc.entities.map((ent, idx) => (
                  <div 
                    key={idx} 
                    className="flex items-center gap-1.5 rounded bg-surface-2 border border-border-subtle px-2 py-1 text-xs"
                  >
                    <span className="h-1.5 w-1.5 rounded-full bg-accent-500" />
                    <span className="font-semibold text-text-primary">{ent.name}</span>
                    <span className="text-[9px] text-text-tertiary uppercase font-mono">({ent.type})</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Ingestion Meta */}
            <div className="space-y-2">
              <span className="text-[10px] font-semibold uppercase tracking-wider text-text-tertiary flex items-center gap-1">
                <Tag size={12} /> Metadata Tags
              </span>
              <div className="flex flex-wrap gap-1.5">
                {selectedDoc.tags.map((tag) => (
                  <span key={tag} className="badge badge-accent text-xs">
                    #{tag}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Footer Action */}
          <div className="p-4 border-t border-border-subtle bg-surface-2/30 flex gap-2">
            <button className="btn-primary w-full text-xs flex justify-center items-center gap-1">
              Ask about this file <ExternalLink size={12} />
            </button>
          </div>
        </div>
      ) : (
        <div className="w-[380px] bg-surface-1 border-l border-border-subtle h-full flex flex-col justify-center items-center text-center p-6 text-text-tertiary">
          <BookOpen size={36} className="mb-2 stroke-1 text-text-tertiary" />
          <p className="text-xs">Select a source file from the list to view its semantic structure and entity associations.</p>
        </div>
      )}
    </div>
  );
}
