import {
  Component,
  OnInit,
  inject,
  signal,
  computed,
  ChangeDetectionStrategy,
  ViewEncapsulation,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NgClass } from '@angular/common';
import { LucideAngularModule } from 'lucide-angular';
import { UserSettingsService } from '../../../core/services/user-settings.service';
import { ToastService } from '../../../core/services/toast.service';
import type { ColorScheme, FontFamily, ThemeMode, UserSettingsUpdate } from '../../../core/models/types';

interface ColorOption {
  value: ColorScheme;
  label: string;
  hex: string;
}

interface FontOption {
  value: FontFamily;
  label: string;
  preview: string;
}

const COLOR_OPTIONS: ColorOption[] = [
  { value: 'red',     label: 'Red',     hex: '#ef4444' },
  { value: 'orange',  label: 'Orange',  hex: '#f97316' },
  { value: 'amber',   label: 'Amber',   hex: '#f59e0b' },
  { value: 'yellow',  label: 'Yellow',  hex: '#eab308' },
  { value: 'lime',    label: 'Lime',    hex: '#84cc16' },
  { value: 'green',   label: 'Green',   hex: '#22c55e' },
  { value: 'emerald', label: 'Emerald', hex: '#10b981' },
  { value: 'teal',    label: 'Teal',    hex: '#14b8a6' },
  { value: 'cyan',    label: 'Cyan',    hex: '#06b6d4' },
  { value: 'sky',     label: 'Sky',     hex: '#0ea5e9' },
  { value: 'blue',    label: 'Blue',    hex: '#3b82f6' },
  { value: 'indigo',  label: 'Indigo',  hex: '#6366f1' },
  { value: 'violet',  label: 'Violet',  hex: '#8b5cf6' },
  { value: 'purple',  label: 'Purple',  hex: '#a855f7' },
  { value: 'pink',    label: 'Pink',    hex: '#ec4899' },
  { value: 'rose',    label: 'Rose',    hex: '#f43f5e' },
  { value: 'slate',   label: 'Slate',   hex: '#64748b' },
];

const FONT_OPTIONS: FontOption[] = [
  { value: 'Inter', label: 'Inter', preview: 'The quick brown fox jumps over the lazy dog.' },
  { value: 'Roboto', label: 'Roboto', preview: 'The quick brown fox jumps over the lazy dog.' },
  { value: 'Outfit', label: 'Outfit', preview: 'The quick brown fox jumps over the lazy dog.' },
  { value: 'Poppins', label: 'Poppins', preview: 'The quick brown fox jumps over the lazy dog.' },
  { value: 'Nunito', label: 'Nunito', preview: 'The quick brown fox jumps over the lazy dog.' },
  { value: 'Open Sans', label: 'Open Sans', preview: 'The quick brown fox jumps over the lazy dog.' },
  { value: 'Lato', label: 'Lato', preview: 'The quick brown fox jumps over the lazy dog.' },
  { value: 'Montserrat', label: 'Montserrat', preview: 'The quick brown fox jumps over the lazy dog.' },
  { value: 'Raleway', label: 'Raleway', preview: 'The quick brown fox jumps over the lazy dog.' },
  { value: 'Ubuntu', label: 'Ubuntu', preview: 'The quick brown fox jumps over the lazy dog.' },
  { value: 'Source Sans 3', label: 'Source Sans 3', preview: 'The quick brown fox jumps over the lazy dog.' },
  { value: 'DM Sans', label: 'DM Sans', preview: 'The quick brown fox jumps over the lazy dog.' },
  { value: 'Space Grotesk', label: 'Space Grotesk', preview: 'The quick brown fox jumps over the lazy dog.' },
  { value: 'Tajawal', label: 'Tajawal (عربي)', preview: 'الثعلب البني السريع يقفز فوق الكلب الكسول.' },
  { value: 'Cairo', label: 'Cairo (عربي)', preview: 'الثعلب البني السريع يقفز فوق الكلب الكسول.' },
  { value: 'Amiri', label: 'Amiri (عربي)', preview: 'الثعلب البني السريع يقفز فوق الكلب الكسول.' },
  { value: 'Noto Naskh Arabic', label: 'Noto Naskh', preview: 'الثعلب البني السريع يقفز فوق الكلب الكسول.' },
  { value: 'El Messiri', label: 'El Messiri (عربي)', preview: 'الثعلب البني السريع يقفز فوق الكلب الكسول.' },
  { value: 'Changa', label: 'Changa (عربي)', preview: 'الثعلب البني السريع يقفز فوق الكلب الكسول.' },
  { value: 'Readex Pro', label: 'Readex Pro', preview: 'The quick brown fox jumps over the lazy dog.' },
  { value: 'JetBrains Mono', label: 'JetBrains Mono', preview: 'const fn = () => "monospace"' },
  { value: 'Fira Code', label: 'Fira Code', preview: 'const fn = () => "ligatures"' },
];

