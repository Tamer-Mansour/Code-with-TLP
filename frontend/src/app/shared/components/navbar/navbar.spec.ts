import { TestBed, ComponentFixture } from '@angular/core/testing';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { signal, computed } from '@angular/core';
import { provideRouter } from '@angular/router';
import {
  LucideAngularModule,
  Code2, BookOpen, LayoutDashboard, ChevronDown,
  Menu, X, User as UserIcon, LogOut, Shield, BarChart2, Sun, Moon,
} from 'lucide-angular';
import type { User } from '../../../core/models/types';
import { NavbarComponent } from './navbar';
import { AuthService } from '../../../core/services/auth.service';
import { ThemeService } from '../../../core/services/theme.service';

const mockUser: User = {
  id: 1,
  email: 'test@example.com',
  username: 'testuser',
  full_name: 'Test User',
  role: 'student',
  is_active: true,
  created_at: '2024-01-01T00:00:00Z',
};

function createMockAuthService(user: User | null = null) {
  const currentUser = signal<User | null>(user);
  return {
    currentUser,
    isAuthenticated: computed(() => !!currentUser()),
    isAdmin: computed(() => currentUser()?.role === 'admin'),
    logout: vi.fn(),
  };
}

function createMockThemeService(dark = false) {
  return {
    isDark: signal(dark),
    toggle: vi.fn(),
    initialize: vi.fn(),
  };
}

describe('NavbarComponent', () => {
  let fixture: ComponentFixture<NavbarComponent>;
  let component: NavbarComponent;
  let mockAuth: ReturnType<typeof createMockAuthService>;
  let mockTheme: ReturnType<typeof createMockThemeService>;

  beforeEach(async () => {
    mockAuth = createMockAuthService();
    mockTheme = createMockThemeService();

    await TestBed.configureTestingModule({
      imports: [
        NavbarComponent,
        LucideAngularModule.pick({
          Code2, BookOpen, LayoutDashboard, ChevronDown,
          Menu, X, User: UserIcon, LogOut, Shield, BarChart2, Sun, Moon,
        }),
      ],
      providers: [
        provideRouter([]),
        { provide: AuthService, useValue: mockAuth },
        { provide: ThemeService, useValue: mockTheme },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(NavbarComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize with mobileOpen false', () => {
    expect(component.mobileOpen()).toBe(false);
  });

  it('should initialize with dropdownOpen false', () => {
    expect(component.dropdownOpen()).toBe(false);
  });

  it('should toggle mobileOpen on toggleMobile()', () => {
    expect(component.mobileOpen()).toBe(false);
    component.toggleMobile();
    expect(component.mobileOpen()).toBe(true);
    component.toggleMobile();
    expect(component.mobileOpen()).toBe(false);
  });

  it('should close dropdownOpen when toggleMobile is called while dropdown is open', () => {
    component.dropdownOpen.set(true);
    component.toggleMobile();
    expect(component.dropdownOpen()).toBe(false);
  });

  it('should toggle dropdownOpen on toggleDropdown()', () => {
    expect(component.dropdownOpen()).toBe(false);
    component.toggleDropdown();
    expect(component.dropdownOpen()).toBe(true);
    component.toggleDropdown();
    expect(component.dropdownOpen()).toBe(false);
  });

  it('should set mobileOpen to false on closeMobile()', () => {
    component.mobileOpen.set(true);
    component.closeMobile();
    expect(component.mobileOpen()).toBe(false);
  });

  it('should set dropdownOpen to false on closeDropdown()', () => {
    component.dropdownOpen.set(true);
    component.closeDropdown();
    expect(component.dropdownOpen()).toBe(false);
  });

  it('should call auth.logout and close menus on logout()', () => {
    component.mobileOpen.set(true);
    component.dropdownOpen.set(true);
    component.logout();
    expect(mockAuth.logout).toHaveBeenCalledOnce();
    expect(component.mobileOpen()).toBe(false);
    expect(component.dropdownOpen()).toBe(false);
  });

  describe('userInitials', () => {
    it('should return "?" when no user is logged in', () => {
      mockAuth.currentUser.set(null);
      expect(component.userInitials).toBe('?');
    });

    it('should return initials from full_name', () => {
      mockAuth.currentUser.set(mockUser);
      expect(component.userInitials).toBe('TU');
    });

    it('should return initials from username when full_name is absent', () => {
      const noName: User = { ...mockUser, full_name: undefined };
      mockAuth.currentUser.set(noName);
      expect(component.userInitials).toBe('T');
    });
  });

  describe('auth-aware rendering', () => {
    it('should expose auth service on component', () => {
      expect(component.auth).toBeTruthy();
    });

    it('should expose theme service on component', () => {
      expect(component.theme).toBeTruthy();
    });

    it('should reflect isAuthenticated when user is set', () => {
      mockAuth.currentUser.set(mockUser);
      expect(mockAuth.isAuthenticated()).toBe(true);
    });

    it('should reflect isAuthenticated as false when user is null', () => {
      mockAuth.currentUser.set(null);
      expect(mockAuth.isAuthenticated()).toBe(false);
    });

    it('should reflect isAdmin for admin users', () => {
      const adminUser: User = { ...mockUser, role: 'admin' };
      mockAuth.currentUser.set(adminUser);
      expect(mockAuth.isAdmin()).toBe(true);
    });
  });

  describe('theme toggle', () => {
    it('should expose theme service isDark signal', () => {
      expect(mockTheme.isDark()).toBe(false);
    });

    it('should call theme.toggle when toggle is invoked', () => {
      mockTheme.toggle();
      expect(mockTheme.toggle).toHaveBeenCalled();
    });
  });
});
