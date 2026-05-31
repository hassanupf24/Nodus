import React, { useState } from 'react';
import { useChatWebSocket } from '../hooks/useChatWebSocket';

export const ChatInterface = () => {
  const { messages, sendMessage } = useChatWebSocket();
  const [input, setInput] = useState("");

  const handleSend = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && input.trim() !== '') {
      sendMessage(input.trim());
      setInput("");
    }
  };

  return (
    <div className="flex flex-col h-full w-full bg-slate-900 text-slate-100">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-sm opacity-50">Nodus Cognitive Engine Ready. Ask me anything.</div>
        )}
        {messages.map((msg, idx) => (
          <div key={idx} className={`p-3 rounded-lg max-w-[80%] ${msg.role === 'user' ? 'bg-blue-600 self-end ml-auto' : 'bg-slate-800'}`}>
            <span className="text-sm font-semibold mb-1 block opacity-70">
              {msg.role === 'user' ? 'You' : 'Nodus'}
            </span>
            <div className="whitespace-pre-wrap">{msg.content}</div>
          </div>
        ))}
      </div>
      <div className="p-4 border-t border-slate-800 bg-slate-900">
        <input 
          type="text" 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleSend}
          placeholder="Ask Nodus..."
          className="w-full bg-slate-800 text-white rounded-xl p-4 outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
    </div>
  );
};
