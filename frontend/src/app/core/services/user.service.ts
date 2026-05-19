import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';
import { User, UserUpdate } from '../models/types';
import { AuthService } from './auth.service';

@Injectable({ providedIn: 'root' })
export class UserService {
  private readonly http = inject(HttpClient);
  private readonly auth = inject(AuthService);
  private readonly base = `${environment.apiUrl}/users`;

  updateProfile(data: UserUpdate): Observable<User> {
    return this.http.patch<User>(`${this.base}/me`, data).pipe(
      tap((user) => this.auth.currentUser.set(user))
    );
  }
}
