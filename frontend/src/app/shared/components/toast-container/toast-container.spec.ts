import { TestBed, ComponentFixture } from '@angular/core/testing';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { signal } from '@angular/core';
import { NgClass } from '@angular/common';
import { ToastContainerComponent } from './toast-container';
import { ToastService, Toast } from '../../../core/services/toast.service';

function makeToast(overrides: Partial<Toast> = {}): Toast {
  return {
    id: 'toast-1',
    type: 'info',
    message: 'Test message',
    duration: 4000,
    ...overrides,
  };
}

describe('ToastContainerComponent', () => {
  let fixture: ComponentFixture<ToastContainerComponent>;
  let component: ToastContainerComponent;
  let toastsSignal: ReturnType<typeof signal<Toast[]>>;
  let mockToastService: { toasts: ReturnType<typeof signal<Toast[]>>; remove: ReturnType<typeof vi.fn> };

  beforeEach(async () => {
    toastsSignal = signal<Toast[]>([]);
    mockToastService = {
      toasts: toastsSignal,
      remove: vi.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [ToastContainerComponent, NgClass],
      providers: [
        { provide: ToastService, useValue: mockToastService },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ToastContainerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should return empty toasts initially', () => {
    expect(component.toasts).toHaveLength(0);
  });

  it('should reflect toasts from service', () => {
    const toast = makeToast();
    toastsSignal.set([toast]);
    fixture.detectChanges();
    expect(component.toasts).toHaveLength(1);
    expect(component.toasts[0]).toEqual(toast);
  });

  it('should call toastService.remove when dismiss() is called', () => {
    component.dismiss('toast-1');
    expect(mockToastService.remove).toHaveBeenCalledWith('toast-1');
  });

  it('should return correct trackById value', () => {
    const toast = makeToast({ id: 'abc-123' });
    expect(component.trackById(0, toast)).toBe('abc-123');
  });

  describe('borderColor()', () => {
    it('should return border-l-green-500 for success', () => {
      expect(component.borderColor('success')).toBe('border-l-green-500');
    });
    it('should return border-l-red-500 for error', () => {
      expect(component.borderColor('error')).toBe('border-l-red-500');
    });
    it('should return border-l-amber-500 for warning', () => {
      expect(component.borderColor('warning')).toBe('border-l-amber-500');
    });
    it('should return border-l-brand for info', () => {
      expect(component.borderColor('info')).toBe('border-l-brand');
    });
  });

  describe('iconColor()', () => {
    it('should return text-green-400 for success', () => {
      expect(component.iconColor('success')).toBe('text-green-400');
    });
    it('should return text-red-400 for error', () => {
      expect(component.iconColor('error')).toBe('text-red-400');
    });
    it('should return text-amber-400 for warning', () => {
      expect(component.iconColor('warning')).toBe('text-amber-400');
    });
    it('should return text-brand-light for info', () => {
      expect(component.iconColor('info')).toBe('text-brand-light');
    });
  });

  describe('progressColor()', () => {
    it('should return bg-green-500 for success', () => {
      expect(component.progressColor('success')).toBe('bg-green-500');
    });
    it('should return bg-red-500 for error', () => {
      expect(component.progressColor('error')).toBe('bg-red-500');
    });
    it('should return bg-amber-500 for warning', () => {
      expect(component.progressColor('warning')).toBe('bg-amber-500');
    });
    it('should return bg-brand for info', () => {
      expect(component.progressColor('info')).toBe('bg-brand');
    });
  });

  describe('label()', () => {
    it('should return Success for success', () => {
      expect(component.label('success')).toBe('Success');
    });
    it('should return Error for error', () => {
      expect(component.label('error')).toBe('Error');
    });
    it('should return Warning for warning', () => {
      expect(component.label('warning')).toBe('Warning');
    });
    it('should return Info for info', () => {
      expect(component.label('info')).toBe('Info');
    });
  });

  describe('animDuration()', () => {
    it('should return the toast duration as a CSS string', () => {
      const toast = makeToast({ duration: 3000 });
      expect(component.animDuration(toast)).toBe('3000ms');
    });

    it('should use 4000ms when duration is undefined', () => {
      const toast = makeToast({ duration: undefined });
      expect(component.animDuration(toast)).toBe('4000ms');
    });
  });
});
