import { TestBed, ComponentFixture } from '@angular/core/testing';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { signal, computed } from '@angular/core';
import { provideRouter } from '@angular/router';
import { of, throwError } from 'rxjs';
import { DatePipe, NgClass } from '@angular/common';
import {
  LucideAngularModule,
  BookOpen, Code2, CheckCircle2, GraduationCap, ArrowRight, Percent, Play, Zap,
} from 'lucide-angular';
import { DashboardComponent } from './dashboard.component';
import { AuthService } from '../../core/services/auth.service';
import { ProgressService } from '../../core/services/progress.service';
import { SubmissionService } from '../../core/services/submission.service';
import { CatalogService } from '../../core/services/catalog.service';
import {
  User, Enrollment, SubmissionSummary, Course,
} from '../../core/models/types';

const mockUser: User = {
  id: 1, email: 'student@test.com', username: 'student',
  full_name: 'Student User', role: 'student', is_active: true,
  created_at: '2024-01-01T00:00:00Z',
};

const mockEnrollments: Enrollment[] = [
  { id: 1, user_id: 1, course_id: 10, progress_percent: 50, created_at: '2024-01-01T00:00:00Z' },
  { id: 2, user_id: 1, course_id: 20, progress_percent: 100, created_at: '2024-01-02T00:00:00Z' },
];

const mockSubmissions: SubmissionSummary[] = [
  {
    id: 1, user_id: 1, exercise_id: 1, language: 'python',
    status: 'accepted', score: 100, passed_tests: 5, total_tests: 5,
    runtime_ms: 42, created_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 2, user_id: 1, exercise_id: 2, language: 'javascript',
    status: 'wrong_answer', score: 0, passed_tests: 2, total_tests: 5,
    runtime_ms: 100, created_at: '2024-01-02T00:00:00Z',
  },
];

const mockCourses: Course[] = [
  {
    id: 10, subject_id: 1, title: 'Python Basics', slug: 'python-basics',
    difficulty: 'beginner', estimated_hours: 10, is_published: true, order_index: 0,
  },
];

