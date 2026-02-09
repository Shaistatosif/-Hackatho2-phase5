// T086 - WebSocket Client Service
// Phase V Todo Chatbot - Real-time Sync Client

export interface TaskUpdateMessage {
  type: 'task_update';
  action: 'created' | 'updated' | 'completed' | 'deleted';
  task_id: string;
  task: {
    id: string;
    title: string;
    status: string;
    priority: string;
    [key: string]: unknown;
  } | null;
  timestamp: string;
}

type MessageHandler = (message: TaskUpdateMessage) => void;

class WebSocketService {
  private ws: WebSocket | null = null;
  private userId: string = '';
  private handlers: Set<MessageHandler> = new Set();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  connect(userId: string): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    this.userId = userId;
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8004';
    const url = `${wsUrl}/ws/${userId}`;

    try {
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data) as TaskUpdateMessage;
          if (message.type === 'task_update') {
            this.handlers.forEach(handler => handler(message));
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.attemptReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      this.attemptReconnect();
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('Max reconnect attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);

    setTimeout(() => {
      if (this.userId) {
        this.connect(this.userId);
      }
    }, delay);
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.handlers.clear();
  }

  subscribe(handler: MessageHandler): () => void {
    this.handlers.add(handler);
    return () => {
      this.handlers.delete(handler);
    };
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

export const websocketService = new WebSocketService();
export default websocketService;
