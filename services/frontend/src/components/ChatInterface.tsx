'use client';

import { useState, useRef, useEffect } from 'react';
import { api, ChatResponse } from '@/services/api';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  taskId?: string;
  action?: string;
}

interface ChatInterfaceProps {
  onTaskChange?: () => void;
}

export default function ChatInterface({ onTaskChange }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: "Hey! I'm your AI task assistant. Just type anything to create a task, or try:\n\n- \"Buy groceries\" - creates a task\n- \"Show my tasks\" - lists all\n- \"Complete groceries\" - marks done\n- \"Delete groceries\" - removes it",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response: ChatResponse = await api.sendMessage(userMessage.content);

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        taskId: response.task_id || undefined,
        action: response.action || undefined,
      };

      setMessages(prev => [...prev, assistantMessage]);

      if (response.action && onTaskChange) {
        onTaskChange();
      }
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Oops! Something went wrong. ${error instanceof Error ? error.message : 'Please try again.'}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full glass rounded-2xl overflow-hidden">
      {/* Header */}
      <div className="px-5 py-4 bg-gradient-to-r from-accent-600 to-accent-500">
        <div className="flex items-center gap-3">
          {/* Mini animated bot */}
          <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center animate-float">
            <svg className="w-6 h-6 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="4" width="18" height="12" rx="3" />
              <circle cx="9" cy="10" r="1.2" fill="currentColor" stroke="none" />
              <circle cx="15" cy="10" r="1.2" fill="currentColor" stroke="none" />
              <path d="M9 13c1 1 2 1.5 3 1.5s2-0.5 3-1.5" strokeLinecap="round" />
            </svg>
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">Task Assistant</h2>
            <div className="flex items-center gap-1.5">
              <div className="w-1.5 h-1.5 rounded-full bg-green-300 animate-pulse" />
              <p className="text-xs text-white/70">Online - Ready to help</p>
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((message, index) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} animate-slide-up`}
            style={{ animationDelay: `${index * 0.05}s` }}
          >
            {message.role === 'assistant' && (
              <div className="w-7 h-7 rounded-lg bg-accent-500/20 flex items-center justify-center mr-2 mt-1 flex-shrink-0">
                <svg className="w-4 h-4 text-accent-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="4" width="18" height="12" rx="3" />
                  <circle cx="9" cy="10" r="1" fill="currentColor" stroke="none" />
                  <circle cx="15" cy="10" r="1" fill="currentColor" stroke="none" />
                </svg>
              </div>
            )}
            <div
              className={`max-w-[75%] rounded-2xl px-4 py-2.5 ${
                message.role === 'user'
                  ? 'bg-accent-500 text-white rounded-br-md'
                  : 'glass-light text-gray-200 rounded-bl-md'
              }`}
            >
              <div className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</div>
              <div className={`text-[10px] mt-1.5 ${message.role === 'user' ? 'text-white/50' : 'text-gray-500'}`}>
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start animate-fade-in">
            <div className="w-7 h-7 rounded-lg bg-accent-500/20 flex items-center justify-center mr-2 mt-1">
              <svg className="w-4 h-4 text-accent-400 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="4" width="18" height="12" rx="3" />
              </svg>
            </div>
            <div className="glass-light rounded-2xl rounded-bl-md px-5 py-3">
              <div className="flex space-x-1.5">
                <div className="w-2 h-2 bg-accent-400 rounded-full dot-pulse-1" />
                <div className="w-2 h-2 bg-accent-400 rounded-full dot-pulse-2" />
                <div className="w-2 h-2 bg-accent-400 rounded-full dot-pulse-3" />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-3 border-t border-white/5">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Type anything to create a task..."
            className="flex-1 px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-accent-500/50 focus:ring-1 focus:ring-accent-500/30 transition-all text-sm"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-5 py-3 bg-gradient-to-r from-accent-500 to-accent-600 text-white rounded-xl hover:from-accent-600 hover:to-accent-700 focus:outline-none focus:ring-2 focus:ring-accent-500/50 disabled:opacity-30 disabled:cursor-not-allowed transition-all glow-orange-sm font-medium text-sm"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}
