import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';
import { UserSettings, UserSettingsUpdate } from '../models/types';

const COLOR_MAP: Record<string, { rgb: string; dark: string; light: string }> = {
  blue:    { rgb: '59 130 246',  dark: '37 99 235',   light: '96 165 250' },
  green:   { rgb: '16 185 129',  dark: '5 150 105',   light: '52 211 153' },
  purple:  { rgb: '139 92 246',  dark: '124 58 237',  light: '167 139 250' },
  amber:   { rgb: '245 158 11',  dark: '217 119 6',   light: '252 211 77' },
  rose:    { rgb: '244 63 94',   dark: '225 29 72',   light: '251 113 133' },
  cyan:    { rgb: '6 182 212',   dark: '8 145 178',   light: '34 211 238' },
  slate:   { rgb: '100 116 139', dark: '71 85 105',   light: '148 163 184' },
  red:     { rgb: '239 68 68',   dark: '220 38 38',   light: '252 129 129' },
  orange:  { rgb: '249 115 22',  dark: '234 88 12',   light: '251 146 60' },
  yellow:  { rgb: '234 179 8',   dark: '202 138 4',   light: '250 204 21' },
  lime:    { rgb: '132 204 22',  dark: '101 163 13',  light: '163 230 53' },
  emerald: { rgb: '16 185 129',  dark: '5 150 105',   light: '110 231 183' },
  teal:    { rgb: '20 184 166',  dark: '13 148 136',  light: '94 234 212' },
  sky:     { rgb: '14 165 233',  dark: '2 132 199',   light: '125 211 252' },
  indigo:  { rgb: '99 102 241',  dark: '79 70 229',   light: '165 180 252' },
  violet:  { rgb: '139 92 246',  dark: '124 58 237',  light: '196 181 253' },
  pink:    { rgb: '236 72 153',  dark: '219 39 119',  light: '249 168 212' },
};

const GOOGLE_FONT_URLS: Record<string, string> = {
  'Inter': 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap',
  'Roboto': 'https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap',
  'Outfit': 'https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap',
  'JetBrains Mono': 'https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap',
  'Fira Code': 'https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&display=swap',
  'Poppins': 'https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap',
  'Nunito': 'https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;500;600;700&display=swap',
  'Open Sans': 'https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;500;600;700&display=swap',
  'Lato': 'https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&display=swap',
  'Montserrat': 'https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap',
  'Raleway': 'https://fonts.googleapis.com/css2?family=Raleway:wght@300;400;500;600;700&display=swap',
  'Ubuntu': 'https://fonts.googleapis.com/css2?family=Ubuntu:wght@300;400;500;700&display=swap',
  'Source Sans 3': 'https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@300;400;500;600;700&display=swap',
  'DM Sans': 'https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap',
  'Space Grotesk': 'https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap',
  'Tajawal': 'https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap',
  'Cairo': 'https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700;800&display=swap',
  'Amiri': 'https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap',
  'Noto Naskh Arabic': 'https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@400;500;600;700&display=swap',
  'El Messiri': 'https://fonts.googleapis.com/css2?family=El+Messiri:wght@400;500;600;700&display=swap',
  'Changa': 'https://fonts.googleapis.com/css2?family=Changa:wght@300;400;500;600;700;800&display=swap',
  'Readex Pro': 'https://fonts.googleapis.com/css2?family=Readex+Pro:wght@300;400;500;600;700&display=swap',
};

const FONT_CLASS_MAP: Record<string, string> = {
  'Inter': 'font-inter',
  'Roboto': 'font-roboto',
  'Outfit': 'font-outfit',
  'JetBrains Mono': 'font-jetbrains-mono',
  'Fira Code': 'font-fira-code',
  'Poppins': 'font-poppins',
  'Nunito': 'font-nunito',
  'Open Sans': 'font-open-sans',
  'Lato': 'font-lato',
  'Montserrat': 'font-montserrat',
  'Raleway': 'font-raleway',
  'Ubuntu': 'font-ubuntu',
  'Source Sans 3': 'font-source-sans-3',
  'DM Sans': 'font-dm-sans',
  'Space Grotesk': 'font-space-grotesk',
  'Tajawal': 'font-tajawal',
  'Cairo': 'font-cairo',
  'Amiri': 'font-amiri',
  'Noto Naskh Arabic': 'font-noto-naskh-arabic',
  'El Messiri': 'font-el-messiri',
  'Changa': 'font-changa',
  'Readex Pro': 'font-readex-pro',
};

function loadGoogleFont(family: string): void {
  const url = GOOGLE_FONT_URLS[family];
  if (!url) return;
  const existing = document.querySelector(`link[data-font="${family}"]`);
  if (existing) return;
  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = url;
  link.dataset['font'] = family;
  document.head.appendChild(link);
}

@Injectable({ providedIn: 'root' })
export class UserSettingsService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/users`;

  readonly currentSettings = signal<UserSettings | null>(null);
  readonly isDrawerOpen = signal(false);

  openDrawer(): void { this.isDrawerOpen.set(true); }
  closeDrawer(): void { this.isDrawerOpen.set(false); }

  load(): Observable<UserSettings> {
    return this.http.get<UserSettings>(`${this.base}/me/settings`).pipe(
      tap((settings) => {
        this.currentSettings.set(settings);
        if (settings) this.applySettings(settings);
      })
    );
  }

  update(payload: UserSettingsUpdate): Observable<UserSettings> {
    return this.http.patch<UserSettings>(`${this.base}/me/settings`, payload).pipe(
      tap((settings) => {
        this.currentSettings.set(settings);
        this.applySettings(settings);
      })
    );
  }

  applySettings(settings: UserSettings): void {
    const root = document.documentElement;

    const isDark = settings.theme === 'dark';
    root.classList.toggle('dark', isDark);
    localStorage.setItem('theme', settings.theme);

    const fontClassMap: Record<string, string> = FONT_CLASS_MAP;

    Object.values(fontClassMap).forEach((cls) => document.body.classList.remove(cls));
    const newClass = fontClassMap[settings.font_family];
    if (newClass) {
      document.body.classList.add(newClass);
      loadGoogleFont(settings.font_family);
    }

    const colors = COLOR_MAP[settings.color_scheme] || COLOR_MAP['blue'];
    root.style.setProperty('--color-brand-rgb', colors.rgb);
    root.style.setProperty('--color-brand-dark-rgb', colors.dark);
    root.style.setProperty('--color-brand-light-rgb', colors.light);

    root.dataset['profileLayout'] = settings.profile_layout;

    localStorage.setItem('color_scheme', settings.color_scheme);
  }
}
