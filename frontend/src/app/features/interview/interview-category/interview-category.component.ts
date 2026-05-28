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
import { FormsModule } from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { MarkdownModule } from 'ngx-markdown';
import {
  LucideAngularModule,
  LucideIconData,
  ArrowLeft,
  ChevronDown,
  ChevronRight,
  Tag,
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
  Search,
  X,
  Filter,
} from 'lucide-angular';
import {
  InterviewService,
  InterviewCategoryDetail,
  InterviewQuestion,
} from '../../../core/services/interview.service';

@Component({
  selector: 'app-interview-category',
  standalone: true,
  imports: [RouterLink, FormsModule, MarkdownModule, LucideAngularModule],
  templateUrl: './interview-category.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class InterviewCategoryComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly interviewSvc = inject(InterviewService);
  private readonly cdr = inject(ChangeDetectorRef);
  private readonly destroyRef = inject(DestroyRef);

  // Icons
  readonly ArrowLeft = ArrowLeft;
  readonly ChevronDown = ChevronDown;
  readonly ChevronRight = ChevronRight;
  readonly Tag = Tag;
  readonly ClipboardList = ClipboardList;
  readonly MessageCircleQuestion = MessageCircleQuestion;
  readonly Search = Search;
  readonly X = X;
  readonly Filter = Filter;

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
    'help-circle':    MessageCircleQuestion,
    'message-circle': MessageCircleQuestion,
    'clipboard':      ClipboardList,
  };

  // State
  readonly category = signal<InterviewCategoryDetail | null>(null);
  readonly loading = signal(true);
  readonly error = signal('');
  readonly expandedIds = signal<Set<number>>(new Set());

  // Filters
  filterDifficulty = '';
  filterQuery = '';

  // Computed filtered questions
  readonly filteredQuestions = computed(() => {
    const cat = this.category();
    if (!cat) return [];
    let qs = cat.questions.slice().sort((a, b) => a.order_index - b.order_index);

    if (this.filterDifficulty) {
      qs = qs.filter(q => q.difficulty === this.filterDifficulty);
    }
    if (this.filterQuery.trim()) {
      const lc = this.filterQuery.toLowerCase();
      qs = qs.filter(
        q => q.question.toLowerCase().includes(lc) ||
             q.tags.some(t => t.toLowerCase().includes(lc))
      );
    }
    return qs;
  });

  ngOnInit(): void {
    this.route.paramMap
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(params => {
        const slug = params.get('slug') ?? '';
        this.loading.set(true);
        this.error.set('');
        this.category.set(null);
        this.expandedIds.set(new Set());
        this.cdr.markForCheck();

        this.interviewSvc
          .getCategoryBySlug(slug)
          .pipe(takeUntilDestroyed(this.destroyRef))
          .subscribe({
            next: (cat) => {
              this.category.set(cat);
              this.loading.set(false);
              this.cdr.markForCheck();
            },
            error: () => {
              this.error.set('Could not load category. Please try again.');
              this.loading.set(false);
              this.cdr.markForCheck();
            },
          });
      });
  }

  toggleExpand(id: number): void {
    const current = new Set(this.expandedIds());
    if (current.has(id)) {
      current.delete(id);
    } else {
      current.add(id);
    }
    this.expandedIds.set(current);
    this.cdr.markForCheck();
  }

  isExpanded(id: number): boolean {
    return this.expandedIds().has(id);
  }

  onFilterChange(): void {
    this.cdr.markForCheck();
  }

  clearFilters(): void {
    this.filterDifficulty = '';
    this.filterQuery = '';
    this.cdr.markForCheck();
  }

  hasFilters(): boolean {
    return !!(this.filterDifficulty || this.filterQuery.trim());
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
