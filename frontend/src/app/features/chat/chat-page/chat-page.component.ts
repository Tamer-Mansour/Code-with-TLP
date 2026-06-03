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
import { NgTemplateOutlet } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MarkdownModule } from 'ngx-markdown';
import {
  LucideAngularModule,
  Bot, Plus, Trash2, Send, Loader2, MessageSquare, Settings, ChevronDown,
  Paperclip, X, Square, PanelLeft, Code2,
} from 'lucide-angular';
import { ChatService } from '../../../core/services/chat.service';
import { CodeBlockService } from '../../../core/services/code-block.service';
import type { ChatSession, ChatMessage, AiKey, AiProvider } from '../../../core/models/chat.model';
import type { CodeArtifact } from '../../../core/models/chat-ui.model';
import type { Attachment, LocalMessage } from '../models/chat-page.model';
import { CodeArtifactPanelComponent } from '../../../shared/components/code-artifact-panel/code-artifact-panel.component';
import { CodeCardComponent } from '../../../shared/components/code-artifact-panel/code-card.component';
import { DragResizeDirective } from '../../../shared/directives/drag-resize.directive';

const PANEL_WIDTH_KEY = 'tlp.chat.panelWidth';
const PANEL_DEFAULT_WIDTH = 520;
const PANEL_MIN_WIDTH = 360;

