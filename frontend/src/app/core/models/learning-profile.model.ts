import type { Course, Subject } from './types';

// ── Persisted profile (mirrors backend LearningProfile) ─────────────────────
export type LearningGoal = 'career' | 'school' | 'interview' | 'hobby' | 'upskill';
export type ExperienceLevel = 'new' | 'beginner' | 'intermediate' | 'advanced';
export type InterestKey = 'foundations' | 'web' | 'data' | 'algorithms' | 'ai' | 'systems' | 'mobile';

export interface LearningProfile {
  id: number;
  user_id: number;
  goal: LearningGoal | null;
  experience_level: ExperienceLevel | null;
  weekly_hours: number | null;
  interests: InterestKey[];
  languages: string[];
  onboarded: boolean;
  created_at: string;
  updated_at: string;
}

export interface LearningProfileUpdate {
  goal?: LearningGoal | null;
  experience_level?: ExperienceLevel | null;
  weekly_hours?: number | null;
  interests?: InterestKey[];
  languages?: string[];
  onboarded?: boolean;
}

// ── Wizard option metadata ───────────────────────────────────────────────────
export interface GoalOption {
  key: LearningGoal;
  label: string;
  blurb: string;
  icon: string;          // Lucide icon name
  gradient: string;      // tailwind gradient classes
}

export interface InterestOption {
  key: InterestKey;
  label: string;
  blurb: string;
  icon: string;
  gradient: string;
  image: string;         // photographic texture (reliable remote source)
  /** Subject slugs this interest maps to, for ranking the catalog. */
  subjects: string[];
  /** Languages implied by this interest (seed defaults). */
  languages: string[];
}

export interface LevelOption {
  key: ExperienceLevel;
  label: string;
  blurb: string;
  icon: string;
}

export interface LanguageOption {
  key: string;
  label: string;
  icon: string;          // Lucide icon name
}

// Reliable real-photography source (always resolves) seeded per topic; swap for
// curated brand assets later without touching the wizard logic.
const photo = (seed: string) => `https://picsum.photos/seed/${seed}/640/420`;

export const GOAL_OPTIONS: GoalOption[] = [
  { key: 'career',    label: 'Land a tech job',      blurb: 'Build job-ready skills & a portfolio',     icon: 'Briefcase',     gradient: 'from-blue-500 to-indigo-500' },
  { key: 'school',    label: 'Ace my coursework',     blurb: 'Keep up with classes & exams',             icon: 'GraduationCap', gradient: 'from-emerald-500 to-teal-500' },
  { key: 'interview', label: 'Prep for interviews',   blurb: 'Master DSA & problem solving',             icon: 'Target',        gradient: 'from-purple-500 to-fuchsia-500' },
  { key: 'upskill',   label: 'Level up at work',      blurb: 'Sharpen skills for my current role',       icon: 'TrendingUp',    gradient: 'from-amber-500 to-orange-500' },
  { key: 'hobby',     label: 'Learn for fun',         blurb: 'Explore & build cool things',              icon: 'Sparkles',      gradient: 'from-rose-500 to-pink-500' },
];

export const INTEREST_OPTIONS: InterestOption[] = [
  { key: 'foundations', label: 'Programming Foundations', blurb: 'Variables, logic, functions — start here', icon: 'Code2',     gradient: 'from-sky-500 to-blue-600',     image: photo('tlp-foundations'), subjects: ['programming-languages'], languages: ['python'] },
  { key: 'web',         label: 'Web Development',         blurb: 'Build modern, interactive web apps',        icon: 'Globe',     gradient: 'from-violet-500 to-purple-600', image: photo('tlp-web'),         subjects: ['web-development'],       languages: ['typescript', 'javascript'] },
  { key: 'data',        label: 'Databases & Data',        blurb: 'Query, model & analyze data with SQL',      icon: 'Database',  gradient: 'from-amber-500 to-orange-600',  image: photo('tlp-data'),        subjects: ['databases'],             languages: ['sql'] },
  { key: 'algorithms',  label: 'Algorithms & DSA',        blurb: 'Problem solving & data structures',         icon: 'Sigma',     gradient: 'from-emerald-500 to-green-600', image: photo('tlp-algorithms'),  subjects: ['algorithms'],            languages: ['python'] },
  { key: 'ai',          label: 'AI & Machine Learning',   blurb: 'Intelligent systems & models',              icon: 'Brain',     gradient: 'from-fuchsia-500 to-pink-600',  image: photo('tlp-ai'),          subjects: ['algorithms'],            languages: ['python'] },
  { key: 'systems',     label: 'Computer Science Core',   blurb: 'How computers really work',                 icon: 'Cpu',       gradient: 'from-cyan-500 to-teal-600',     image: photo('tlp-systems'),     subjects: ['algorithms'],            languages: [] },
];