describe('DashboardComponent', () => {
  let fixture: ComponentFixture<DashboardComponent>;
  let component: DashboardComponent;
  let mockAuth: ReturnType<typeof buildMockAuth>;
  let mockProgress: { getMyEnrollments: ReturnType<typeof vi.fn> };
  let mockSubmission: { getMySubmissions: ReturnType<typeof vi.fn> };
  let mockCatalog: { getCourses: ReturnType<typeof vi.fn> };

  function buildMockAuth(user: User | null = mockUser) {
    const currentUser = signal<User | null>(user);
    return {
      currentUser,
      isAuthenticated: computed(() => !!currentUser()),
      isAdmin: computed(() => currentUser()?.role === 'admin'),
      logout: vi.fn(),
    };
  }

  beforeEach(async () => {
    mockAuth = buildMockAuth();
    mockProgress = { getMyEnrollments: vi.fn().mockReturnValue(of(mockEnrollments)) };
    mockSubmission = { getMySubmissions: vi.fn().mockReturnValue(of(mockSubmissions)) };
    mockCatalog = { getCourses: vi.fn().mockReturnValue(of(mockCourses)) };

    await TestBed.configureTestingModule({
      imports: [
        DashboardComponent,
        NgClass,
        DatePipe,
        LucideAngularModule.pick({
          BookOpen, Code2, CheckCircle2, GraduationCap, ArrowRight, Percent, Play, Zap,
        }),
      ],
      providers: [
        provideRouter([]),
        { provide: AuthService, useValue: mockAuth },
        { provide: ProgressService, useValue: mockProgress },
        { provide: SubmissionService, useValue: mockSubmission },
        { provide: CatalogService, useValue: mockCatalog },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(DashboardComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should start with loadingEnrollments true', () => {
    expect(component.loadingEnrollments()).toBe(true);
  });

  it('should start with loadingSubmissions true', () => {
    expect(component.loadingSubmissions()).toBe(true);
  });

  it('should expose currentUser from auth service', () => {
    expect(component.currentUser).toBe(mockAuth.currentUser);
  });

  it('should load enrollments on init', async () => {
    fixture.detectChanges();
    await fixture.whenStable();
    expect(component.enrollments()).toHaveLength(2);
    expect(component.loadingEnrollments()).toBe(false);
  });

  it('should load submissions on init', async () => {
    fixture.detectChanges();
    await fixture.whenStable();
    expect(component.recentSubmissions()).toHaveLength(2);
    expect(component.loadingSubmissions()).toBe(false);
  });

  it('should limit submissions to 10', async () => {
    const manySubs: SubmissionSummary[] = Array.from({ length: 15 }, (_, i) => ({
      id: i + 1, user_id: 1, exercise_id: 1, language: 'python',
      status: 'accepted' as const, score: 100, passed_tests: 5, total_tests: 5,
      runtime_ms: 10, created_at: '2024-01-01T00:00:00Z',
    }));
    mockSubmission.getMySubmissions.mockReturnValue(of(manySubs));
    fixture.detectChanges();
    await fixture.whenStable();
    expect(component.recentSubmissions()).toHaveLength(10);
  });

  it('should compute enrolledCount from enrollments', async () => {
    fixture.detectChanges();
    await fixture.whenStable();
    expect(component.enrolledCount()).toBe(2);
  });

  it('should compute completedExercises from accepted submissions', async () => {
    fixture.detectChanges();
    await fixture.whenStable();
    expect(component.completedExercises()).toBe(1);
  });

  it('should compute acceptanceRate correctly', async () => {
    fixture.detectChanges();
    await fixture.whenStable();
    // 1 accepted out of 2 total = 50%
    expect(component.acceptanceRate()).toBe(50);
  });

  it('should return 0 for acceptanceRate when no submissions', () => {
    component.recentSubmissions.set([]);
    expect(component.acceptanceRate()).toBe(0);
  });

  it('should compute totalPoints from submissions', async () => {
    fixture.detectChanges();
    await fixture.whenStable();
    expect(component.totalPoints()).toBe(100);
  });

  it('should handle enrollment load error gracefully', async () => {
    mockProgress.getMyEnrollments.mockReturnValue(throwError(() => new Error('Network')));
    fixture.detectChanges();
    await fixture.whenStable();
    expect(component.loadingEnrollments()).toBe(false);
    expect(component.enrollments()).toHaveLength(0);
  });

  it('should handle submission load error gracefully', async () => {
    mockSubmission.getMySubmissions.mockReturnValue(throwError(() => new Error('Network')));
    fixture.detectChanges();
    await fixture.whenStable();
    expect(component.loadingSubmissions()).toBe(false);
  });

  describe('userInitials()', () => {
    it('should return "?" when no user', () => {
      mockAuth.currentUser.set(null);
      expect(component.userInitials()).toBe('?');
    });

    it('should return initials from full_name', () => {
      expect(component.userInitials()).toBe('SU');
    });

    it('should return initials from username when full_name is absent', () => {
      mockAuth.currentUser.set({ ...mockUser, full_name: undefined });
      expect(component.userInitials()).toBe('S');
    });
  });

  describe('getStatusBadge()', () => {
    it('should return badge-accepted for accepted status', () => {
      expect(component.getStatusBadge('accepted')).toBe('badge-accepted');
    });
    it('should return badge-wrong for wrong_answer status', () => {
      expect(component.getStatusBadge('wrong_answer')).toBe('badge-wrong');
    });
    it('should return badge-error for pending status', () => {
      expect(component.getStatusBadge('pending')).toBe('badge-error');
    });
  });

  describe('getStatusLabel()', () => {
    it('should return Accepted for accepted status', () => {
      expect(component.getStatusLabel('accepted')).toBe('Accepted');
    });
    it('should return Wrong Answer for wrong_answer status', () => {
      expect(component.getStatusLabel('wrong_answer')).toBe('Wrong Answer');
    });
  });

  describe('getDifficultyBadge()', () => {
    it('should return badge-easy for beginner', () => {
      expect(component.getDifficultyBadge('beginner')).toBe('badge-easy');
    });
    it('should return badge-medium for intermediate', () => {
      expect(component.getDifficultyBadge('intermediate')).toBe('badge-medium');
    });
    it('should return badge-hard for other difficulties', () => {
      expect(component.getDifficultyBadge('advanced')).toBe('badge-hard');
    });
  });

  describe('formatRuntime()', () => {
    it('should format runtime in milliseconds', () => {
      expect(component.formatRuntime(42)).toBe('42ms');
    });
    it('should return em dash when ms is null', () => {
      expect(component.formatRuntime(null as unknown as number)).toBe('—');
    });
  });
});
