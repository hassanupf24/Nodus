/* ============================================================
   CHAT VIEW — AI Chat Interface with Streaming
   Premium chat UI with message bubbles, streaming, attachments
   ============================================================ */

import { useState, useRef, useEffect, useCallback } from "react";
import { useChatStore } from "@/stores";
import { streamChatCompletion } from "@/services/api";
import type { ChatMessage } from "@/types";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import {
  Send,
  Paperclip,
  Copy,
  Check,
  Sparkles,
  Bot,
  User,
  StopCircle,
  ChevronDown,
} from "lucide-react";
import clsx from "clsx";

export function ChatView() {
  const conversations = useChatStore((s) => s.conversations);
  const activeConversationId = useChatStore((s) => s.activeConversationId);
  const isGenerating = useChatStore((s) => s.isGenerating);
  const selectedModel = useChatStore((s) => s.selectedModel);
  const createConversation = useChatStore((s) => s.createConversation);
  const addMessage = useChatStore((s) => s.addMessage);
  const appendToMessage = useChatStore((s) => s.appendToMessage);
  const updateMessage = useChatStore((s) => s.updateMessage);
  const setIsGenerating = useChatStore((s) => s.setIsGenerating);

  const [input, setInput] = useState("");
  const [showScrollButton, setShowScrollButton] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const activeConversation = conversations.find((c) => c.id === activeConversationId);
  const messages = activeConversation?.messages ?? [];

  // Auto-scroll to bottom
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    if (isGenerating) {
      scrollToBottom();
    }
  }, [messages.length, isGenerating, scrollToBottom]);

  // Detect if scrolled away from bottom
  const handleScroll = useCallback(() => {
    const container = scrollContainerRef.current;
    if (!container) return;
    const distanceFromBottom = container.scrollHeight - container.scrollTop - container.clientHeight;
    setShowScrollButton(distanceFromBottom > 100);
  }, []);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = inputRef.current;
    if (!textarea) return;
    textarea.style.height = "auto";
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + "px";
  }, [input]);

  // Send message
  const handleSend = useCallback(async () => {
    const trimmed = input.trim();
    if (!trimmed || isGenerating) return;

    let convId = activeConversationId;
    if (!convId) {
      convId = createConversation();
    }

    // Add user message
    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmed,
      timestamp: Date.now(),
    };
    addMessage(convId, userMessage);
    setInput("");

    // Create assistant message placeholder
    const assistantId = crypto.randomUUID();
    const assistantMessage: ChatMessage = {
      id: assistantId,
      role: "assistant",
      content: "",
      timestamp: Date.now(),
      model: selectedModel,
      isStreaming: true,
    };
    addMessage(convId, assistantMessage);
    setIsGenerating(true);

    // Stream response
    const abortController = new AbortController();
    abortControllerRef.current = abortController;
    const startTime = Date.now();

    try {
      const allMessages = [
        ...messages.map((m) => ({ role: m.role, content: m.content })),
        { role: "user" as const, content: trimmed },
      ];

      const stream = streamChatCompletion(
        {
          model: selectedModel,
          messages: allMessages,
          temperature: 0.7,
          stream: true,
        },
        abortController.signal,
      );

      for await (const chunk of stream) {
        const content = chunk.choices[0]?.delta?.content;
        if (content) {
          appendToMessage(convId!, assistantId, content);
        }
      }

      updateMessage(convId!, assistantId, {
        isStreaming: false,
        latencyMs: Date.now() - startTime,
      });
    } catch (error) {
      if ((error as Error).name !== "AbortError") {
        updateMessage(convId!, assistantId, {
          content:
            "⚠️ Failed to get a response. Make sure AI services are running.\n\n```\n" +
            (error instanceof Error ? error.message : "Unknown error") +
            "\n```",
          isStreaming: false,
        });
      }
    } finally {
      setIsGenerating(false);
      abortControllerRef.current = null;
    }
  }, [
    input,
    isGenerating,
    activeConversationId,
    selectedModel,
    messages,
    createConversation,
    addMessage,
    appendToMessage,
    updateMessage,
    setIsGenerating,
  ]);

  const handleStop = useCallback(() => {
    abortControllerRef.current?.abort();
    setIsGenerating(false);
  }, [setIsGenerating]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend],
  );

  // Empty state
  if (!activeConversation && conversations.length === 0) {
    return <EmptyState onCreate={() => createConversation()} />;
  }

  return (
    <div className="flex h-full flex-col" id="chat-view">
      {/* Messages Area */}
      <div
        ref={scrollContainerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto"
      >
        <div className="mx-auto max-w-3xl px-4 py-6">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center py-20 text-center animate-fade-in">
              <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-accent-600 to-accent-400 shadow-glow">
                <Sparkles size={24} className="text-white" />
              </div>
              <h2 className="text-lg font-semibold text-text-primary">How can I help you?</h2>
              <p className="mt-1 text-sm text-text-tertiary max-w-md">
                Ask me anything about your knowledge base, or start a new conversation. All processing happens locally on your device.
              </p>
            </div>
          )}

          <div className="space-y-1 stagger-children">
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
          </div>
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Scroll-to-bottom button */}
      {showScrollButton && (
        <button
          onClick={scrollToBottom}
          className="absolute bottom-24 right-8 z-10 flex h-8 w-8 items-center justify-center rounded-full bg-surface-3 border border-border-subtle shadow-elevated text-text-secondary hover:text-text-primary transition-all animate-scale-in"
          aria-label="Scroll to bottom"
        >
          <ChevronDown size={16} />
        </button>
      )}

      {/* Input Area */}
      <div className="shrink-0 border-t border-border-subtle bg-surface-1/50 p-4">
        <div className="mx-auto max-w-3xl">
          <div className="relative flex items-end gap-2 rounded-xl border border-border-subtle bg-surface-2 p-2 focus-within:border-accent-500 focus-within:shadow-glow transition-all">
            {/* Attachment button */}
            <button
              className="btn-ghost shrink-0 p-2 text-text-tertiary hover:text-text-primary"
              aria-label="Attach file"
              id="chat-attach-btn"
            >
              <Paperclip size={18} />
            </button>

            {/* Textarea */}
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Message Nodus..."
              rows={1}
              className="flex-1 resize-none bg-transparent text-sm text-text-primary outline-none placeholder:text-text-tertiary max-h-[200px]"
              disabled={isGenerating}
              id="chat-input"
            />

            {/* Send / Stop button */}
            {isGenerating ? (
              <button
                onClick={handleStop}
                className="btn-ghost shrink-0 p-2 text-error hover:bg-error/10"
                aria-label="Stop generating"
                id="chat-stop-btn"
              >
                <StopCircle size={18} />
              </button>
            ) : (
              <button
                onClick={handleSend}
                disabled={!input.trim()}
                className={clsx(
                  "shrink-0 rounded-lg p-2 transition-all",
                  input.trim()
                    ? "bg-accent-500 text-white hover:bg-accent-400 shadow-glow"
                    : "text-text-tertiary",
                )}
                aria-label="Send message"
                id="chat-send-btn"
              >
                <Send size={16} />
              </button>
            )}
          </div>
          <p className="mt-2 text-center text-[11px] text-text-tertiary">
            Processing locally with {selectedModel} · Your data never leaves your device
          </p>
        </div>
      </div>
    </div>
  );
}

