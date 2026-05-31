/* ============================================================
   GRAPH VIEW — Personal Knowledge Graph
   ============================================================ */

import { useState, useCallback, useMemo } from "react";
import { 
  Network, 
  Search, 
  HelpCircle, 
  BookOpen, 
  Building2, 
  Brain, 
  Layers 
} from "lucide-react";
import { 
  ReactFlow, 
  MiniMap, 
  Controls, 
  Background, 
  useNodesState, 
  useEdgesState,
  Node,
  Edge
} from "@xyflow/react";

// Custom styles for React Flow elements
import "@xyflow/react/dist/style.css";

const INITIAL_NODES: Node[] = [
  {
    id: "nodus",
    type: "default",
    data: { label: "Nodus System", type: "project", description: "Local-First private AI knowledge memory platform." },
    position: { x: 250, y: 150 },
    style: { background: "oklch(0.58 0.26 270 / 0.15)", border: "1px solid var(--color-accent-500)", color: "var(--color-text-primary)", borderRadius: "var(--radius-md)", padding: "10px", width: 140 }
  },
  {
    id: "qdrant",
    type: "default",
    data: { label: "Qdrant Vector DB", type: "organization", description: "Embedded high performance vector indexer." },
    position: { x: 100, y: 300 },
    style: { background: "oklch(0.72 0.19 155 / 0.15)", border: "1px solid var(--color-success)", color: "var(--color-text-primary)", borderRadius: "var(--radius-md)", padding: "10px", width: 140 }
  },
  {
    id: "sqlite",
    type: "default",
    data: { label: "SQLite DB", type: "organization", description: "Relational storage for notes and structural graphs." },
    position: { x: 400, y: 300 },
    style: { background: "oklch(0.72 0.19 155 / 0.15)", border: "1px solid var(--color-success)", color: "var(--color-text-primary)", borderRadius: "var(--radius-md)", padding: "10px", width: 140 }
  },
  {
    id: "rag",
    type: "default",
    data: { label: "RAG Engine", type: "concept", description: "Retrieval Augmented Generation matching queries to embeddings." },
    position: { x: 250, y: 420 },
    style: { background: "oklch(0.70 0.15 240 / 0.15)", border: "1px solid var(--color-info)", color: "var(--color-text-primary)", borderRadius: "var(--radius-md)", padding: "10px", width: 140 }
  },
  {
    id: "aes",
    type: "default",
    data: { label: "AES-256 Encryption", type: "concept", description: "Cryptographic layer protecting SQLite data at rest." },
    position: { x: 550, y: 200 },
    style: { background: "oklch(0.65 0.22 25 / 0.15)", border: "1px solid var(--color-error)", color: "var(--color-text-primary)", borderRadius: "var(--radius-md)", padding: "10px", width: 140 }
  }
];

const INITIAL_EDGES: Edge[] = [
  { id: "e-nodus-qdrant", source: "nodus", target: "qdrant", label: "indexes to", style: { stroke: "var(--color-border-strong)" } },
  { id: "e-nodus-sqlite", source: "nodus", target: "sqlite", label: "persists in", style: { stroke: "var(--color-border-strong)" } },
  { id: "e-qdrant-rag", source: "qdrant", target: "rag", label: "feeds", style: { stroke: "var(--color-border-strong)" } },
  { id: "e-sqlite-rag", source: "sqlite", target: "rag", label: "joins", style: { stroke: "var(--color-border-strong)" } },
  { id: "e-sqlite-aes", source: "sqlite", target: "aes", label: "encrypted by", style: { stroke: "var(--color-border-strong)" } }
];

