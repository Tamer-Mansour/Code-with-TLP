import { TestBed } from '@angular/core/testing';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { ThemeService } from './theme.service';

// Stub localStorage since jsdom may not provide it in this test environment
const localStorageStub: Record<string, string> = {};
const mockLocalStorage = {
  getItem: (key: string) => localStorageStub[key] ?? null,
  setItem: (key: string, value: string) => { localStorageStub[key] = value; },
  removeItem: (key: string) => { delete localStorageStub[key]; },
  clear: () => { Object.keys(localStorageStub).forEach(k => delete localStorageStub[k]); },
};

describe('ThemeService', () => {
  let service: ThemeService;

  beforeEach(() => {
    vi.stubGlobal('localStorage', mockLocalStorage);
    mockLocalStorage.clear();
    document.documentElement.classList.remove('dark');
    TestBed.resetTestingModule();
    TestBed.configureTestingModule({});
    service = TestBed.inject(ThemeService);
    service.isDark.set(false);
  });

  afterEach(() => {
    mockLocalStorage.clear();
    document.documentElement.classList.remove('dark');
    vi.unstubAllGlobals();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should have isDark signal initialized to false', () => {
    expect(service.isDark()).toBe(false);
  });

  describe('initialize()', () => {
    it('should set isDark to false when no theme is stored', () => {
      mockLocalStorage.removeItem('theme');
      service.initialize();
      expect(service.isDark()).toBe(false);
    });

    it('should set isDark to true when stored theme is "dark"', () => {
      mockLocalStorage.setItem('theme', 'dark');
      service.initialize();
      expect(service.isDark()).toBe(true);
    });

    it('should set isDark to false when stored theme is "light"', () => {
      mockLocalStorage.setItem('theme', 'light');
      service.initialize();
      expect(service.isDark()).toBe(false);
    });

    it('should add "dark" class to documentElement when theme is dark', () => {
      mockLocalStorage.setItem('theme', 'dark');
      service.initialize();
      expect(document.documentElement.classList.contains('dark')).toBe(true);
    });

    it('should not add "dark" class to documentElement when theme is light', () => {
      mockLocalStorage.setItem('theme', 'light');
      service.initialize();
      expect(document.documentElement.classList.contains('dark')).toBe(false);
    });
  });

  describe('toggle()', () => {
    it('should switch isDark from false to true', () => {
      service.isDark.set(false);
      service.toggle();
      expect(service.isDark()).toBe(true);
    });

    it('should switch isDark from true to false', () => {
      service.isDark.set(true);
      service.toggle();
      expect(service.isDark()).toBe(false);
    });

    it('should persist "dark" to localStorage when toggling on', () => {
      service.isDark.set(false);
      service.toggle();
      expect(mockLocalStorage.getItem('theme')).toBe('dark');
    });

    it('should persist "light" to localStorage when toggling off', () => {
      service.isDark.set(true);
      service.toggle();
      expect(mockLocalStorage.getItem('theme')).toBe('light');
    });

    it('should add dark class to documentElement when toggling on', () => {
      document.documentElement.classList.remove('dark');
      service.isDark.set(false);
      service.toggle();
      expect(document.documentElement.classList.contains('dark')).toBe(true);
    });

    it('should remove dark class from documentElement when toggling off', () => {
      document.documentElement.classList.add('dark');
      service.isDark.set(true);
      service.toggle();
      expect(document.documentElement.classList.contains('dark')).toBe(false);
    });

    it('should toggle back and forth correctly', () => {
      service.isDark.set(false);
      service.toggle();
      expect(service.isDark()).toBe(true);
      service.toggle();
      expect(service.isDark()).toBe(false);
      expect(mockLocalStorage.getItem('theme')).toBe('light');
    });
  });
});
