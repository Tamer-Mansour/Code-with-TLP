export interface LocalMessage {
  role: 'user' | 'assistant';
  content: string;
  model?: string;
  streaming?: boolean;
}

export interface QuickAction {
  label: string;
  icon: any;
  prompt: string;
}
