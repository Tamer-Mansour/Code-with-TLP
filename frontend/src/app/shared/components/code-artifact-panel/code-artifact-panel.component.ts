import {
  Component,
  inject,
  input,
  output,
  computed,
  signal,
  ChangeDetectionStrategy,
} from '@angular/core';
import {
  LucideAngularModule,
  Copy, Check, X, Maximize2, Minimize2, Download, ChevronLeft, ChevronRight, FileCode2,
} from 'lucide-angular';
import { MonacoEditorComponent } from '../monaco-editor/monaco-editor';
import { ThemeService } from '../../../core/services/theme.service';
import { ToastService } from '../../../core/services/toast.service';
import { CodeBlockService } from '../../../core/services/code-block.service';
import type { CodeArtifact } from '../../../core/models/chat-ui.model';

/**
 * The Claude-style "artifact" side panel. Renders the active fenced code block
 * in a read-only Monaco editor with a header (title, language, copy, download,
 * expand, close) and prev/next navigation across all artifacts in the message.
 */
@Component({
  selector: 'app-code-artifact-panel',
  standalone: true,
  imports: [LucideAngularModule, MonacoEditorComponent],
  templateUrl: './code-artifact-panel.component.html',
  styleUrl: './code-artifact-panel.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CodeArtifactPanelComponent {
  private readonly theme = inject(ThemeService);
  private readonly toast = inject(ToastService);
  private readonly codeBlocks = inject(CodeBlockService);

  readonly Copy = Copy;
  readonly Check = Check;
  readonly X = X;
  readonly Maximize2 = Maximize2;
  readonly Minimize2 = Minimize2;
  readonly Download = Download;
  readonly ChevronLeft = ChevronLeft;
  readonly ChevronRight = ChevronRight;
  readonly FileCode2 = FileCode2;

  /** All artifacts available to page through. */
  readonly artifacts = input<CodeArtifact[]>([]);
  /** Currently shown artifact id. */
  readonly activeId = input<string | null>(null);
  /** True while the owning message is still streaming. */
  readonly streaming = input<boolean>(false);
  /** Whether the panel is currently expanded full-width. */
  readonly expanded = input<boolean>(false);

  readonly activeIdChange = output<string>();
  readonly closed = output<void>();
  readonly toggleExpand = output<void>();

  readonly justCopied = signal(false);

  readonly active = computed<CodeArtifact | null>(() => {
    const list = this.artifacts();
    if (list.length === 0) return null;
    return list.find(a => a.id === this.activeId()) ?? list[list.length - 1];
  });

  readonly activeIndex = computed(() => {
    const a = this.active();
    return a ? this.artifacts().findIndex(x => x.id === a.id) : -1;
  });

  readonly monacoTheme = computed(() => (this.theme.isDark() ? 'vs-dark' : 'vs'));
  readonly monacoLanguage = computed(() =>
    this.codeBlocks.toMonacoLanguage(this.active()?.language ?? 'text')
  );

  prev(): void {
    const list = this.artifacts();
    const i = this.activeIndex();
    if (i > 0) this.activeIdChange.emit(list[i - 1].id);
  }

  next(): void {
    const list = this.artifacts();
    const i = this.activeIndex();
    if (i >= 0 && i < list.length - 1) this.activeIdChange.emit(list[i + 1].id);
  }

  async copy(): Promise<void> {
    const code = this.active()?.code ?? '';
    if (!code) return;
    try {
      await navigator.clipboard.writeText(code);
      this.justCopied.set(true);
      setTimeout(() => this.justCopied.set(false), 1600);
    } catch {
      this.toast.error('Could not copy to clipboard.');
    }
  }

  download(): void {
    const a = this.active();
    if (!a) return;
    const blob = new Blob([a.code], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `code.${this.extFor(a.language)}`;
    link.click();
    URL.revokeObjectURL(url);
  }

  private extFor(language: string): string {
    const map: Record<string, string> = {
      python: 'py', typescript: 'ts', javascript: 'js', csharp: 'cs',
      cpp: 'cpp', rust: 'rs', ruby: 'rb', shell: 'sh', markdown: 'md',
      plaintext: 'txt', text: 'txt',
    };
    const mono = this.codeBlocks.toMonacoLanguage(language);
    return map[mono] ?? mono ?? 'txt';
  }
}
