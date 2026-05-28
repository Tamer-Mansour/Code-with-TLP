// ── Auth ──────────────────────────────────────────────────
export interface LoginRequest {
  identifier: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// ── Users ─────────────────────────────────────────────────
export type UserRole = 'student' | 'admin';

export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  avatar_url?: string;
  bio?: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface UserUpdate {
  full_name?: string;
  avatar_url?: string;
  bio?: string;
  password?: string;
}

export interface UserAdminUpdate extends UserUpdate {
  role?: UserRole;
  is_active?: boolean;
}

// ── Catalog ───────────────────────────────────────────────
export interface Subject {
  id: number;
  name: string;
  slug: string;
  description?: string;
  icon?: string;
  color?: string;
  order_index: number;
}

export type Difficulty = 'beginner' | 'intermediate' | 'advanced';

export interface Course {
  id: number;
  subject_id: number;
  title: string;
  slug: string;
  summary?: string;
  description?: string;
  cover_image?: string;
  difficulty: string;
  estimated_hours: number;
  is_published: boolean;
  order_index: number;
}

export interface LessonInTree {
  id: number;
  title: string;
  slug: string;
  lesson_type: LessonType;
  duration_minutes: number;
  order_index: number;
}

export interface ModuleInTree {
  id: number;
  title: string;
  summary?: string;
  order_index: number;
  lessons: LessonInTree[];
}

export interface CourseTree extends Course {
  modules: ModuleInTree[];
}

export type LessonType = 'reading' | 'video' | 'quiz' | 'exercise';

export interface Lesson {
  id: number;
  module_id: number;
  title: string;
  slug: string;
  lesson_type: LessonType;
  content_md?: string;
  video_url?: string;
  duration_minutes: number;
  order_index: number;
}

export interface Tag {
  id: number;
  name: string;
  slug: string;
}

export interface LearningPath {
  id: number;
  title: string;
  slug: string;
  description?: string;
  cover_image?: string;
  is_published: boolean;
  courses: Course[];
}

// ── Exercises ─────────────────────────────────────────────
export type ExerciseDifficulty = 'easy' | 'medium' | 'hard';

export type SupportedLanguage = 'python' | 'javascript' | 'typescript' | 'java' | 'csharp';

export interface TestCasePublic {
  id: number;
  name?: string;
  stdin: string;
  expected_stdout: string;
  order_index: number;
}

export interface ExerciseSummary {
  id: number;
  lesson_id?: number;
  title: string;
  slug: string;
  difficulty: ExerciseDifficulty;
  points: number;
  supported_languages: SupportedLanguage[];
  course_slug?: string;
  course_title?: string;
}

export interface Exercise {
  id: number;
  lesson_id?: number;
  title: string;
  slug: string;
  prompt_md: string;
  difficulty: ExerciseDifficulty;
  is_published: boolean;
  starter_code: Record<SupportedLanguage, string>;
  solution_code: Record<string, string>;
  supported_languages: SupportedLanguage[];
  time_limit_ms: number;
  memory_limit_mb: number;
  points: number;
  test_cases: TestCasePublic[];
}

// ── Submissions ───────────────────────────────────────────
export type SubmissionStatus =
  | 'pending' | 'running' | 'accepted' | 'wrong_answer'
  | 'time_limit_exceeded' | 'memory_limit_exceeded'
  | 'runtime_error' | 'compile_error' | 'internal_error';

export interface CodeRunRequest {
  language: string;
  code: string;
  stdin: string;
}

export interface CodeRunResult {
  status: SubmissionStatus;
  stdout: string;
  stderr: string;
  runtime_ms: number;
  memory_kb: number;
  error?: string;
}

export interface SubmissionCreate {
  exercise_id: number;
  language: string;
  code: string;
}

export interface TestCaseResult {
  id: number;
  test_case_id: number;
  passed: boolean;
  actual_stdout?: string;
  stderr?: string;
  runtime_ms: number;
  error?: string;
  is_hidden: boolean;
}

export interface Submission {
  id: number;
  user_id: number;
  exercise_id: number;
  language: string;
  code: string;
  status: SubmissionStatus;
  score: number;
  passed_tests: number;
  total_tests: number;
  runtime_ms: number;
  memory_kb: number;
  stdout?: string;
  stderr?: string;
  error_message?: string;
  created_at: string;
  results: TestCaseResult[];
}

export interface SubmissionSummary {
  id: number;
  user_id: number;
  exercise_id: number;
  language: string;
  code: string;
  status: SubmissionStatus;
  score: number;
  passed_tests: number;
  total_tests: number;
  runtime_ms: number;
  created_at: string;
}

// ── Progress ──────────────────────────────────────────────
export type ProgressStatus = 'not_started' | 'in_progress' | 'completed';

export interface Enrollment {
  id: number;
  user_id: number;
  course_id: number;
  progress_percent: number;
  completed_at?: string;
  created_at: string;
}

export interface LessonProgress {
  id: number;
  user_id: number;
  lesson_id: number;
  status: ProgressStatus;
  completed_at?: string;
}

// ── Admin ─────────────────────────────────────────────────
export interface AdminStats {
  users_total: number;
  users_active: number;
  students: number;
  admins: number;
  subjects: number;
  courses: number;
  courses_published: number;
  lessons: number;
  exercises: number;
  exercises_published: number;
  submissions: number;
  submissions_accepted: number;
}

// ── User Settings ─────────────────────────────────────────
export type ThemeMode = 'light' | 'dark';
export type FontFamily = 'Inter' | 'Roboto' | 'Outfit' | 'JetBrains Mono' | 'Fira Code' | 'Poppins' | 'Nunito' | 'Open Sans' | 'Lato' | 'Montserrat' | 'Raleway' | 'Ubuntu' | 'Source Sans 3' | 'DM Sans' | 'Space Grotesk' | 'Tajawal' | 'Cairo' | 'Amiri' | 'Noto Naskh Arabic' | 'El Messiri' | 'Changa' | 'Readex Pro';
export type ColorScheme = 'blue' | 'green' | 'purple' | 'amber' | 'rose' | 'cyan' | 'slate' | 'red' | 'orange' | 'yellow' | 'lime' | 'emerald' | 'teal' | 'sky' | 'indigo' | 'violet' | 'pink';
export type ProfileLayout = 'default' | 'minimal' | 'split';

export interface UserSettings {
  id: number;
  user_id: number;
  theme: ThemeMode;
  font_family: FontFamily;
  color_scheme: ColorScheme;
  background_image_url?: string;
  profile_layout: ProfileLayout;
  created_at: string;
  updated_at: string;
}

export interface UserSettingsUpdate {
  theme?: ThemeMode;
  font_family?: FontFamily;
  color_scheme?: ColorScheme;
  background_image_url?: string;
  profile_layout?: ProfileLayout;
}

// ── Helpers ───────────────────────────────────────────────
export const LANGUAGE_LABELS: Record<string, string | undefined> = {
  python: 'Python',
  javascript: 'JavaScript',
  typescript: 'TypeScript',
  java: 'Java',
  csharp: 'C#',
};

export const MONACO_LANGUAGE_MAP: Record<string, string> = {
  python: 'python',
  javascript: 'javascript',
  typescript: 'typescript',
  java: 'java',
  csharp: 'csharp',
};

export const STATUS_LABEL: Record<SubmissionStatus, string> = {
  pending: 'Pending',
  running: 'Running',
  accepted: 'Accepted',
  wrong_answer: 'Wrong Answer',
  time_limit_exceeded: 'Time Limit Exceeded',
  memory_limit_exceeded: 'Memory Limit Exceeded',
  runtime_error: 'Runtime Error',
  compile_error: 'Compile Error',
  internal_error: 'Internal Error',
};

export const STATUS_BADGE_CLASS: Record<SubmissionStatus, string> = {
  pending: 'badge-error',
  running: 'badge-error',
  accepted: 'badge-accepted',
  wrong_answer: 'badge-wrong',
  time_limit_exceeded: 'badge-tle',
  memory_limit_exceeded: 'badge-mle',
  runtime_error: 'badge-error',
  compile_error: 'badge-error',
  internal_error: 'badge-error',
};
