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
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { forkJoin, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { MarkdownModule } from 'ngx-markdown';
import {
  LucideAngularModule,
  ChevronRight,
  ChevronLeft,
  CheckCircle2,
  Circle,
  Clock,
  FileText,
  Video,
  Code2,
  ListChecks,
  ArrowLeft,
  ArrowRight,
  ExternalLink,
} from 'lucide-angular';
import { CatalogService } from '../../../core/services/catalog.service';
import { ProgressService } from '../../../core/services/progress.service';
import { AuthService } from '../../../core/services/auth.service';
import { ToastService } from '../../../core/services/toast.service';
import { Lesson, LessonProgress, LessonType } from '../../../core/models/types';

@Component({
  selector: 'app-lesson-reader',
  standalone: true,
  imports: [RouterLink, MarkdownModule, LucideAngularModule],
  templateUrl: './lesson-reader.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LessonReaderComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  readonly router = inject(Router);
  private readonly catalog = inject(CatalogService);
  private readonly progress = inject(ProgressService);
  readonly auth = inject(AuthService);
  private readonly toast = inject(ToastService);
  private readonly cdr = inject(ChangeDetectorRef);
  private readonly destroyRef = inject(DestroyRef);

  readonly ChevronRight = ChevronRight;
  readonly ChevronLeft = ChevronLeft;
  readonly CheckCircle2 = CheckCircle2;
  readonly Circle = Circle;
  readonly Clock = Clock;
  readonly FileText = FileText;
  readonly Video = Video;
  readonly Code2 = Code2;
  readonly ListChecks = ListChecks;
  readonly ArrowLeft = ArrowLeft;
  readonly ArrowRight = ArrowRight;
  readonly ExternalLink = ExternalLink;

  readonly lesson = signal<Lesson | null>(null);
  readonly lessonProgress = signal<LessonProgress | null>(null);
  readonly loading = signal(true);
  readonly marking = signal(false);
  readonly error = signal('');

  get isCompleted(): boolean {
    return this.lessonProgress()?.status === 'completed';
  }

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));

    const progressReq$ = this.auth.isAuthenticated()
      ? this.progress.getLessonProgress(id).pipe(catchError(() => of<LessonProgress | null>(null)))
      : of<LessonProgress | null>(null);

    forkJoin({
      lesson: this.catalog.getLesson(id),
      lessonProgress: progressReq$,
    })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: ({ lesson, lessonProgress }) => {
          this.lesson.set(lesson);
          this.lessonProgress.set(lessonProgress);
          this.loading.set(false);
          this.cdr.markForCheck();
        },
        error: () => {
          this.error.set('Could not load lesson. Please try again.');
          this.loading.set(false);
          this.cdr.markForCheck();
        },
      });
  }

  markComplete(): void {
    if (!this.auth.isAuthenticated()) {
      this.router.navigate(['/login']);
      return;
    }
    const lesson = this.lesson();
    if (!lesson || this.marking()) return;

    this.marking.set(true);
    this.progress.setLessonProgress(lesson.id, 'completed')
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (prog: LessonProgress) => {
          this.lessonProgress.set(prog);
          this.marking.set(false);
          this.toast.success('Lesson completed! Progress saved.');
          this.cdr.markForCheck();
        },
        error: () => {
          this.marking.set(false);
          this.toast.error('Could not save progress. Please try again.');
          this.cdr.markForCheck();
        },
      });
  }

  lessonTypeLabel(type: LessonType): string {
    switch (type) {
      case 'video':    return 'Video';
      case 'exercise': return 'Exercise';
      case 'quiz':     return 'Quiz';
      default:         return 'Reading';
    }
  }

  lessonTypeBadgeClass(type: LessonType): string {
    switch (type) {
      case 'video':    return 'bg-purple-950/60 text-purple-300 border border-purple-800/50';
      case 'exercise': return 'bg-amber-950/60 text-amber-300 border border-amber-800/50';
      case 'quiz':     return 'bg-cyan-950/60 text-cyan-300 border border-cyan-800/50';
      default:         return 'bg-app-surface-2 text-app-text-2 border border-app-border';
    }
  }

  lessonIcon(type: LessonType): any {
    switch (type) {
      case 'video':    return this.Video;
      case 'exercise': return this.Code2;
      case 'quiz':     return this.ListChecks;
      default:         return this.FileText;
    }
  }
}
