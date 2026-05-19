import {
  Component,
  inject,
  signal,
  OnInit,
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  DestroyRef,
} from '@angular/core';
import { RouterLink, ActivatedRoute } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { forkJoin, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import {
  LucideAngularModule,
  BookOpen,
  Clock,
  ChevronRight,
  Layers,
  CheckCircle2,
  PlayCircle,
} from 'lucide-angular';
import { CatalogService } from '../../../core/services/catalog.service';
import { ProgressService } from '../../../core/services/progress.service';
import { AuthService } from '../../../core/services/auth.service';
import { Subject, Course, Enrollment } from '../../../core/models/types';

@Component({
  selector: 'app-subject-detail',
  standalone: true,
  imports: [RouterLink, LucideAngularModule],
  templateUrl: './subject-detail.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SubjectDetailComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly catalog = inject(CatalogService);
  private readonly progress = inject(ProgressService);
  readonly auth = inject(AuthService);
  private readonly cdr = inject(ChangeDetectorRef);
  private readonly destroyRef = inject(DestroyRef);

  readonly BookOpen = BookOpen;
  readonly Clock = Clock;
  readonly ChevronRight = ChevronRight;
  readonly Layers = Layers;
  readonly CheckCircle2 = CheckCircle2;
  readonly PlayCircle = PlayCircle;

  readonly subject = signal<Subject | null>(null);
  readonly courses = signal<Course[]>([]);
  readonly enrollments = signal<Enrollment[]>([]);
  readonly loading = signal(true);
  readonly error = signal('');

  ngOnInit(): void {
    const slug = this.route.snapshot.paramMap.get('slug') ?? '';

    const enrollments$ = this.auth.isAuthenticated()
      ? this.progress.getMyEnrollments().pipe(catchError(() => of<Enrollment[]>([])))
      : of<Enrollment[]>([]);

    forkJoin({
      subject: this.catalog.getSubject(slug),
      courses: this.catalog.getSubjectCourses(slug),
      enrollments: enrollments$,
    })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: ({ subject, courses, enrollments }) => {
          this.subject.set(subject);
          this.courses.set(courses);
          this.enrollments.set(enrollments);
          this.loading.set(false);
          this.cdr.markForCheck();
        },
        error: () => {
          this.error.set('Could not load subject. Please try again.');
          this.loading.set(false);
          this.cdr.markForCheck();
        },
      });
  }

  getEnrollment(courseId: number): Enrollment | undefined {
    return this.enrollments().find(e => e.course_id === courseId);
  }

  isEnrolled(courseId: number): boolean {
    return !!this.getEnrollment(courseId);
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

  trackById(_: number, item: { id: number }): number {
    return item.id;
  }
}