export const LEVEL_OPTIONS: LevelOption[] = [
  { key: 'new',          label: 'Brand new',     blurb: "I've never written code",       icon: 'Sprout' },
  { key: 'beginner',     label: 'Beginner',      blurb: 'I know a few basics',           icon: 'BookOpen' },
  { key: 'intermediate', label: 'Intermediate',  blurb: 'I can build small programs',    icon: 'Rocket' },
  { key: 'advanced',     label: 'Advanced',      blurb: 'I want deep, advanced topics',  icon: 'Trophy' },
];

export const LANGUAGE_OPTIONS: LanguageOption[] = [
  { key: 'python',     label: 'Python',     icon: 'Code' },
  { key: 'javascript', label: 'JavaScript', icon: 'Code' },
  { key: 'typescript', label: 'TypeScript', icon: 'Code' },
  { key: 'sql',        label: 'SQL',        icon: 'Database' },
  { key: 'java',       label: 'Java',       icon: 'Coffee' },
  { key: 'csharp',     label: 'C#',         icon: 'Hash' },
  { key: 'cpp',        label: 'C++',        icon: 'Braces' },
  { key: 'go',         label: 'Go',         icon: 'Code' },
];

// ── Demand scoring — ranks courses "interested first" ────────────────────────
export interface ScoredCourse {
  course: Course;
  score: number;
  /** Short human reason, e.g. "Matches your interest in Web Development". */
  reason: string;
  /** True when it clearly aligns with a chosen interest. */
  recommended: boolean;
}

const LEVEL_TO_DIFFICULTY: Record<ExperienceLevel, string> = {
  new: 'beginner',
  beginner: 'beginner',
  intermediate: 'intermediate',
  advanced: 'advanced',
};

/** Best-effort language inference from a course slug/title. */
function inferCourseLanguages(course: Course): string[] {
  const hay = `${course.slug} ${course.title}`.toLowerCase();
  const langs: string[] = [];
  if (/\bpython\b/.test(hay)) langs.push('python');
  if (/\bangular|typescript|frontend|web\b/.test(hay)) langs.push('typescript', 'javascript');
  if (/\bsql|database\b/.test(hay)) langs.push('sql');
  if (/\bjava\b/.test(hay)) langs.push('java');
  if (/\bc\+\+|cpp\b/.test(hay)) langs.push('cpp');
  return langs;
}

/**
 * Rank courses against a learning profile. Courses that match the learner's
 * earliest-picked interests, level and languages float to the top — powering
 * the "show all courses, interested first" experience.
 */
export function rankCourses(
  courses: Course[],
  subjects: Subject[],
  profile: LearningProfile | null,
): ScoredCourse[] {
  const subjectSlugById = new Map(subjects.map(s => [s.id, s.slug]));

  // Subject slug -> best (earliest) interest that targets it.
  const interestBySubject = new Map<string, { option: InterestOption; rank: number }>();
  const interests = profile?.interests ?? [];
  interests.forEach((key, idx) => {
    const opt = INTEREST_OPTIONS.find(o => o.key === key);
    if (!opt) return;
    for (const slug of opt.subjects) {
      const existing = interestBySubject.get(slug);
      if (!existing || idx < existing.rank) interestBySubject.set(slug, { option: opt, rank: idx });
    }
  });

  const preferredDifficulty = profile?.experience_level
    ? LEVEL_TO_DIFFICULTY[profile.experience_level]
    : null;
  const langs = new Set((profile?.languages ?? []).map(l => l.toLowerCase()));

  const scored = courses.map<ScoredCourse>(course => {
    let score = 0;
    let reason = '';
    let recommended = false;

    const slug = subjectSlugById.get(course.subject_id);
    const match = slug ? interestBySubject.get(slug) : undefined;
    if (match) {
      // Earlier-picked interests rank higher.
      score += 120 - match.rank * 12;
      reason = `Matches your interest in ${match.option.label}`;
      recommended = true;
    }

    if (preferredDifficulty) {
      const order = ['beginner', 'intermediate', 'advanced'];
      const diff = Math.abs(order.indexOf(course.difficulty) - order.indexOf(preferredDifficulty));
      if (diff === 0) score += 30;
      else if (diff === 1) score += 14;
    }

    if (langs.size) {
      const courseLangs = inferCourseLanguages(course);
      if (courseLangs.some(l => langs.has(l))) {
        score += 22;
        if (!reason) reason = 'Uses a language you picked';
      }
    }

    // Gentle tie-breaker: earlier curriculum order first.
    score += Math.max(0, 10 - (course.order_index ?? 0));

    return { course, score, reason, recommended };
  });

  return scored.sort((a, b) => b.score - a.score || a.course.order_index - b.course.order_index);
}
