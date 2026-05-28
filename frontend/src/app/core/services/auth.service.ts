import { Injectable, inject, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap, switchMap, catchError, from, EMPTY } from 'rxjs';
import { environment } from '../../../environments/environment';
import { User, TokenPair, LoginRequest, RegisterRequest } from '../models/types';
import { UserSettingsService } from './user-settings.service';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  private readonly userSettings = inject(UserSettingsService);
  private readonly base = `${environment.apiUrl}/auth`;

  readonly currentUser = signal<User | null>(null);
  readonly isAuthenticated = computed(() => !!this.currentUser());
  readonly isAdmin = computed(() => this.currentUser()?.role === 'admin');

  login(req: LoginRequest): Observable<TokenPair> {
    return this.http.post<TokenPair>(`${this.base}/login`, req).pipe(
      tap((tokens) => {
        localStorage.setItem('access_token', tokens.access_token);
        localStorage.setItem('refresh_token', tokens.refresh_token);
      }),
      tap(() => {
        this.loadUser().subscribe();
      }),
      tap(() => {
        this.userSettings.load().subscribe();
      })
    );
  }

  register(req: RegisterRequest): Observable<User> {
    return this.http.post<User>(`${this.base}/register`, req);
  }

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.currentUser.set(null);
    this.router.navigate(['/login']);
  }

  loadUser(): Observable<User> {
    return this.http.get<User>(`${this.base}/me`).pipe(
      tap((user) => this.currentUser.set(user))
    );
  }

  refreshToken(): Observable<TokenPair> {
    const refresh_token = localStorage.getItem('refresh_token');
    return this.http.post<TokenPair>(`${this.base}/refresh`, { refresh_token }).pipe(
      tap((tokens) => {
        localStorage.setItem('access_token', tokens.access_token);
        localStorage.setItem('refresh_token', tokens.refresh_token);
      })
    );
  }

  getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  initialize(): Promise<void> {
    const accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
      return Promise.resolve();
    }

    return new Promise<void>((resolve) => {
      this.loadUser().subscribe({
        next: () => {
          this.userSettings.load().subscribe({ next: () => resolve(), error: () => resolve() });
        },
        error: () => {
          this.refreshToken().pipe(
            switchMap(() => this.loadUser()),
            catchError(() => {
              localStorage.removeItem('access_token');
              localStorage.removeItem('refresh_token');
              return EMPTY;
            })
          ).subscribe({
            next: () => {
              this.userSettings.load().subscribe({ next: () => resolve(), error: () => resolve() });
            },
            error: () => resolve(),
            complete: () => resolve(),
          });
        },
      });
    });
  }
}
