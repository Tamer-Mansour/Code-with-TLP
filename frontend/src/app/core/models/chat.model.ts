// ── AI Providers & Keys ────────────────────────────────────────────────────
export interface AiProvider {
  id: string;
  name: string;
  base_url: string;
  models: string[];
  openai_compatible: boolean;
}

export interface AiKey {
  id: string;
  provider: string;
  base_url?: string;
  default_model?: string;
  label?: string;
  masked_key: string;
}

export interface AiKeyCreate {
  provider: string;
  api_key: string;
  base_url?: string;
  default_model?: string;
  label?: string;
}

// ── Chat Sessions & Messages ───────────────────────────────────────────────
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  model?: string;
  created_at: string;
}

export interface ChatSession {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ChatSessionDetail extends ChatSession {
  messages: ChatMessage[];
}

export interface SendMessageRequest {
  message: string;
  provider?: string;
  model?: string;
  attachments?: { name: string; content: string }[];
  /** Lesson content injected into the system prompt as primary context. */
  context?: string;
  /** Enable web-search grounding (Gemini only). */
  web_search?: boolean;
}

export interface SendMessageResponse {
  reply: string;
  model: string;
}

// ── Streaming SSE event ────────────────────────────────────────────────────
export interface SseEvent {
  token?: string;
  done?: boolean;
  model?: string;
  error?: string;
}
