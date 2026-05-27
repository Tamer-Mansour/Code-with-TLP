import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, Subject } from 'rxjs';
import { environment } from '../../../environments/environment';
import { AuthService } from './auth.service';

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

@Injectable({ providedIn: 'root' })
export class ChatService {
  private readonly http   = inject(HttpClient);
  private readonly auth   = inject(AuthService);
  private readonly base   = `${environment.apiUrl}/ai`;

  // ── Providers ────────────────────────────────────────────────────────────
  getProviders(): Observable<AiProvider[]> {
    return this.http.get<AiProvider[]>(`${this.base}/providers`);
  }

  // ── Keys ─────────────────────────────────────────────────────────────────
  getKeys(): Observable<AiKey[]> {
    return this.http.get<AiKey[]>(`${this.base}/keys`);
  }

  addKey(payload: AiKeyCreate): Observable<AiKey> {
    return this.http.post<AiKey>(`${this.base}/keys`, payload);
  }

  deleteKey(id: string): Observable<void> {
    return this.http.delete<void>(`${this.base}/keys/${id}`);
  }

  // ── Sessions ─────────────────────────────────────────────────────────────
  getSessions(): Observable<ChatSession[]> {
    return this.http.get<ChatSession[]>(`${this.base}/chat/sessions`);
  }

  createSession(title?: string): Observable<ChatSession> {
    return this.http.post<ChatSession>(`${this.base}/chat/sessions`, title ? { title } : {});
  }

  getSession(id: string): Observable<ChatSessionDetail> {
    return this.http.get<ChatSessionDetail>(`${this.base}/chat/sessions/${id}`);
  }

  deleteSession(id: string): Observable<void> {
    return this.http.delete<void>(`${this.base}/chat/sessions/${id}`);
  }

  // ── Messages (non-stream fallback) ────────────────────────────────────────
  sendMessage(sessionId: string, req: SendMessageRequest): Observable<SendMessageResponse> {
    return this.http.post<SendMessageResponse>(
      `${this.base}/chat/sessions/${sessionId}/messages`,
      req
    );
  }

  // ── Streaming via fetch + ReadableStream ──────────────────────────────────
  /**
   * Streams assistant reply token-by-token using the SSE endpoint.
   * Returns a Subject that emits SseEvent objects and completes on `done` or errors.
   * The caller must subscribe; an AbortController is returned so streaming can be cancelled.
   */
  streamMessage(
    sessionId: string,
    req: SendMessageRequest
  ): { events$: Subject<SseEvent>; abort: () => void } {
    const subject    = new Subject<SseEvent>();
    const controller = new AbortController();

    const token = this.auth.getAccessToken();
    const url   = `${this.base}/chat/sessions/${sessionId}/messages/stream`;

    const run = async () => {
      try {
        const response = await fetch(url, {
          method:  'POST',
          signal:  controller.signal,
          headers: {
            'Content-Type':  'application/json',
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          body: JSON.stringify(req),
        });

        if (!response.ok || !response.body) {
          subject.error(new Error(`HTTP ${response.status}`));
          return;
        }

        const reader  = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let   buffer  = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          // SSE messages are separated by double newline
          const parts = buffer.split('\n\n');
          buffer = parts.pop() ?? '';          // keep incomplete chunk

          for (const part of parts) {
            const line = part.trim();
            if (!line.startsWith('data:')) continue;
            const raw = line.slice(5).trim();
            try {
              const evt: SseEvent = JSON.parse(raw);
              subject.next(evt);
              if (evt.done || evt.error) {
                subject.complete();
                return;
              }
            } catch {
              // ignore malformed JSON
            }
          }
        }

        subject.complete();
      } catch (err: unknown) {
        if (err instanceof Error && err.name === 'AbortError') {
          subject.complete();   // user cancelled — not an error
        } else {
          subject.error(err);
        }
      }
    };

    run();

    return { events$: subject, abort: () => controller.abort() };
  }
}
