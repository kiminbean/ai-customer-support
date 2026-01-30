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

// ── Data Hub API ──

export interface DatahubDomain {
  domain: string;
  count: number;
  icon?: string;
  description?: string;
}

export interface DatahubDataset {
  id: string;
  name: string;
  description?: string;
  domain?: string;
  size?: string;
  language?: string;
  quality_score?: number;
  format?: string;
  use_cases?: string[];
  status?: 'not_downloaded' | 'downloading' | 'downloaded' | 'processing' | 'imported';
  download_progress?: number;
  process_progress?: number;
}

export interface DatahubJobResponse {
  job_id: string;
}

export interface DatahubJobStatus {
  job_id: string;
  status: string;
  progress: number;
  error?: string;
}

export interface DatahubImportedDataset {
  dataset_id: string;
  name?: string;
  imported_at?: string;
  qa_pairs?: number;
  documents?: number;
}

export async function getDatahubDomains(): Promise<DatahubDomain[]> {
  const res = await fetch(`${API_BASE}/api/datahub/domains`);
  if (!res.ok) throw new Error(`Datahub domains error: ${res.status}`);
  return res.json();
}

export async function getDatahubDatasets(domain?: string): Promise<DatahubDataset[]> {
  const url = domain
    ? `${API_BASE}/api/datahub/datasets?domain=${encodeURIComponent(domain)}`
    : `${API_BASE}/api/datahub/datasets`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Datahub datasets error: ${res.status}`);
  return res.json();
}

export async function searchDatahubDatasets(query: string): Promise<DatahubDataset[]> {
  const res = await fetch(`${API_BASE}/api/datahub/search?q=${encodeURIComponent(query)}`);
  if (!res.ok) throw new Error(`Datahub search error: ${res.status}`);
  return res.json();
}

export async function downloadDataset(datasetId: string): Promise<DatahubJobResponse> {
  const res = await fetch(`${API_BASE}/api/datahub/download`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dataset_id: datasetId }),
  });
  if (!res.ok) throw new Error(`Datahub download error: ${res.status}`);
  return res.json();
}

export async function getDownloadStatus(jobId: string): Promise<DatahubJobStatus> {
  const res = await fetch(`${API_BASE}/api/datahub/download/${encodeURIComponent(jobId)}/status`);
  if (!res.ok) throw new Error(`Datahub download status error: ${res.status}`);
  return res.json();
}

export async function processDataset(datasetId: string, translate: boolean): Promise<DatahubJobResponse> {
  const res = await fetch(`${API_BASE}/api/datahub/process`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dataset_id: datasetId, translate }),
  });
  if (!res.ok) throw new Error(`Datahub process error: ${res.status}`);
  return res.json();
}

export async function getProcessStatus(jobId: string): Promise<DatahubJobStatus> {
  const res = await fetch(`${API_BASE}/api/datahub/process/${encodeURIComponent(jobId)}/status`);
  if (!res.ok) throw new Error(`Datahub process status error: ${res.status}`);
  return res.json();
}

export async function importDataset(datasetId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/datahub/import`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dataset_id: datasetId }),
  });
  if (!res.ok) throw new Error(`Datahub import error: ${res.status}`);
}

export async function getImportedDatasets(): Promise<DatahubImportedDataset[]> {
  const res = await fetch(`${API_BASE}/api/datahub/imported`);
  if (!res.ok) throw new Error(`Datahub imported error: ${res.status}`);
  return res.json();
}

// ── Crawler API ──

export interface CrawlStartResponse {
  job_id: string;
}

export interface CrawlStatus {
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  pages_crawled: number;
  pages_total: number;
  current_url?: string;
}

export interface CrawlFAQ {
  question: string;
  answer: string;
  sourceUrl: string;
}

export interface CrawlArticle {
  title: string;
  content: string;
  sourceUrl: string;
}

export interface CrawlProduct {
  name: string;
  description: string;
  sourceUrl: string;
}

export interface CrawlPolicy {
  title: string;
  content: string;
  sourceUrl: string;
}

export interface CrawlResults {
  pages?: number;
  faqs: CrawlFAQ[];
  articles: CrawlArticle[];
  products: CrawlProduct[];
  policies: CrawlPolicy[];
}

export interface CrawlJob {
  job_id: string;
  url: string;
  status: string;
  created_at: string;
  pages_crawled?: number;
  items_found?: number;
}

export async function startCrawl(
  url: string,
  options?: { maxDepth?: number; maxPages?: number; includePatterns?: string[]; extractMode?: string }
): Promise<CrawlStartResponse> {
  const res = await fetch(`${API_BASE}/api/crawler/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      url,
      max_depth: options?.maxDepth,
      max_pages: options?.maxPages,
      include_patterns: options?.includePatterns,
      extract_mode: options?.extractMode,
    }),
  });
  if (!res.ok) throw new Error(`Crawler start error: ${res.status}`);
  return res.json();
}

export async function getCrawlStatus(jobId: string): Promise<CrawlStatus> {
  const res = await fetch(`${API_BASE}/api/crawler/status/${encodeURIComponent(jobId)}`);
  if (!res.ok) throw new Error(`Crawler status error: ${res.status}`);
  return res.json();
}

export async function getCrawlResults(jobId: string): Promise<CrawlResults> {
  const res = await fetch(`${API_BASE}/api/crawler/results/${encodeURIComponent(jobId)}`);
  if (!res.ok) throw new Error(`Crawler results error: ${res.status}`);
  return res.json();
}

export async function convertCrawlResults(jobId: string, selectedItems?: number[]): Promise<void> {
  const res = await fetch(`${API_BASE}/api/crawler/results/${encodeURIComponent(jobId)}/convert`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ selected_items: selectedItems }),
  });
  if (!res.ok) throw new Error(`Crawler convert error: ${res.status}`);
}

export async function importCrawlResults(jobId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/crawler/results/${encodeURIComponent(jobId)}/import`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error(`Crawler import error: ${res.status}`);
}

export async function getCrawlJobs(): Promise<CrawlJob[]> {
  const res = await fetch(`${API_BASE}/api/crawler/jobs`);
  if (!res.ok) throw new Error(`Crawler jobs error: ${res.status}`);
  return res.json();
}
