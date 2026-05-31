/* ============================================================
   SETTINGS VIEW — Core Platform Configuration
   ============================================================ */

import { useState } from "react";
import { 
  Settings, 
  Cpu, 
  ShieldCheck, 
  Palette, 
  Save, 
  Folder,
  EyeOff,
  Server
} from "lucide-react";
import { useSettingsStore } from "@/stores";

type TabId = "general" | "ai" | "privacy" | "appearance";

export function SettingsView() {
  const settingsStore = useSettingsStore();
  const [activeTab, setActiveTab] = useState<TabId>("general");

  // Temporary local state for modifications
  const [dataDir, setDataDir] = useState(settingsStore.settings.general.dataDirectory || "D:/projects/Nodus/data");
  const [ollamaEndpoint, setOllamaEndpoint] = useState(settingsStore.settings.ai.ollamaEndpoint);
  const [temperature, setTemperature] = useState(settingsStore.settings.ai.temperature);
  const [maxContext, setMaxContext] = useState(settingsStore.settings.ai.maxContextLength);
  
  const handleSave = () => {
    settingsStore.updateGeneralSettings({ dataDirectory: dataDir });
    settingsStore.updateAISettings({ 
      ollamaEndpoint,
      temperature,
      maxContextLength: maxContext
    });
    alert("Settings updated successfully!");
  };

  const handleToggleLocalMode = (val: boolean) => {
    settingsStore.updatePrivacySettings({ localOnlyMode: val });
  };

  const handleToggleGPU = (val: boolean) => {
    settingsStore.updateAISettings({ gpuEnabled: val });
  };

  const handleToggleCloudEscalation = (val: boolean) => {
    settingsStore.updatePrivacySettings({ cloudEscalationEnabled: val });
  };

  return (
    <div className="h-full flex bg-surface-0 overflow-hidden text-xs">
      {/* Settings Navigation Sidebar */}
      <div className="w-[200px] border-r border-border-subtle bg-surface-1/40 p-4 space-y-1 shrink-0">
        <div className="flex items-center gap-2 px-3 py-2 text-text-primary font-semibold mb-4">
          <Settings size={16} />
          <span className="text-xs uppercase tracking-wider">Control Panel</span>
        </div>

        <button
          onClick={() => setActiveTab("general")}
          className={`nav-item w-full ${activeTab === "general" ? "active" : ""}`}
        >
          <Folder size={14} /> General Settings
        </button>

        <button
          onClick={() => setActiveTab("ai")}
          className={`nav-item w-full ${activeTab === "ai" ? "active" : ""}`}
        >
          <Cpu size={14} /> AI Configuration
        </button>

        <button
          onClick={() => setActiveTab("privacy")}
          className={`nav-item w-full ${activeTab === "privacy" ? "active" : ""}`}
        >
          <ShieldCheck size={14} /> Privacy & Security
        </button>

        <button
          onClick={() => setActiveTab("appearance")}
          className={`nav-item w-full ${activeTab === "appearance" ? "active" : ""}`}
        >
          <Palette size={14} /> Appearance Theme
        </button>
      </div>

      {/* Settings Content Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        <div className="flex-1 overflow-y-auto p-6 max-w-2xl space-y-6">
          {activeTab === "general" && (
            <div className="space-y-4 animate-fade-in">
              <h2 className="text-sm font-bold text-text-primary border-b border-border-subtle pb-2">General</h2>
              
              <div className="space-y-1.5">
                <label className="font-semibold text-text-secondary">Local Storage Directory</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={dataDir}
                    onChange={(e) => setDataDir(e.target.value)}
                    className="input-field py-1.5 flex-1"
                  />
                  <button className="btn-secondary px-3 py-1.5 flex items-center gap-1">
                    Browse
                  </button>
                </div>
                <p className="text-[10px] text-text-tertiary">Paths where semantic vector nodes, SQLite DB replicas, and GGUF model files reside.</p>
              </div>

              <div className="flex items-center justify-between p-3 rounded-lg bg-surface-1 border border-border-subtle">
                <div>
                  <h3 className="font-semibold text-text-primary">Minimize to System Tray</h3>
                  <p className="text-[10px] text-text-tertiary mt-0.5">Keep Nodus indexing process active in background when closed.</p>
                </div>
                <input 
                  type="checkbox" 
                  checked={settingsStore.settings.general.minimizeToTray}
                  onChange={(e) => settingsStore.updateGeneralSettings({ minimizeToTray: e.target.checked })}
                  className="h-4 w-4 rounded border-border-subtle bg-surface-2 focus:ring-accent-500"
                />
              </div>

              <div className="flex items-center justify-between p-3 rounded-lg bg-surface-1 border border-border-subtle">
                <div>
                  <h3 className="font-semibold text-text-primary">Launch on Startup</h3>
                  <p className="text-[10px] text-text-tertiary mt-0.5">Auto-run server and scan directory directories on boot.</p>
                </div>
                <input 
                  type="checkbox" 
                  checked={settingsStore.settings.general.autoStartup}
                  onChange={(e) => settingsStore.updateGeneralSettings({ autoStartup: e.target.checked })}
                  className="h-4 w-4 rounded border-border-subtle bg-surface-2 focus:ring-accent-500"
                />
              </div>
            </div>
          )}

          {activeTab === "ai" && (
            <div className="space-y-4 animate-fade-in">
              <h2 className="text-sm font-bold text-text-primary border-b border-border-subtle pb-2">AI Configuration</h2>

              <div className="space-y-1.5">
                <label className="font-semibold text-text-secondary flex items-center gap-1">
                  <Server size={12} /> Local Ollama Endpoint
                </label>
                <input
                  type="text"
                  value={ollamaEndpoint}
                  onChange={(e) => setOllamaEndpoint(e.target.value)}
                  className="input-field py-1.5"
                />
                <p className="text-[10px] text-text-tertiary">System default: http://localhost:11434 (Make sure Ollama server is active).</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="font-semibold text-text-secondary">Inference Temperature: {temperature}</label>
                  <input
                    type="range"
                    min="0.1"
                    max="1.2"
                    step="0.1"
                    value={temperature}
                    onChange={(e) => setTemperature(parseFloat(e.target.value))}
                    className="w-full h-1 bg-surface-3 rounded-lg appearance-none cursor-pointer accent-accent-500"
                  />
                  <p className="text-[10px] text-text-tertiary">Higher temperature produces more creative/diverse summaries.</p>
                </div>

                <div className="space-y-1.5">
                  <label className="font-semibold text-text-secondary">Context Length: {maxContext} tokens</label>
                  <select
                    value={maxContext}
                    onChange={(e) => setMaxContext(parseInt(e.target.value))}
                    className="bg-surface-1 border border-border-subtle rounded-lg w-full px-2 py-1.5 text-text-secondary outline-none focus:border-accent-500"
                  >
                    <option value={2048}>2048 Tokens</option>
                    <option value={4096}>4096 Tokens</option>
                    <option value={8192}>8192 Tokens</option>
                  </select>
                </div>
              </div>

              <div className="flex items-center justify-between p-3 rounded-lg bg-surface-1 border border-border-subtle">
                <div>
                  <h3 className="font-semibold text-text-primary">GPU Threads Acceleration</h3>
                  <p className="text-[10px] text-text-tertiary mt-0.5">Attempt to load model layers directly into VRAM for prompt acceleration.</p>
                </div>
                <input 
                  type="checkbox" 
                  checked={settingsStore.settings.ai.gpuEnabled}
                  onChange={(e) => handleToggleGPU(e.target.checked)}
                  className="h-4 w-4 rounded border-border-subtle bg-surface-2 focus:ring-accent-500"
                />
              </div>
            </div>
          )}

          {activeTab === "privacy" && (
            <div className="space-y-4 animate-fade-in">
              <h2 className="text-sm font-bold text-text-primary border-b border-border-subtle pb-2">Privacy & Cryptography</h2>

              <div className="flex items-center justify-between p-3 rounded-lg bg-surface-1 border border-border-subtle">
                <div className="pr-4">
                  <h3 className="font-semibold text-text-primary flex items-center gap-1">
                    <EyeOff size={14} className="text-success" /> Strict Local-Only Execution
                  </h3>
                  <p className="text-[10px] text-text-tertiary mt-0.5">Ensure zero external network calls are performed. Models are kept on physical machine disk.</p>
                </div>
                <input 
                  type="checkbox" 
                  checked={settingsStore.settings.privacy.localOnlyMode}
                  onChange={(e) => handleToggleLocalMode(e.target.checked)}
                  className="h-4 w-4 rounded border-border-subtle bg-surface-2 focus:ring-accent-500"
                />
              </div>

              <div className="flex items-center justify-between p-3 rounded-lg bg-surface-1 border border-border-subtle">
                <div>
                  <h3 className="font-semibold text-text-primary">Encrypted Local Sync</h3>
                  <p className="text-[10px] text-text-tertiary mt-0.5">E2E encrypt storage indices using XChaCha20 keys stored inside the OS secure keychain.</p>
                </div>
                <input 
                  type="checkbox" 
                  checked={settingsStore.settings.privacy.encryptionEnabled}
                  onChange={(e) => settingsStore.updatePrivacySettings({ encryptionEnabled: e.target.checked })}
                  className="h-4 w-4 rounded border-border-subtle bg-surface-2 focus:ring-accent-500"
                />
              </div>

              <div className="flex items-center justify-between p-3 rounded-lg bg-surface-1 border border-border-subtle">
                <div>
                  <h3 className="font-semibold text-text-primary">Cloud Scaling Escalation</h3>
                  <p className="text-[10px] text-text-tertiary mt-0.5">Allows temporal routing to Anthropic/Google API endpoints when prompt size exceeds memory.</p>
                </div>
                <input 
                  type="checkbox" 
                  checked={settingsStore.settings.privacy.cloudEscalationEnabled}
                  onChange={(e) => handleToggleCloudEscalation(e.target.checked)}
                  className="h-4 w-4 rounded border-border-subtle bg-surface-2 focus:ring-accent-500"
                />
              </div>
            </div>
          )}

          {activeTab === "appearance" && (
            <div className="space-y-4 animate-fade-in">
              <h2 className="text-sm font-bold text-text-primary border-b border-border-subtle pb-2">Appearance</h2>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="font-semibold text-text-secondary">UI Design Theme</label>
                  <select
                    value={settingsStore.settings.appearance.theme}
                    onChange={(e) => settingsStore.updateAppearanceSettings({ theme: e.target.value as any })}
                    className="bg-surface-1 border border-border-subtle rounded-lg w-full px-2 py-1.5 text-text-secondary outline-none focus:border-accent-500"
                  >
                    <option value="dark">Dark Theme</option>
                    <option value="light">Light Theme</option>
                    <option value="system">Follow System</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="font-semibold text-text-secondary">Text Scaling</label>
                  <select
                    value={settingsStore.settings.appearance.fontSize}
                    onChange={(e) => settingsStore.updateAppearanceSettings({ fontSize: e.target.value as any })}
                    className="bg-surface-1 border border-border-subtle rounded-lg w-full px-2 py-1.5 text-text-secondary outline-none focus:border-accent-500"
                  >
                    <option value="small">Small Font</option>
                    <option value="medium">Medium Font</option>
                    <option value="large">Large Font</option>
                  </select>
                </div>
              </div>

              <div className="flex items-center justify-between p-3 rounded-lg bg-surface-1 border border-border-subtle">
                <div>
                  <h3 className="font-semibold text-text-primary">Fluid UI Animations</h3>
                  <p className="text-[10px] text-text-tertiary mt-0.5">Toggle motion transitions and slide-in panels. Disable to conserve energy.</p>
                </div>
                <input 
                  type="checkbox" 
                  checked={settingsStore.settings.appearance.animationsEnabled}
                  onChange={(e) => settingsStore.updateAppearanceSettings({ animationsEnabled: e.target.checked })}
                  className="h-4 w-4 rounded border-border-subtle bg-surface-2 focus:ring-accent-500"
                />
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="p-4 border-t border-border-subtle bg-surface-1/40 flex justify-end gap-3 shrink-0">
          <button 
            onClick={() => {
              setDataDir("D:/projects/Nodus/data");
              setOllamaEndpoint("http://localhost:11434");
              setTemperature(0.7);
            }} 
            className="btn-secondary"
          >
            Reset Defaults
          </button>
          <button onClick={handleSave} className="btn-primary flex items-center gap-1.5">
            <Save size={14} /> Save Configuration
          </button>
        </div>
      </div>
    </div>
  );
}
