import {
  Component,
  inject,
  signal,
  OnInit,
  OnDestroy,
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  DestroyRef,
} from '@angular/core';
import { RouterLink } from '@angular/router';
import { NgClass } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { Subject as RxSubject, Subscription } from 'rxjs';
import { debounceTime, distinctUntilChanged, switchMap, catchError } from 'rxjs/operators';
import { of } from 'rxjs';
import {
  LucideAngularModule,
  Search,
  Code2,
  Filter,
  ChevronDown,
  Zap,
  ArrowRight,
  Inbox,
  RefreshCw,
  Plus,
  CheckCircle2,
  BookOpen,
} from 'lucide-angular';
import { CatalogService } from '../../../core/services/catalog.service';
import { AuthService } from '../../../core/services/auth.service';
import { SubmissionService } from '../../../core/services/submission.service';
import { ExerciseSummary, ExerciseDifficulty, LANGUAGE_LABELS } from '../../../core/models/types';

interface FilterState {
  q: string;
  difficulty: string;
  language: string;
}

const PAGE_SIZE = 12;

@Component({
  selector: 'app-exercise-list',
  standalone: true,
  imports: [RouterLink, NgClass, FormsModule, LucideAngularModule],
  templateUrl: './exercise-list.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ExerciseListComponent implements OnInit, OnDestroy {
  private readonly catalog = inject(CatalogService);
  private readonly auth = inject(AuthService);
  private readonly submissionService = inject(SubmissionService);
  private readonly cdr = inject(ChangeDetectorRef);
  private readonly destroyRef = inject(DestroyRef);
  private readonly filterChange$ = new RxSubject<FilterState>();
  private filterSub?: Subscription;

  readonly Search = Search;
  readonly Code2 = Code2;
  readonly Filter = Filter;
  readonly ChevronDown = ChevronDown;
  readonly Zap = Zap;
  readonly ArrowRight = ArrowRight;
  readonly Inbox = Inbox;
  readonly RefreshCw = RefreshCw;
  readonly Plus = Plus;
  readonly CheckCircle2 = CheckCircle2;
  readonly BookOpen = BookOpen;

  readonly LANGUAGE_LABELS = LANGUAGE_LABELS;

  readonly exercises = signal<ExerciseSummary[]>([]);
  readonly solvedIds = signal<Set<number>>(new Set());
  readonly loading = signal(true);
  readonly loadingMore = signal(false);
  readonly error = signal('');
  readonly hasMore = signal(false);
  readonly offset = signal(0);

  searchValue = '';
  difficultyValue = '';
  languageValue = '';

  readonly difficulties: { value: string; label: string }[] = [
    { value: '', label: 'All Difficulties' },
    { value: 'easy', label: 'Easy' },
    { value: 'medium', label: 'Medium' },
    { value: 'hard', label: 'Hard' },
  ];

  readonly languages: { value: string; label: string }[] = [
    { value: '', label: 'All Languages' },
    { value: 'python', label: 'Python' },
    { value: 'javascript', label: 'JavaScript' },
    { value: 'typescript', label: 'TypeScript' },
    { value: 'java', label: 'Java' },
    { value: 'csharp', label: 'C#' },
  ];

  ngOnInit(): void {
    this.filterSub = this.filterChange$
      .pipe(
        debounceTime(300),
        distinctUntilChanged((a, b) => JSON.stringify(a) === JSON.stringify(b)),
        switchMap((filters: FilterState) => {
          this.loading.set(true);
          this.offset.set(0);
          this.cdr.markForCheck();
          return this.catalog.getExercises({
            q: filters.q || undefined,
            difficulty: filters.difficulty || undefined,
            language: filters.language || undefined,
            limit: PAGE_SIZE,
            offset: 0,
          }).pipe(catchError(() => of<ExerciseSummary[] | null>(null)));
        }),
        takeUntilDestroyed(this.destroyRef)
      )
      .subscribe((results: ExerciseSummary[] | null) => {
        if (results === null) {
          this.error.set('Failed to load exercises.');
          this.exercises.set([]);
        } else {
          this.error.set('');
          this.exercises.set(results);
          this.hasMore.set(results.length === PAGE_SIZE);
          this.offset.set(results.length);
        }
        this.loading.set(false);
        this.cdr.markForCheck();
      });

    this.emitFilters();

    if (this.auth.isAuthenticated()) {
      this.submissionService.getMySubmissions().pipe(
        takeUntilDestroyed(this.destroyRef)
      ).subscribe({
        next: (subs) => {
          const solved = new Set(
            subs.filter(s => s.status === 'accepted').map(s => s.exercise_id)
          );
          this.solvedIds.set(solved);
          this.cdr.markForCheck();
        },
      });
    }
  }

  ngOnDestroy(): void {
    this.filterSub?.unsubscribe();
  }

  onSearchChange(value: string): void {
    this.searchValue = value;
    this.emitFilters();
  }

  onDifficultyChange(value: string): void {
    this.difficultyValue = value;
    this.emitFilters();
  }

  onLanguageChange(value: string): void {
    this.languageValue = value;
    this.emitFilters();
  }

  emitFilters(): void {
    this.filterChange$.next({
      q: this.searchValue,
      difficulty: this.difficultyValue,
      language: this.languageValue,
    });
  }

  loadMore(): void {
    if (this.loadingMore() || !this.hasMore()) return;
    this.loadingMore.set(true);

    this.catalog.getExercises({
      q: this.searchValue || undefined,
      difficulty: this.difficultyValue || undefined,
      language: this.languageValue || undefined,
      limit: PAGE_SIZE,
      offset: this.offset(),
    })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (results: ExerciseSummary[]) => {
          this.exercises.update(prev => [...prev, ...results]);
          this.hasMore.set(results.length === PAGE_SIZE);
          this.offset.update(o => o + results.length);
          this.loadingMore.set(false);
          this.cdr.markForCheck();
        },
        error: () => {
          this.loadingMore.set(false);
          this.cdr.markForCheck();
        },
      });
  }

  difficultyLabel(difficulty: string): string {
    if (!difficulty) return difficulty;
    return difficulty.charAt(0).toUpperCase() + difficulty.slice(1).toLowerCase();
  }

  difficultyBadge(difficulty: ExerciseDifficulty): string {
    switch (difficulty) {
      case 'easy':   return 'badge-easy';
      case 'medium': return 'badge-medium';
      case 'hard':   return 'badge-hard';
      default:       return 'badge-easy';
    }
  }

  trackById(_: number, item: ExerciseSummary): number {
    return item.id;
  }
}
