import type { MessagePart } from '../../../core/models/chat-ui.model';

export interface LocalMessage {
  role: 'user' | 'assistant';
  content: string;
  model?: string;
  streaming?: boolean;
  /** Parsed text/code parts — computed for assistant messages (Claude-style). */
  parts?: MessagePart[];
}

export interface QuickAction {
  label: string;
  icon: any;
  prompt: string;
}
