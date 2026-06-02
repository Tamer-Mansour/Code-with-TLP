import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import type {
  InterviewCategory,
  InterviewQuestion,
  InterviewCategoryDetail,
} from '../models/interview.model';

@Injectable({ providedIn: 'root' })
export class InterviewService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/interview`;

  getCategories(): Observable<InterviewCategory[]> {
    return this.http.get<InterviewCategory[]>(`${this.base}/categories`);
  }

  getCategoryBySlug(slug: string): Observable<InterviewCategoryDetail> {
    return this.http.get<InterviewCategoryDetail>(`${this.base}/categories/${slug}`);
  }

  searchQuestions(params?: {
    q?: string;
    category?: string;
    difficulty?: string;
  }): Observable<InterviewQuestion[]> {
    let httpParams = new HttpParams();
    if (params?.q)          httpParams = httpParams.set('q', params.q);
    if (params?.category)   httpParams = httpParams.set('category', params.category);
    if (params?.difficulty) httpParams = httpParams.set('difficulty', params.difficulty);
    return this.http.get<InterviewQuestion[]>(`${this.base}/questions`, { params: httpParams });
  }
}
