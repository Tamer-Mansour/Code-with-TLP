import type { MessagePart } from '../../../core/models/chat-ui.model';

export interface Attachment {
  name: string;
  content: string;
}

export interface LocalMessage {
  role: 'user' | 'assistant';
  content: string;
  model?: string;
  streaming?: boolean;
  attachments?: { name: string }[];
  /** Parsed text/code parts — computed for assistant messages (Claude-style). */
  parts?: MessagePart[];
}
