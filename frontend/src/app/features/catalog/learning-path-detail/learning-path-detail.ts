import {
  Component,
  inject,
  signal,
  computed,
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
  Layers,
  Lock,
  CheckCircle2,
  BookOpen,
  ArrowRight,
  Trophy,
  ChevronRight,
} from 'lucide-angular';
import { CatalogService } from '../../../core/services/catalog.service';
import { LearningPath, PathCourseProgress } from '../../../core/models/types';

@Component({
  selector: 'app-learning-path-detail',
  standalone: true,
  imports: [RouterLink, LucideAngularModule],
  templateUrl: './learning-path-detail.html',
  styleUrl: './learning-path-detail.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LearningPathDetailComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly catalog = inject(CatalogService);
  private readonly cdr = inject(ChangeDetectorRef);
  private readonly destroyRef = inject(DestroyRef);

  // Icons
  readonly Layers = Layers;
  readonly Lock = Lock;
  readonly CheckCircle2 = CheckCircle2;
  readonly BookOpen = BookOpen;
  readonly ArrowRight = ArrowRight;
  readonly Trophy = Trophy;
  readonly ChevronRight = ChevronRight;

  readonly path = signal<LearningPath | null>(null);
  readonly courses = signal<PathCourseProgress[]>([]);
  readonly loading = signal(true);
  readonly error = signal('');

  /** Overall path progress: average of course progress_percent, falling back to completed/total. */
  readonly overallProgress = computed(() => {
    const list = this.courses();
    if (list.length === 0) return 0;

    const hasPercent = list.some((c) => typeof c.progress_percent === 'number');
    if (hasPercent) {
      const sum = list.reduce((acc, c) => acc + (c.progress_percent ?? 0), 0);
      return Math.round(sum / list.length);
    }
    const completed = list.filter((c) => c.completed).length;
    return Math.round((completed / list.length) * 100);
  });

  readonly completedCount = computed(() => this.courses().filter((c) => c.completed).length);

  ngOnInit(): void {
    const slug = this.route.snapshot.paramMap.get('slug') ?? '';

    forkJoin({
      path: this.catalog.getLearningPath(slug),
      // getLearningPathProgress already normalizes bare-array vs { courses } shapes.
      // Tolerate failure (e.g. endpoint still being built) by degrading gracefully.
      progress: this.catalog
        .getLearningPathProgress(slug)
        .pipe(catchError(() => of<PathCourseProgress[]>([]))),
    })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: ({ path, progress }) => {
          this.path.set(path);
          this.courses.set(this.normalizeOrder(progress));
          this.loading.set(false);
          this.cdr.markForCheck();
        },
        error: () => {
          this.error.set('Could not load learning path. Please try again.');
          this.loading.set(false);
          this.cdr.markForCheck();
        },
      });
  }

  /** Defensive: ensure stable order by order_index regardless of API ordering. */
  private normalizeOrder(list: PathCourseProgress[]): PathCourseProgress[] {
    return [...(list ?? [])].sort(
      (a, b) => (a.order_index ?? 0) - (b.order_index ?? 0),
    );
  }

  /** Connector above a node is brand-colored when the PREVIOUS course is completed. */
  isConnectorActive(index: number): boolean {
    if (index <= 0) return false;
    return !!this.courses()[index - 1]?.completed;
  }

  difficultyBadge(difficulty: string): string {
    switch (difficulty?.toLowerCase()) {
      case 'beginner':
      case 'easy':
        return 'badge-easy';
      case 'intermediate':
      case 'medium':
        return 'badge-medium';
      case 'advanced':
      case 'hard':
        return 'badge-hard';
      default:
        return 'badge-easy';
    }
  }

  difficultyLabel(difficulty: string): string {
    if (!difficulty) return '';
    return difficulty.charAt(0).toUpperCase() + difficulty.slice(1);
  }

  trackByCourseId(_: number, item: PathCourseProgress): number {
    return item.course_id;
  }
}
