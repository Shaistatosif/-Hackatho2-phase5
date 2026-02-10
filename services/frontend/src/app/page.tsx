'use client';

import { useState, useEffect } from 'react';
import ChatInterface from '@/components/ChatInterface';
import TaskList from '@/components/TaskList';
import { api } from '@/services/api';

export default function Home() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [userId, setUserId] = useState<string>('');

  useEffect(() => {
    let storedUserId = localStorage.getItem('todo-chatbot-user-id');
    if (!storedUserId) {
      storedUserId = `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('todo-chatbot-user-id', storedUserId);
    }
    setUserId(storedUserId);
    api.setToken(storedUserId);
  }, []);

  const handleTaskChange = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  if (!userId) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-navy-900">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-accent-500" />
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-navy-900 via-navy-800 to-navy-700 p-4 md:p-6">
      {/* Animated background blobs */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-accent-500/5 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-navy-400/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '1.5s' }} />
        <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-accent-600/5 rounded-full blur-3xl animate-float" style={{ animationDelay: '3s' }} />
      </div>

      {/* Header */}
      <header className="relative mb-6 animate-fade-in">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            {/* Animated Chatbot Icon */}
            <div className="relative">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-accent-500 to-accent-600 flex items-center justify-center glow-orange animate-float">
                <svg className="w-8 h-8 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                  <rect x="3" y="4" width="18" height="12" rx="3" />
                  <circle cx="9" cy="10" r="1.5" fill="currentColor" stroke="none" />
                  <circle cx="15" cy="10" r="1.5" fill="currentColor" stroke="none" />
                  <path d="M9 13.5c0 0 1.5 1.5 3 1.5s3-1.5 3-1.5" strokeLinecap="round" />
                  <path d="M12 16v2" />
                  <path d="M8 18h8" strokeLinecap="round" />
                  <path d="M2 8h1" strokeLinecap="round" />
                  <path d="M21 8h1" strokeLinecap="round" />
                  <path d="M12 2v2" strokeLinecap="round" />
                </svg>
              </div>
              {/* Pulse ring */}
              <div className="absolute inset-0 rounded-2xl border-2 border-accent-500/40 animate-ping" style={{ animationDuration: '2s' }} />
            </div>
            <div>
              <h1 className="text-2xl md:text-3xl font-bold text-white">
                Shaista&apos;s <span className="text-accent-500 text-glow">Todo Chatbot</span>
              </h1>
              <p className="text-gray-400 text-sm">
                AI-Powered Task Management &bull; Phase V
              </p>
            </div>
          </div>

          {/* Status badge */}
          <div className="hidden md:flex items-center gap-2 glass rounded-full px-4 py-2">
            <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            <span className="text-green-400 text-sm font-medium">Live</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="relative grid grid-cols-1 lg:grid-cols-2 gap-5 h-[calc(100vh-160px)]">
        <div className="h-full animate-slide-in-left">
          <ChatInterface onTaskChange={handleTaskChange} />
        </div>
        <div className="h-full animate-slide-in-right">
          <TaskList refreshTrigger={refreshTrigger} />
        </div>
      </div>

    </main>
  );
}
