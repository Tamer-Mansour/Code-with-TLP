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
import { combineLatest, forkJoin, of } from 'rxjs';
import { catchError, switchMap } from 'rxjs/operators';
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
  Timer,
} from 'lucide-angular';
import { CatalogService } from '../../../core/services/catalog.service';
import { ProgressService } from '../../../core/services/progress.service';
import { AuthService } from '../../../core/services/auth.service';
import { ToastService } from '../../../core/services/toast.service';
import { Lesson, LessonProgress, LessonType, CourseTree, LessonInTree } from '../../../core/models/types';

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
  readonly Timer = Timer;

  readonly lesson = signal<Lesson | null>(null);
  readonly lessonProgress = signal<LessonProgress | null>(null);
  readonly loading = signal(true);
  readonly marking = signal(false);
  readonly error = signal('');
  readonly courseSlug = signal('');
  readonly courseTree = signal<CourseTree | null>(null);
  readonly timeSpent = signal(0); // seconds since page loaded

  private timerHandle: ReturnType<typeof setInterval> | null = null;

  get isCompleted(): boolean {
    return this.lessonProgress()?.status === 'completed';
  }

  get flatLessons(): LessonInTree[] {
    const tree = this.courseTree();
    if (!tree) return [];
    return tree.modules.flatMap(m => m.lessons);
  }

  get currentIndex(): number {
    const lesson = this.lesson();
    if (!lesson) return -1;
    return this.flatLessons.findIndex(l => l.id === lesson.id);
  }

  get prevLesson(): LessonInTree | null {
    const idx = this.currentIndex;
    return idx > 0 ? this.flatLessons[idx - 1] : null;
  }

  get nextLesson(): LessonInTree | null {
    const idx = this.currentIndex;
    const flat = this.flatLessons;
    return idx >= 0 && idx < flat.length - 1 ? flat[idx + 1] : null;
  }

  get timeSpentLabel(): string {
    const t = this.timeSpent();
    const m = Math.floor(t / 60);
    const s = t % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  }

  /** Markdown body with a leading H1 stripped when it just repeats the lesson title
   *  (the title is already shown in the header, so authoring it as the first heading
   *  would render it twice). */
  get contentBody(): string {
    const ls = this.lesson();
    if (!ls?.content_md) return '';
    return this.stripDuplicateTitle(ls.content_md, ls.title);
  }

  private stripDuplicateTitle(md: string, title: string): string {
    const norm = (s: string) =>
      s.replace(/[#*_`]/g, '').replace(/[^\p{L}\p{N}]+/gu, ' ').trim().toLowerCase();
    const lines = md.split('\n');
    let i = 0;
    while (i < lines.length && lines[i].trim() === '') i++;
    const heading = lines[i]?.match(/^#{1,6}\s+(.+?)\s*#*\s*$/);
    if (heading && norm(heading[1]) === norm(title)) {
      lines.splice(0, i + 1);
      while (lines.length && lines[0].trim() === '') lines.shift();
      return lines.join('\n');
    }
    return md;
  }

  private startTimer(): void {
    this.stopTimer();
    this.timeSpent.set(0);
    this.timerHandle = setInterval(() => {
      this.timeSpent.update(v => v + 1);
      this.cdr.markForCheck();
    }, 1000);
  }

  private stopTimer(): void {
    if (this.timerHandle !== null) {
      clearInterval(this.timerHandle);
      this.timerHandle = null;
    }
  }

  ngOnInit(): void {
    this.destroyRef.onDestroy(() => this.stopTimer());

    combineLatest([this.route.paramMap, this.route.queryParamMap])
      .pipe(
        takeUntilDestroyed(this.destroyRef),
        switchMap(([params, queryParams]) => {
          const id = Number(params.get('id'));
          const slug = queryParams.get('course') ?? '';
          this.courseSlug.set(slug);
          this.loading.set(true);
          this.lesson.set(null);
          this.lessonProgress.set(null);
          this.courseTree.set(null);
          this.error.set('');
          this.marking.set(false);
          this.stopTimer();
          this.cdr.markForCheck();

          const progressReq$ = this.auth.isAuthenticated()
            ? this.progress.getLessonProgress(id).pipe(catchError(() => of<LessonProgress | null>(null)))
            : of<LessonProgress | null>(null);

          const treeReq$ = slug
            ? this.catalog.getCourseTree(slug).pipe(catchError(() => of<CourseTree | null>(null)))
            : of<CourseTree | null>(null);

          return forkJoin({
            lesson: this.catalog.getLesson(id),
            lessonProgress: progressReq$,
            tree: treeReq$,
          });
        })
      )
      .subscribe({
        next: ({ lesson, lessonProgress, tree }) => {
          this.lesson.set(lesson);
          this.lessonProgress.set(lessonProgress);
          if (tree) this.courseTree.set(tree);
          this.loading.set(false);
          this.startTimer();
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
          this.cdr.markForCheck();
        },
        error: () => {
          this.marking.set(false);
          this.cdr.markForCheck();
        },
      });
  }

  navQueryParams(): Record<string, string> {
    return this.courseSlug() ? { course: this.courseSlug() } : {};
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
