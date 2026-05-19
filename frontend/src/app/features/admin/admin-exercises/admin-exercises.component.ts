import {
  Component,
  OnInit,
  inject,
  signal,
  computed,
  ChangeDetectionStrategy,
} from '@angular/core';
import { NgClass } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormArray, Validators } from '@angular/forms';
import { LucideAngularModule } from 'lucide-angular';
import { MonacoEditorComponent } from '../../../shared/components/monaco-editor/monaco-editor';
import { AdminService } from '../../../core/services/admin.service';
import { ToastService } from '../../../core/services/toast.service';
import { LANGUAGE_LABELS, MONACO_LANGUAGE_MAP, SupportedLanguage } from '../../../core/models/types';

const ALL_LANGUAGES: SupportedLanguage[] = ['python', 'javascript', 'typescript', 'java', 'csharp'];

interface ExerciseRow {
  id: number;
  title: string;
  slug: string;
  difficulty: string;
  supported_languages: SupportedLanguage[];
  is_published: boolean;
}

@Component({
  selector: 'app-admin-exercises',
  standalone: true,
  templateUrl: './admin-exercises.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [NgClass, FormsModule, ReactiveFormsModule, LucideAngularModule, MonacoEditorComponent],
})
export class AdminExercisesComponent implements OnInit {
  private readonly adminService = inject(AdminService);
  private readonly toast = inject(ToastService);
  private readonly fb = inject(FormBuilder);

  readonly LANGUAGE_LABELS = LANGUAGE_LABELS;
  readonly ALL_LANGUAGES = ALL_LANGUAGES;
  readonly MONACO_LANGUAGE_MAP = MONACO_LANGUAGE_MAP;

  // ── State ─────────────────────────────────────────────────
  exercises = signal<ExerciseRow[]>([]);
  loading = signal(true);
  panelOpen = signal(false);
  editingExercise = signal<ExerciseRow | null>(null);
  saveLoading = signal(false);
  deletingId = signal<number | null>(null);
  deleteLoading = signal(false);
  activeCodeTab = signal<SupportedLanguage>('python');

  // Starter code map (not in FormGroup — managed separately)
  starterCodeMap = signal<Record<string, string>>({
    python: '',
    javascript: '',
    typescript: '',
    java: '',
    csharp: '',
  });

  exerciseForm = this.fb.group({
    title: ['', [Validators.required, Validators.minLength(3)]],
    slug: ['', Validators.required],
    difficulty: ['easy', Validators.required],
    supported_languages: this.fb.array(
      ALL_LANGUAGES.map(() => this.fb.control(false))
    ),
    prompt_md: ['', Validators.required],
    is_published: [false],
    test_cases: this.fb.array([]),
  });

  get supportedLangsArray(): FormArray {
    return this.exerciseForm.get('supported_languages') as FormArray;
  }

  get testCasesArray(): FormArray {
    return this.exerciseForm.get('test_cases') as FormArray;
  }

  selectedLanguages = computed(() => {
    const vals = this.supportedLangsArray.value as boolean[];
    return ALL_LANGUAGES.filter((_, i) => vals[i]);
  });

  ngOnInit(): void {
    this.loadExercises();
  }

  private loadExercises(): void {
    this.loading.set(true);
    this.adminService.getExercises().subscribe({
      next: (data) => {
        this.exercises.set(data as ExerciseRow[]);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.toast.error('Failed to load exercises.');
      },
    });
  }

  openCreate(): void {
    this.editingExercise.set(null);
    this.exerciseForm.reset({ difficulty: 'easy', is_published: false });
    this.supportedLangsArray.controls.forEach((c) => c.setValue(false));
    // Default python selected
    this.supportedLangsArray.at(0).setValue(true);
    this.activeCodeTab.set('python');
    this.starterCodeMap.set({ python: '', javascript: '', typescript: '', java: '', csharp: '' });
    this.clearTestCases();
    this.panelOpen.set(true);
  }

