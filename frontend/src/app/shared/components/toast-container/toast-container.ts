import {
  Component,
  inject,
  ChangeDetectionStrategy,
  signal,
  OnInit,
} from '@angular/core';
import { NgClass } from '@angular/common';
import { ToastService, Toast } from '../../../core/services/toast.service';

@Component({
  selector: 'app-toast-container',
  standalone: true,
  imports: [NgClass],
  templateUrl: './toast-container.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ToastContainerComponent {
  readonly toastService = inject(ToastService);

  get toasts() {
    return this.toastService.toasts();
  }

  dismiss(id: string): void {
    this.toastService.remove(id);
  }

  trackById(_: number, toast: Toast): string {
    return toast.id;
  }

  borderColor(type: Toast['type']): string {
    switch (type) {
      case 'success': return 'border-l-green-500';
      case 'error':   return 'border-l-red-500';
      case 'warning': return 'border-l-amber-500';
      case 'info':    return 'border-l-brand';
      default:        return 'border-l-brand';
    }
  }

  iconColor(type: Toast['type']): string {
    switch (type) {
      case 'success': return 'text-green-400';
      case 'error':   return 'text-red-400';
      case 'warning': return 'text-amber-400';
      case 'info':    return 'text-brand-light';
      default:        return 'text-brand-light';
    }
  }

  progressColor(type: Toast['type']): string {
    switch (type) {
      case 'success': return 'bg-green-500';
      case 'error':   return 'bg-red-500';
      case 'warning': return 'bg-amber-500';
      case 'info':    return 'bg-brand';
      default:        return 'bg-brand';
    }
  }

  icon(type: Toast['type']): string {
    switch (type) {
      case 'success': return 'M5 13l4 4L19 7';
      case 'error':   return 'M6 18L18 6M6 6l12 12';
      case 'warning': return 'M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z';
      case 'info':    return 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z';
      default:        return 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z';
    }
  }

  label(type: Toast['type']): string {
    switch (type) {
      case 'success': return 'Success';
      case 'error':   return 'Error';
      case 'warning': return 'Warning';
      case 'info':    return 'Info';
      default:        return 'Info';
    }
  }

  animDuration(toast: Toast): string {
    return `${toast.duration ?? 4000}ms`;
  }
}
