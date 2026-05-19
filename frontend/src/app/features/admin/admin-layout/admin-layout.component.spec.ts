import { TestBed, ComponentFixture } from '@angular/core/testing';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { signal, computed } from '@angular/core';
import { provideRouter } from '@angular/router';
import {
  LucideAngularModule,
  Shield, ArrowLeft, LogOut,
  BarChart2, Users, BookOpen, Code2, Send,
} from 'lucide-angular';
import { AdminLayoutComponent } from './admin-layout.component';
import { AuthService } from '../../../core/services/auth.service';

describe('AdminLayoutComponent', () => {
  let fixture: ComponentFixture<AdminLayoutComponent>;
  let component: AdminLayoutComponent;
  let mockAuth: {
    currentUser: ReturnType<typeof signal>;
    isAuthenticated: ReturnType<typeof computed>;
    isAdmin: ReturnType<typeof computed>;
    logout: ReturnType<typeof vi.fn>;
  };

  beforeEach(async () => {
    const currentUser = signal({
      id: 1, email: 'admin@test.com', username: 'admin',
      role: 'admin' as const, is_active: true, created_at: '2024-01-01T00:00:00Z',
    });
    mockAuth = {
      currentUser,
      isAuthenticated: computed(() => true),
      isAdmin: computed(() => true),
      logout: vi.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [
        AdminLayoutComponent,
        LucideAngularModule.pick({
          Shield, ArrowLeft, LogOut,
          BarChart2, Users, BookOpen, Code2, Send,
        }),
      ],
      providers: [
        provideRouter([]),
        { provide: AuthService, useValue: mockAuth },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(AdminLayoutComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize sidebarOpen as true', () => {
    expect(component.sidebarOpen()).toBe(true);
  });

  it('should toggle sidebarOpen on toggleSidebar()', () => {
    expect(component.sidebarOpen()).toBe(true);
    component.toggleSidebar();
    expect(component.sidebarOpen()).toBe(false);
    component.toggleSidebar();
    expect(component.sidebarOpen()).toBe(true);
  });

  it('should call auth.logout on logout()', () => {
    component.logout();
    expect(mockAuth.logout).toHaveBeenCalledOnce();
  });

  it('should have correct nav items defined', () => {
    expect(component.navItems).toHaveLength(5);
  });

  it('should have Dashboard nav item pointing to /admin/stats', () => {
    const dashItem = component.navItems.find(n => n.label === 'Dashboard');
    expect(dashItem).toBeDefined();
    expect(dashItem?.route).toBe('/admin/stats');
  });

  it('should have Users nav item pointing to /admin/users', () => {
    const usersItem = component.navItems.find(n => n.label === 'Users');
    expect(usersItem).toBeDefined();
    expect(usersItem?.route).toBe('/admin/users');
  });

  it('should have Courses nav item pointing to /admin/courses', () => {
    const coursesItem = component.navItems.find(n => n.label === 'Courses');
    expect(coursesItem).toBeDefined();
    expect(coursesItem?.route).toBe('/admin/courses');
  });

  it('should have Exercises nav item pointing to /admin/exercises', () => {
    const exercisesItem = component.navItems.find(n => n.label === 'Exercises');
    expect(exercisesItem).toBeDefined();
    expect(exercisesItem?.route).toBe('/admin/exercises');
  });

  it('should have Submissions nav item pointing to /admin/submissions', () => {
    const submissionsItem = component.navItems.find(n => n.label === 'Submissions');
    expect(submissionsItem).toBeDefined();
    expect(submissionsItem?.route).toBe('/admin/submissions');
  });

  it('each nav item should have a label, icon, and route', () => {
    for (const item of component.navItems) {
      expect(item.label).toBeTruthy();
      expect(item.icon).toBeTruthy();
      expect(item.route).toMatch(/^\/admin\//);
    }
  });
});
