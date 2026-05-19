import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  CodeRunRequest,
  CodeRunResult,
  SubmissionCreate,
  Submission,
  SubmissionSummary,
} from '../models/types';

@Injectable({ providedIn: 'root' })
export class SubmissionService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/submissions`;

  runCode(req: CodeRunRequest): Observable<CodeRunResult> {
    return this.http.post<CodeRunResult>(`${this.base}/run`, req);
  }

  submit(req: SubmissionCreate): Observable<Submission> {
    return this.http.post<Submission>(`${this.base}`, req);
  }

  getMySubmissions(exerciseId?: number): Observable<SubmissionSummary[]> {
    let httpParams = new HttpParams();
    if (exerciseId != null) httpParams = httpParams.set('exercise_id', String(exerciseId));
    return this.http.get<SubmissionSummary[]>(`${this.base}/me`, { params: httpParams });
  }

  getSubmission(id: number): Observable<Submission> {
    return this.http.get<Submission>(`${this.base}/${id}`);
  }
}
