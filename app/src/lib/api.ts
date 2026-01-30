const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || '';

function getAuthHeaders(): Record<string, string> {
  if (!API_KEY) return {};
  return { 'X-API-Key': API_KEY };
}

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
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify({ message, conversation_id: conversationId }),
  });
  if (!res.ok) throw new Error(`Chat API error: ${res.status}`);
  const data = await res.json();
  return {
    response: data.answer ?? data.response ?? '',
    conversation_id: data.conversation_id ?? '',
    agent_type: data.agent ?? data.agent_type,
    confidence: data.confidence,
    sources: data.source_documents ?? data.sources ?? [],
  };
}

export interface UploadResponse {
  status: string;
  filename: string;
  chunks_created: number;
  message: string;
}

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/api/documents/upload`, {
    method: 'POST',
    headers: { ...getAuthHeaders() },
    body: formData,
  });
  if (!res.ok) throw new Error(`Upload error: ${res.status}`);
  return res.json();
}

export async function getDocuments(): Promise<Document[]> {
  const res = await fetch(`${API_BASE}/api/documents`, { headers: { ...getAuthHeaders() } });
  if (!res.ok) throw new Error(`Documents API error: ${res.status}`);
  const data = await res.json();
  return Array.isArray(data) ? data : data.documents || [];
}

export async function deleteDocument(docId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/documents/${docId}`, {
    method: 'DELETE',
    headers: { ...getAuthHeaders() },
  });
  if (!res.ok) throw new Error(`Delete error: ${res.status}`);
}

export async function getConversations(): Promise<Conversation[]> {
  const res = await fetch(`${API_BASE}/api/conversations`, { headers: { ...getAuthHeaders() } });
  if (!res.ok) throw new Error(`Conversations API error: ${res.status}`);
  const data = await res.json();
  return Array.isArray(data) ? data : data.conversations || [];
}

export async function getAnalytics(): Promise<Analytics> {
  const res = await fetch(`${API_BASE}/api/analytics`, { headers: { ...getAuthHeaders() } });
  if (!res.ok) throw new Error(`Analytics API error: ${res.status}`);
  const data = await res.json();
  return {
    total_conversations: data.total_conversations ?? 0,
    avg_response_time: data.avg_response_time ?? '0.3초',
    satisfaction_rate: data.satisfaction_rate ?? '95%',
    active_chats: data.active_chats ?? 0,
    ai_resolution_rate: data.ai_resolution_rate,
    escalation_rate: data.escalation_rate,
    avg_turns: data.avg_messages_per_conversation ?? data.avg_turns,
    daily_data: data.daily_data,
    category_data: data.category_data,
    hourly_data: data.hourly_data,
    satisfaction_distribution: data.satisfaction_distribution,
  };
}

export async function updateSettings(settings: Record<string, unknown>): Promise<void> {
  const res = await fetch(`${API_BASE}/api/settings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify(settings),
  });
  if (!res.ok) throw new Error(`Settings API error: ${res.status}`);
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/api/health`, { headers: { ...getAuthHeaders() }, signal: AbortSignal.timeout(3000) });
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
  const res = await fetch(`${API_BASE}/api/datahub/domains`, { headers: { ...getAuthHeaders() } });
  if (!res.ok) throw new Error(`Datahub domains error: ${res.status}`);
  const data = await res.json();
  return data.domains ?? data;
}

export async function getDatahubDatasets(domain?: string): Promise<DatahubDataset[]> {
  const url = domain
    ? `${API_BASE}/api/datahub/datasets?domain=${encodeURIComponent(domain)}`
    : `${API_BASE}/api/datahub/datasets`;
  const res = await fetch(url, { headers: { ...getAuthHeaders() } });
  if (!res.ok) throw new Error(`Datahub datasets error: ${res.status}`);
  const data = await res.json();
  return data.datasets ?? data;
}

export async function searchDatahubDatasets(query: string): Promise<DatahubDataset[]> {
  const res = await fetch(`${API_BASE}/api/datahub/search?q=${encodeURIComponent(query)}`, { headers: { ...getAuthHeaders() } });
  if (!res.ok) throw new Error(`Datahub search error: ${res.status}`);
  const data = await res.json();
  return data.results ?? data.datasets ?? data;
}

export async function downloadDataset(datasetId: string): Promise<DatahubJobResponse> {
  const res = await fetch(`${API_BASE}/api/datahub/download`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify({ dataset_id: datasetId }),
  });
  if (!res.ok) throw new Error(`Datahub download error: ${res.status}`);
  return res.json();
}

export async function getDownloadStatus(jobId: string): Promise<DatahubJobStatus> {
  const res = await fetch(`${API_BASE}/api/datahub/download/${encodeURIComponent(jobId)}/status`, { headers: { ...getAuthHeaders() } });
  if (!res.ok) throw new Error(`Datahub download status error: ${res.status}`);
  return res.json();
}

export async function processDataset(datasetId: string, translate: boolean): Promise<DatahubJobResponse> {
  const res = await fetch(`${API_BASE}/api/datahub/process`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify({ dataset_id: datasetId, translate }),
  });
  if (!res.ok) throw new Error(`Datahub process error: ${res.status}`);
  return res.json();
}

export async function getProcessStatus(jobId: string): Promise<DatahubJobStatus> {
  const res = await fetch(`${API_BASE}/api/datahub/process/${encodeURIComponent(jobId)}/status`, { headers: { ...getAuthHeaders() } });
  if (!res.ok) throw new Error(`Datahub process status error: ${res.status}`);
  return res.json();
}

