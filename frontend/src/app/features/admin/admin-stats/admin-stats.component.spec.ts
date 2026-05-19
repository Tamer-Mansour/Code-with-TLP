import { TestBed, ComponentFixture } from '@angular/core/testing';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { NgClass, DecimalPipe } from '@angular/common';
import { of, throwError } from 'rxjs';
import {
  LucideAngularModule,
  RefreshCw, AlertTriangle,
  Users, GraduationCap, Shield, BookOpen, Code2, Send, CheckCircle2, Activity,
  Target, Library, CodeSquare,
} from 'lucide-angular';
import { AdminStatsComponent } from './admin-stats.component';
import { AdminService } from '../../../core/services/admin.service';
import { AdminStats } from '../../../core/models/types';

const mockStats: AdminStats = {
  users_total: 100,
  users_active: 80,
  students: 95,
  admins: 5,
  subjects: 10,
  courses: 25,
  courses_published: 20,
  lessons: 200,
  exercises: 150,
  exercises_published: 130,
  submissions: 500,
  submissions_accepted: 350,
};

describe('AdminStatsComponent', () => {
  let fixture: ComponentFixture<AdminStatsComponent>;
  let component: AdminStatsComponent;
  let mockAdminService: { getStats: ReturnType<typeof vi.fn> };

  beforeEach(async () => {
    mockAdminService = {
      getStats: vi.fn().mockReturnValue(of(mockStats)),
    };

    await TestBed.configureTestingModule({
      imports: [
        AdminStatsComponent,
        NgClass,
        DecimalPipe,
        LucideAngularModule.pick({
          RefreshCw, AlertTriangle,
          Users, GraduationCap, Shield, BookOpen, Code2, Send, CheckCircle2, Activity,
          Target, Library, CodeSquare,
        }),
      ],
      providers: [
        { provide: AdminService, useValue: mockAdminService },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(AdminStatsComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize stats as null', () => {
    expect(component.stats()).toBeNull();
  });

  it('should initialize loading as true', () => {
    expect(component.loading()).toBe(true);
  });

  it('should initialize error as false', () => {
    expect(component.error()).toBe(false);
  });

  it('should load stats on init', async () => {
    fixture.detectChanges();
    await fixture.whenStable();
    expect(component.stats()).toEqual(mockStats);
    expect(component.loading()).toBe(false);
    expect(component.error()).toBe(false);
  });

  it('should set error to true on load failure', async () => {
    mockAdminService.getStats.mockReturnValue(throwError(() => new Error('Server error')));
    fixture.detectChanges();
    await fixture.whenStable();
    expect(component.error()).toBe(true);
    expect(component.loading()).toBe(false);
    expect(component.stats()).toBeNull();
  });

  it('should call adminService.getStats on init', async () => {
    fixture.detectChanges();
    await fixture.whenStable();
    expect(mockAdminService.getStats).toHaveBeenCalledOnce();
  });

  describe('getStatValue()', () => {
    it('should return the correct stat value after loading', async () => {
      fixture.detectChanges();
      await fixture.whenStable();
      expect(component.getStatValue('users_total')).toBe(100);
      expect(component.getStatValue('students')).toBe(95);
      expect(component.getStatValue('admins')).toBe(5);
      expect(component.getStatValue('courses_published')).toBe(20);
      expect(component.getStatValue('exercises_published')).toBe(130);
      expect(component.getStatValue('submissions')).toBe(500);
      expect(component.getStatValue('submissions_accepted')).toBe(350);
      expect(component.getStatValue('users_active')).toBe(80);
    });

    it('should return 0 when stats is null', () => {
      expect(component.getStatValue('users_total')).toBe(0);
    });
  });

  describe('statCards', () => {
    it('should have 8 stat cards defined', () => {
      expect(component.statCards).toHaveLength(8);
    });

    it('should have a Total Users card', () => {
      const card = component.statCards.find(c => c.label === 'Total Users');
      expect(card).toBeDefined();
      expect(card?.key).toBe('users_total');
    });

    it('should have an Accepted card', () => {
      const card = component.statCards.find(c => c.label === 'Accepted');
      expect(card).toBeDefined();
      expect(card?.key).toBe('submissions_accepted');
    });

    it('each card should have label, key, icon, colorClass, bgClass', () => {
      for (const card of component.statCards) {
        expect(card.label).toBeTruthy();
        expect(card.key).toBeTruthy();
        expect(card.icon).toBeTruthy();
        expect(card.colorClass).toBeTruthy();
        expect(card.bgClass).toBeTruthy();
      }
    });
  });
});
