import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  Subject,
  Course,
  CourseTree,
  Lesson,
  ExerciseSummary,
  Exercise,
  LearningPath,
} from '../models/types';

@Injectable({ providedIn: 'root' })
export class CatalogService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/catalog`;

  getSubjects(): Observable<Subject[]> {
    return this.http.get<Subject[]>(`${this.base}/subjects`);
  }

  getSubject(slug: string): Observable<Subject> {
    return this.http.get<Subject>(`${this.base}/subjects/${slug}`);
  }

  getSubjectCourses(slug: string): Observable<Course[]> {
    return this.http.get<Course[]>(`${this.base}/subjects/${slug}/courses`);
  }

  getCourses(params?: { q?: string; difficulty?: string; subject_id?: number }): Observable<Course[]> {
    let httpParams = new HttpParams();
    if (params?.q) httpParams = httpParams.set('q', params.q);
    if (params?.difficulty) httpParams = httpParams.set('difficulty', params.difficulty);
    if (params?.subject_id != null) httpParams = httpParams.set('subject_id', String(params.subject_id));
    return this.http.get<Course[]>(`${this.base}/courses`, { params: httpParams });
  }

  getCourseTree(slug: string): Observable<CourseTree> {
    return this.http.get<CourseTree>(`${this.base}/courses/${slug}`);
  }

  getLesson(id: number): Observable<Lesson> {
    return this.http.get<Lesson>(`${this.base}/lessons/${id}`);
  }

  getExercises(params?: {
    difficulty?: string;
    language?: string;
    q?: string;
    limit?: number;
    offset?: number;
  }): Observable<ExerciseSummary[]> {
    let httpParams = new HttpParams();
    if (params?.difficulty) httpParams = httpParams.set('difficulty', params.difficulty);
    if (params?.language) httpParams = httpParams.set('language', params.language);
    if (params?.q) httpParams = httpParams.set('q', params.q);
    if (params?.limit != null) httpParams = httpParams.set('limit', String(params.limit));
    if (params?.offset != null) httpParams = httpParams.set('offset', String(params.offset));
    return this.http.get<ExerciseSummary[]>(`${this.base}/exercises`, { params: httpParams });
  }

  getExercise(slug: string): Observable<Exercise> {
    return this.http.get<Exercise>(`${this.base}/exercises/${slug}`);
  }

  getLearningPaths(): Observable<LearningPath[]> {
    return this.http.get<LearningPath[]>(`${this.base}/learning-paths`);
  }
}
