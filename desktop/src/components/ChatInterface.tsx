import React from 'react';

export const ChatInterface = () => {
  return (
    <div className="flex flex-col h-full w-full bg-slate-900 text-slate-100">
      <div className="flex-1 overflow-y-auto p-4">
        {/* Chat messages */}
        <div className="text-sm opacity-50">Nodus Cognitive Engine Ready</div>
      </div>
      <div className="p-4 border-t border-slate-800">
        <input 
          type="text" 
          placeholder="Ask Nodus..."
          className="w-full bg-slate-800 text-white rounded p-3 outline-none"
        />
      </div>
    </div>
  );
};
