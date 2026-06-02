import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import type {
  QuizQuestion,
  QuizAnswer,
  QuizSubmitRequest,
  QuizSubmitResponse,
  QuizMyAnswer,
} from '../models/quiz.model';

@Injectable({ providedIn: 'root' })
export class QuizService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/quiz`;

  getQuestions(lessonId: number): Observable<QuizQuestion[]> {
    return this.http.get<QuizQuestion[]>(`${this.base}/lessons/${lessonId}/questions`);
  }

  submit(lessonId: number, answers: QuizAnswer[]): Observable<QuizSubmitResponse> {
    const body: QuizSubmitRequest = { answers };
    return this.http.post<QuizSubmitResponse>(`${this.base}/lessons/${lessonId}/submit`, body);
  }

  getMyAnswers(lessonId: number): Observable<QuizMyAnswer[]> {
    return this.http.get<QuizMyAnswer[]>(`${this.base}/lessons/${lessonId}/my-answers`);
  }
}
