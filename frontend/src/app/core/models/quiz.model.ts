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
