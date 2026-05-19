import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  AdminStats,
  User,
  Course,
  Subject,
  SubmissionSummary,
} from '../models/types';

@Injectable({ providedIn: 'root' })
export class AdminService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/admin`;

  // ── Stats ─────────────────────────────────────────────────

  getStats(): Observable<AdminStats> {
    return this.http.get<AdminStats>(`${this.base}/stats`);
  }

  // ── Users ─────────────────────────────────────────────────

  getUsers(params?: { role?: string; q?: string; limit?: number }): Observable<User[]> {
    let httpParams = new HttpParams();
    if (params?.role) httpParams = httpParams.set('role', params.role);
    if (params?.q) httpParams = httpParams.set('q', params.q);
    if (params?.limit != null) httpParams = httpParams.set('limit', String(params.limit));
    return this.http.get<User[]>(`${this.base}/users`, { params: httpParams });
  }

  updateUser(id: number, data: Partial<User & { password?: string }>): Observable<User> {
    return this.http.patch<User>(`${this.base}/users/${id}`, data);
  }

  deleteUser(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/users/${id}`);
  }

  // ── Courses ───────────────────────────────────────────────

  getCourses(): Observable<Course[]> {
    return this.http.get<Course[]>(`${this.base}/courses`);
  }

  createCourse(data: any): Observable<Course> {
    return this.http.post<Course>(`${this.base}/courses`, data);
  }

  updateCourse(id: number, data: any): Observable<Course> {
    return this.http.patch<Course>(`${this.base}/courses/${id}`, data);
  }

  deleteCourse(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/courses/${id}`);
  }

  // ── Exercises ─────────────────────────────────────────────

  getExercises(): Observable<any[]> {
    return this.http.get<any[]>(`${this.base}/exercises`);
  }

  createExercise(data: any): Observable<any> {
    return this.http.post<any>(`${this.base}/exercises`, data);
  }

  updateExercise(id: number, data: any): Observable<any> {
    return this.http.patch<any>(`${this.base}/exercises/${id}`, data);
  }

  deleteExercise(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/exercises/${id}`);
  }

  // ── Submissions ───────────────────────────────────────────

  getSubmissions(params?: any): Observable<SubmissionSummary[]> {
    let httpParams = new HttpParams();
    if (params) {
      Object.keys(params).forEach((key) => {
        if (params[key] != null) httpParams = httpParams.set(key, String(params[key]));
      });
    }
    return this.http.get<SubmissionSummary[]>(`${this.base}/submissions`, { params: httpParams });
  }

  // ── Subjects ─────────────────────────────────────────────

  createSubject(data: any): Observable<Subject> {
    return this.http.post<Subject>(`${this.base}/subjects`, data);
  }

  updateSubject(id: number, data: any): Observable<Subject> {
    return this.http.patch<Subject>(`${this.base}/subjects/${id}`, data);
  }

  // ── Modules ───────────────────────────────────────────────

  createModule(data: any): Observable<any> {
    return this.http.post<any>(`${this.base}/modules`, data);
  }

  // ── Lessons ───────────────────────────────────────────────

  createLesson(data: any): Observable<any> {
    return this.http.post<any>(`${this.base}/lessons`, data);
  }

  // ── Test Cases ────────────────────────────────────────────

  addTestCase(exerciseId: number, data: any): Observable<any> {
    return this.http.post<any>(`${this.base}/exercises/${exerciseId}/test-cases`, data);
  }
}
