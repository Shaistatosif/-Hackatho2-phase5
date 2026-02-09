'use client';

import { useState, useEffect, useCallback } from 'react';
import { api, Task, TaskListResponse } from '@/services/api';

interface TaskListProps {
  refreshTrigger?: number;
}

const priorityConfig = {
  High: { color: 'text-red-400', bg: 'bg-red-500/20', border: 'border-red-500/30', dot: 'bg-red-400' },
  Medium: { color: 'text-accent-400', bg: 'bg-accent-500/20', border: 'border-accent-500/30', dot: 'bg-accent-400' },
  Low: { color: 'text-green-400', bg: 'bg-green-500/20', border: 'border-green-500/30', dot: 'bg-green-400' },
};

export default function TaskList({ refreshTrigger }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [filters, setFilters] = useState({
    status: '' as '' | 'pending' | 'completed',
    priority: '' as '' | 'High' | 'Medium' | 'Low',
    search: '',
    sort_by: 'created_at',
    sort_order: 'desc',
  });

  const loadTasks = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params: Record<string, string> = {};
      if (filters.status) params.status = filters.status;
      if (filters.priority) params.priority = filters.priority;
      if (filters.search) params.search = filters.search;
      params.sort_by = filters.sort_by;
      params.sort_order = filters.sort_order;

      const response: TaskListResponse = await api.listTasks(params);
      setTasks(response.tasks);
      setTotal(response.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load tasks');
    } finally {
      setIsLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    loadTasks();
  }, [loadTasks, refreshTrigger]);

  const handleComplete = async (taskId: string) => {
    try {
      await api.completeTask(taskId);
      loadTasks();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to complete task');
    }
  };

  const handleDelete = async (taskId: string) => {
    if (!confirm('Delete this task?')) return;
    try {
      await api.deleteTask(taskId);
      loadTasks();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete task');
    }
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return null;
    return new Date(dateStr).toLocaleDateString([], { month: 'short', day: 'numeric' });
  };

  return (
    <div className="glass rounded-2xl h-full flex flex-col overflow-hidden">
      {/* Header */}
      <div className="px-5 py-4 border-b border-white/5">
        <div className="flex justify-between items-center mb-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-navy-700 flex items-center justify-center">
              <svg className="w-5 h-5 text-accent-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">My Tasks</h2>
              <p className="text-xs text-gray-400">{total} total</p>
            </div>
          </div>
          <button
            onClick={loadTasks}
            className="p-2 rounded-lg hover:bg-white/5 text-gray-400 hover:text-accent-400 transition-all"
            title="Refresh"
          >
            <svg className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-2">
          <select
            value={filters.status}
            onChange={e => setFilters(f => ({ ...f, status: e.target.value as any }))}
            className="px-3 py-1.5 text-xs bg-white/5 border border-white/10 rounded-lg text-gray-300 focus:outline-none focus:border-accent-500/50 transition-all"
          >
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="completed">Completed</option>
          </select>

          <select
            value={filters.priority}
            onChange={e => setFilters(f => ({ ...f, priority: e.target.value as any }))}
            className="px-3 py-1.5 text-xs bg-white/5 border border-white/10 rounded-lg text-gray-300 focus:outline-none focus:border-accent-500/50 transition-all"
          >
            <option value="">All Priority</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>

          <input
            type="text"
            placeholder="Search..."
            value={filters.search}
            onChange={e => setFilters(f => ({ ...f, search: e.target.value }))}
            className="px-3 py-1.5 text-xs bg-white/5 border border-white/10 rounded-lg text-gray-300 placeholder-gray-500 focus:outline-none focus:border-accent-500/50 transition-all flex-1 min-w-[100px]"
          />
        </div>
      </div>

      {/* Task List */}
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-accent-500" />
          </div>
        ) : error ? (
          <div className="p-6 text-center">
            <p className="text-red-400 text-sm">{error}</p>
            <button onClick={loadTasks} className="mt-2 text-accent-400 text-xs hover:underline">Try again</button>
          </div>
        ) : tasks.length === 0 ? (
          <div className="p-8 text-center animate-fade-in">
            <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-white/5 flex items-center justify-center">
              <svg className="w-8 h-8 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </div>
            <p className="text-gray-400 text-sm">No tasks yet</p>
            <p className="text-gray-500 text-xs mt-1">Type in the chat to create your first task!</p>
          </div>
        ) : (
          <ul className="p-2 space-y-2">
            {tasks.map((task, index) => {
              const pConfig = priorityConfig[task.priority] || priorityConfig.Medium;
              return (
                <li
                  key={task.id}
                  className={`glass-light rounded-xl p-3.5 hover-lift animate-slide-up`}
                  style={{ animationDelay: `${index * 0.05}s` }}
                >
                  <div className="flex items-start gap-3">
                    {/* Checkbox */}
                    <button
                      onClick={() => task.status === 'pending' && handleComplete(task.id)}
                      className={`mt-0.5 w-5 h-5 rounded-md border-2 flex items-center justify-center transition-all ${
                        task.status === 'completed'
                          ? 'bg-green-500/20 border-green-500 text-green-400'
                          : `border-white/20 hover:border-accent-500 hover:bg-accent-500/10`
                      }`}
                      disabled={task.status === 'completed'}
                    >
                      {task.status === 'completed' && (
                        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      )}
                    </button>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className={`font-medium text-sm ${task.status === 'completed' ? 'text-gray-500 line-through' : 'text-white'}`}>
                          {task.title}
                        </span>
                        <span className={`px-2 py-0.5 text-[10px] font-semibold rounded-full ${pConfig.bg} ${pConfig.color} border ${pConfig.border}`}>
                          {task.priority}
                        </span>
                        {task.recurrence_pattern && (
                          <span className="px-2 py-0.5 text-[10px] font-semibold rounded-full bg-purple-500/20 text-purple-400 border border-purple-500/30">
                            {task.recurrence_pattern}
                          </span>
                        )}
                      </div>

                      {task.description && (
                        <p className="mt-1 text-xs text-gray-400 truncate">{task.description}</p>
                      )}

                      <div className="mt-1.5 flex flex-wrap items-center gap-2 text-[10px] text-gray-500">
                        {task.due_at && (
                          <span className="flex items-center gap-1">
                            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                              <path strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                            {formatDate(task.due_at)}
                          </span>
                        )}
                        {task.tags.length > 0 && (
                          <div className="flex gap-1">
                            {task.tags.map(tag => (
                              <span key={tag} className="px-1.5 py-0.5 bg-white/5 text-gray-400 rounded-md border border-white/10">
                                #{tag}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Delete */}
                    <button
                      onClick={() => handleDelete(task.id)}
                      className="text-gray-600 hover:text-red-400 transition-all p-1 rounded-lg hover:bg-red-500/10"
                      title="Delete"
                    >
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </div>
  );
}
