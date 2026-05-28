import {
  Component,
  inject,
  signal,
  OnInit,
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  DestroyRef,
} from '@angular/core';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { Subject as RxSubject } from 'rxjs';
import { debounceTime, distinctUntilChanged, switchMap } from 'rxjs/operators';
import {
  LucideAngularModule,
  LucideIconData,
  HelpCircle,
  Search,
  ArrowRight,
  Code2,
  Brain,
  Database,
  Server,
  Globe,
  Cpu,
  Layers,
  GitBranch,
  Lightbulb,
  Sigma,
  MessageCircleQuestion,
  ClipboardList,
  X,
} from 'lucide-angular';
import {
  InterviewService,
  InterviewCategory,
  InterviewQuestion,
} from '../../../core/services/interview.service';

@Component({
  selector: 'app-interview-list',
  standalone: true,
  imports: [RouterLink, FormsModule, LucideAngularModule],
  templateUrl: './interview-list.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class InterviewListComponent implements OnInit {
  private readonly interviewSvc = inject(InterviewService);
  private readonly cdr = inject(ChangeDetectorRef);
  private readonly destroyRef = inject(DestroyRef);

  // Icons
  readonly HelpCircle = HelpCircle;
  readonly Search = Search;
  readonly ArrowRight = ArrowRight;
  readonly ClipboardList = ClipboardList;
  readonly MessageCircleQuestion = MessageCircleQuestion;
  readonly X = X;

  private readonly iconMap: Record<string, LucideIconData> = {
    'code':           Code2,
    'code2':          Code2,
    'brain':          Brain,
    'database':       Database,
    'server':         Server,
    'globe':          Globe,
    'cpu':            Cpu,
    'layers':         Layers,
    'git-branch':     GitBranch,
    'lightbulb':      Lightbulb,
    'sigma':          Sigma,
    'help-circle':    HelpCircle,
    'message-circle': MessageCircleQuestion,
    'clipboard':      ClipboardList,
  };

  // State
  readonly categories = signal<InterviewCategory[]>([]);
  readonly searchResults = signal<InterviewQuestion[]>([]);
  readonly loading = signal(true);
  readonly searching = signal(false);
  readonly error = signal('');
  searchQuery = '';

  private readonly searchInput$ = new RxSubject<string>();

  ngOnInit(): void {
    // Load categories
    this.interviewSvc
      .getCategories()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (cats) => {
          this.categories.set(cats.sort((a, b) => a.order_index - b.order_index));
          this.loading.set(false);
          this.cdr.markForCheck();
        },
        error: () => {
          this.error.set('Failed to load interview categories. Please refresh.');
          this.loading.set(false);
          this.cdr.markForCheck();
        },
      });

    // Debounced search
    this.searchInput$
      .pipe(
        debounceTime(350),
        distinctUntilChanged(),
        switchMap((q) => {
          if (!q.trim()) {
            this.searchResults.set([]);
            this.searching.set(false);
            this.cdr.markForCheck();
            return [];
          }
          this.searching.set(true);
          this.cdr.markForCheck();
          return this.interviewSvc.searchQuestions({ q });
        }),
        takeUntilDestroyed(this.destroyRef)
      )
      .subscribe({
        next: (results) => {
          this.searchResults.set(results);
          this.searching.set(false);
          this.cdr.markForCheck();
        },
        error: () => {
          this.searching.set(false);
          this.cdr.markForCheck();
        },
      });
  }

  onSearchChange(query: string): void {
    this.searchQuery = query;
    this.searchInput$.next(query);
  }

  clearSearch(): void {
    this.searchQuery = '';
    this.searchResults.set([]);
    this.searching.set(false);
    this.searchInput$.next('');
    this.cdr.markForCheck();
  }

  isSearchActive(): boolean {
    return this.searchQuery.trim().length > 0;
  }

  categoryIcon(iconKey: string | undefined): LucideIconData {
    if (!iconKey) return ClipboardList;
    return this.iconMap[iconKey.toLowerCase()] ?? ClipboardList;
  }

  difficultyLabel(d: string): string {
    return d.charAt(0).toUpperCase() + d.slice(1);
  }

  difficultyClass(d: string): string {
    switch (d?.toLowerCase()) {
      case 'easy':   return 'bg-green-100 text-green-700 border border-green-200 dark:bg-green-950/50 dark:text-green-400 dark:border-green-800/60';
      case 'medium': return 'bg-amber-100 text-amber-700 border border-amber-200 dark:bg-amber-950/50 dark:text-amber-400 dark:border-amber-800/60';
      case 'hard':   return 'bg-red-100 text-red-700 border border-red-200 dark:bg-red-950/50 dark:text-red-400 dark:border-red-800/60';
      default:       return 'bg-app-surface-2 text-app-text-2 border border-app-border';
    }
  }
}
