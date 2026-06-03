import { Injectable, inject, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';
import type { LearningProfile, LearningProfileUpdate } from '../models/learning-profile.model';

@Injectable({ providedIn: 'root' })
export class LearningProfileService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/users`;

  readonly currentProfile = signal<LearningProfile | null>(null);
  readonly loaded = signal(false);

  /** A signed-in learner who hasn't completed the wizard yet. */
  readonly needsOnboarding = computed(() => {
    const p = this.currentProfile();
    return this.loaded() && p != null && !p.onboarded;
  });

  /** Whether the "Personalize your path" CTA should be offered. */
  readonly canPersonalize = computed(() => {
    const p = this.currentProfile();
    return !p || !p.onboarded || (p.interests?.length ?? 0) === 0;
  });

  load(): Observable<LearningProfile> {
    return this.http.get<LearningProfile>(`${this.base}/me/learning-profile`).pipe(
      tap(profile => {
        this.currentProfile.set(profile);
        this.loaded.set(true);
      })
    );
  }

  save(payload: LearningProfileUpdate): Observable<LearningProfile> {
    return this.http.put<LearningProfile>(`${this.base}/me/learning-profile`, payload).pipe(
      tap(profile => {
        this.currentProfile.set(profile);
        this.loaded.set(true);
      })
    );
  }

  /** Clear cached profile (e.g. on logout). */
  reset(): void {
    this.currentProfile.set(null);
    this.loaded.set(false);
  }
}
