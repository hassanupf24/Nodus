/* ============================================================
   FILES VIEW — Ingestion Workspace & Local Storage
   ============================================================ */

import { useState, useEffect } from "react";
import { 
  FolderOpen, 
  Upload, 
  File, 
  CheckCircle, 
  Clock, 
  AlertCircle, 
  Play, 
  Trash2, 
  Search,
  RefreshCw,
  FilePlus
} from "lucide-react";
import { useIngestionStore, tauriStore } from "@/stores";
import type { IngestionJob } from "@/types";
import { open } from "@tauri-apps/plugin-dialog";
import { stat } from "@tauri-apps/plugin-fs";

interface LocalFile {
  id: string;
  name: string;
  path: string;
  size: number;
  type: string;
  status: "not_ingested" | "queued" | "indexing" | "completed" | "failed";
}

export function FilesView() {
  const [localFiles, setLocalFiles] = useState<LocalFile[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const addJob = useIngestionStore((s) => s.addJob);
  const updateJob = useIngestionStore((s) => s.updateJob);

  // Load from store on mount
  useEffect(() => {
    tauriStore.get<LocalFile[]>("localFiles").then(saved => {
      if (saved) setLocalFiles(saved);
    });
  }, []);

  // Save to store when localFiles changes
  useEffect(() => {
    tauriStore.set("localFiles", localFiles).then(() => tauriStore.save()).catch(console.error);
  }, [localFiles]);

  const filteredFiles = localFiles.filter((f) => 
    f.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleIngest = async (file: LocalFile) => {
    // 1. Update file status in UI
    setLocalFiles(prev => prev.map(f => f.id === file.id ? { ...f, status: "indexing" } : f));

    try {
      // 2. Call backend ingest API
      const { ingestFile, getIngestionStatus } = await import("@/services/api");
      const resp = await ingestFile(file.path);
      const jobId = resp.job_id;

      // 3. Register job in global store
      const newJob: IngestionJob = {
        id: jobId,
        fileName: file.name,
        fileType: file.type,
        fileSize: file.size,
        status: "processing",
        progress: 0,
        startedAt: Date.now()
      };
      addJob(newJob);

      // 4. Poll status
      const interval = setInterval(async () => {
        try {
          const statusResp = await getIngestionStatus(jobId);
          // Backend might return status: 'processing', 'completed', 'failed'
          // We map it to the job update
          
          if (statusResp.status === "completed") {
            clearInterval(interval);
            updateJob(jobId, { 
              status: "completed", 
              progress: 100,
              completedAt: Date.now()
            });
            setLocalFiles(prev => prev.map(f => f.id === file.id ? { ...f, status: "completed" } : f));
          } else if (statusResp.status === "failed") {
            clearInterval(interval);
            updateJob(jobId, { status: "failed" });
            setLocalFiles(prev => prev.map(f => f.id === file.id ? { ...f, status: "failed" } : f));
          } else {
            // processing
            updateJob(jobId, { progress: 50 }); // Indeterminate progress for now
          }
        } catch (e) {
          console.error("Failed to get job status", e);
        }
      }, 2000);
    } catch (e) {
      console.error("Ingestion request failed", e);
      setLocalFiles(prev => prev.map(f => f.id === file.id ? { ...f, status: "failed" } : f));
    }
  };

  const handleRemove = (id: string) => {
    setLocalFiles(prev => prev.filter(f => f.id !== id));
  };

  const handleAddFiles = async () => {
    try {
      const selected = await open({
        multiple: true,
        directory: false,
      });
      if (selected) {
        const paths = Array.isArray(selected) ? selected : [selected];
        for (const p of paths) {
          const fileInfo = await stat(p);
          // Basic check for duplicates
          if (!localFiles.some(f => f.path === p)) {
            const fileName = p.split(/[\\/]/).pop() || "unknown";
            const ext = fileName.split('.').pop()?.toLowerCase() || "unknown";
            const newFile: LocalFile = {
              id: crypto.randomUUID(),
              name: fileName,
              path: p,
              size: fileInfo.size,
              type: ext,
              status: "not_ingested"
            };
            setLocalFiles(prev => [...prev, newFile]);
          }
        }
      }
    } catch (e) {
      console.error("Failed to select files:", e);
    }
  };

  const getStatusBadge = (status: LocalFile["status"]) => {
    switch (status) {
      case "completed":
        return (
          <span className="badge badge-success flex items-center gap-1 text-[10px]">
            <CheckCircle size={10} /> Indexed
          </span>
        );
      case "indexing":
        return (
          <span className="badge badge-warning flex items-center gap-1 text-[10px]">
            <RefreshCw size={10} className="animate-spin" /> Processing
          </span>
        );
      case "failed":
        return (
          <span className="badge badge-error flex items-center gap-1 text-[10px]">
            <AlertCircle size={10} /> Failed
          </span>
        );
      case "queued":
        return (
          <span className="badge flex items-center gap-1 text-[10px] bg-surface-3 text-text-secondary border-border-subtle">
            <Clock size={10} /> Queued
          </span>
        );
      default:
        return (
          <span className="badge flex items-center gap-1 text-[10px] bg-surface-2 text-text-tertiary border-border-subtle">
            Not Indexed
          </span>
        );
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes > 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    return `${(bytes / 1024).toFixed(1)} KB`;
  };

  return (
    <div className="h-full flex flex-col bg-surface-0 overflow-hidden">
      {/* Top Banner & Actions */}
      <div className="flex flex-col gap-3 border-b border-border-subtle bg-surface-1/50 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FolderOpen size={18} className="text-accent-400" />
            <h1 className="text-sm font-semibold uppercase tracking-wider text-text-primary">
              Local Ingestion Workspace
            </h1>
          </div>
          <span className="text-xs text-text-tertiary">
            Scan directories and feed AI memory
          </span>
        </div>

        <div className="flex gap-3">
          {/* Search bar */}
          <div className="relative flex-1">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-text-tertiary" />
            <input
              type="text"
              placeholder="Search local documents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input-field pl-9 py-1.5"
            />
          </div>

          <button onClick={handleAddFiles} className="btn-primary flex items-center gap-1 text-xs">
            <FilePlus size={14} /> Add Files
          </button>
        </div>
      </div>

      {/* Files List Table */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-5xl mx-auto">
          <div className="card overflow-hidden !p-0 border border-border-subtle bg-surface-1/30">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-border-subtle bg-surface-2/40 text-text-tertiary font-mono uppercase tracking-wider text-[10px]">
                  <th className="p-4 font-semibold">File Name</th>
                  <th className="p-4 font-semibold">File Path</th>
                  <th className="p-4 font-semibold">Size</th>
                  <th className="p-4 font-semibold">Ingestion Status</th>
                  <th className="p-4 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border-subtle/55">
                {filteredFiles.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="p-8 text-center text-text-tertiary">
                      No files match the search criteria.
                    </td>
                  </tr>
                ) : (
                  filteredFiles.map((file) => (
                    <tr key={file.id} className="hover:bg-surface-2/40 transition-colors group">
                      <td className="p-4 font-semibold text-text-primary">
                        <div className="flex items-center gap-2">
                          <File size={16} className="text-accent-400 shrink-0" />
                          <span className="truncate max-w-[200px]" title={file.name}>
                            {file.name}
                          </span>
                        </div>
                      </td>
                      <td className="p-4 text-text-secondary font-mono text-[11px] max-w-[240px] truncate" title={file.path}>
                        {file.path}
                      </td>
                      <td className="p-4 text-text-tertiary font-mono">
                        {formatSize(file.size)}
                      </td>
                      <td className="p-4">
                        {getStatusBadge(file.status)}
                      </td>
                      <td className="p-4 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          {file.status === "not_ingested" || file.status === "failed" ? (
                            <button
                              onClick={() => handleIngest(file)}
                              className="p-1.5 text-text-secondary hover:text-success rounded hover:bg-surface-3 transition-all"
                              title="Index into vector store"
                            >
                              <Play size={14} />
                            </button>
                          ) : null}
                          
                          <button
                            onClick={() => handleRemove(file.id)}
                            className="p-1.5 text-text-secondary hover:text-error rounded hover:bg-surface-3 transition-all"
                            title="Remove file reference"
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
