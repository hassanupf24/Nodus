/* ============================================================
   SEARCH VIEW — Semantic Search Interface
   Hybrid search with filters, mode selection, and results
   ============================================================ */

import { useState, useCallback, useRef, useEffect } from "react";
import { useSearchStore } from "@/stores";
import { search } from "@/services/api";
import type { SearchMode } from "@/types";
import {
  Search,
  SlidersHorizontal,
  Sparkles,
  Type,
  Blend,
  FileText,
  Clock,
  Tag,
  X,
  Loader2,
} from "lucide-react";
import clsx from "clsx";

const SEARCH_MODES: { id: SearchMode; label: string; icon: React.ReactNode; desc: string }[] = [
  { id: "hybrid", label: "Hybrid", icon: <Blend size={14} />, desc: "Semantic + keyword" },
  { id: "semantic", label: "Semantic", icon: <Sparkles size={14} />, desc: "Meaning-based" },
  { id: "keyword", label: "Keyword", icon: <Type size={14} />, desc: "Exact matching" },
];

export function SearchView() {
  const query = useSearchStore((s) => s.query);
  const mode = useSearchStore((s) => s.mode);
  const results = useSearchStore((s) => s.results);
  const isSearching = useSearchStore((s) => s.isSearching);
  const totalResults = useSearchStore((s) => s.totalResults);
  const queryTimeMs = useSearchStore((s) => s.queryTimeMs);
  const setQuery = useSearchStore((s) => s.setQuery);
  const setMode = useSearchStore((s) => s.setMode);
  const setResults = useSearchStore((s) => s.setResults);
  const setIsSearching = useSearchStore((s) => s.setIsSearching);

  const [showFilters, setShowFilters] = useState(false);
  const [selectedFileTypes, setSelectedFileTypes] = useState<string[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSearch = useCallback(async () => {
    if (!query.trim()) return;
    setIsSearching(true);

    try {
      const response = await search({
        query: query.trim(),
        mode,
        limit: 20,
        filters: selectedFileTypes.length > 0 ? { file_types: selectedFileTypes } : undefined,
      });
      setResults(
        response.results.map((r) => ({
          id: r.id,
          content: r.content,
          score: r.score,
          source: r.source,
          sourceType: r.source_type,
          metadata: r.metadata,
          highlights: r.highlights,
          timestamp: new Date(r.timestamp).getTime(),
        })),
        response.total,
        response.query_time_ms,
      );
    } catch {
      setResults([], 0, 0);
    }
  }, [query, mode, selectedFileTypes, setIsSearching, setResults]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter") {
        handleSearch();
      }
    },
    [handleSearch],
  );

  return (
    <div className="flex h-full flex-col" id="search-view">
      {/* Search Header */}
      <div className="shrink-0 border-b border-border-subtle bg-surface-1/30 p-6">
        <div className="mx-auto max-w-3xl">
          <h2 className="mb-4 text-lg font-semibold gradient-text">Semantic Search</h2>

          {/* Search Input */}
          <div className="relative flex items-center gap-2 rounded-xl border border-border-subtle bg-surface-2 p-1 focus-within:border-accent-500 focus-within:shadow-glow transition-all">
            <Search size={18} className="ml-3 shrink-0 text-text-tertiary" />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Search your knowledge base..."
              className="flex-1 bg-transparent py-2.5 text-sm text-text-primary outline-none placeholder:text-text-tertiary"
              id="search-input"
            />
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={clsx(
                "btn-ghost p-2",
                showFilters && "text-accent-400",
              )}
              aria-label="Toggle filters"
              id="search-filters-toggle"
            >
              <SlidersHorizontal size={16} />
            </button>
            <button
              onClick={handleSearch}
              disabled={!query.trim() || isSearching}
              className="btn-primary py-2 px-4"
              id="search-submit"
            >
              {isSearching ? <Loader2 size={14} className="animate-spin" /> : "Search"}
            </button>
          </div>

          {/* Search Mode Selector */}
          <div className="mt-3 flex items-center gap-2">
            {SEARCH_MODES.map((m) => (
              <button
                key={m.id}
                onClick={() => setMode(m.id)}
                className={clsx(
                  "flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition-all",
                  mode === m.id
                    ? "bg-accent-500/15 text-accent-400 border border-accent-500/30"
                    : "text-text-tertiary hover:text-text-secondary hover:bg-surface-3",
                )}
                id={`search-mode-${m.id}`}
              >
                {m.icon}
                {m.label}
              </button>
            ))}
            <span className="ml-auto text-[11px] text-text-tertiary">
              {mode === "hybrid" && "Combines semantic understanding with keyword matching"}
              {mode === "semantic" && "Finds results by meaning, not exact words"}
              {mode === "keyword" && "Traditional text matching"}
            </span>
          </div>

          {/* Filters Panel */}
          {showFilters && (
            <div className="mt-3 rounded-lg border border-border-subtle bg-surface-2 p-4 animate-fade-in">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-xs font-semibold text-text-secondary">Filters</h3>
                <button
                  onClick={() => setShowFilters(false)}
                  className="btn-ghost p-1"
                  aria-label="Close filters"
                >
                  <X size={14} />
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {["PDF", "DOCX", "Markdown", "HTML", "Text", "Image", "Audio"].map((ft) => (
                  <button
                    key={ft}
                    onClick={() => {
                      setSelectedFileTypes((prev) =>
                        prev.includes(ft) ? prev.filter((t) => t !== ft) : [...prev, ft],
                      );
                    }}
                    className={clsx(
                      "flex items-center gap-1 rounded-full px-3 py-1 text-xs transition-all",
                      selectedFileTypes.includes(ft)
                        ? "bg-accent-500/15 text-accent-400 border border-accent-500/30"
                        : "bg-surface-3 text-text-tertiary hover:text-text-secondary",
                    )}
                  >
                    <FileText size={10} />
                    {ft}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Results */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="mx-auto max-w-3xl">
          {/* Results Header */}
          {results.length > 0 && (
            <div className="mb-4 flex items-center justify-between">
              <p className="text-xs text-text-tertiary">
                {totalResults} result{totalResults !== 1 ? "s" : ""} in {queryTimeMs}ms
              </p>
            </div>
          )}

          {/* Result Cards */}
          <div className="space-y-3 stagger-children">
            {results.map((result) => (
              <div
                key={result.id}
                className="card card-interactive"
                id={`result-${result.id}`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <FileText size={14} className="text-accent-400" />
                    <span className="text-xs font-medium text-text-primary truncate">
                      {result.source}
                    </span>
                    <span className="badge badge-accent">{result.sourceType}</span>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <span className="text-[10px] text-text-tertiary">
                      Score: {(result.score * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
                <p className="text-sm text-text-secondary leading-relaxed line-clamp-3">
                  {result.content}
                </p>
                <div className="mt-2 flex items-center gap-3">
                  <div className="flex items-center gap-1 text-[10px] text-text-tertiary">
                    <Clock size={10} />
                    {new Date(result.timestamp).toLocaleDateString()}
                  </div>
                  {result.highlights.length > 0 && (
                    <div className="flex items-center gap-1 text-[10px] text-text-tertiary">
                      <Tag size={10} />
                      {result.highlights.slice(0, 3).join(", ")}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Empty State */}
          {results.length === 0 && !isSearching && (
            <div className="flex flex-col items-center justify-center py-20 text-center animate-fade-in">
              <Search size={48} className="text-text-tertiary opacity-30 mb-4" />
              <h3 className="text-sm font-medium text-text-secondary">
                {query ? "No results found" : "Search your knowledge base"}
              </h3>
              <p className="mt-1 text-xs text-text-tertiary max-w-sm">
                {query
                  ? "Try different keywords or switch to semantic search mode"
                  : "Enter a query to find relevant information across all your documents and conversations"}
              </p>
            </div>
          )}

          {/* Loading */}
          {isSearching && (
            <div className="flex flex-col items-center justify-center py-20 animate-fade-in">
              <Loader2 size={32} className="animate-spin text-accent-400 mb-3" />
              <p className="text-sm text-text-tertiary">Searching...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
