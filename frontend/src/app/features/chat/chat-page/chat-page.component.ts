import {
  Component,
  inject,
  signal,
  computed,
  OnInit,
  OnDestroy,
  AfterViewChecked,
  AfterViewInit,
  ElementRef,
  ViewChild,
  ChangeDetectionStrategy,
  ChangeDetectorRef,
} from '@angular/core';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MarkdownModule } from 'ngx-markdown';
import {
  LucideAngularModule,
  LucideIconData,
  Bot, Plus, Trash2, Send, Loader2, MessageSquare, Settings, ChevronDown,
  Paperclip, X, Square, Sparkles, Zap, Code, HelpCircle, BookOpen,
} from 'lucide-angular';
import { ChatService, ChatSession, ChatMessage, AiKey, AiProvider } from '../../../core/services/chat.service';

interface Attachment {
  name: string;
  content: string;
}

interface LocalMessage {
  role: 'user' | 'assistant';
  content: string;
  model?: string;
  streaming?: boolean;
  attachments?: { name: string }[];
}

const SUGGESTED_PROMPTS: { icon: string; label: string; text: string }[] = [
  { icon: 'sparkles', label: 'Explain a concept',   text: 'Explain the concept of Big O notation and why it matters in algorithm design.' },
  { icon: 'code',     label: 'Write code',           text: 'Write a Python function that finds the longest common subsequence of two strings.' },
  { icon: 'zap',      label: 'Debug this',           text: 'Help me debug: my binary search always returns -1 even when the value exists.' },
  { icon: 'book',     label: 'Study plan',           text: 'Create a 2-week study plan to master dynamic programming for coding interviews.' },
];

