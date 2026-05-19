import {
  Component,
  OnInit,
  inject,
  signal,
  computed,
  ChangeDetectionStrategy,
} from '@angular/core';
import { NgClass, DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { LucideAngularModule } from 'lucide-angular';
import { MonacoEditorComponent } from '../../../shared/components/monaco-editor/monaco-editor';
import { AdminService } from '../../../core/services/admin.service';
import { SubmissionService } from '../../../core/services/submission.service';
import { ToastService } from '../../../core/services/toast.service';
import {
  SubmissionSummary,
  Submission,
  STATUS_LABEL,
  STATUS_BADGE_CLASS,
  LANGUAGE_LABELS,
  SubmissionStatus,
} from '../../../core/models/types';

@Component({
  selector: 'app-admin-submissions',
  standalone: true,
  templateUrl: './admin-submissions.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [NgClass, DatePipe, FormsModule, LucideAngularModule, MonacoEditorComponent],
})
export class AdminSubmissionsComponent implements OnInit {
  private readonly adminService = inject(AdminService);
  private readonly submissionService = inject(SubmissionService);
  private readonly toast = inject(ToastService);

  readonly STATUS_LABEL = STATUS_LABEL;
  readonly STATUS_BADGE_CLASS = STATUS_BADGE_CLASS;
  readonly LANGUAGE_LABELS = LANGUAGE_LABELS;

  readonly STATUS_OPTIONS: SubmissionStatus[] = [
    'accepted', 'wrong_answer', 'time_limit_exceeded',
    'memory_limit_exceeded', 'runtime_error', 'compile_error', 'internal_error',
  ];

  // ── State ─────────────────────────────────────────────────
  submissions = signal<SubmissionSummary[]>([]);
  loading = signal(true);
  expandedId = signal<number | null>(null);
  expandedDetail = signal<Submission | null>(null);
  detailLoading = signal(false);

  // Filter state
  filterUserId = signal('');
  filterExerciseId = signal('');
  filterStatus = signal('');

  // ── Load ──────────────────────────────────────────────────
  ngOnInit(): void {
    this.applyFilters();
  }

  applyFilters(): void {
    this.loading.set(true);
    this.expandedId.set(null);
    this.expandedDetail.set(null);

    const params: Record<string, string> = {};
    if (this.filterUserId()) params['user_id'] = this.filterUserId();
    if (this.filterExerciseId()) params['exercise_id'] = this.filterExerciseId();
    if (this.filterStatus()) params['status'] = this.filterStatus();

    this.adminService.getSubmissions(Object.keys(params).length ? params : undefined).subscribe({
      next: (data) => {
        this.submissions.set(data);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.toast.error('Failed to load submissions.');
      },
    });
  }

  clearFilters(): void {
    this.filterUserId.set('');
    this.filterExerciseId.set('');
    this.filterStatus.set('');
    this.applyFilters();
  }

  toggleExpand(sub: SubmissionSummary): void {
    if (this.expandedId() === sub.id) {
      this.expandedId.set(null);
      this.expandedDetail.set(null);
      return;
    }
    this.expandedId.set(sub.id);
    this.expandedDetail.set(null);
    this.detailLoading.set(true);
    this.submissionService.getSubmission(sub.id).subscribe({
      next: (detail) => {
        this.expandedDetail.set(detail);
        this.detailLoading.set(false);
      },
      error: () => {
        this.detailLoading.set(false);
        this.toast.error('Failed to load submission detail.');
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

  getMonacoLang(language: string): string {
    const map: Record<string, string> = {
      python: 'python',
      javascript: 'javascript',
      typescript: 'typescript',
      java: 'java',
      csharp: 'csharp',
    };
    return map[language] ?? 'plaintext';
  }
}
