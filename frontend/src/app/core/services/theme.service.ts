import { Injectable, signal } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  readonly isDark = signal<boolean>(false);

  initialize(): void {
    const stored = localStorage.getItem('theme');
    const dark = stored === 'dark';
    this.isDark.set(dark);
    document.documentElement.classList.toggle('dark', dark);
  }

  toggle(): void {
    const next = !this.isDark();
    this.isDark.set(next);
    document.documentElement.classList.toggle('dark', next);
    localStorage.setItem('theme', next ? 'dark' : 'light');
  }
}