export function GraphView() {
  const [nodes, setNodes, onNodesChange] = useNodesState(INITIAL_NODES);
  const [edges, setEdges, onEdgesChange] = useEdgesState(INITIAL_EDGES);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedType, setSelectedType] = useState<string>("all");

  const onNodeClick = useCallback((_: React.MouseEvent, node: Node) => {
    setSelectedNodeId(node.id);
  }, []);

  const onPaneClick = useCallback(() => {
    setSelectedNodeId(null);
  }, []);

  const selectedNode = useMemo(() => {
    return nodes.find((n) => n.id === selectedNodeId) || null;
  }, [nodes, selectedNodeId]);

  // Filters based on criteria
  const handleApplyFilters = () => {
    let filteredNodes = INITIAL_NODES;

    if (selectedType !== "all") {
      filteredNodes = filteredNodes.filter((n) => (n.data as any).type === selectedType);
    }
    if (searchQuery.trim() !== "") {
      filteredNodes = filteredNodes.filter((n) => 
        (n.data as any).label.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    setNodes(filteredNodes);
    
    // Filter edges to only keep those connecting active nodes
    const nodeIds = new Set(filteredNodes.map((n) => n.id));
    const filteredEdges = INITIAL_EDGES.filter(
      (e) => nodeIds.has(e.source) && nodeIds.has(e.target)
    );
    setEdges(filteredEdges);
  };

  const getEntityIcon = (type: string) => {
    switch (type) {
      case "project": return <Layers size={14} className="text-accent-400" />;
      case "organization": return <Building2 size={14} className="text-success" />;
      case "concept": return <Brain size={14} className="text-info" />;
      default: return <HelpCircle size={14} className="text-text-tertiary" />;
    }
  };

  return (
    <div className="flex h-full bg-surface-0 overflow-hidden relative">
      {/* Graph Area */}
      <div className="flex-1 h-full overflow-hidden relative">
        {/* Floating toolbar */}
        <div className="absolute left-4 top-4 z-10 flex flex-col gap-2 rounded-xl border border-border-subtle bg-surface-1/90 backdrop-blur p-4 w-[280px]">
          <div className="flex items-center gap-2 mb-2">
            <Network size={16} className="text-accent-400" />
            <span className="text-xs font-semibold uppercase tracking-wider text-text-primary">
              Graph Explorer
            </span>
          </div>

          <div className="space-y-3">
            <div className="relative">
              <Search className="absolute left-2.5 top-2 h-3.5 w-3.5 text-text-tertiary" />
              <input
                type="text"
                placeholder="Find node..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="input-field pl-8 py-1 text-xs"
              />
            </div>

            <div className="flex gap-2">
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="flex-1 bg-surface-2 border border-border-subtle rounded-lg px-2 py-1 text-[11px] text-text-secondary outline-none focus:border-accent-500"
              >
                <option value="all">All Types</option>
                <option value="project">Project</option>
                <option value="organization">DB/Services</option>
                <option value="concept">Concept</option>
              </select>

              <button 
                onClick={handleApplyFilters}
                className="btn-primary text-[11px] px-3 py-1"
              >
                Apply
              </button>
            </div>
          </div>
        </div>

        {/* ReactFlow Canvas */}
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={onNodeClick}
          onPaneClick={onPaneClick}
          fitView
          className="h-full w-full"
        >
          <Background color="var(--color-border-subtle)" gap={16} size={1} />
          <Controls className="!bg-surface-2 !border-border-subtle !text-text-primary fill-text-primary" />
          <MiniMap 
            nodeColor={(node) => {
              if ((node.data as any).type === "project") return "oklch(0.58 0.26 270)";
              if ((node.data as any).type === "organization") return "oklch(0.72 0.19 155)";
              return "oklch(0.70 0.15 240)";
            }}
            className="!bg-surface-2 !border-border-subtle"
            maskColor="rgba(0, 0, 0, 0.4)"
          />
        </ReactFlow>
      </div>

      {/* Node Inspector Sidebar */}
      {selectedNode ? (
        <div className="w-[340px] bg-surface-1 border-l border-border-subtle h-full flex flex-col overflow-hidden animate-slide-in-right z-10">
          <div className="p-4 border-b border-border-subtle bg-surface-2/30">
            <div className="flex items-center gap-2 mb-2">
              {getEntityIcon((selectedNode.data as any).type)}
              <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-text-secondary">
                {(selectedNode.data as any).type}
              </span>
            </div>
            <h2 className="text-sm font-bold text-text-primary">
              {(selectedNode.data as any).label}
            </h2>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs text-text-secondary leading-relaxed">
            <div className="space-y-1">
              <span className="text-[10px] uppercase font-bold text-text-tertiary flex items-center gap-1">
                <BookOpen size={12} /> Description
              </span>
              <p className="bg-surface-2 border border-border-subtle p-3 rounded-lg">
                {(selectedNode.data as any).description}
              </p>
            </div>

            <div className="space-y-2">
              <span className="text-[10px] uppercase font-bold text-text-tertiary">
                Direct Connections
              </span>
              <div className="space-y-1.5">
                {edges
                  .filter((e) => e.source === selectedNode.id || e.target === selectedNode.id)
                  .map((e) => {
                    const isSource = e.source === selectedNode.id;
                    const counterpartId = isSource ? e.target : e.source;
                    const counterpart = nodes.find((n) => n.id === counterpartId);
                    return (
                      <div key={e.id} className="flex justify-between items-center bg-surface-2/50 border border-border-subtle p-2 rounded-lg text-[11px]">
                        <span className="font-semibold text-text-primary">
                          {(counterpart?.data as any)?.label || counterpartId}
                        </span>
                        <span className="text-[10px] text-text-tertiary italic">
                          ({e.label})
                        </span>
                      </div>
                    );
                  })}
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="w-[340px] bg-surface-1 border-l border-border-subtle h-full flex flex-col justify-center items-center text-center p-6 text-text-tertiary z-10">
          <Network size={36} className="mb-2 stroke-1 text-text-tertiary animate-pulse-glow" />
          <p className="text-xs">Select a graph node to inspect its schema properties, connection edges, and temporal validity.</p>
        </div>
      )}
    </div>
  );
}
