import {
  Component,
  inject,
  signal,
  OnInit,
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  DestroyRef,
} from '@angular/core';
import { RouterLink, ActivatedRoute, Router } from '@angular/router';
import { NgClass, SlicePipe } from '@angular/common';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { forkJoin, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import {
  LucideAngularModule,
  BookOpen,
  Clock,
  ChevronRight,
  ChevronDown,
  CheckCircle2,
  Circle,
  PlayCircle,
  FileText,
  Video,
  Code2,
  ListChecks,
  BarChart2,
  Unlock,
} from 'lucide-angular';
import { CatalogService } from '../../../core/services/catalog.service';
import { ProgressService } from '../../../core/services/progress.service';
import { AuthService } from '../../../core/services/auth.service';
import { ToastService } from '../../../core/services/toast.service';
import { CourseTree, Enrollment, LessonType } from '../../../core/models/types';

@Component({
  selector: 'app-course-detail',
  standalone: true,
  imports: [RouterLink, NgClass, SlicePipe, LucideAngularModule],
  templateUrl: './course-detail.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CourseDetailComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly catalog = inject(CatalogService);
  private readonly progress = inject(ProgressService);
  readonly auth = inject(AuthService);
  private readonly toast = inject(ToastService);
  private readonly cdr = inject(ChangeDetectorRef);
  private readonly destroyRef = inject(DestroyRef);

  readonly BookOpen = BookOpen;
  readonly Clock = Clock;
  readonly ChevronRight = ChevronRight;
  readonly ChevronDown = ChevronDown;
  readonly CheckCircle2 = CheckCircle2;
  readonly Circle = Circle;
  readonly PlayCircle = PlayCircle;
  readonly FileText = FileText;
  readonly Video = Video;
  readonly Code2 = Code2;
  readonly ListChecks = ListChecks;
  readonly BarChart2 = BarChart2;
  readonly Unlock = Unlock;

  readonly courseTree = signal<CourseTree | null>(null);
  readonly enrollment = signal<Enrollment | null>(null);
  readonly loading = signal(true);
  readonly enrolling = signal(false);
  readonly error = signal('');
  readonly expandedModules = signal<Set<number>>(new Set());
  readonly completedLessonIds = signal<Set<number>>(new Set());

  ngOnInit(): void {
    const slug = this.route.snapshot.paramMap.get('slug') ?? '';

    const enrollments$ = this.auth.isAuthenticated()
      ? this.progress.getMyEnrollments().pipe(catchError(() => of<Enrollment[]>([])))
      : of<Enrollment[]>([]);

    forkJoin({
      tree: this.catalog.getCourseTree(slug),
      enrollments: enrollments$,
    })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: ({ tree, enrollments }) => {
          this.courseTree.set(tree);
          if (tree.modules.length > 0) {
            this.expandedModules.set(new Set([tree.modules[0].id]));
          }
          const enr = enrollments.find((e: Enrollment) => e.course_id === tree.id);
          this.enrollment.set(enr ?? null);
          this.loading.set(false);
          this.cdr.markForCheck();
          if (this.auth.isAuthenticated()) {
            this.progress.getCourseProgress(tree.id)
              .pipe(takeUntilDestroyed(this.destroyRef))
              .subscribe({
                next: (records) => {
                  this.completedLessonIds.set(
                    new Set(records.filter(r => r.status === 'completed').map(r => r.lesson_id))
                  );
                  this.cdr.markForCheck();
                },
              });
          }
        },
        error: () => {
          this.error.set('Could not load course. Please try again.');
          this.loading.set(false);
          this.cdr.markForCheck();
        },
      });
  }

  get isEnrolled(): boolean {
    return !!this.enrollment();
  }

  get progressPercent(): number {
    return this.enrollment()?.progress_percent ?? 0;
  }

  get totalLessons(): number {
    return this.courseTree()?.modules?.reduce((acc, m) => acc + m.lessons.length, 0) ?? 0;
  }

  toggleModule(id: number): void {
    this.expandedModules.update(set => {
      const next = new Set(set);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }

  isModuleExpanded(id: number): boolean {
    return this.expandedModules().has(id);
  }

  enroll(): void {
    if (!this.auth.isAuthenticated()) {
      this.router.navigate(['/login'], { queryParams: { returnUrl: this.router.url } });
      return;
    }
    const tree = this.courseTree();
    if (!tree || this.enrolling()) return;

    this.enrolling.set(true);
    this.progress.enroll(tree.id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (enr: Enrollment) => {
          this.enrollment.set(enr);
          this.enrolling.set(false);
          this.toast.success(`Enrolled in ${tree.title}!`);
          this.cdr.markForCheck();
        },
        error: () => {
          this.enrolling.set(false);
          this.toast.error('Enrollment failed. Please try again.');
          this.cdr.markForCheck();
        },
      });
  }

  lessonIcon(type: LessonType): any {
    switch (type) {
      case 'video':    return this.Video;
      case 'exercise': return this.Code2;
      case 'quiz':     return this.ListChecks;
      default:         return this.FileText;
    }
  }

  lessonTypeLabel(type: LessonType): string {
    switch (type) {
      case 'video':    return 'Video';
      case 'exercise': return 'Exercise';
      case 'quiz':     return 'Quiz';
      default:         return 'Reading';
    }
  }

  difficultyBadge(difficulty: string): string {
    switch (difficulty?.toLowerCase()) {
      case 'beginner':     return 'badge-easy';
      case 'intermediate': return 'badge-medium';
      case 'advanced':     return 'badge-hard';
      default:             return 'badge-easy';
    }
  }

  difficultyLabel(difficulty: string): string {
    switch (difficulty?.toLowerCase()) {
      case 'beginner':     return 'Beginner';
      case 'intermediate': return 'Intermediate';
      case 'advanced':     return 'Advanced';
      default:             return difficulty;
    }
  }

  getFirstLessonId(tree: CourseTree): number | null {
    const lesson = tree.modules[0]?.lessons[0];
    return lesson ? lesson.id : null;
  }

  trackById(_: number, item: { id: number }): number {
    return item.id;
  }
}
