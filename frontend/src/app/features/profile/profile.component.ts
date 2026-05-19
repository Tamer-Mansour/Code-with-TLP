import {
  Component,
  OnInit,
  inject,
  signal,
  computed,
  ChangeDetectionStrategy,
} from '@angular/core';
import { NgClass, DatePipe, DecimalPipe, PercentPipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { LucideAngularModule } from 'lucide-angular';
import { AuthService } from '../../core/services/auth.service';
import { SubmissionService } from '../../core/services/submission.service';
import { UserService } from '../../core/services/user.service';
import { ToastService } from '../../core/services/toast.service';
import {
  SubmissionSummary,
  SubmissionStatus,
  LANGUAGE_LABELS,
  STATUS_LABEL,
  STATUS_BADGE_CLASS,
  UserUpdate,
} from '../../core/models/types';

// ── Rank system ────────────────────────────────────────────
export interface RankInfo {
  tier: number;
  name: string;
  label: string;
  minScore: number;
  nextScore: number | null;
  gradientFrom: string;
  gradientTo: string;
  accentColor: string;
  glowColor: string;
  textColor: string;
  animated: boolean;
  icon: string;
}

export const RANKS: RankInfo[] = [
  {
    tier: 0, name: 'Newcomer', label: 'Just Getting Started',
    minScore: 0, nextScore: 10,
    gradientFrom: '#1c1c1e', gradientTo: '#3a3a3c',
    accentColor: '#9ca3af', glowColor: 'rgba(156,163,175,0.3)',
    textColor: '#f9fafb', animated: false, icon: 'user',
  },
  {
    tier: 1, name: 'Bronze', label: 'Rising Coder',
    minScore: 10, nextScore: 50,
    gradientFrom: '#431407', gradientTo: '#9a3412',
    accentColor: '#fb923c', glowColor: 'rgba(251,146,60,0.35)',
    textColor: '#fff7ed', animated: false, icon: 'award',
  },
  {
    tier: 2, name: 'Silver', label: 'Skilled Developer',
    minScore: 50, nextScore: 150,
    gradientFrom: '#1e293b', gradientTo: '#475569',
    accentColor: '#cbd5e1', glowColor: 'rgba(203,213,225,0.35)',
    textColor: '#f8fafc', animated: false, icon: 'award',
  },
  {
    tier: 3, name: 'Gold', label: 'Expert Programmer',
    minScore: 150, nextScore: 400,
    gradientFrom: '#422006', gradientTo: '#92400e',
    accentColor: '#fbbf24', glowColor: 'rgba(251,191,36,0.45)',
    textColor: '#fefce8', animated: false, icon: 'star',
  },
  {
    tier: 4, name: 'Platinum', label: 'Code Artisan',
    minScore: 400, nextScore: 900,
    gradientFrom: '#042f2e', gradientTo: '#0e7490',
    accentColor: '#22d3ee', glowColor: 'rgba(34,211,238,0.45)',
    textColor: '#ecfeff', animated: false, icon: 'zap',
  },
  {
    tier: 5, name: 'Diamond', label: 'Algorithm Master',
    minScore: 900, nextScore: 2000,
    gradientFrom: '#1e1b4b', gradientTo: '#4338ca',
    accentColor: '#818cf8', glowColor: 'rgba(129,140,248,0.55)',
    textColor: '#eef2ff', animated: true, icon: 'zap',
  },
  {
    tier: 6, name: 'Master', label: 'Elite Engineer',
    minScore: 2000, nextScore: 5000,
    gradientFrom: '#2e1065', gradientTo: '#7c3aed',
    accentColor: '#c084fc', glowColor: 'rgba(192,132,252,0.6)',
    textColor: '#faf5ff', animated: true, icon: 'trophy',
  },
  {
    tier: 7, name: 'Legend', label: 'Coding Legend',
    minScore: 5000, nextScore: null,
    gradientFrom: '#450a0a', gradientTo: '#b91c1c',
    accentColor: '#f87171', glowColor: 'rgba(248,113,113,0.65)',
    textColor: '#fff1f2', animated: true, icon: 'flame',
  },
];

function resolveRank(score: number): RankInfo {
  for (let i = RANKS.length - 1; i >= 0; i--) {
    if (score >= RANKS[i].minScore) return RANKS[i];
  }
  return RANKS[0];
}

const BG_OPTIONS = [
  { value: 'gradient', label: 'Gradient' },
  { value: 'geometric', label: 'Geometric' },
  { value: 'mesh', label: 'Mesh' },
] as const;

@Component({
  selector: 'app-profile',
  standalone: true,
  templateUrl: './profile.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [NgClass, DatePipe, DecimalPipe, PercentPipe, RouterLink, ReactiveFormsModule, LucideAngularModule],
})
export class ProfileComponent implements OnInit {
  private readonly auth = inject(AuthService);
  private readonly submissionService = inject(SubmissionService);
  private readonly userService = inject(UserService);
  private readonly toast = inject(ToastService);
  private readonly fb = inject(FormBuilder);

  readonly LANGUAGE_LABELS = LANGUAGE_LABELS;
  readonly STATUS_LABEL = STATUS_LABEL;
  readonly STATUS_BADGE_CLASS = STATUS_BADGE_CLASS;
  readonly RANKS = RANKS;
  readonly BG_OPTIONS = BG_OPTIONS;

  // ── State ──────────────────────────────────────────────────
  user = this.auth.currentUser;
  submissions = signal<SubmissionSummary[]>([]);
  loading = signal(true);
  editOpen = signal(false);
  saving = signal(false);
  passwordOpen = signal(false);
  selectedBg = signal<string>(localStorage.getItem('profile_bg') ?? 'gradient');

  // ── Stats ──────────────────────────────────────────────────
  totalSubmissions = computed(() => this.submissions().length);

  acceptedSubmissions = computed(() =>
    this.submissions().filter((s) => s.status === 'accepted')
  );

  totalScore = computed(() =>
    this.acceptedSubmissions().reduce((sum, s) => sum + (s.score ?? 0), 0)
  );

  acceptanceRate = computed(() => {
    const total = this.totalSubmissions();
    return total === 0 ? 0 : (this.acceptedSubmissions().length / total) * 100;
  });

  languageCounts = computed(() => {
    const counts: Record<string, number> = {};
    for (const s of this.acceptedSubmissions()) {
      counts[s.language] = (counts[s.language] ?? 0) + 1;
    }
    return Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5);
  });

  recentSubmissions = computed(() => this.submissions().slice(0, 15));

  // ── Rank ───────────────────────────────────────────────────
  rankInfo = computed(() => resolveRank(this.totalScore()));

  rankProgress = computed(() => {
    const rank = this.rankInfo();
    if (rank.nextScore === null) return 100;
    const range = rank.nextScore - rank.minScore;
    const progress = this.totalScore() - rank.minScore;
    return Math.min(100, Math.round((progress / range) * 100));
  });

  nextRankName = computed(() => {
    const idx = RANKS.indexOf(this.rankInfo());
    return idx < RANKS.length - 1 ? RANKS[idx + 1].name : null;
  });

  bannerStyle = computed(() => {
    const rank = this.rankInfo();
    const bg = this.selectedBg();
    const base = `linear-gradient(135deg, ${rank.gradientFrom} 0%, ${rank.gradientTo} 100%)`;

    if (bg === 'geometric') {
      return `background: ${base}; position: relative;`;
    }
    if (bg === 'mesh') {
      return `background: radial-gradient(ellipse at 20% 50%, ${rank.gradientTo}88 0%, transparent 60%),
               radial-gradient(ellipse at 80% 20%, ${rank.accentColor}44 0%, transparent 50%),
               ${base};`;
    }
    return `background: ${base};`;
  });

  // ── Edit form ──────────────────────────────────────────────
  editForm = this.fb.group({
    full_name: [''],
    bio: [''],
    avatar_url: [''],
    new_password: ['', [Validators.minLength(8)]],
  });

  ngOnInit(): void {
    this.submissionService.getMySubmissions().subscribe({
      next: (subs) => {
        this.submissions.set(subs);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }

  openEdit(): void {
    const u = this.user();
    this.editForm.patchValue({
      full_name: u?.full_name ?? '',
      bio: u?.bio ?? '',
      avatar_url: u?.avatar_url ?? '',
      new_password: '',
    });
    this.passwordOpen.set(false);
    this.editOpen.set(true);
  }

  closeEdit(): void {
    this.editOpen.set(false);
    this.editForm.reset();
  }

  saveProfile(): void {
    if (this.saving()) return;
    const val = this.editForm.value;
    const payload: UserUpdate = {};
    if (val.full_name !== null && val.full_name !== undefined) payload.full_name = val.full_name;
    if (val.bio !== null && val.bio !== undefined) payload.bio = val.bio;
    if (val.avatar_url) payload.avatar_url = val.avatar_url;
    if (val.new_password) payload.password = val.new_password;

    this.saving.set(true);
    this.userService.updateProfile(payload).subscribe({
      next: () => {
        this.saving.set(false);
        this.closeEdit();
        this.toast.success('Profile updated');
      },
      error: () => {
        this.saving.set(false);
        this.toast.error('Failed to update profile');
      },
    });
  }

  setBg(value: string): void {
    this.selectedBg.set(value);
    localStorage.setItem('profile_bg', value);
  }

  togglePasswordSection(): void {
    this.passwordOpen.update((v) => !v);
  }

  getBannerPreview(value: string): string {
    const rank = this.rankInfo();
    const base = `linear-gradient(135deg, ${rank.gradientFrom} 0%, ${rank.gradientTo} 100%)`;
    if (value === 'geometric') return `background: ${base};`;
    if (value === 'mesh') {
      return `background: radial-gradient(ellipse at 30% 60%, ${rank.gradientTo}cc 0%, transparent 70%), ${base};`;
    }
    return `background: ${base};`;
  }

  getStatusBadge(status: SubmissionStatus): string {
    return STATUS_BADGE_CLASS[status] ?? 'badge-error';
  }

  getStatusLabel(status: SubmissionStatus): string {
    return STATUS_LABEL[status] ?? status;
  }

  initials(): string {
    const u = this.user();
    if (!u) return '?';
    const name = u.full_name ?? u.username ?? '';
    return name.split(' ').map((w) => w[0]).join('').toUpperCase().slice(0, 2) || '?';
  }
}