@Component({
  selector: 'app-chat-page',
  standalone: true,
  imports: [
    FormsModule, MarkdownModule, LucideAngularModule, RouterLink, NgTemplateOutlet,
    CodeArtifactPanelComponent, CodeCardComponent, DragResizeDirective,
  ],
  templateUrl: './chat-page.component.html',
  styleUrl: './chat-page.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ChatPageComponent implements OnInit, OnDestroy, AfterViewChecked, AfterViewInit {
  @ViewChild('messagesEnd')    private messagesEnd!:    ElementRef<HTMLDivElement>;
  @ViewChild('fileInput')      private fileInput!:      ElementRef<HTMLInputElement>;
  @ViewChild('textareaRef')    private textareaRef!:    ElementRef<HTMLTextAreaElement>;
  @ViewChild('splitContainer') private splitContainer?: ElementRef<HTMLElement>;

  private readonly chatSvc    = inject(ChatService);
  private readonly codeBlocks = inject(CodeBlockService);
  private readonly cdr        = inject(ChangeDetectorRef);

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
  readonly PanelLeft     = PanelLeft;
  readonly Code2         = Code2;

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

  // ── Code-artifact panel (Claude-style) ────────────────────────────────────
  readonly panelOpen      = signal(false);
  readonly panelExpanded  = signal(false);
  readonly panelArtifacts = signal<CodeArtifact[]>([]);
  readonly activeArtifactId = signal<string | null>(null);
  readonly panelStreaming = signal(false);
  readonly panelWidth     = signal<number>(this.readStoredWidth());
  /** Index of the message whose artifacts populate the panel. */
  private panelMsgIndex: number | null = null;
  /** True once the user closes the panel during a stream — don't auto-reopen. */
  private panelDismissed = false;

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

  // ── Lifecycle ──────────────────────────────────────────────────────────────
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

  private focusInput(): void {
    setTimeout(() => {
      try { this.textareaRef?.nativeElement?.focus(); } catch { /* ignore */ }
    }, 60);
  }

  private scrollToBottom(): void {
    try {
      this.messagesEnd?.nativeElement.scrollIntoView({ behavior: 'smooth' });
    } catch { /* ignore */ }
  }

  // ── Loaders ─────────────────────────────────────────────────────────────────
  private loadProviders(): void {
    this.chatSvc.getProviders().subscribe({ next: ps => this.providers.set(ps), error: () => {} });
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
      next: ss => { this.sessions.set(ss); this.loadingSessions.set(false); },
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
    this.closePanel();
    this.activeSessionId.set(id);
    this.loadingMessages.set(true);
    this.messages.set([]);
    this.chatSvc.getSession(id).subscribe({
      next: detail => {
        this.messages.set(
          detail.messages.map(m => this.decorate({ role: m.role, content: m.content, model: m.model }))
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
          this.closePanel();
        }
      },
      error: () => {},
    });
  }

  stopStreaming(): void {
    this.abortStream?.();
    this.abortStream = null;
    this.messages.update(ms =>
      ms.map((m, i) => (i === ms.length - 1 && m.streaming ? { ...m, streaming: false } : m))
    );
    this.streaming.set(false);
    this.panelStreaming.set(false);
    this.cdr.markForCheck();
  }

  // ── Send / stream ────────────────────────────────────────────────────────────
  send(prefill?: string): void {
    const text = (prefill ?? this.inputText()).trim();
    if (!text || this.streaming()) return;

    const key      = this.keys().find(k => k.id === this.selectedKeyId());
    const model    = this.selectedModel() || undefined;
    const provider = key?.provider ?? undefined;
    const atts     = this.attachments();

    const userMsg: LocalMessage = {
      role: 'user',
      content: text,
      attachments: atts.map(a => ({ name: a.name })),
    };

    const doSend = (sessionId: string) => {
      this.streaming.set(true);
      this.panelDismissed = false;
      this.inputText.set('');
      this.attachments.set([]);
      this.messages.update(ms => [...ms, userMsg, { role: 'assistant', content: '', streaming: true, parts: [] }]);
      this.shouldScroll = true;
      this.cdr.markForCheck();

      const { events$, abort } = this.chatSvc.streamMessage(sessionId, {
        message: text, provider, model,
        attachments: atts.length > 0 ? atts : undefined,
      });
      this.abortStream = abort;

      events$.subscribe({
        next: evt => {
          if (evt.token) this.onToken(evt.token);
          if (evt.done) this.onStreamEnd(evt.model);
          if (evt.error) this.onStreamEnd(undefined, evt.error);
        },
        error: () => this.onStreamEnd(undefined, 'Something went wrong. Please try again.'),
      });

      // Title the session from the first user message.
      this.sessions.update(ss =>
        ss.map(s => (s.id === sessionId && s.title === 'New Chat' ? { ...s, title: text.slice(0, 40) } : s))
      );
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

  private onToken(token: string): void {
    let lastIndex = -1;
    this.messages.update(ms => {
      const updated = [...ms];
      const i = updated.length - 1;
      const last = updated[i];
      if (last?.streaming) {
        updated[i] = this.decorate({ ...last, content: last.content + token });
        lastIndex = i;
      }
      return updated;
    });
    if (lastIndex >= 0) this.syncPanel(lastIndex, true);
    this.shouldScroll = true;
    this.cdr.markForCheck();
  }

  private onStreamEnd(model?: string, errorContent?: string): void {
    let lastIndex = -1;
    this.messages.update(ms => {
      const updated = [...ms];
      const i = updated.length - 1;
      const last = updated[i];
      if (last?.streaming) {
        updated[i] = this.decorate({
          ...last,
          streaming: false,
          model: model ?? last.model,
          content: errorContent ? (last.content || errorContent) : last.content,
        });
        lastIndex = i;
      }
      return updated;
    });
    if (lastIndex >= 0) this.syncPanel(lastIndex, false);
    this.streaming.set(false);
    this.panelStreaming.set(false);
    this.abortStream = null;
    this.shouldScroll = true;
    this.cdr.markForCheck();
    this.focusInput();
  }

  /** Attach parsed parts to assistant messages so the template renders text + code cards. */
  private decorate(msg: LocalMessage): LocalMessage {
    if (msg.role !== 'assistant') return msg;
    return { ...msg, parts: this.codeBlocks.segment(msg.content) };
  }

  // ── Artifact panel ───────────────────────────────────────────────────────────
  /** Refresh the panel from a message's code artifacts (called as tokens stream). */
  private syncPanel(msgIndex: number, streaming: boolean): void {
    const msg = this.messages()[msgIndex];
    if (!msg) return;
    const artifacts = (msg.parts ?? [])
      .filter((p): p is { kind: 'code'; artifact: CodeArtifact } => p.kind === 'code')
      .map(p => p.artifact);

    if (artifacts.length === 0) return;

    this.panelMsgIndex = msgIndex;
    this.panelArtifacts.set(artifacts);
    this.panelStreaming.set(streaming);

    const last = artifacts[artifacts.length - 1];
    const shouldAutoOpen = !this.panelDismissed && last.lineCount >= this.codeBlocks.AUTO_OPEN_MIN_LINES;
    if (shouldAutoOpen) {
      this.panelOpen.set(true);
      // Keep following the freshest block while streaming.
      if (streaming || !this.activeArtifactId()) this.activeArtifactId.set(last.id);
    }
  }

  /** Open a specific artifact from an inline code card. */
  openArtifact(msgIndex: number, id: string): void {
    const msg = this.messages()[msgIndex];
    if (!msg) return;
    const artifacts = (msg.parts ?? [])
      .filter((p): p is { kind: 'code'; artifact: CodeArtifact } => p.kind === 'code')
      .map(p => p.artifact);
    if (artifacts.length === 0) return;
    this.panelMsgIndex = msgIndex;
    this.panelArtifacts.set(artifacts);
    this.activeArtifactId.set(id);
    this.panelStreaming.set(!!msg.streaming);
    this.panelDismissed = false;
    this.panelOpen.set(true);
  }

  isActiveArtifact(msgIndex: number, id: string): boolean {
    return this.panelOpen() && this.panelMsgIndex === msgIndex && this.activeArtifactId() === id;
  }

  onActiveIdChange(id: string): void { this.activeArtifactId.set(id); }

  closePanel(): void {
    this.panelOpen.set(false);
    this.panelExpanded.set(false);
    if (this.streaming()) this.panelDismissed = true;
  }

  toggleExpand(): void { this.panelExpanded.update(v => !v); }

  // ── Resize ───────────────────────────────────────────────────────────────────
  private readStoredWidth(): number {
    const raw = Number(localStorage.getItem(PANEL_WIDTH_KEY));
    return Number.isFinite(raw) && raw >= PANEL_MIN_WIDTH ? raw : PANEL_DEFAULT_WIDTH;
  }

  onResizeMove(clientX: number): void {
    const host = this.splitContainer?.nativeElement;
    if (!host) return;
    const rect = host.getBoundingClientRect();
    const maxWidth = Math.max(PANEL_MIN_WIDTH, rect.width - 380);
    const next = Math.min(maxWidth, Math.max(PANEL_MIN_WIDTH, rect.right - clientX));
    this.panelWidth.set(Math.round(next));
  }

  persistWidth(): void {
    localStorage.setItem(PANEL_WIDTH_KEY, String(this.panelWidth()));
  }

  resetPanelWidth(): void {
    this.panelWidth.set(PANEL_DEFAULT_WIDTH);
    this.persistWidth();
  }

  // ── Composer / misc (unchanged behaviour) ─────────────────────────────────────
  onKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.send();
    }
  }

  onKeyChange(keyId: string): void {
    this.selectedKeyId.set(keyId);
    const key = this.keys().find(k => k.id === keyId);
    if (key?.default_model) this.selectedModel.set(key.default_model);
    else this.selectedModel.set(this.modelOptions()[0] ?? '');
    this.pickerOpen.set(false);
  }

  toggleSidebar(): void { this.sidebarOpen.update(v => !v); }
  togglePicker(): void { this.pickerOpen.update(v => !v); }

  getSessionTitle(session: ChatSession): string { return session.title || 'New Chat'; }

  formatTime(dateStr: string): string {
    try {
      return new Date(dateStr).toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    } catch { return ''; }
  }

  readonly selectedKeyLabel = computed(() => {
    const k = this.keys().find(k => k.id === this.selectedKeyId());
    if (!k) return 'Select model';
    const prov = this.providers().find(p => p.id === k.provider);
    const model = this.selectedModel() || k.default_model || '';
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

  openFilePicker(): void { this.fileInput?.nativeElement.click(); }

  onFilesSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (!input.files) return;
    Array.from(input.files).forEach(file => this.readFile(file));
    input.value = '';
  }

  private readFile(file: File): void {
    const ext = '.' + file.name.split('.').pop()?.toLowerCase();
    const isText = this.ACCEPTED_TYPES.includes(file.type) || this.ACCEPTED_EXTS.includes(ext);
    if (!isText) {
      this.attachments.update(atts => [...atts, { name: `[unsupported] ${file.name}`, content: '' }]);
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

  isUnsupported(att: Attachment): boolean { return att.name.startsWith('[unsupported]'); }
}
