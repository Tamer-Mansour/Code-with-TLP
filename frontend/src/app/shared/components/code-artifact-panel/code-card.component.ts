import {
  Component,
  inject,
  input,
  output,
  computed,
  signal,
  ChangeDetectionStrategy,
} from '@angular/core';
import { LucideAngularModule, Copy, Check, FileCode2, ArrowUpRight } from 'lucide-angular';
import { ToastService } from '../../../core/services/toast.service';
import type { CodeArtifact } from '../../../core/models/chat-ui.model';

/**
 * Compact inline reference to a code artifact, shown in the message stream.
 * Clicking it opens the artifact in the side panel — like Claude's inline
 * artifact chips.
 */
@Component({
  selector: 'app-code-card',
  standalone: true,
  imports: [LucideAngularModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <button
      type="button"
      (click)="open.emit()"
      class="group/codecard w-full text-left rounded-xl border bg-app-surface-2/50 hover:bg-app-surface-2 transition-all overflow-hidden"
      [class.border-app-border]="!isActive()"
      [class.border-brand]="isActive()"
      [class.ring-1]="isActive()"
      [class.ring-brand/30]="isActive()"
    >
      <div class="flex items-center gap-2.5 px-3 py-2.5">
        <span class="w-8 h-8 rounded-lg brand-gradient flex items-center justify-center shrink-0 shadow-sm">
          <lucide-icon [img]="FileCode2" [size]="15" class="text-white"></lucide-icon>
        </span>
        <div class="min-w-0 flex-1">
          <p class="text-[13px] font-semibold text-app-text leading-tight truncate">{{ artifact().title }}</p>
          <p class="text-[11px] text-app-text-muted leading-tight">
            {{ artifact().lineCount }} {{ artifact().lineCount === 1 ? 'line' : 'lines' }}
            @if (!artifact().complete) { · writing… }
          </p>
        </div>
        <span
          class="shrink-0 inline-flex items-center gap-1 text-[11px] font-medium text-brand opacity-0 group-hover/codecard:opacity-100 transition-opacity"
        >
          Open <lucide-icon [img]="ArrowUpRight" [size]="13"></lucide-icon>
        </span>
      </div>
      @if (preview().length) {
        <pre class="px-3.5 pb-3 pt-0 text-[11px] leading-snug font-mono text-app-text-2 overflow-hidden whitespace-pre max-h-[4.5rem]"><code>{{ preview() }}</code></pre>
      }
    </button>
  `,
})
export class CodeCardComponent {
  private readonly toast = inject(ToastService);

  readonly Copy = Copy;
  readonly Check = Check;
  readonly FileCode2 = FileCode2;
  readonly ArrowUpRight = ArrowUpRight;

  readonly artifact = input.required<CodeArtifact>();
  readonly isActive = input<boolean>(false);
  readonly open = output<void>();

  readonly justCopied = signal(false);

  /** First few lines for a glanceable preview. */
  readonly preview = computed(() =>
    this.artifact().code.split('\n').slice(0, 3).join('\n')
  );
}
