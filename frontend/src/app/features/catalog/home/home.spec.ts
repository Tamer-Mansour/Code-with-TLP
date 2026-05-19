import { TestBed, ComponentFixture } from '@angular/core/testing';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { provideRouter } from '@angular/router';
import { of, throwError } from 'rxjs';
import {
  LucideAngularModule,
  BookOpen, Code2, Clock, ChevronRight, Zap, BarChart2, Layers, ArrowRight,
} from 'lucide-angular';
import { HomeComponent } from './home';
import { CatalogService } from '../../../core/services/catalog.service';
import { Subject, Course } from '../../../core/models/types';

const mockSubjects: Subject[] = [
  { id: 1, name: 'Python', slug: 'python', order_index: 0 },
  { id: 2, name: 'JavaScript', slug: 'javascript', order_index: 1 },
];

const mockCourses: Course[] = [
  {
    id: 1, subject_id: 1, title: 'Python Basics', slug: 'python-basics',
    difficulty: 'beginner', estimated_hours: 10, is_published: true, order_index: 0,
  },
  {
    id: 2, subject_id: 1, title: 'Advanced Python', slug: 'advanced-python',
    difficulty: 'advanced', estimated_hours: 20, is_published: true, order_index: 1,
  },
];

describe('HomeComponent', () => {
  let fixture: ComponentFixture<HomeComponent>;
  let component: HomeComponent;
  let mockCatalog: { getSubjects: ReturnType<typeof vi.fn>; getCourses: ReturnType<typeof vi.fn> };

  beforeEach(async () => {
    mockCatalog = {
      getSubjects: vi.fn().mockReturnValue(of(mockSubjects)),
      getCourses: vi.fn().mockReturnValue(of(mockCourses)),
    };

    await TestBed.configureTestingModule({
      imports: [
        HomeComponent,
        LucideAngularModule.pick({
          BookOpen, Code2, Clock, ChevronRight, Zap, BarChart2, Layers, ArrowRight,
        }),
      ],
      providers: [
        provideRouter([]),
        { provide: CatalogService, useValue: mockCatalog },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(HomeComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should start with loading true', () => {
    expect(component.loading()).toBe(true);
  });

  it('should start with empty subjects and courses', () => {
    expect(component.subjects()).toHaveLength(0);
    expect(component.courses()).toHaveLength(0);
  });

  it('should set loading to false after data loads', async () => {
    fixture.detectChanges();
    await fixture.whenStable();
    expect(component.loading()).toBe(false);
  });

  it('should populate subjects after successful load', async () => {
    fixture.detectChanges();
    await fixture.whenStable();
    expect(component.subjects()).toHaveLength(2);
    expect(component.subjects()[0].name).toBe('Python');
  });

  it('should populate courses after successful load', async () => {
    fixture.detectChanges();
    await fixture.whenStable();
    expect(component.courses()).toHaveLength(2);
    expect(component.courses()[0].title).toBe('Python Basics');
  });

  it('should limit courses to 6', async () => {
    const manyCourses: Course[] = Array.from({ length: 10 }, (_, i) => ({
      id: i + 1, subject_id: 1, title: `Course ${i + 1}`, slug: `course-${i + 1}`,
      difficulty: 'beginner', estimated_hours: 5, is_published: true, order_index: i,
    }));
    mockCatalog.getCourses.mockReturnValue(of(manyCourses));
    fixture.detectChanges();
    await fixture.whenStable();
    expect(component.courses()).toHaveLength(6);
  });

  it('should set error message on catalog load failure', async () => {
    mockCatalog.getSubjects.mockReturnValue(throwError(() => new Error('Network error')));
    fixture.detectChanges();
    await fixture.whenStable();
    expect(component.error()).toBe('Failed to load catalog. Please refresh.');
    expect(component.loading()).toBe(false);
  });

  describe('difficultyBadge()', () => {
    it('should return badge-easy for beginner', () => {
      expect(component.difficultyBadge('beginner')).toBe('badge-easy');
    });
    it('should return badge-medium for intermediate', () => {
      expect(component.difficultyBadge('intermediate')).toBe('badge-medium');
    });
    it('should return badge-hard for advanced', () => {
      expect(component.difficultyBadge('advanced')).toBe('badge-hard');
    });
    it('should return badge-easy for unknown difficulty', () => {
      expect(component.difficultyBadge('unknown')).toBe('badge-easy');
    });
  });

  describe('difficultyLabel()', () => {
    it('should return Beginner for beginner', () => {
      expect(component.difficultyLabel('beginner')).toBe('Beginner');
    });
    it('should return Intermediate for intermediate', () => {
      expect(component.difficultyLabel('intermediate')).toBe('Intermediate');
    });
    it('should return Advanced for advanced', () => {
      expect(component.difficultyLabel('advanced')).toBe('Advanced');
    });
    it('should pass through unknown values', () => {
      expect(component.difficultyLabel('unknown')).toBe('unknown');
    });
  });

  describe('subjectGradient()', () => {
    it('should return a gradient string for index 0', () => {
      expect(component.subjectGradient(0)).toContain('from-blue-600');
    });
    it('should cycle through gradients', () => {
      const g0 = component.subjectGradient(0);
      const g6 = component.subjectGradient(6);
      expect(g0).toBe(g6);
    });
  });

  describe('subjectIconColor()', () => {
    it('should return a color string for index 0', () => {
      expect(component.subjectIconColor(0)).toBe('text-blue-400');
    });
    it('should cycle through colors', () => {
      const c0 = component.subjectIconColor(0);
      const c6 = component.subjectIconColor(6);
      expect(c0).toBe(c6);
    });
  });

  describe('trackById()', () => {
    it('should return the item id', () => {
      expect(component.trackById(0, { id: 42 })).toBe(42);
    });
  });
});