export async function importDataset(datasetId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/datahub/import`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify({ dataset_id: datasetId }),
  });
  if (!res.ok) throw new Error(`Datahub import error: ${res.status}`);
}

export async function getImportedDatasets(): Promise<DatahubImportedDataset[]> {
  const res = await fetch(`${API_BASE}/api/datahub/imported`, { headers: { ...getAuthHeaders() } });
  if (!res.ok) throw new Error(`Datahub imported error: ${res.status}`);
  const data = await res.json();
  return data.imported_datasets ?? data;
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
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
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
  const res = await fetch(`${API_BASE}/api/crawler/status/${encodeURIComponent(jobId)}`, { headers: { ...getAuthHeaders() } });
  if (!res.ok) throw new Error(`Crawler status error: ${res.status}`);
  return res.json();
}

export async function getCrawlResults(jobId: string): Promise<CrawlResults> {
  const res = await fetch(`${API_BASE}/api/crawler/results/${encodeURIComponent(jobId)}`, { headers: { ...getAuthHeaders() } });
  if (!res.ok) throw new Error(`Crawler results error: ${res.status}`);
  return res.json();
}

export async function convertCrawlResults(jobId: string, selectedItems?: number[]): Promise<void> {
  const res = await fetch(`${API_BASE}/api/crawler/results/${encodeURIComponent(jobId)}/convert`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify({ selected_items: selectedItems }),
  });
  if (!res.ok) throw new Error(`Crawler convert error: ${res.status}`);
}

export async function importCrawlResults(jobId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/crawler/results/${encodeURIComponent(jobId)}/import`, {
    method: 'POST',
    headers: { ...getAuthHeaders() },
  });
  if (!res.ok) throw new Error(`Crawler import error: ${res.status}`);
}

export async function getCrawlJobs(): Promise<CrawlJob[]> {
  const res = await fetch(`${API_BASE}/api/crawler/jobs`, { headers: { ...getAuthHeaders() } });
  if (!res.ok) throw new Error(`Crawler jobs error: ${res.status}`);
  return res.json();
}

// ── Voice API ──

export interface VoiceJobResponse {
  job_id: string;
  status: string;
  progress: number;
  current_step: string;
  source_file: string;
  message: string;
}

export interface VoiceJobStatus {
  job_id: string;
  status: string;
  progress: number;
  current_step: string;
  source_file: string;
  created_at: string;
  updated_at: string;
  error_message: string | null;
}

export interface VoiceTranscriptSegment {
  speaker: string;
  text: string;
  start_time: number;
  end_time: number;
}

export interface VoiceTranscript {
  job_id: string;
  transcript: {
    segments: VoiceTranscriptSegment[];
    language: string;
    duration: number;
    method: string;
  };
  full_text: string;
}

export interface VoiceQAPair {
  question: string;
  answer: string;
  category: string;
  confidence: number;
}

export interface VoiceDocument {
  job_id: string;
  status: string;
  document: {
    qa_pairs: VoiceQAPair[];
    qa_count: number;
    primary_category: string;
    confidence: number;
    source_file: string;
    generated_date: string;
    markdown: string;
  };
  preview: string;
}

export interface VoiceJob {
  job_id: string;
  status: string;
  progress: number;
  current_step: string;
  source_file: string;
  created_at: string;
  updated_at: string;
  error_message: string | null;
  transcript_summary?: {
    segment_count: number;
    duration: number;
    language: string;
    method: string;
  };
  document_summary?: {
    qa_count: number;
    primary_category: string;
    confidence: number;
  };
}

export async function uploadVoice(file: File): Promise<VoiceJobResponse> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/api/voice/upload`, {
    method: 'POST',
    headers: { ...getAuthHeaders() },
    body: formData,
  });
  if (!res.ok) throw new Error(`Voice upload error: ${res.status}`);
  return res.json();
}

export async function runVoiceDemo(): Promise<VoiceJobResponse> {
  const res = await fetch(`${API_BASE}/api/voice/demo`, {
    method: 'POST',
    headers: { ...getAuthHeaders() },
  });
  if (!res.ok) throw new Error(`Voice demo error: ${res.status}`);
  return res.json();
}

export async function getVoiceJobStatus(jobId: string): Promise<VoiceJobStatus> {
  const res = await fetch(`${API_BASE}/api/voice/status/${encodeURIComponent(jobId)}`, {
    headers: { ...getAuthHeaders() },
  });
  if (!res.ok) throw new Error(`Voice status error: ${res.status}`);
  return res.json();
}

export async function getVoiceTranscript(jobId: string): Promise<VoiceTranscript> {
  const res = await fetch(`${API_BASE}/api/voice/transcript/${encodeURIComponent(jobId)}`, {
    headers: { ...getAuthHeaders() },
  });
  if (!res.ok) throw new Error(`Voice transcript error: ${res.status}`);
  return res.json();
}

export async function getVoiceDocument(jobId: string): Promise<VoiceDocument> {
  const res = await fetch(`${API_BASE}/api/voice/document/${encodeURIComponent(jobId)}`, {
    headers: { ...getAuthHeaders() },
  });
  if (!res.ok) throw new Error(`Voice document error: ${res.status}`);
  return res.json();
}

export async function approveVoiceDocument(
  jobId: string,
  qaPairs?: VoiceQAPair[]
): Promise<{ status: string; documents_added: number; message: string }> {
  const res = await fetch(`${API_BASE}/api/voice/document/${encodeURIComponent(jobId)}/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify({ qa_pairs: qaPairs }),
  });
  if (!res.ok) throw new Error(`Voice approve error: ${res.status}`);
  return res.json();
}

export async function getVoiceJobs(): Promise<{ jobs: VoiceJob[]; total: number }> {
  const res = await fetch(`${API_BASE}/api/voice/jobs`, {
    headers: { ...getAuthHeaders() },
  });
  if (!res.ok) throw new Error(`Voice jobs error: ${res.status}`);
  return res.json();
}
