import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Enrollment, LessonProgress } from '../models/types';

@Injectable({ providedIn: 'root' })
export class ProgressService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/progress`;

  enroll(courseId: number): Observable<Enrollment> {
    return this.http.post<Enrollment>(`${this.base}/enroll/${courseId}`, {});
  }

  unenroll(courseId: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/enroll/${courseId}`);
  }

  getMyEnrollments(): Observable<Enrollment[]> {
    return this.http.get<Enrollment[]>(`${this.base}/enrollments`);
  }

  getLessonProgress(lessonId: number): Observable<LessonProgress> {
    return this.http.get<LessonProgress>(`${this.base}/lessons/${lessonId}`);
  }

  setLessonProgress(lessonId: number, status: string): Observable<LessonProgress> {
    return this.http.put<LessonProgress>(`${this.base}/lessons/${lessonId}`, { status });
  }

  getCourseProgress(courseId: number): Observable<LessonProgress[]> {
    return this.http.get<LessonProgress[]>(`${this.base}/course/${courseId}/lessons`);
  }
}
