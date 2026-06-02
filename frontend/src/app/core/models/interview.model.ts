export interface InterviewCategory {
  id: number;
  name: string;
  slug: string;
  description: string;
  icon: string;
  color: string;
  order_index: number;
  question_count: number;
}

export interface InterviewQuestion {
  id: number;
  question: string;
  answer: string; // markdown
  difficulty: 'easy' | 'medium' | 'hard';
  tags: string[];
  order_index: number;
}

export interface InterviewCategoryDetail extends InterviewCategory {
  questions: InterviewQuestion[];
}
