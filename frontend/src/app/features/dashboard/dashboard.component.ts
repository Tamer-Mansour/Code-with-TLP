import {
  Component,
  OnInit,
  inject,
  signal,
  computed,
  ChangeDetectionStrategy,
} from '@angular/core';
import { NgClass, DatePipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { AuthService } from '../../core/services/auth.service';
import { ProgressService } from '../../core/services/progress.service';
import { SubmissionService } from '../../core/services/submission.service';
import { CatalogService } from '../../core/services/catalog.service';
import {
  Enrollment,
  SubmissionSummary,
  Course,
  STATUS_LABEL,
  STATUS_BADGE_CLASS,
  LANGUAGE_LABELS,
  SubmissionStatus,
} from '../../core/models/types';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  templateUrl: './dashboard.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [NgClass, DatePipe, RouterLink, LucideAngularModule],
})
export class DashboardComponent implements OnInit {
  private readonly auth = inject(AuthService);
  private readonly progressService = inject(ProgressService);
  private readonly submissionService = inject(SubmissionService);
  private readonly catalogService = inject(CatalogService);

  readonly STATUS_LABEL = STATUS_LABEL;
  readonly STATUS_BADGE_CLASS = STATUS_BADGE_CLASS;
  readonly LANGUAGE_LABELS = LANGUAGE_LABELS;

  // ── State ─────────────────────────────────────────────────
  currentUser = this.auth.currentUser;
  enrollments = signal<Enrollment[]>([]);
  enrolledCourses = signal<Course[]>([]);
  recentSubmissions = signal<SubmissionSummary[]>([]);
  loadingEnrollments = signal(true);
  loadingSubmissions = signal(true);

  // ── Computed stats ────────────────────────────────────────
  enrolledCount = computed(() => this.enrollments().length);

  completedExercises = computed(() =>
    this.recentSubmissions().filter((s) => s.status === 'accepted').length
  );

  acceptanceRate = computed(() => {
    const subs = this.recentSubmissions();
    if (subs.length === 0) return 0;
    const accepted = subs.filter((s) => s.status === 'accepted').length;
    return Math.round((accepted / subs.length) * 100);
  });

  totalPoints = computed(() =>
    this.recentSubmissions().reduce((sum, s) => sum + (s.score ?? 0), 0)
  );

  coursesWithProgress = computed(() => {
    const courses = this.enrolledCourses();
    return this.enrollments().map((enr) => {
      const course = courses.find((c) => c.id === enr.course_id);
      return { enrollment: enr, course };
    }).filter((item) => item.course != null);
  });

  ngOnInit(): void {
    this.progressService.getMyEnrollments().subscribe({
      next: (enrollments) => {
        this.enrollments.set(enrollments);
        this.loadingEnrollments.set(false);
        // Load course details for each enrollment
        if (enrollments.length > 0) {
          this.catalogService.getCourses().subscribe({
            next: (courses) => {
              const enrolled = courses.filter((c) =>
                enrollments.some((e) => e.course_id === c.id)
              );
              this.enrolledCourses.set(enrolled);
            },
          });
        }
      },
      error: () => this.loadingEnrollments.set(false),
    });

    this.submissionService.getMySubmissions().subscribe({
      next: (subs) => {
        this.recentSubmissions.set(subs.slice(0, 10));
        this.loadingSubmissions.set(false);
      },
      error: () => this.loadingSubmissions.set(false),
    });
  }

  getStatusBadge(status: SubmissionStatus): string {
    return STATUS_BADGE_CLASS[status] ?? 'badge-error';
  }

  getStatusLabel(status: SubmissionStatus): string {
    return STATUS_LABEL[status] ?? status;
  }

  getDifficultyBadge(difficulty: string): string {
    if (difficulty === 'beginner') return 'badge-easy';
    if (difficulty === 'intermediate') return 'badge-medium';
    return 'badge-hard';
  }

  formatRuntime(ms: number): string {
    return ms != null ? `${ms}ms` : '—';
  }

  userInitials(): string {
    const user = this.currentUser();
    if (!user) return '?';
    const name = user.full_name ?? user.username ?? '';
    return name
      .split(' ')
      .map((w) => w[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  }
}
