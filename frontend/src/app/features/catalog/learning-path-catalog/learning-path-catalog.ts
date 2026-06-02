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
import {
  LucideAngularModule,
  LucideIconData,
  Layers,
  Trophy,
  BookOpen,
  ArrowRight,
  Route,
} from 'lucide-angular';
import { CatalogService } from '../../../core/services/catalog.service';
import { LearningPath } from '../../../core/models/types';

@Component({
  selector: 'app-learning-path-catalog',
  standalone: true,
  imports: [RouterLink, LucideAngularModule],
  templateUrl: './learning-path-catalog.html',
  styleUrl: './learning-path-catalog.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LearningPathCatalogComponent implements OnInit {
  private readonly catalog = inject(CatalogService);
  private readonly cdr = inject(ChangeDetectorRef);
  private readonly destroyRef = inject(DestroyRef);

  readonly Layers = Layers;
  readonly Trophy = Trophy;
  readonly BookOpen = BookOpen;
  readonly ArrowRight = ArrowRight;
  readonly Route = Route;

  readonly paths = signal<LearningPath[]>([]);
  readonly loading = signal(true);
  readonly error = signal('');

  ngOnInit(): void {
    this.catalog
      .getLearningPaths()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (paths) => {
          this.paths.set(paths ?? []);
          this.loading.set(false);
          this.cdr.markForCheck();
        },
        error: () => {
          this.error.set('Failed to load learning paths. Please refresh.');
          this.loading.set(false);
          this.cdr.markForCheck();
        },
      });
  }

  /** Alternate the banner icon so the grid feels less monotonous. */
  bannerIcon(index: number): LucideIconData {
    return index % 2 === 0 ? this.Layers : this.Trophy;
  }

  /** First few course titles for the roadmap preview. */
  previewCourses(path: LearningPath): { title: string }[] {
    return (path.courses ?? []).slice(0, 4);
  }

  courseCount(path: LearningPath): number {
    return path.courses?.length ?? 0;
  }

  trackById(_: number, item: { id: number }): number {
    return item.id;
  }
}
