import {
  Component,
  OnInit,
  inject,
  signal,
  computed,
  ChangeDetectionStrategy,
} from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { NgClass, DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MarkdownModule } from 'ngx-markdown';
import { LucideAngularModule } from 'lucide-angular';
import { MonacoEditorComponent } from '../../../shared/components/monaco-editor/monaco-editor';
import { CatalogService } from '../../../core/services/catalog.service';
import { SubmissionService } from '../../../core/services/submission.service';
import { ToastService } from '../../../core/services/toast.service';
import {
  Exercise,
  SupportedLanguage,
  CodeRunResult,
  Submission,
  SubmissionSummary,
  MONACO_LANGUAGE_MAP,
  STATUS_LABEL,
  STATUS_BADGE_CLASS,
  LANGUAGE_LABELS,
  SubmissionStatus,
} from '../../../core/models/types';

type ActiveTab = 'description' | 'testcases' | 'submissions';

@Component({
  selector: 'app-exercise-page',
  standalone: true,
  templateUrl: './exercise-page.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [NgClass, DatePipe, FormsModule, LucideAngularModule, MonacoEditorComponent, MarkdownModule],
})
export class ExercisePageComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly catalogService = inject(CatalogService);
  private readonly submissionService = inject(SubmissionService);
  private readonly toast = inject(ToastService);

  readonly LANGUAGE_LABELS = LANGUAGE_LABELS;
  readonly STATUS_LABEL = STATUS_LABEL;

  // ── State signals ─────────────────────────────────────────
  exercise = signal<Exercise | null>(null);
  loading = signal(true);
  selectedLanguage = signal<SupportedLanguage>('python');
  code = signal('');
  activeTab = signal<ActiveTab>('description');
  isRunning = signal(false);
  isSubmitting = signal(false);
  runResult = signal<CodeRunResult | null>(null);
  lastSubmission = signal<Submission | null>(null);
  submissions = signal<SubmissionSummary[]>([]);
  submissionsLoading = signal(false);

  // ── Computed ──────────────────────────────────────────────
  monacoLanguage = computed(() => MONACO_LANGUAGE_MAP[this.selectedLanguage()] ?? 'python');

  statusLabel = computed(() => {
    const status = this.runResult()?.status;
    return status ? STATUS_LABEL[status] : '';
  });

  statusBadgeClass = computed(() => {
    const status = this.runResult()?.status;
    return status ? STATUS_BADGE_CLASS[status] : 'badge-error';
  });

  difficultyBadge = computed(() => {
    const d = this.exercise()?.difficulty;
    if (d === 'easy') return 'badge-easy';
    if (d === 'medium') return 'badge-medium';
    return 'badge-hard';
  });

  supportedLanguagesList = computed(
    () => this.exercise()?.supported_languages ?? []
  );

  visibleTestCases = computed(() =>
    (this.exercise()?.test_cases ?? []).filter((tc) => !('is_hidden' in tc && (tc as any).is_hidden))
  );

  actualOutputMap = computed<Record<number, string>>(() => {
    const result = this.runResult();
    if (!result) return {};
    const tc = this.visibleTestCases();
    const map: Record<number, string> = {};
    if (tc.length === 1) {
      map[tc[0].id] = result.stdout ?? '';
    }
    return map;
  });

  ngOnInit(): void {
    const slug = this.route.snapshot.paramMap.get('slug') ?? '';
    this.catalogService.getExercise(slug).subscribe({
      next: (ex) => {
        this.exercise.set(ex);
        const lang = ex.supported_languages[0] ?? 'python';
        this.selectedLanguage.set(lang);
        this.code.set(ex.starter_code[lang] ?? '');
        this.loading.set(false);
        this.loadSubmissions(ex.id);
      },
      error: () => {
        this.loading.set(false);
        this.toast.error('Failed to load exercise.');
      },
    });
  }

  private loadSubmissions(exerciseId: number): void {
    this.submissionsLoading.set(true);
    this.submissionService.getMySubmissions(exerciseId).subscribe({
      next: (subs) => {
        this.submissions.set(subs);
        this.submissionsLoading.set(false);
      },
      error: () => this.submissionsLoading.set(false),
    });
  }

  setLanguage(lang: string): void {
    const l = lang as SupportedLanguage;
    this.selectedLanguage.set(l);
    const starter = this.exercise()?.starter_code[l] ?? '';
    this.code.set(starter);
    this.runResult.set(null);
  }

  setTab(tab: ActiveTab): void {
    this.activeTab.set(tab);
  }

  setCode(value: string): void {
    this.code.set(value);
  }

  runCode(): void {
    if (this.isRunning()) return;
    this.isRunning.set(true);
    this.runResult.set(null);
    this.submissionService
      .runCode({ language: this.selectedLanguage(), code: this.code(), stdin: '' })
      .subscribe({
        next: (result) => {
          this.runResult.set(result);
          this.isRunning.set(false);
        },
        error: () => {
          this.isRunning.set(false);
          this.toast.error('Failed to run code. Please try again.');
        },
      });
  }

  submitCode(): void {
    const ex = this.exercise();
    if (!ex || this.isSubmitting()) return;
    this.isSubmitting.set(true);
    this.submissionService
      .submit({ exercise_id: ex.id, language: this.selectedLanguage(), code: this.code() })
      .subscribe({
        next: (sub) => {
          this.lastSubmission.set(sub);
          this.isSubmitting.set(false);
          const label = STATUS_LABEL[sub.status];
          if (sub.status === 'accepted') {
            this.toast.success(`${label} — ${sub.score}/${ex.points} pts`);
          } else {
            this.toast.error(`${label} — ${sub.passed_tests}/${sub.total_tests} tests passed`);
          }
          this.loadSubmissions(ex.id);
          this.activeTab.set('submissions');
        },
        error: () => {
          this.isSubmitting.set(false);
          this.toast.error('Submission failed. Please try again.');
        },
      });
  }

  getStatusBadge(status: SubmissionStatus): string {
    return STATUS_BADGE_CLASS[status] ?? 'badge-error';
  }

  getStatusLabel(status: SubmissionStatus): string {
    return STATUS_LABEL[status] ?? status;
  }

  formatRuntime(ms: number): string {
    return ms != null ? `${ms}ms` : '—';
  }

  clearOutput(): void {
    this.runResult.set(null);
  }
}
