/* ============================================================
   STATUS BAR — Bottom system status strip
   Shows connection, resource usage, and active model
   ============================================================ */

import { useHealthStore, useChatStore, useIngestionStore } from "@/stores";
import { Cpu, HardDrive, Activity, Loader2 } from "lucide-react";
import clsx from "clsx";

export function StatusBar() {
  const health = useHealthStore((s) => s.health);
  const isConnected = useHealthStore((s) => s.isConnected);
  const selectedModel = useChatStore((s) => s.selectedModel);
  const isGenerating = useChatStore((s) => s.isGenerating);
  const jobs = useIngestionStore((s) => s.jobs);

  const activeJobs = jobs.filter((j) => j.status === "processing");
  const resources = health?.resources;

  return (
    <footer
      className="flex h-[var(--spacing-statusbar)] shrink-0 items-center justify-between border-t border-border-subtle bg-surface-1/80 px-4 text-[11px] text-text-tertiary"
      id="status-bar"
    >
      {/* Left — Connection & Model */}
      <div className="flex items-center gap-4">
        {/* Connection indicator */}
        <div className="flex items-center gap-1.5">
          <div
            className={clsx(
              "h-1.5 w-1.5 rounded-full",
              isConnected ? "bg-success" : "bg-error",
            )}
          />
          <span>{isConnected ? "Connected" : "Offline"}</span>
        </div>

        {/* Active model */}
        <div className="flex items-center gap-1.5">
          <Cpu size={11} className="opacity-60" />
          <span className="font-medium text-text-secondary">{selectedModel}</span>
          {isGenerating && (
            <Loader2 size={11} className="animate-spin text-accent-400" />
          )}
        </div>

        {/* Active ingestion jobs */}
        {activeJobs.length > 0 && (
          <div className="flex items-center gap-1.5 text-accent-400">
            <Activity size={11} />
            <span>
              {activeJobs.length} file{activeJobs.length > 1 ? "s" : ""} processing
            </span>
          </div>
        )}
      </div>

      {/* Right — Resources */}
      <div className="flex items-center gap-4">
        {resources && (
          <>
            <div className="flex items-center gap-1.5" title={`CPU: ${resources.cpuPercent.toFixed(0)}%`}>
              <Cpu size={11} className="opacity-60" />
              <span>{resources.cpuPercent.toFixed(0)}%</span>
            </div>
            <div
              className="flex items-center gap-1.5"
              title={`RAM: ${resources.ramUsedMb.toFixed(0)} / ${resources.ramTotalMb.toFixed(0)} MB`}
            >
              <HardDrive size={11} className="opacity-60" />
              <span>
                {(resources.ramUsedMb / 1024).toFixed(1)} /{" "}
                {(resources.ramTotalMb / 1024).toFixed(0)} GB
              </span>
            </div>
            {resources.gpuPercent !== undefined && (
              <div className="flex items-center gap-1.5 text-accent-400" title="GPU">
                <Activity size={11} />
                <span>GPU {resources.gpuPercent.toFixed(0)}%</span>
              </div>
            )}
          </>
        )}
        <span className="opacity-50">Nodus v0.1.0</span>
      </div>
    </footer>
  );
}