// ---- Message Bubble ----

function MessageBubble({ message }: { message: ChatMessage }) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === "user";

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, [message.content]);

  return (
    <div
      className={clsx(
        "group flex gap-3 py-3 animate-fade-in",
        isUser ? "flex-row-reverse" : "flex-row",
      )}
      id={`message-${message.id}`}
    >
      {/* Avatar */}
      <div
        className={clsx(
          "flex h-8 w-8 shrink-0 items-center justify-center rounded-lg",
          isUser
            ? "bg-surface-4"
            : "bg-gradient-to-br from-accent-600 to-accent-400 shadow-glow",
        )}
      >
        {isUser ? (
          <User size={14} className="text-text-secondary" />
        ) : (
          <Bot size={14} className="text-white" />
        )}
      </div>

      {/* Content */}
      <div className={clsx("max-w-[85%] min-w-0", isUser ? "text-right" : "text-left")}>
        <div
          className={clsx(
            "inline-block rounded-xl px-4 py-3 text-sm leading-relaxed",
            isUser
              ? "bg-accent-500/15 text-text-primary rounded-tr-sm"
              : "bg-surface-2 text-text-primary rounded-tl-sm",
          )}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="prose prose-invert prose-sm max-w-none">
              <ReactMarkdown
                components={{
                  code({ className, children, ...props }) {
                    const match = /language-(\w+)/.exec(className || "");
                    const isInline = !match;
                    return isInline ? (
                      <code
                        className="rounded bg-surface-3 px-1.5 py-0.5 font-mono text-xs text-accent-300"
                        {...props}
                      >
                        {children}
                      </code>
                    ) : (
                      <SyntaxHighlighter
                        style={oneDark}
                        language={match[1]}
                        PreTag="div"
                        customStyle={{
                          borderRadius: "8px",
                          fontSize: "12px",
                          margin: "8px 0",
                        }}
                      >
                        {String(children).replace(/\n$/, "")}
                      </SyntaxHighlighter>
                    );
                  },
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          )}

          {/* Streaming indicator */}
          {message.isStreaming && (
            <div className="typing-indicator mt-1">
              <span />
              <span />
              <span />
            </div>
          )}
        </div>

        {/* Actions bar */}
        {!isUser && !message.isStreaming && message.content && (
          <div className="mt-1 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              onClick={handleCopy}
              className="btn-ghost p-1 text-text-tertiary text-xs"
              aria-label="Copy message"
            >
              {copied ? <Check size={12} className="text-success" /> : <Copy size={12} />}
            </button>
            {message.latencyMs && (
              <span className="text-[10px] text-text-tertiary ml-1">
                {(message.latencyMs / 1000).toFixed(1)}s
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// ---- Empty State ----

function EmptyState({ onCreate }: { onCreate: () => void }) {
  return (
    <div className="flex h-full items-center justify-center animate-fade-in" id="chat-empty-state">
      <div className="text-center max-w-md px-4">
        <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-3xl bg-gradient-to-br from-accent-600 to-accent-400 shadow-glow-strong">
          <Sparkles size={36} className="text-white" />
        </div>
        <h1 className="text-2xl font-bold gradient-text mb-2">Welcome to Nodus</h1>
        <p className="text-sm text-text-secondary mb-6 leading-relaxed">
          Your private AI memory system. Chat with your knowledge base, search semantically, and let AI organize your thoughts — all locally on your device.
        </p>
        <button onClick={onCreate} className="btn-primary text-sm px-6 py-2.5" id="start-chat-btn">
          <Sparkles size={16} />
          Start a Conversation
        </button>
        <div className="mt-8 grid grid-cols-2 gap-3 text-left">
          {[
            { icon: "🔒", title: "100% Private", desc: "Everything runs locally" },
            { icon: "🧠", title: "AI Memory", desc: "Remembers your context" },
            { icon: "🔍", title: "Semantic Search", desc: "Find by meaning, not keywords" },
            { icon: "📊", title: "Knowledge Graph", desc: "Connected insights" },
          ].map((feature) => (
            <div key={feature.title} className="card p-3">
              <span className="text-lg">{feature.icon}</span>
              <h3 className="mt-1 text-xs font-semibold text-text-primary">{feature.title}</h3>
              <p className="text-[11px] text-text-tertiary">{feature.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
