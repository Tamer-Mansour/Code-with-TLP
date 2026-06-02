import {
  Component,
  inject,
  signal,
  computed,
  input,
  effect,
  OnDestroy,
  ElementRef,
  ViewChild,
  AfterViewChecked,
  ChangeDetectionStrategy,
  ChangeDetectorRef,
} from '@angular/core';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MarkdownModule } from 'ngx-markdown';
import {
  LucideAngularModule,
  Bot, Send, Square, Settings, ChevronDown, Globe, Sparkles,
  Languages, ListChecks, FileText, RefreshCcw, LogIn,
} from 'lucide-angular';
import { ChatService } from '../../../../core/services/chat.service';
import type { AiKey, AiProvider } from '../../../../core/models/chat.model';
import { AuthService } from '../../../../core/services/auth.service';
import type { LocalMessage, QuickAction } from '../../models/lesson-chat.model';

@Component({
  selector: 'app-lesson-chat',
  standalone: true,
  imports: [FormsModule, MarkdownModule, LucideAngularModule, RouterLink],
  templateUrl: './lesson-chat.component.html',
  styleUrl: './lesson-chat.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LessonChatComponent implements OnDestroy, AfterViewChecked {
  @ViewChild('messagesEnd') private messagesEnd!: ElementRef<HTMLDivElement>;
  @ViewChild('textareaRef') private textareaRef!: ElementRef<HTMLTextAreaElement>;

  // ── Inputs (lesson context) ───────────────────────────────────────────────
  readonly lessonId = input<number | null>(null);
  readonly lessonTitle = input<string>('');
  readonly lessonContent = input<string>('');

  private readonly chatSvc = inject(ChatService);
  readonly auth = inject(AuthService);
  private readonly cdr = inject(ChangeDetectorRef);

  // Icons
  readonly Bot = Bot;
  readonly Send = Send;
  readonly Square = Square;
  readonly Settings = Settings;
  readonly ChevronDown = ChevronDown;
  readonly Globe = Globe;
  readonly Sparkles = Sparkles;
  readonly RefreshCcw = RefreshCcw;
  readonly LogIn = LogIn;

  // State
  readonly keys = signal<AiKey[]>([]);
  readonly providers = signal<AiProvider[]>([]);
  readonly messages = signal<LocalMessage[]>([]);
  readonly streaming = signal(false);
  readonly inputText = signal('');
  readonly selectedKeyId = signal<string>('');
  readonly selectedModel = signal<string>('');
  readonly webSearch = signal(false);
  readonly pickerOpen = signal(false);

  private sessionId: string | null = null;
  private abortStream: (() => void) | null = null;
  private shouldScroll = false;
  private loaded = false;

  readonly quickActions: QuickAction[] = [
    { label: 'Explain simply', icon: Sparkles, prompt: 'Explain this lesson in simple terms, as if I am a beginner.' },
    { label: 'Summarize', icon: FileText, prompt: 'Summarize the key points of this lesson as a short bullet list.' },
    { label: 'Quiz me', icon: ListChecks, prompt: 'Ask me 3 short questions to test my understanding of this lesson. Wait for my answers before revealing the solutions.' },
    { label: 'Translate to Arabic', icon: Languages, prompt: 'Translate this lesson into Arabic, keeping any code unchanged.' },
  ];
  readonly Languages = Languages;
  readonly ListChecks = ListChecks;
  readonly FileText = FileText;

  // Derived: models for the selected key's provider
  readonly modelOptions = computed<string[]>(() => {
    const key = this.keys().find(k => k.id === this.selectedKeyId());
    if (!key) return [];
    const provider = this.providers().find(p => p.id === key.provider);
    return provider?.models ?? (key.default_model ? [key.default_model] : []);
  });

  readonly hasKeys = computed(() => this.keys().length > 0);

  /** Selected key's provider id — drives the web-search toggle visibility. */
  readonly selectedProvider = computed<string>(() => {
    return this.keys().find(k => k.id === this.selectedKeyId())?.provider ?? '';
  });

  readonly supportsWebSearch = computed(() => this.selectedProvider() === 'gemini');

  readonly selectedLabel = computed(() => {
    const k = this.keys().find(k => k.id === this.selectedKeyId());
    if (!k) return 'Select model';
    const prov = this.providers().find(p => p.id === k.provider);
    const model = this.selectedModel() || k.default_model || '';
    const name = k.label || prov?.name || k.provider;
    return model ? `${name} · ${model}` : name;
  });

  constructor() {
    // Load keys/providers once the user is known (auth + lesson available).
    effect(() => {
      // Reading lessonId registers the dependency so a new lesson resets the chat.
      this.lessonId();
      if (this.auth.isAuthenticated() && !this.loaded) {
        this.loaded = true;
        this.loadProvidersAndKeys();
      }
      // Fresh conversation per lesson.
      this.resetConversation();
    });
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

  private resetConversation(): void {
    this.abortStream?.();
    this.abortStream = null;
    this.sessionId = null;
    this.messages.set([]);
    this.streaming.set(false);
  }

  private scrollToBottom(): void {
    try {
      this.messagesEnd?.nativeElement.scrollIntoView({ behavior: 'smooth' });
    } catch { /* ignore */ }
  }

  private loadProvidersAndKeys(): void {
    this.chatSvc.getProviders().subscribe({ next: ps => { this.providers.set(ps); this.cdr.markForCheck(); } });
    this.chatSvc.getKeys().subscribe({
      next: keys => {
        this.keys.set(keys);
        if (keys.length > 0 && !this.selectedKeyId()) {
          // Prefer a Gemini key if the user has one (it unlocks web search).
          const gemini = keys.find(k => k.provider === 'gemini');
          const pick = gemini ?? keys[0];
          this.selectedKeyId.set(pick.id);
          if (pick.default_model) this.selectedModel.set(pick.default_model);
          else this.selectedModel.set(this.modelOptions()[0] ?? '');
        }
        this.cdr.markForCheck();
      },
    });
  }

  togglePicker(): void { this.pickerOpen.update(v => !v); }

  onKeyChange(keyId: string): void {
    this.selectedKeyId.set(keyId);
    const key = this.keys().find(k => k.id === keyId);
    this.selectedModel.set(key?.default_model || this.modelOptions()[0] || '');
    if (this.selectedProvider() !== 'gemini') this.webSearch.set(false);
    this.pickerOpen.set(false);
  }

  pickModel(model: string): void {
    this.selectedModel.set(model);
    this.pickerOpen.set(false);
  }

  toggleWebSearch(): void {
    if (this.supportsWebSearch()) this.webSearch.update(v => !v);
  }

  onKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.send();
    }
  }

  runQuickAction(action: QuickAction): void {
    this.send(action.prompt);
  }

  stopStreaming(): void {
    this.abortStream?.();
    this.abortStream = null;
    this.messages.update(ms =>
      ms.map((m, i) => (i === ms.length - 1 && m.streaming ? { ...m, streaming: false } : m))
    );
    this.streaming.set(false);
    this.cdr.markForCheck();
  }

  send(prefill?: string): void {
    const text = (prefill ?? this.inputText()).trim();
    if (!text || this.streaming() || !this.hasKeys()) return;

    const key = this.keys().find(k => k.id === this.selectedKeyId());
    const provider = key?.provider;
    const model = this.selectedModel() || undefined;
    const context = this.buildContext();
    const webSearch = this.webSearch();

    const start = (sessionId: string) => {
      this.streaming.set(true);
      this.inputText.set('');
      this.messages.update(ms => [
        ...ms,
        { role: 'user', content: text },
        { role: 'assistant', content: '', streaming: true },
      ]);
      this.shouldScroll = true;
      this.cdr.markForCheck();

      const { events$, abort } = this.chatSvc.streamMessage(sessionId, {
        message: text,
        provider,
        model,
        context,
        web_search: webSearch,
      });
      this.abortStream = abort;

      events$.subscribe({
        next: evt => {
          if (evt.token) {
            this.appendToken(evt.token);
          }
          if (evt.done) {
            this.finishStreaming(evt.model);
          }
          if (evt.error) {
            this.finishStreaming(undefined, evt.error);
          }
        },
        error: () => this.finishStreaming(undefined, 'Something went wrong. Please try again.'),
      });
    };

    if (this.sessionId) {
      start(this.sessionId);
    } else {
      const title = `Lesson: ${this.lessonTitle() || 'Chat'}`.slice(0, 60);
      this.chatSvc.createSession(title).subscribe({
        next: session => {
          this.sessionId = session.id;
          start(session.id);
        },
        error: () => {},
      });
    }
  }

  private appendToken(token: string): void {
    this.messages.update(ms => {
      const updated = [...ms];
      const last = updated[updated.length - 1];
      if (last?.streaming) updated[updated.length - 1] = { ...last, content: last.content + token };
      return updated;
    });
    this.shouldScroll = true;
    this.cdr.markForCheck();
  }

  private finishStreaming(model?: string, errorContent?: string): void {
    this.messages.update(ms => {
      const updated = [...ms];
      const last = updated[updated.length - 1];
      if (last?.streaming) {
        updated[updated.length - 1] = {
          ...last,
          streaming: false,
          model,
          content: errorContent ? (last.content || errorContent) : last.content,
        };
      }
      return updated;
    });
    this.streaming.set(false);
    this.abortStream = null;
    this.shouldScroll = true;
    this.cdr.markForCheck();
  }

  /** Lesson markdown folded into a single context string for the system prompt. */
  private buildContext(): string {
    const title = this.lessonTitle();
    const body = this.lessonContent();
    if (!body && !title) return '';
    return title ? `# ${title}\n\n${body}` : body;
  }
}
