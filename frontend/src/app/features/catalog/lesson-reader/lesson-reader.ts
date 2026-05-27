import {
  Component,
  inject,
  signal,
  computed,
  OnInit,
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  DestroyRef,
  HostListener,
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
  XCircle,
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
  BookOpen,
} from 'lucide-angular';
import { CatalogService } from '../../../core/services/catalog.service';
import { ProgressService } from '../../../core/services/progress.service';
import { AuthService } from '../../../core/services/auth.service';
import { ToastService } from '../../../core/services/toast.service';
import { QuizService, QuizQuestion, QuizMyAnswer, QuizQuestionResult } from '../../../core/services/quiz.service';
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
  private readonly quiz = inject(QuizService);
  private readonly cdr = inject(ChangeDetectorRef);
  private readonly destroyRef = inject(DestroyRef);

  readonly ChevronRight = ChevronRight;
  readonly ChevronLeft = ChevronLeft;
  readonly CheckCircle2 = CheckCircle2;
  readonly XCircle = XCircle;
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
  readonly BookOpen = BookOpen;

  readonly lesson = signal<Lesson | null>(null);
  readonly lessonProgress = signal<LessonProgress | null>(null);
  readonly loading = signal(true);
  readonly marking = signal(false);
  readonly error = signal('');
  readonly courseSlug = signal('');
  readonly courseTree = signal<CourseTree | null>(null);
  readonly timeSpent = signal(0); // seconds since page loaded
  readonly readingProgressPct = signal(0); // 0–100 scroll progress

  // ── Quiz state ───────────────────────────────────────────────────────────
  readonly quizQuestions = signal<QuizQuestion[]>([]);
  readonly quizLoading = signal(false);
  /** Map of question_id → selected_index (-1 = not selected) */
  readonly quizSelections = signal<Map<number, number>>(new Map());
  readonly quizSubmitting = signal(false);
  readonly quizResults = signal<QuizQuestionResult[] | null>(null);
  readonly quizScore = signal<{ total: number; correct: number; passed: boolean } | null>(null);
  /** True for non-quiz lessons; true for quiz lessons once submitted */
  readonly quizGateOpen = signal(false);

  /** All quiz questions have a selection */
  readonly allAnswered = computed(() => {
    const qs = this.quizQuestions();
    if (qs.length === 0) return false;
    const sel = this.quizSelections();
    return qs.every(q => (sel.get(q.id) ?? -1) >= 0);
  });

  /** Two-digit minutes for the flip counter */
  readonly timerMinutes = computed(() => Math.floor(this.timeSpent() / 60).toString().padStart(2, '0'));
  /** Two-digit seconds for the flip counter */
  readonly timerSeconds = computed(() => (this.timeSpent() % 60).toString().padStart(2, '0'));

  private timerHandle: ReturnType<typeof setInterval> | null = null;

  @HostListener('window:scroll')
  onWindowScroll(): void {
    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    const docHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const pct = docHeight > 0 ? Math.min(100, Math.round((scrollTop / docHeight) * 100)) : 0;
    this.readingProgressPct.set(pct);
    this.cdr.markForCheck();
  }

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

  /** Markdown body with a leading H1 stripped when it just repeats the lesson title */
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

  /** Reset all quiz state between lesson navigations */
  private resetQuizState(): void {
    this.quizQuestions.set([]);
    this.quizSelections.set(new Map());
    this.quizResults.set(null);
    this.quizScore.set(null);
    this.quizGateOpen.set(false);
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
          this.resetQuizState();
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

          // Open gate immediately for non-quiz lessons
          if (lesson.lesson_type !== 'quiz') {
            this.quizGateOpen.set(true);
          } else {
            // Load questions and pre-existing answers in parallel
            this.loadQuiz(lesson.id);
          }

          this.cdr.markForCheck();
        },
        error: () => {
          this.error.set('Could not load lesson. Please try again.');
          this.loading.set(false);
          this.cdr.markForCheck();
        },
      });
  }

  private loadQuiz(lessonId: number): void {
    this.quizLoading.set(true);
    this.cdr.markForCheck();

    const questions$ = this.quiz.getQuestions(lessonId).pipe(catchError(() => of<QuizQuestion[]>([])));
    const myAnswers$ = this.auth.isAuthenticated()
      ? this.quiz.getMyAnswers(lessonId).pipe(catchError(() => of<QuizMyAnswer[]>([])))
      : of<QuizMyAnswer[]>([]);

    forkJoin({ questions: questions$, myAnswers: myAnswers$ })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(({ questions, myAnswers }) => {
        this.quizQuestions.set(questions);

        if (myAnswers.length > 0) {
          // Pre-fill prior selections
          const selMap = new Map<number, number>();
          for (const a of myAnswers) {
            selMap.set(a.question_id, a.selected_index);
          }
          this.quizSelections.set(selMap);

          // If all questions were previously answered, open the gate
          const allPreviouslyAnswered = questions.every(q => selMap.has(q.id) && (selMap.get(q.id) ?? -1) >= 0);
          if (allPreviouslyAnswered && questions.length > 0) {
            this.quizGateOpen.set(true);
          }
        }

        this.quizLoading.set(false);
        this.cdr.markForCheck();
      });
  }

  selectOption(questionId: number, optionIndex: number): void {
    // Do not allow changes after submission
    if (this.quizResults() !== null) return;
    const next = new Map(this.quizSelections());
    next.set(questionId, optionIndex);
    this.quizSelections.set(next);
    this.cdr.markForCheck();
  }

  submitQuiz(): void {
    if (!this.allAnswered() || this.quizSubmitting()) return;

    const lessonId = this.lesson()?.id;
    if (!lessonId) return;

    const answers = Array.from(this.quizSelections().entries()).map(([question_id, selected_index]) => ({
      question_id,
      selected_index,
    }));

    this.quizSubmitting.set(true);
    this.cdr.markForCheck();

    this.quiz.submit(lessonId, answers)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (resp) => {
          this.quizResults.set(resp.results);
          this.quizScore.set({ total: resp.total, correct: resp.correct, passed: resp.passed });
          this.quizGateOpen.set(true);
          this.quizSubmitting.set(false);
          this.cdr.markForCheck();
        },
        error: () => {
          this.quizSubmitting.set(false);
          this.cdr.markForCheck();
        },
      });
  }

  /** Helper: get result for a specific question (after submission) */
  getResult(questionId: number): QuizQuestionResult | undefined {
    return this.quizResults()?.find(r => r.question_id === questionId);
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
