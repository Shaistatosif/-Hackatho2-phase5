// T047 - API Service for Backend Calls
// Phase V Todo Chatbot - Frontend API Client

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  status: 'pending' | 'completed';
  priority: 'High' | 'Medium' | 'Low';
  tags: string[];
  due_at: string | null;
  remind_at: string | null;
  recurrence_pattern: 'daily' | 'weekly' | 'monthly' | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

export interface ChatResponse {
  response: string;
  task_id: string | null;
  action: string | null;
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
  page: number;
  page_size: number;
}

class ApiService {
  private token: string = '';

  setToken(token: string) {
    this.token = token;
  }

  private async fetch<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(this.token && { Authorization: `Bearer ${this.token}` }),
      ...options.headers,
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `API error: ${response.status}`);
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  }

  // Chat API
  async sendMessage(message: string): Promise<ChatResponse> {
    return this.fetch<ChatResponse>('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ message }),
    });
  }

  // Task CRUD
  async listTasks(params?: {
    status?: string;
    priority?: string;
    tags?: string;
    search?: string;
    sort_by?: string;
    sort_order?: string;
    page?: number;
    page_size?: number;
  }): Promise<TaskListResponse> {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, String(value));
        }
      });
    }
    const query = queryParams.toString();
    return this.fetch<TaskListResponse>(`/api/tasks${query ? `?${query}` : ''}`);
  }

  async createTask(data: {
    title: string;
    description?: string;
    priority?: 'High' | 'Medium' | 'Low';
    tags?: string[];
    due_at?: string;
    remind_at?: string;
    recurrence_pattern?: 'daily' | 'weekly' | 'monthly';
  }): Promise<Task> {
    return this.fetch<Task>('/api/tasks', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateTask(
    taskId: string,
    data: Partial<{
      title: string;
      description: string;
      priority: 'High' | 'Medium' | 'Low';
      tags: string[];
      due_at: string;
      remind_at: string;
      recurrence_pattern: 'daily' | 'weekly' | 'monthly';
    }>
  ): Promise<Task> {
    return this.fetch<Task>(`/api/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteTask(taskId: string): Promise<void> {
    await this.fetch<void>(`/api/tasks/${taskId}`, {
      method: 'DELETE',
    });
  }

  async completeTask(taskId: string): Promise<Task> {
    return this.fetch<Task>(`/api/tasks/${taskId}/complete`, {
      method: 'POST',
    });
  }

  async addTags(taskId: string, tags: string[]): Promise<Task> {
    return this.fetch<Task>(`/api/tasks/${taskId}/tags`, {
      method: 'POST',
      body: JSON.stringify(tags),
    });
  }

  async removeTags(taskId: string, tags: string[]): Promise<Task> {
    const query = tags.map(t => `tags=${encodeURIComponent(t)}`).join('&');
    return this.fetch<Task>(`/api/tasks/${taskId}/tags?${query}`, {
      method: 'DELETE',
    });
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    return this.fetch<{ status: string }>('/health');
  }
}

export const api = new ApiService();
export default api;
