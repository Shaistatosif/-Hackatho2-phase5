// T048, T059 - Main Page
// Phase V Todo Chatbot - Chat UI Page
'use client';

import { useState, useEffect } from 'react';
import ChatInterface from '@/components/ChatInterface';
import TaskList from '@/components/TaskList';
import { api } from '@/services/api';

export default function Home() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [userId, setUserId] = useState<string>('');

  useEffect(() => {
    // Generate or retrieve user ID
    let storedUserId = localStorage.getItem('todo-chatbot-user-id');
    if (!storedUserId) {
      storedUserId = `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('todo-chatbot-user-id', storedUserId);
    }
    setUserId(storedUserId);
    api.setToken(storedUserId);
  }, []);

  const handleTaskChange = () => {
    // Trigger task list refresh when chat performs an action
    setRefreshTrigger(prev => prev + 1);
  };

  if (!userId) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
      </div>
    );
  }

  return (
    <main className="min-h-screen p-4 md:p-8">
      {/* Header */}
      <header className="mb-6">
        <h1 className="text-2xl md:text-3xl font-bold text-gray-900">
          Todo Chatbot
        </h1>
        <p className="text-gray-600">
          Phase V - Event-driven task management with natural language interface
        </p>
      </header>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-180px)]">
        {/* Chat Panel */}
        <div className="h-full">
          <ChatInterface onTaskChange={handleTaskChange} />
        </div>

        {/* Task List Panel */}
        <div className="h-full">
          <TaskList refreshTrigger={refreshTrigger} />
        </div>
      </div>

      {/* Footer */}
      <footer className="mt-6 text-center text-sm text-gray-500">
        <p>
          Powered by Dapr, Kafka, and Kubernetes |{' '}
          <a
            href="/docs"
            target="_blank"
            className="text-primary-600 hover:underline"
          >
            API Docs
          </a>
        </p>
      </footer>
    </main>
  );
}