@Component({
  selector: 'app-personalization',
  standalone: true,
  templateUrl: './personalization.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  encapsulation: ViewEncapsulation.None,
  imports: [FormsModule, NgClass, LucideAngularModule],
})
export class PersonalizationComponent implements OnInit {
  readonly settingsService = inject(UserSettingsService);
  private readonly toast = inject(ToastService);

  readonly COLOR_OPTIONS = COLOR_OPTIONS;
  readonly FONT_OPTIONS = FONT_OPTIONS;

  readonly settings = this.settingsService.currentSettings;
  readonly saving = signal(false);
  readonly backdropUrlInput = signal('');

  readonly previewUrl = computed(() => {
    const input = this.backdropUrlInput().trim();
    if (input) return input;
    return this.settings()?.background_image_url ?? '';
  });

  ngOnInit(): void {
    this.backdropUrlInput.set(this.settings()?.background_image_url ?? '');
  }

  close(): void {
    this.settingsService.closeDrawer();
  }

  setTheme(mode: ThemeMode): void {
    if (this.saving()) return;
    this.saving.set(true);
    this.settingsService.update({ theme: mode }).subscribe({
      next: () => {
        this.saving.set(false);
        this.toast.success(`Theme switched to ${mode} mode`);
      },
      error: () => {
        this.saving.set(false);
        this.toast.error('Failed to update theme');
      },
    });
  }

  setColorScheme(scheme: ColorScheme): void {
    if (this.saving()) return;
    this.saving.set(true);
    this.settingsService.update({ color_scheme: scheme }).subscribe({
      next: () => {
        this.saving.set(false);
        this.toast.success(`Color scheme changed to ${scheme}`);
      },
      error: () => {
        this.saving.set(false);
        this.toast.error('Failed to update color scheme');
      },
    });
  }

  setFontFamily(family: FontFamily): void {
    if (this.saving()) return;
    this.saving.set(true);
    this.settingsService.update({ font_family: family }).subscribe({
      next: () => {
        this.saving.set(false);
        this.toast.success(`Font changed to ${family}`);
      },
      error: () => {
        this.saving.set(false);
        this.toast.error('Failed to update font');
      },
    });
  }

  saveBackgroundUrl(): void {
    if (this.saving()) return;
    const url = this.backdropUrlInput().trim();
    if (url && !url.match(/^https?:\/\/.+/)) {
      this.toast.error('Please enter a valid URL starting with http:// or https://');
      return;
    }
    this.saving.set(true);
    this.settingsService.update({ background_image_url: url || '' }).subscribe({
      next: () => {
        this.saving.set(false);
        this.toast.success('Backdrop image saved');
      },
      error: () => {
        this.saving.set(false);
        this.toast.error('Failed to save backdrop image');
      },
    });
  }

  clearBackgroundUrl(): void {
    if (this.saving()) return;
    this.saving.set(true);
    this.settingsService.update({ background_image_url: '' }).subscribe({
      next: () => {
        this.saving.set(false);
        this.backdropUrlInput.set('');
        this.toast.success('Backdrop image removed');
      },
      error: () => {
        this.saving.set(false);
        this.toast.error('Failed to remove backdrop image');
      },
    });
  }
}
