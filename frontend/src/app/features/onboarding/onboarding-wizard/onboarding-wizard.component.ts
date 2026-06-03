import {
  Component,
  inject,
  signal,
  computed,
  OnInit,
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  DestroyRef,
} from '@angular/core';
import { Router } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { forkJoin, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import {
  LucideAngularModule, LucideIconData,
  Briefcase, GraduationCap, Target, TrendingUp, Sparkles, Code2, Globe, Database,
  Sigma, Brain, Cpu, Sprout, BookOpen, Rocket, Trophy, Code, Coffee, Hash, Braces,
  ArrowLeft, ArrowRight, Check, X, Loader2, Wand2, Clock, Layers, Star, Compass, PartyPopper,
} from 'lucide-angular';
import { CatalogService } from '../../../core/services/catalog.service';
import { LearningProfileService } from '../../../core/services/learning-profile.service';
import { ToastService } from '../../../core/services/toast.service';
import type { Course, Subject } from '../../../core/models/types';
import {
  GOAL_OPTIONS, INTEREST_OPTIONS, LEVEL_OPTIONS, LANGUAGE_OPTIONS, rankCourses,
} from '../../../core/models/learning-profile.model';
import type {
  LearningGoal, ExperienceLevel, InterestKey, ScoredCourse,
} from '../../../core/models/learning-profile.model';

interface HourOption { value: number; label: string; sub: string; }

@Component({
  selector: 'app-onboarding-wizard',
  standalone: true,
  imports: [LucideAngularModule],
  templateUrl: './onboarding-wizard.component.html',
  styleUrl: './onboarding-wizard.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class OnboardingWizardComponent implements OnInit {
  private readonly catalog = inject(CatalogService);
  private readonly profileSvc = inject(LearningProfileService);
  private readonly toast = inject(ToastService);
  private readonly router = inject(Router);
  private readonly cdr = inject(ChangeDetectorRef);
  private readonly destroyRef = inject(DestroyRef);

  // Option data
  readonly goals = GOAL_OPTIONS;
  readonly interestOptions = INTEREST_OPTIONS;
  readonly levels = LEVEL_OPTIONS;
  readonly languageOptions = LANGUAGE_OPTIONS;
  readonly hourOptions: HourOption[] = [
    { value: 2,  label: 'Casual',   sub: '~2 h / week' },
    { value: 5,  label: 'Steady',   sub: '~5 h / week' },
    { value: 10, label: 'Serious',  sub: '~10 h / week' },
    { value: 20, label: 'Intense',  sub: '20+ h / week' },
  ];

  // Icons (name → data, rendered with [img] so we don't depend on global registration)
  readonly iconMap: Record<string, LucideIconData> = {
    Briefcase, GraduationCap, Target, TrendingUp, Sparkles, Code2, Globe, Database,
    Sigma, Brain, Cpu, Sprout, BookOpen, Rocket, Trophy, Code, Coffee, Hash, Braces,
    Clock, Layers, Star, Compass,
  };
  readonly ArrowLeft = ArrowLeft;
  readonly ArrowRight = ArrowRight;
  readonly Check = Check;
  readonly X = X;
  readonly Loader2 = Loader2;
  readonly Wand2 = Wand2;
  readonly Sparkles = Sparkles;
  readonly PartyPopper = PartyPopper;
  readonly Clock = Clock;
  readonly Star = Star;

  // ── Wizard state ────────────────────────────────────────────────────────────
  /** 0 welcome · 1 goal · 2 interests · 3 level · 4 time · 5 languages · 6 building · 7 result */
  readonly step = signal(0);
  readonly TOTAL_QUESTION_STEPS = 5; // steps 1..5 count toward the progress bar

  readonly goal = signal<LearningGoal | null>(null);
  readonly interests = signal<InterestKey[]>([]);
  readonly level = signal<ExperienceLevel | null>(null);
  readonly weeklyHours = signal<number | null>(null);
  readonly languages = signal<string[]>([]);

  readonly saving = signal(false);
  readonly subjects = signal<Subject[]>([]);
  readonly courses = signal<Course[]>([]);

  readonly ranked = computed<ScoredCourse[]>(() =>
    rankCourses(this.courses(), this.subjects(), {
      id: 0, user_id: 0, goal: this.goal(), experience_level: this.level(),
      weekly_hours: this.weeklyHours(), interests: this.interests(),
      languages: this.languages(), onboarded: false,
      created_at: '', updated_at: '',
    })
  );

  readonly recommended = computed(() => this.ranked().filter(s => s.recommended).slice(0, 5));
  readonly recommendedOrFallback = computed(() => {
    const rec = this.recommended();
    return rec.length ? rec : this.ranked().slice(0, 4);
  });

  readonly totalHours = computed(() =>
    this.recommendedOrFallback().reduce((sum, s) => sum + (s.course.estimated_hours || 0), 0)
  );

  readonly weeksToFinish = computed(() => {
    const hrs = this.weeklyHours();
    const total = this.totalHours();
    if (!hrs || !total) return null;
    return Math.max(1, Math.ceil(total / hrs));
  });

  readonly progressPct = computed(() => {
    const s = this.step();
    if (s <= 0) return 0;
    if (s >= 6) return 100;
    return Math.round((s / (this.TOTAL_QUESTION_STEPS + 1)) * 100);
  });

  /** Whether the current step's requirement is satisfied. */
  readonly canAdvance = computed(() => {
    switch (this.step()) {
      case 1: return this.goal() !== null;
      case 2: return this.interests().length > 0;
      case 3: return this.level() !== null;
      case 4: return this.weeklyHours() !== null;
      default: return true; // welcome, languages (optional)
    }
  });

  ngOnInit(): void {
    forkJoin({
      subjects: this.catalog.getSubjects().pipe(catchError(() => of<Subject[]>([]))),
      courses: this.catalog.getCourses().pipe(catchError(() => of<Course[]>([]))),
    })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(({ subjects, courses }) => {
        this.subjects.set(subjects);
        this.courses.set(courses.filter(c => c.is_published !== false));
        this.cdr.markForCheck();
      });
  }

  // ── Selection handlers ──────────────────────────────────────────────────────
  selectGoal(g: LearningGoal): void { this.goal.set(g); }

  toggleInterest(key: InterestKey): void {
    this.interests.update(list =>
      list.includes(key) ? list.filter(k => k !== key) : [...list, key]
    );
  }
  isInterest(key: InterestKey): boolean { return this.interests().includes(key); }

  selectLevel(l: ExperienceLevel): void { this.level.set(l); }
  selectHours(h: number): void { this.weeklyHours.set(h); }

  toggleLanguage(key: string): void {
    this.languages.update(list =>
      list.includes(key) ? list.filter(k => k !== key) : [...list, key]
    );
  }
  isLanguage(key: string): boolean { return this.languages().includes(key); }

  // ── Navigation ──────────────────────────────────────────────────────────────
  next(): void {
    if (!this.canAdvance()) return;
    const s = this.step();
    if (s === 5) { this.startBuilding(); return; }
    this.step.set(s + 1);
  }

  back(): void {
    if (this.step() > 0) this.step.set(this.step() - 1);
  }

  private startBuilding(): void {
    this.step.set(6);
    this.cdr.markForCheck();
    // Brief, deliberate "crafting your plan" beat — feels considered, not instant.
    setTimeout(() => {
      this.step.set(7);
      this.cdr.markForCheck();
    }, 1900);
  }

  /** Persist the profile and head into the catalog with the plan applied. */
  finish(): void {
    if (this.saving()) return;
    this.saving.set(true);
    this.profileSvc.save({
      goal: this.goal(),
      experience_level: this.level(),
      weekly_hours: this.weeklyHours(),
      interests: this.interests(),
      languages: this.languages(),
      onboarded: true,
    })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.saving.set(false);
          this.toast.success('Your personalized learning path is ready!');
          this.router.navigate(['/catalog']);
        },
        error: () => {
          this.saving.set(false);
          this.toast.error('Could not save your preferences. Please try again.');
          this.cdr.markForCheck();
        },
      });
  }

  skip(): void {
    this.router.navigate(['/catalog']);
  }

  // ── Display helpers ─────────────────────────────────────────────────────────
  difficultyLabel(d: string): string {
    return d ? d.charAt(0).toUpperCase() + d.slice(1) : '';
  }

  goalLabel(): string {
    return this.goals.find(g => g.key === this.goal())?.label ?? '';
  }
}
