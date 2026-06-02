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
}
