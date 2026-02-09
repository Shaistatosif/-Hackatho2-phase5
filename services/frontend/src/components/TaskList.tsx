// T046, T073, T081, T087 - Task List Component
// Phase V Todo Chatbot - Task Display with Filters
'use client';

import { useState, useEffect, useCallback } from 'react';
import { api, Task, TaskListResponse } from '@/services/api';

interface TaskListProps {
  refreshTrigger?: number;
}

const priorityColors = {
  High: 'text-red-600 bg-red-100',
  Medium: 'text-yellow-600 bg-yellow-100',
  Low: 'text-green-600 bg-green-100',
};

export default function TaskList({ refreshTrigger }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // T073 - Filter/sort state
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
    if (!confirm('Are you sure you want to delete this task?')) return;
    try {
      await api.deleteTask(taskId);
      loadTasks();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete task');
    }
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return null;
    return new Date(dateStr).toLocaleDateString([], {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-lg h-full flex flex-col">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-200">
        <div className="flex justify-between items-center">
          <h2 className="text-lg font-semibold text-gray-900">Tasks ({total})</h2>
          <button
            onClick={loadTasks}
            className="text-sm text-primary-600 hover:text-primary-800"
          >
            Refresh
          </button>
        </div>

        {/* T073 - Filters */}
        <div className="mt-3 flex flex-wrap gap-2">
          <select
            value={filters.status}
            onChange={e => setFilters(f => ({ ...f, status: e.target.value as any }))}
            className="px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary-500"
          >
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="completed">Completed</option>
          </select>

          <select
            value={filters.priority}
            onChange={e => setFilters(f => ({ ...f, priority: e.target.value as any }))}
            className="px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary-500"
          >
            <option value="">All Priority</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>

          <select
            value={filters.sort_by}
            onChange={e => setFilters(f => ({ ...f, sort_by: e.target.value }))}
            className="px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary-500"
          >
            <option value="created_at">Created</option>
            <option value="due_at">Due Date</option>
            <option value="priority">Priority</option>
          </select>

          <input
            type="text"
            placeholder="Search..."
            value={filters.search}
            onChange={e => setFilters(f => ({ ...f, search: e.target.value }))}
            className="px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-primary-500"
          />
        </div>
      </div>

      {/* Task List */}
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
          </div>
        ) : error ? (
          <div className="p-4 text-center text-red-600">{error}</div>
        ) : tasks.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            No tasks found. Use the chat to create one!
          </div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {tasks.map(task => (
              <li key={task.id} className="p-4 hover:bg-gray-50">
                <div className="flex items-start space-x-3">
                  {/* Checkbox */}
                  <button
                    onClick={() => task.status === 'pending' && handleComplete(task.id)}
                    className={`mt-1 w-5 h-5 rounded border-2 flex items-center justify-center ${
                      task.status === 'completed'
                        ? 'bg-green-500 border-green-500 text-white'
                        : 'border-gray-300 hover:border-primary-500'
                    }`}
                    disabled={task.status === 'completed'}
                  >
                    {task.status === 'completed' && (
                      <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path
                          fillRule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          clipRule="evenodd"
                        />
                      </svg>
                    )}
                  </button>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      <span
                        className={`font-medium ${
                          task.status === 'completed' ? 'text-gray-400 line-through' : 'text-gray-900'
                        }`}
                      >
                        {task.title}
                      </span>
                      <span
                        className={`px-2 py-0.5 text-xs font-medium rounded ${
                          priorityColors[task.priority]
                        }`}
                      >
                        {task.priority}
                      </span>
                      {task.recurrence_pattern && (
                        <span className="px-2 py-0.5 text-xs font-medium rounded bg-purple-100 text-purple-600">
                          {task.recurrence_pattern}
                        </span>
                      )}
                    </div>

                    {task.description && (
                      <p className="mt-1 text-sm text-gray-500 truncate">{task.description}</p>
                    )}

                    <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-gray-500">
                      {task.due_at && (
                        <span className="flex items-center">
                          <svg className="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          </svg>
                          {formatDate(task.due_at)}
                        </span>
                      )}
                      {task.remind_at && (
                        <span className="flex items-center text-amber-600">
                          <svg className="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                          </svg>
                          Reminder
                        </span>
                      )}

                      {/* T081 - Tags */}
                      {task.tags.length > 0 && (
                        <div className="flex gap-1">
                          {task.tags.map(tag => (
                            <span
                              key={tag}
                              className="px-1.5 py-0.5 bg-gray-200 text-gray-600 rounded"
                            >
                              #{tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Actions */}
                  <button
                    onClick={() => handleDelete(task.id)}
                    className="text-gray-400 hover:text-red-600"
                    title="Delete task"
                  >
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
