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
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { forkJoin } from 'rxjs';
import {
  LucideAngularModule,
  LucideIconData,
  BookOpen,
  Brain,
  Code,
  Code2,
  Clock,
  ChevronRight,
  Cpu,
  Database,
  GitBranch,
  Globe,
  Lightbulb,
  Server,
  Sigma,
  Zap,
  BarChart2,
  Layers,
  ArrowRight,
} from 'lucide-angular';
import { CatalogService } from '../../../core/services/catalog.service';
import { Subject, Course } from '../../../core/models/types';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [RouterLink, LucideAngularModule],
  templateUrl: './home.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HomeComponent implements OnInit {
  private readonly catalog = inject(CatalogService);
  private readonly cdr = inject(ChangeDetectorRef);
  private readonly destroyRef = inject(DestroyRef);

  readonly BookOpen = BookOpen;
  readonly Code2 = Code2;
  readonly Clock = Clock;
  readonly ChevronRight = ChevronRight;
  readonly Zap = Zap;
  readonly BarChart2 = BarChart2;
  readonly Layers = Layers;
  readonly ArrowRight = ArrowRight;

  private readonly iconMap: Record<string, LucideIconData> = {
    'lightbulb':  Lightbulb,
    'code':       Code,
    'server':     Server,
    'sigma':      Sigma,
    'git-branch': GitBranch,
    'brain':      Brain,
    'cpu':        Cpu,
    'globe':      Globe,
    'database':   Database,
  };

  readonly subjects = signal<Subject[]>([]);
  readonly courses = signal<Course[]>([]);
  readonly loading = signal(true);
  readonly error = signal('');

  ngOnInit(): void {
    forkJoin({
      subjects: this.catalog.getSubjects(),
      courses: this.catalog.getCourses(),
    })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: ({ subjects, courses }) => {
          this.subjects.set(subjects);
          this.courses.set(courses.slice(0, 6));
          this.loading.set(false);
          this.cdr.markForCheck();
        },
        error: () => {
          this.error.set('Failed to load catalog. Please refresh.');
          this.loading.set(false);
          this.cdr.markForCheck();
        },
      });
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

  subjectIcon(iconKey: string | undefined): LucideIconData {
    return (iconKey && this.iconMap[iconKey]) ? this.iconMap[iconKey] : Layers;
  }

  subjectAccentStyle(color: string | undefined): Record<string, string> {
    if (!color) return {};
    return { 'border-left-color': color, 'color': color };
  }

  subjectGradient(index: number): string {
    const gradients = [
      'from-blue-600/20 to-blue-800/10',
      'from-purple-600/20 to-purple-800/10',
      'from-emerald-600/20 to-emerald-800/10',
      'from-amber-600/20 to-amber-800/10',
      'from-rose-600/20 to-rose-800/10',
      'from-cyan-600/20 to-cyan-800/10',
    ];
    return gradients[index % gradients.length];
  }

  subjectIconColor(index: number): string {
    const colors = [
      'text-blue-400', 'text-purple-400', 'text-emerald-400',
      'text-amber-400', 'text-rose-400', 'text-cyan-400',
    ];
    return colors[index % colors.length];
  }

  trackById(_: number, item: { id: number }): number {
    return item.id;
  }
}
