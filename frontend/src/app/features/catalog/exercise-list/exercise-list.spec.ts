import { TestBed, ComponentFixture } from '@angular/core/testing';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { provideRouter } from '@angular/router';
import { of, throwError } from 'rxjs';
import { FormsModule } from '@angular/forms';
import {
  LucideAngularModule,
  Search, Code2, Filter, ChevronDown, Zap, ArrowRight, Inbox, RefreshCw, Plus,
} from 'lucide-angular';
import { ExerciseListComponent } from './exercise-list';
import { CatalogService } from '../../../core/services/catalog.service';
import { ExerciseSummary } from '../../../core/models/types';

const mockExercises: ExerciseSummary[] = [
  { id: 1, title: 'Two Sum', slug: 'two-sum', difficulty: 'easy', points: 10, supported_languages: ['python'] },
  { id: 2, title: 'Binary Search', slug: 'binary-search', difficulty: 'medium', points: 20, supported_languages: ['python', 'javascript'] },
];

describe('ExerciseListComponent', () => {
  let fixture: ComponentFixture<ExerciseListComponent>;
  let component: ExerciseListComponent;
  let mockCatalog: { getExercises: ReturnType<typeof vi.fn> };

  beforeEach(async () => {
    vi.useFakeTimers();
    mockCatalog = {
      getExercises: vi.fn().mockReturnValue(of(mockExercises)),
    };

    await TestBed.configureTestingModule({
      imports: [
        ExerciseListComponent,
        FormsModule,
        LucideAngularModule.pick({
          Search, Code2, Filter, ChevronDown, Zap, ArrowRight, Inbox, RefreshCw, Plus,
        }),
      ],
      providers: [
        provideRouter([]),
        { provide: CatalogService, useValue: mockCatalog },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ExerciseListComponent);
    component = fixture.componentInstance;
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.clearAllMocks();
  });

  function init() {
    fixture.detectChanges(); // triggers ngOnInit -> emitFilters -> filterChange$.next()
    vi.advanceTimersByTime(300); // advance past debounce
    fixture.detectChanges();
  }

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should start with loading true', () => {
    expect(component.loading()).toBe(true);
  });

  it('should start with empty exercises list', () => {
    expect(component.exercises()).toHaveLength(0);
  });

  it('should start with loadingMore false', () => {
    expect(component.loadingMore()).toBe(false);
  });

  it('should call getExercises on init', () => {
    init();
    expect(mockCatalog.getExercises).toHaveBeenCalled();
  });

  it('should load exercises after init and debounce', () => {
    init();
    expect(component.exercises()).toHaveLength(2);
    expect(component.loading()).toBe(false);
  });

  it('should set hasMore to false when results are fewer than PAGE_SIZE (12)', () => {
    init();
    expect(component.hasMore()).toBe(false);
  });

  it('should set hasMore to true when results equal PAGE_SIZE (12)', () => {
    const fullPage: ExerciseSummary[] = Array.from({ length: 12 }, (_, i) => ({
      id: i + 1, title: `Exercise ${i + 1}`, slug: `exercise-${i + 1}`,
      difficulty: 'easy' as const, points: 10, supported_languages: ['python'] as const,
    }));
    mockCatalog.getExercises.mockReturnValue(of(fullPage));
    init();
    expect(component.hasMore()).toBe(true);
  });

  it('should set error on load failure', () => {
    mockCatalog.getExercises.mockReturnValue(throwError(() => new Error('Network error')));
    init();
    expect(component.error()).toBe('Failed to load exercises.');
    expect(component.exercises()).toHaveLength(0);
  });

  it('should update searchValue and call service on onSearchChange()', () => {
    init();
    mockCatalog.getExercises.mockClear();
    component.onSearchChange('two sum');
    vi.advanceTimersByTime(300);
    expect(component.searchValue).toBe('two sum');
    expect(mockCatalog.getExercises).toHaveBeenCalled();
  });

  it('should update difficultyValue on onDifficultyChange()', () => {
    init();
    component.onDifficultyChange('easy');
    expect(component.difficultyValue).toBe('easy');
  });

  it('should update languageValue on onLanguageChange()', () => {
    init();
    component.onLanguageChange('python');
    expect(component.languageValue).toBe('python');
  });

  it('should not trigger loadMore when loadingMore is true', () => {
    init();
    component.hasMore.set(true);
    component.loadingMore.set(true);
    mockCatalog.getExercises.mockClear();
    component.loadMore();
    // loadMore returns early when loadingMore is true
    expect(component.loadingMore()).toBe(true);
  });

  it('should not trigger loadMore when hasMore is false', () => {
    init();
    component.hasMore.set(false);
    const callsBefore = mockCatalog.getExercises.mock.calls.length;
    component.loadMore();
    expect(mockCatalog.getExercises.mock.calls.length).toBe(callsBefore);
  });

  it('should append exercises on loadMore', () => {
    init();
    component.hasMore.set(true);
    component.offset.set(2);
    const moreMock: ExerciseSummary[] = [
      { id: 3, title: 'Merge Sort', slug: 'merge-sort', difficulty: 'hard', points: 30, supported_languages: ['python'] },
    ];
    mockCatalog.getExercises.mockReturnValue(of(moreMock));
    component.loadMore();
    fixture.detectChanges();
    expect(component.exercises()).toHaveLength(3);
    expect(component.loadingMore()).toBe(false);
  });

  describe('difficultyLabel()', () => {
    it('should capitalize first letter', () => {
      expect(component.difficultyLabel('easy')).toBe('Easy');
      expect(component.difficultyLabel('medium')).toBe('Medium');
      expect(component.difficultyLabel('hard')).toBe('Hard');
    });

    it('should return unchanged when empty string', () => {
      expect(component.difficultyLabel('')).toBe('');
    });
  });

  describe('difficultyBadge()', () => {
    it('should return badge-easy for easy', () => {
      expect(component.difficultyBadge('easy')).toBe('badge-easy');
    });
    it('should return badge-medium for medium', () => {
      expect(component.difficultyBadge('medium')).toBe('badge-medium');
    });
    it('should return badge-hard for hard', () => {
      expect(component.difficultyBadge('hard')).toBe('badge-hard');
    });
  });

  describe('trackById()', () => {
    it('should return the item id', () => {
      const ex = mockExercises[0];
      expect(component.trackById(0, ex)).toBe(1);
    });
  });

  describe('languages and difficulties arrays', () => {
    it('should have a default "All Difficulties" entry', () => {
      expect(component.difficulties[0]).toEqual({ value: '', label: 'All Difficulties' });
    });
    it('should have a default "All Languages" entry', () => {
      expect(component.languages[0]).toEqual({ value: '', label: 'All Languages' });
    });
  });
});
