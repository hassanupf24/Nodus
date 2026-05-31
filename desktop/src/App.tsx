import { useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import "./App.css";
import { ChatInterface } from "./components/ChatInterface";
import { FileDropzone } from "./components/FileDropzone";

function App() {
  return (
    <main className="container mx-auto h-screen w-screen overflow-hidden bg-slate-900">
      <FileDropzone>
        <ChatInterface />
      </FileDropzone>
    </main>
  );
}

export default App;
