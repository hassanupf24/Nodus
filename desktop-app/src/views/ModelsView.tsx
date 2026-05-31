/* ============================================================
   MODELS VIEW — Local Model Manager
   ============================================================ */

import { useState } from "react";
import { 
  Download, 
  Cpu, 
  Trash2, 
  Play, 
  Square, 
  CheckCircle,
  TrendingUp
} from "lucide-react";
import type { AIModel } from "@/types";

const INITIAL_MODELS: AIModel[] = [
  {
    name: "llama3.2:3b",
    displayName: "Llama 3.2 (3B)",
    size: 2020102042,
    quantization: "Q4_K_M",
    family: "llama",
    parameterCount: "3B",
    status: "loaded",
    vramUsage: 2147483648,
    ramUsage: 536870912
  },
  {
    name: "nomic-embed-text:latest",
    displayName: "Nomic Embed Text",
    size: 282030200,
    quantization: "F16",
    family: "nomic",
    parameterCount: "137M",
    status: "available"
  },
  {
    name: "phi3:medium",
    displayName: "Phi-3 Medium (14B)",
    size: 7902030204,
    quantization: "Q4_K_S",
    family: "phi",
    parameterCount: "14B",
    status: "available"
  }
];

export function ModelsView() {
  const [localModels, setLocalModels] = useState<AIModel[]>(INITIAL_MODELS);
  const [pullModelName, setPullModelName] = useState("");
  const [isPulling, setIsPulling] = useState(false);
  const [pullProgress, setPullProgress] = useState(0);

  const handlePullModel = () => {
    if (!pullModelName.trim()) return;
    setIsPulling(true);
    setPullProgress(0);

    // Register temporary downloading model in local list
    const newModel: AIModel = {
      name: pullModelName,
      displayName: pullModelName.charAt(0).toUpperCase() + pullModelName.slice(1),
      size: 3802030200,
      quantization: "Q4_K_M",
      family: pullModelName.includes("llama") ? "llama" : "unknown",
      parameterCount: "8B",
      status: "downloading",
      downloadProgress: 0
    };
    
    setLocalModels(prev => [...prev, newModel]);

    // Simulate download progress
    let progress = 0;
    const interval = setInterval(() => {
      progress += 10;
      setPullProgress(progress);
      setLocalModels(prev => prev.map(m => 
        m.name === pullModelName ? { ...m, downloadProgress: progress } : m
      ));

      if (progress >= 100) {
        clearInterval(interval);
        setIsPulling(false);
        setPullModelName("");
        setLocalModels(prev => prev.map(m => 
          m.name === pullModelName ? { ...m, status: "available", downloadProgress: undefined } : m
        ));
      }
    }, 800);
  };

  const handleLoadModel = (name: string) => {
    setLocalModels(prev => prev.map(m => {
      if (m.name === name) {
        return {
          ...m,
          status: "loaded",
          vramUsage: m.name.includes("3b") ? 2147483648 : 5368709120,
          ramUsage: 536870912
        };
      }
      // Unload others (simulate single active LLM)
      if (m.status === "loaded" && m.name !== "nomic-embed-text:latest") {
        return { ...m, status: "available", vramUsage: undefined, ramUsage: undefined };
      }
      return m;
    }));
  };

  const handleUnloadModel = (name: string) => {
    setLocalModels(prev => prev.map(m => 
      m.name === name ? { ...m, status: "available", vramUsage: undefined, ramUsage: undefined } : m
    ));
  };

  const handleDeleteModel = (name: string) => {
    setLocalModels(prev => prev.filter(m => m.name !== name));
  };

  const formatSize = (bytes: number) => {
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
  };

  return (
    <div className="h-full flex flex-col bg-surface-0 overflow-hidden text-xs">
      {/* Header and Download Model Input */}
      <div className="flex flex-col gap-3 border-b border-border-subtle bg-surface-1/50 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Cpu size={18} className="text-accent-400" />
            <h1 className="text-sm font-semibold uppercase tracking-wider text-text-primary">
              Local AI Engine & Models
            </h1>
          </div>
          <span className="text-xs text-text-tertiary">
            Quantized inference engines
          </span>
        </div>

        <div className="flex gap-3">
          <div className="relative flex-1">
            <Download className="absolute left-3 top-2.5 h-4 w-4 text-text-tertiary" />
            <input
              type="text"
              placeholder="Enter model tag from Ollama library (e.g. mistral, qwen2.5:7b)..."
              value={pullModelName}
              onChange={(e) => setPullModelName(e.target.value)}
              disabled={isPulling}
              className="input-field pl-9 py-1.5"
            />
          </div>
          <button 
            onClick={handlePullModel} 
            disabled={isPulling}
            className="btn-primary flex items-center gap-1.5"
          >
            {isPulling ? "Downloading..." : "Pull Model"}
          </button>
        </div>

        {isPulling && (
          <div className="mt-1 flex items-center gap-3">
            <div className="h-1.5 flex-1 rounded bg-surface-3 overflow-hidden">
              <div 
                className="h-full bg-accent-500 transition-all duration-300"
                style={{ width: `${pullProgress}%` }}
              />
            </div>
            <span className="font-mono text-[10px] text-text-secondary">{pullProgress}%</span>
          </div>
        )}
      </div>

      {/* Models Grid/List */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-5xl mx-auto space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {localModels.map((model) => (
              <div 
                key={model.name} 
                className={`card relative flex flex-col justify-between border transition-all ${
                  model.status === "loaded" 
                    ? "border-accent-500/40 bg-accent-500/5 glow" 
                    : "border-border-subtle"
                }`}
              >
                <div>
                  {/* Status indicator */}
                  <div className="flex justify-between items-start mb-3">
                    <span className="badge badge-accent uppercase tracking-wider text-[8px] font-mono">
                      {model.quantization}
                    </span>
                    {model.status === "loaded" ? (
                      <span className="badge badge-success flex items-center gap-0.5 text-[9px]">
                        <CheckCircle size={10} /> Active LLM
                      </span>
                    ) : model.status === "downloading" ? (
                      <span className="badge badge-warning flex items-center gap-1 text-[9px]">
                        Downloading ({model.downloadProgress}%)
                      </span>
                    ) : null}
                  </div>

                  <h2 className="text-sm font-bold text-text-primary leading-tight">
                    {model.displayName}
                  </h2>
                  <p className="font-mono text-[10px] text-text-tertiary mt-1">Tag: {model.name}</p>

                  <div className="mt-4 grid grid-cols-2 gap-2 text-[10px] font-mono text-text-secondary border-t border-border-subtle/40 pt-3">
                    <div>
                      <span className="text-text-tertiary">Params:</span> {model.parameterCount}
                    </div>
                    <div>
                      <span className="text-text-tertiary">Disk Size:</span> {formatSize(model.size)}
                    </div>
                  </div>

                  {model.status === "loaded" && (
                    <div className="mt-3 p-2 bg-surface-2 rounded border border-border-subtle/50 text-[10px] font-mono text-text-secondary space-y-1">
                      <div className="flex justify-between">
                        <span className="text-text-tertiary">VRAM:</span> 
                        <span>{(model.vramUsage! / (1024 * 1024 * 1024)).toFixed(1)} GB</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-text-tertiary">Sys RAM:</span> 
                        <span>{(model.ramUsage! / (1024 * 1024)).toFixed(0)} MB</span>
                      </div>
                    </div>
                  )}
                </div>

                <div className="mt-5 pt-3 border-t border-border-subtle/40 flex justify-end gap-2 shrink-0">
                  {model.status === "loaded" ? (
                    <button 
                      onClick={() => handleUnloadModel(model.name)}
                      className="btn-secondary py-1 px-3 text-[10px] flex items-center gap-1 hover:text-error"
                    >
                      <Square size={10} /> Unload
                    </button>
                  ) : model.status === "available" ? (
                    <button 
                      onClick={() => handleLoadModel(model.name)}
                      className="btn-primary py-1 px-3 text-[10px] flex items-center gap-1"
                    >
                      <Play size={10} /> Load Model
                    </button>
                  ) : null}

                  <button 
                    onClick={() => handleDeleteModel(model.name)}
                    disabled={model.status === "loaded" || model.status === "downloading"}
                    className="p-1.5 text-text-tertiary hover:text-error rounded hover:bg-surface-3 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                    title="Delete model from host disk"
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Model selection help */}
          <div className="card flex items-start gap-3 bg-surface-1/40">
            <TrendingUp size={20} className="text-accent-400 mt-0.5 shrink-0" />
            <div>
              <h3 className="font-semibold text-text-primary text-xs">VRAM Allocation Recommendations</h3>
              <p className="text-text-secondary text-[11px] leading-relaxed mt-1">
                For devices with less than 8GB of VRAM (e.g. integrated GPUs or laptops), 3B parameters or highly quantized 8B GGUF models are recommended. If your computer doesn't have a discrete graphics card, Ollama automatically falls back to CPU execution, which has a higher latency overhead.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