@Component({
  selector: 'app-chat-page',
  standalone: true,
  imports: [FormsModule, MarkdownModule, LucideAngularModule, RouterLink],
  templateUrl: './chat-page.component.html',
  styleUrl: './chat-page.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ChatPageComponent implements OnInit, OnDestroy, AfterViewChecked, AfterViewInit {
  @ViewChild('messagesEnd')   private messagesEnd!:   ElementRef<HTMLDivElement>;
  @ViewChild('fileInput')     private fileInput!:     ElementRef<HTMLInputElement>;
  @ViewChild('textareaRef')   private textareaRef!:   ElementRef<HTMLTextAreaElement>;

  private readonly chatSvc = inject(ChatService);
  private readonly cdr     = inject(ChangeDetectorRef);

  // Icons
  readonly Bot           = Bot;
  readonly Plus          = Plus;
  readonly Trash2        = Trash2;
  readonly Send          = Send;
  readonly Loader2       = Loader2;
  readonly MessageSquare = MessageSquare;
  readonly Settings      = Settings;
  readonly ChevronDown   = ChevronDown;
  readonly Paperclip     = Paperclip;
  readonly X             = X;
  readonly Square        = Square;
  readonly Sparkles      = Sparkles;
  readonly Zap           = Zap;
  readonly Code          = Code;
  readonly HelpCircle    = HelpCircle;
  readonly BookOpen      = BookOpen;

  // Suggestions
  readonly suggestedPrompts = SUGGESTED_PROMPTS;

  // State
  readonly sessions        = signal<ChatSession[]>([]);
  readonly activeSessionId = signal<string | null>(null);
  readonly messages        = signal<LocalMessage[]>([]);
  readonly keys            = signal<AiKey[]>([]);
  readonly providers       = signal<AiProvider[]>([]);

  readonly loadingSessions = signal(false);
  readonly loadingMessages = signal(false);
  readonly streaming       = signal(false);
  readonly sidebarOpen     = signal(true);

  // Composer
  readonly inputText       = signal('');
  readonly selectedKeyId   = signal<string>('');
  readonly selectedModel   = signal<string>('');
  readonly pickerOpen      = signal(false);

  // Attachments
  readonly attachments     = signal<Attachment[]>([]);

  private abortStream: (() => void) | null = null;
  private shouldScroll = false;

  // Derived: available models from selected key's provider
  readonly modelOptions = computed<string[]>(() => {
    const keyId = this.selectedKeyId();
    const key   = this.keys().find(k => k.id === keyId);
    if (!key) return [];
    const provider = this.providers().find(p => p.id === key.provider);
    return provider?.models ?? (key.default_model ? [key.default_model] : []);
  });

  readonly hasKeys = computed(() => this.keys().length > 0);

  readonly sending = computed(() => this.streaming());

  ngOnInit(): void {
    this.loadProviders();
    this.loadKeys();
    this.loadSessions();
  }

  ngOnDestroy(): void {
    this.abortStream?.();
  }

  ngAfterViewChecked(): void {
    if (this.shouldScroll) {
      this.scrollToBottom();
      this.shouldScroll = false;
    }
  }

  ngAfterViewInit(): void {
    this.focusInput();
  }

  /** Put the cursor in the message box so the user can type immediately (no mouse). */
  private focusInput(): void {
    setTimeout(() => {
      try { this.textareaRef?.nativeElement?.focus(); } catch { /* ignore */ }
    }, 60);
  }

  private scrollToBottom(): void {
    try {
      this.messagesEnd?.nativeElement.scrollIntoView({ behavior: 'smooth' });
    } catch {
      // ignore
    }
  }

  private loadProviders(): void {
    this.chatSvc.getProviders().subscribe({
      next: ps => this.providers.set(ps),
      error: () => {},
    });
  }

  private loadKeys(): void {
    this.chatSvc.getKeys().subscribe({
      next: keys => {
        this.keys.set(keys);
        if (keys.length > 0 && !this.selectedKeyId()) {
          this.selectedKeyId.set(keys[0].id);
          const first = keys[0];
          if (first.default_model) this.selectedModel.set(first.default_model);
        }
        this.focusInput();
      },
      error: () => {},
    });
  }

  private loadSessions(): void {
    this.loadingSessions.set(true);
    this.chatSvc.getSessions().subscribe({
      next: ss => {
        this.sessions.set(ss);
        this.loadingSessions.set(false);
      },
      error: () => this.loadingSessions.set(false),
    });
  }

  newChat(): void {
    this.chatSvc.createSession().subscribe({
      next: session => {
        this.sessions.update(ss => [session, ...ss]);
        this.selectSession(session.id);
      },
      error: () => {},
    });
  }

  selectSession(id: string): void {
    if (this.activeSessionId() === id) return;
    this.abortStream?.();
    this.activeSessionId.set(id);
    this.loadingMessages.set(true);
    this.messages.set([]);
    this.chatSvc.getSession(id).subscribe({
      next: detail => {
        this.messages.set(
          detail.messages.map(m => ({ role: m.role, content: m.content, model: m.model }))
        );
        this.loadingMessages.set(false);
        this.shouldScroll = true;
        this.focusInput();
      },
      error: () => this.loadingMessages.set(false),
    });
  }

  deleteSession(id: string, event: MouseEvent): void {
    event.stopPropagation();
    this.chatSvc.deleteSession(id).subscribe({
      next: () => {
        this.sessions.update(ss => ss.filter(s => s.id !== id));
        if (this.activeSessionId() === id) {
          this.activeSessionId.set(null);
          this.messages.set([]);
        }
      },
      error: () => {},
    });
  }

  stopStreaming(): void {
    this.abortStream?.();
    this.abortStream = null;
    // Mark last streaming message as complete
    this.messages.update(ms =>
      ms.map((m, i) =>
        i === ms.length - 1 && m.streaming ? { ...m, streaming: false } : m
      )
    );
    this.streaming.set(false);
    this.cdr.markForCheck();
  }

  send(prefill?: string): void {
    const text = (prefill ?? this.inputText()).trim();
    if (!text || this.streaming()) return;

    const key       = this.keys().find(k => k.id === this.selectedKeyId());
    const model     = this.selectedModel() || undefined;
    const provider  = key?.provider ?? undefined;
    const atts      = this.attachments();

    const userMsg: LocalMessage = {
      role: 'user',
      content: text,
      attachments: atts.map(a => ({ name: a.name })),
    };

    const doSend = (sessionId: string) => {
      this.streaming.set(true);
      this.inputText.set('');
      this.attachments.set([]);
      this.messages.update(ms => [...ms, userMsg]);
      this.shouldScroll = true;

      // Append a placeholder streaming message
      const assistantPlaceholder: LocalMessage = {
        role: 'assistant',
        content: '',
        streaming: true,
      };
      this.messages.update(ms => [...ms, assistantPlaceholder]);
      this.cdr.markForCheck();

      const { events$, abort } = this.chatSvc.streamMessage(sessionId, {
        message:     text,
        provider,
        model,
        attachments: atts.length > 0 ? atts : undefined,
      });

      this.abortStream = abort;

      events$.subscribe({
        next: evt => {
          if (evt.token) {
            this.messages.update(ms => {
              const updated = [...ms];
              const last    = updated[updated.length - 1];
              if (last?.streaming) {
                updated[updated.length - 1] = {
                  ...last,
                  content: last.content + evt.token,
                };
              }
              return updated;
            });
            this.shouldScroll = true;
            this.cdr.markForCheck();
          }
          if (evt.done) {
            this.messages.update(ms => {
              const updated = [...ms];
              const last    = updated[updated.length - 1];
              if (last?.streaming) {
                updated[updated.length - 1] = {
                  ...last,
                  streaming: false,
                  model: evt.model,
                };
              }
              return updated;
            });
            this.streaming.set(false);
            this.abortStream = null;
            this.shouldScroll = true;
            this.cdr.markForCheck();
            this.focusInput();

            // Update session title from first message
            this.sessions.update(ss =>
              ss.map(s =>
                s.id === sessionId && s.title === 'New Chat'
                  ? { ...s, title: text.slice(0, 40) }
                  : s
              )
            );
          }
          if (evt.error) {
            this.messages.update(ms => {
              const updated = [...ms];
              const last    = updated[updated.length - 1];
              if (last?.streaming) {
                updated[updated.length - 1] = {
                  ...last,
                  streaming: false,
                  content:   last.content || 'Something went wrong. Please try again.',
                };
              }
              return updated;
            });
            this.streaming.set(false);
            this.abortStream = null;
            this.shouldScroll = true;
            this.cdr.markForCheck();
          }
        },
        error: () => {
          this.messages.update(ms => {
            const updated = [...ms];
            const last    = updated[updated.length - 1];
            if (last?.streaming) {
              updated[updated.length - 1] = {
                ...last,
                streaming: false,
                content: last.content || 'Something went wrong. Please try again.',
              };
            }
            return updated;
          });
          this.streaming.set(false);
          this.abortStream = null;
          this.shouldScroll = true;
          this.cdr.markForCheck();
        },
      });
    };

    const sessionId = this.activeSessionId();
    if (sessionId) {
      doSend(sessionId);
    } else {
      this.chatSvc.createSession(text.slice(0, 40)).subscribe({
        next: session => {
          this.sessions.update(ss => [session, ...ss]);
          this.activeSessionId.set(session.id);
          doSend(session.id);
        },
        error: () => {},
      });
    }
  }

  onKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.send();
    }
  }

  onKeyChange(keyId: string): void {
    this.selectedKeyId.set(keyId);
    const key = this.keys().find(k => k.id === keyId);
    if (key?.default_model) {
      this.selectedModel.set(key.default_model);
    } else {
      const models = this.modelOptions();
      this.selectedModel.set(models[0] ?? '');
    }
    this.pickerOpen.set(false);
  }

  toggleSidebar(): void {
    this.sidebarOpen.update(v => !v);
  }

  togglePicker(): void {
    this.pickerOpen.update(v => !v);
  }

  getSessionTitle(session: ChatSession): string {
    return session.title || 'New Chat';
  }

  formatTime(dateStr: string): string {
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    } catch {
      return '';
    }
  }

  readonly selectedKeyLabel = computed(() => {
    const k    = this.keys().find(k => k.id === this.selectedKeyId());
    if (!k) return 'Select model';
    const prov = this.providers().find(p => p.id === k.provider);
    const model   = this.selectedModel() || k.default_model || '';
    const provName = k.label || prov?.name || k.provider;
    return model ? `${provName} / ${model}` : provName;
  });

  // ── File attachment helpers ──────────────────────────────────────────────
  readonly ACCEPTED_TYPES = [
    'text/plain', 'text/markdown', 'text/x-python', 'text/x-typescript',
    'text/javascript', 'application/json', 'text/csv', 'text/html', 'text/css',
    'application/x-javascript', 'text/x-java-source', 'text/x-csrc',
    'text/x-c++src', 'text/x-shellscript',
  ];
  readonly ACCEPTED_EXTS = ['.txt','.md','.py','.js','.ts','.json','.csv','.html','.css','.sh','.java','.c','.cpp','.rs','.go'];

  openFilePicker(): void {
    this.fileInput?.nativeElement.click();
  }

  onFilesSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (!input.files) return;
    Array.from(input.files).forEach(file => this.readFile(file));
    input.value = '';   // reset so same file can be re-added
  }

  private readFile(file: File): void {
    const ext = '.' + file.name.split('.').pop()?.toLowerCase();
    const isText = this.ACCEPTED_TYPES.includes(file.type) || this.ACCEPTED_EXTS.includes(ext);

    if (!isText) {
      // Add a "unsupported" placeholder so the user gets visual feedback
      this.attachments.update(atts => [
        ...atts,
        { name: `[unsupported] ${file.name}`, content: '' },
      ]);
      this.cdr.markForCheck();
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string ?? '';
      this.attachments.update(atts => [...atts, { name: file.name, content }]);
      this.cdr.markForCheck();
    };
    reader.readAsText(file);
  }

  removeAttachment(index: number): void {
    this.attachments.update(atts => atts.filter((_, i) => i !== index));
  }

  isUnsupported(att: Attachment): boolean {
    return att.name.startsWith('[unsupported]');
  }

  getSuggestionIcon(icon: string): LucideIconData {
    switch (icon) {
      case 'sparkles': return this.Sparkles;
      case 'code':     return this.Code;
      case 'zap':      return this.Zap;
      case 'book':     return this.BookOpen;
      default:         return this.HelpCircle;
    }
  }
}