  openEdit(ex: ExerciseRow): void {
    this.editingExercise.set(ex);
    this.exerciseForm.patchValue({
      title: ex.title,
      slug: ex.slug,
      difficulty: ex.difficulty,
      prompt_md: '',
      is_published: ex.is_published,
    });
    ALL_LANGUAGES.forEach((lang, i) => {
      this.supportedLangsArray.at(i).setValue(ex.supported_languages.includes(lang));
    });
    this.activeCodeTab.set(ex.supported_languages[0] ?? 'python');
    this.clearTestCases();
    this.panelOpen.set(true);
  }

  closePanel(): void {
    this.panelOpen.set(false);
    this.editingExercise.set(null);
  }

  onTitleChange(title: string): void {
    if (!this.editingExercise()) {
      const slug = title
        .toLowerCase()
        .replace(/[^a-z0-9\s-]/g, '')
        .replace(/\s+/g, '-')
        .replace(/-+/g, '-')
        .slice(0, 80);
      this.exerciseForm.patchValue({ slug });
    }
  }

  setStarterCode(lang: SupportedLanguage, code: string): void {
    this.starterCodeMap.update((map) => ({ ...map, [lang]: code }));
  }

  getStarterCode(lang: SupportedLanguage): string {
    return this.starterCodeMap()[lang] ?? '';
  }

  // ── Test cases ─────────────────────────────────────────────
  private clearTestCases(): void {
    while (this.testCasesArray.length) {
      this.testCasesArray.removeAt(0);
    }
  }

  addTestCase(): void {
    this.testCasesArray.push(
      this.fb.group({
        stdin: [''],
        expected_stdout: ['', Validators.required],
        is_hidden: [false],
        weight: [1, [Validators.required, Validators.min(1)]],
      })
    );
  }

  removeTestCase(index: number): void {
    this.testCasesArray.removeAt(index);
  }

  // ── Save ───────────────────────────────────────────────────
  save(): void {
    if (this.exerciseForm.invalid) return;
    const val = this.exerciseForm.value;
    const langs = ALL_LANGUAGES.filter((_, i) => (val.supported_languages as boolean[])[i]);
    if (langs.length === 0) {
      this.toast.error('Select at least one supported language.');
      return;
    }

    const starterCode: Record<string, string> = {};
    langs.forEach((lang) => { starterCode[lang] = this.starterCodeMap()[lang] ?? ''; });

    const payload = {
      title: val.title,
      slug: val.slug,
      difficulty: val.difficulty,
      prompt_md: val.prompt_md,
      is_published: val.is_published,
      supported_languages: langs,
      starter_code: starterCode,
      test_cases: val.test_cases ?? [],
    };

    this.saveLoading.set(true);
    const editing = this.editingExercise();
    const obs = editing
      ? this.adminService.updateExercise(editing.id, payload)
      : this.adminService.createExercise(payload);

    obs.subscribe({
      next: (ex) => {
        if (editing) {
          this.exercises.update((list) => list.map((e) => (e.id === ex.id ? ex : e)));
          this.toast.success('Exercise updated.');
        } else {
          this.exercises.update((list) => [ex, ...list]);
          this.toast.success('Exercise created.');
        }
        this.saveLoading.set(false);
        this.closePanel();
      },
      error: () => {
        this.saveLoading.set(false);
        this.toast.error('Failed to save exercise.');
      },
    });
  }

  confirmDelete(id: number): void {
    this.deletingId.set(id);
  }

  cancelDelete(): void {
    this.deletingId.set(null);
  }

  executeDelete(id: number): void {
    this.deleteLoading.set(true);
    this.adminService.deleteExercise(id).subscribe({
      next: () => {
        this.exercises.update((list) => list.filter((e) => e.id !== id));
        this.deletingId.set(null);
        this.deleteLoading.set(false);
        this.toast.success('Exercise deleted.');
      },
      error: () => {
        this.deleteLoading.set(false);
        this.toast.error('Failed to delete exercise.');
      },
    });
  }

  getDifficultyBadge(difficulty: string): string {
    if (difficulty === 'easy') return 'badge-easy';
    if (difficulty === 'medium') return 'badge-medium';
    return 'badge-hard';
  }

  getMonacoLang(lang: SupportedLanguage): string {
    return MONACO_LANGUAGE_MAP[lang] ?? 'plaintext';
  }
}
