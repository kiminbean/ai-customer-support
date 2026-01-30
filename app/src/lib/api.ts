const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ChatResponse {
  response: string;
  conversation_id: string;
  agent_type?: 'faq' | 'order' | 'escalation' | string;
  confidence?: number;
  sources?: { title: string; content?: string; score?: number }[];
}

export interface Document {
  id: string;
  filename: string;
  uploaded_at: string;
  size?: number;
  chunk_count?: number;
}

export interface Conversation {
  id: string;
  user?: string;
  avatar?: string;
  last_message: string;
  status: string;
  satisfaction?: number | null;
  time: string;
  created_at?: string;
}

export interface Analytics {
  total_conversations: number;
  avg_response_time: string;
  satisfaction_rate: string;
  active_chats: number;
  ai_resolution_rate?: number;
  escalation_rate?: number;
  avg_turns?: number;
  daily_data?: { day: string; value: number }[];
  category_data?: { label: string; percentage: number; color: string }[];
  hourly_data?: { hour: string; v: number }[];
  satisfaction_distribution?: { stars: number; count: number; pct: number }[];
}

export async function sendMessage(message: string, conversationId?: string): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, conversation_id: conversationId }),
  });
  if (!res.ok) throw new Error(`Chat API error: ${res.status}`);
  return res.json();
}

export async function uploadDocument(file: File): Promise<Document> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/api/documents/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error(`Upload error: ${res.status}`);
  return res.json();
}

export async function getDocuments(): Promise<Document[]> {
  const res = await fetch(`${API_BASE}/api/documents`);
  if (!res.ok) throw new Error(`Documents API error: ${res.status}`);
  const data = await res.json();
  return Array.isArray(data) ? data : data.documents || [];
}

export async function deleteDocument(docId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/documents/${docId}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error(`Delete error: ${res.status}`);
}

export async function getConversations(): Promise<Conversation[]> {
  const res = await fetch(`${API_BASE}/api/conversations`);
  if (!res.ok) throw new Error(`Conversations API error: ${res.status}`);
  const data = await res.json();
  return Array.isArray(data) ? data : data.conversations || [];
}

export async function getAnalytics(): Promise<Analytics> {
  const res = await fetch(`${API_BASE}/api/analytics`);
  if (!res.ok) throw new Error(`Analytics API error: ${res.status}`);
  return res.json();
}

export async function updateSettings(settings: Record<string, unknown>): Promise<void> {
  const res = await fetch(`${API_BASE}/api/settings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings),
  });
  if (!res.ok) throw new Error(`Settings API error: ${res.status}`);
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/api/health`, { signal: AbortSignal.timeout(3000) });
    return res.ok;
  } catch {
    return false;
  }
}
