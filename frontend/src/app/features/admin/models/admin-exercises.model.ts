import type { SupportedLanguage } from '../../../core/models/types';

export interface ExerciseRow {
  id: number;
  title: string;
  slug: string;
  difficulty: string;
  supported_languages: SupportedLanguage[];
  is_published: boolean;
}
