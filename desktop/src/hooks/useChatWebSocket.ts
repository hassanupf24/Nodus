import { useEffect, useRef, useState, useCallback } from 'react';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export function useChatWebSocket() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Assuming backend runs on 8000
    ws.current = new WebSocket('ws://127.0.0.1:8000/api/v1/chat/stream');

    ws.current.onopen = () => console.log("WebSocket Connected");
    
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'token') {
        setMessages((prev) => {
          const newMessages = [...prev];
          const lastIndex = newMessages.length - 1;
          if (lastIndex >= 0 && newMessages[lastIndex].role === 'assistant') {
            newMessages[lastIndex].content += data.content;
          } else {
            newMessages.push({ role: 'assistant', content: data.content });
          }
          return newMessages;
        });
      }
    };

    return () => {
      ws.current?.close();
    };
  }, []);

  const sendMessage = useCallback((msg: string) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      setMessages((prev) => [...prev, { role: 'user', content: msg }]);
      ws.current.send(JSON.stringify({ message: msg }));
    }
  }, []);

  return { messages, sendMessage };
}
