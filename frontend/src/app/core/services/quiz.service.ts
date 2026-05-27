import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

// ── Quiz interfaces (local to this file) ─────────────────────────────────────

export interface QuizQuestion {
  id: number;
  lesson_id: number;
  prompt: string;
  options: string[];
  order_index: number;
}

export interface QuizAnswer {
  question_id: number;
  selected_index: number;
}

export interface QuizSubmitRequest {
  answers: QuizAnswer[];
}

export interface QuizQuestionResult {
  question_id: number;
  selected_index: number;
  correct_index: number;
  is_correct: boolean;
  explanation: string;
}

export interface QuizSubmitResponse {
  total: number;
  correct: number;
  passed: boolean;
  results: QuizQuestionResult[];
}

export interface QuizMyAnswer {
  question_id: number;
  selected_index: number;
  is_correct: boolean;
}

// ── Service ───────────────────────────────────────────────────────────────────

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
