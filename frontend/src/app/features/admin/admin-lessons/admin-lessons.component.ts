import {
  Component,
  OnInit,
  inject,
  signal,
  computed,
  ChangeDetectionStrategy,
} from '@angular/core';
import { NgClass } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { LucideAngularModule } from 'lucide-angular';
import { MarkdownModule } from 'ngx-markdown';
import { AdminService } from '../../../core/services/admin.service';
import { CatalogService } from '../../../core/services/catalog.service';
import { ToastService } from '../../../core/services/toast.service';
import { Course, CourseTree, Lesson, LessonInTree, LessonType, ModuleInTree } from '../../../core/models/types';

@Component({
  selector: 'app-admin-lessons',
  standalone: true,
  templateUrl: './admin-lessons.component.html',
  styleUrl: './admin-lessons.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [NgClass, FormsModule, ReactiveFormsModule, LucideAngularModule, MarkdownModule],
})
export class AdminLessonsComponent implements OnInit {
  private readonly adminService = inject(AdminService);
  private readonly catalogService = inject(CatalogService);
  private readonly toast = inject(ToastService);
  private readonly fb = inject(FormBuilder);

  // ── State ─────────────────────────────────────────────────
  courses = signal<Course[]>([]);
  selectedCourseId = signal<number | null>(null);
  tree = signal<CourseTree | null>(null);
  loadingCourses = signal(true);
  loadingTree = signal(false);

  panelOpen = signal(false);
  editingLesson = signal<Lesson | null>(null);
  loadingContent = signal(false);
  saveLoading = signal(false);
  showPreview = signal(false);

  deletingId = signal<number | null>(null);
  deleteLoading = signal(false);

  // ── Group (module) state ──────────────────────────────────
  modulePanelOpen = signal(false);
  editingModule = signal<ModuleInTree | null>(null);
  moduleSaveLoading = signal(false);
  deletingModuleId = signal<number | null>(null);
  deleteModuleLoading = signal(false);

  // Collapse: modules are collapsed by default; this set holds the expanded ones.
  expandedModules = signal<Set<number>>(new Set<number>());

  readonly lessonTypes: { value: LessonType; label: string }[] = [
    { value: 'reading', label: 'Reading' },
    { value: 'video', label: 'Video' },
    { value: 'quiz', label: 'Quiz' },
    { value: 'exercise', label: 'Exercise' },
  ];

  modules = computed<ModuleInTree[]>(() => this.tree()?.modules ?? []);

  moduleForm = this.fb.group({
    title: ['', [Validators.required, Validators.minLength(2)]],
    summary: [''],
    order_index: [0],
  });

  lessonForm = this.fb.group({
    module_id: [null as number | null, Validators.required],
    title: ['', [Validators.required, Validators.minLength(2)]],
    slug: ['', Validators.required],
    lesson_type: ['reading' as LessonType, Validators.required],
    content_md: [''],
    video_url: [''],
    duration_minutes: [5],
    order_index: [0],
  });

  ngOnInit(): void {
    this.adminService.getCourses().subscribe({
      next: (courses) => {
        this.courses.set(courses);
        this.loadingCourses.set(false);
        if (courses.length) this.selectCourse(courses[0].id);
      },
      error: () => {
        this.loadingCourses.set(false);
        this.toast.error('Failed to load courses.');
      },
    });
  }

  selectCourse(id: number | null): void {
    this.selectedCourseId.set(id);
    this.tree.set(null);
    if (id == null) return;
    const course = this.courses().find((c) => c.id === id);
    if (!course) return;
    this.loadingTree.set(true);
    this.catalogService.getCourseTree(course.slug).subscribe({
      next: (tree) => {
        this.tree.set(tree);
        this.loadingTree.set(false);
      },
      error: () => {
        this.loadingTree.set(false);
        this.toast.error('Failed to load course content.');
      },
    });
  }

  private reloadTree(): void {
    const id = this.selectedCourseId();
    if (id != null) this.selectCourse(id);
  }

  // ── Collapse ──────────────────────────────────────────────
  isExpanded(id: number): boolean {
    return this.expandedModules().has(id);
  }

  toggleModule(id: number): void {
    this.expandedModules.update((set) => {
      const next = new Set(set);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  private expand(id: number): void {
    this.expandedModules.update((set) => new Set(set).add(id));
  }

  // ── Group (module) panel ──────────────────────────────────
  openCreateModule(): void {
    if (!this.selectedCourseId()) {
      this.toast.error('Select a course first.');
      return;
    }
    this.editingModule.set(null);
    this.moduleForm.reset({ title: '', summary: '', order_index: this.modules().length + 1 });
    this.modulePanelOpen.set(true);
  }

  openEditModule(module: ModuleInTree): void {
    this.editingModule.set(module);
    this.moduleForm.reset({
      title: module.title,
      summary: module.summary ?? '',
      order_index: module.order_index,
    });
    this.modulePanelOpen.set(true);
  }

  closeModulePanel(): void {
    this.modulePanelOpen.set(false);
    this.editingModule.set(null);
    this.moduleForm.reset();
  }

  saveModule(): void {
    if (this.moduleForm.invalid) return;
    const v = this.moduleForm.value;
    this.moduleSaveLoading.set(true);
    const editing = this.editingModule();
    if (editing) {
      this.adminService
        .updateModule(editing.id, { title: v.title, summary: v.summary, order_index: v.order_index })
        .subscribe({
          next: () => {
            this.moduleSaveLoading.set(false);
            this.toast.success('Group updated.');
            this.closeModulePanel();
            this.reloadTree();
          },
          error: () => {
            this.moduleSaveLoading.set(false);
            this.toast.error('Failed to update group.');
          },
        });
    } else {
      this.adminService
        .createModule({
          course_id: this.selectedCourseId(),
          title: v.title,
          summary: v.summary,
          order_index: v.order_index,
        })
        .subscribe({
          next: (m: any) => {
            this.moduleSaveLoading.set(false);
            this.toast.success('Group created.');
            if (m?.id) this.expand(m.id);
            this.closeModulePanel();
            this.reloadTree();
          },
          error: () => {
            this.moduleSaveLoading.set(false);
            this.toast.error('Failed to create group.');
          },
        });
    }
  }

  confirmDeleteModule(id: number): void {
    this.deletingModuleId.set(id);
  }

  cancelDeleteModule(): void {
    this.deletingModuleId.set(null);
  }

  executeDeleteModule(id: number): void {
    this.deleteModuleLoading.set(true);
    this.adminService.deleteModule(id).subscribe({
      next: () => {
        this.deletingModuleId.set(null);
        this.deleteModuleLoading.set(false);
        this.toast.success('Group deleted.');
        this.reloadTree();
      },
      error: () => {
        this.deleteModuleLoading.set(false);
        this.toast.error('Failed to delete group.');
      },
    });
  }

  // ── Lesson panel ──────────────────────────────────────────
  openCreate(moduleId?: number): void {
    const mods = this.modules();
    if (!mods.length) {
      this.toast.error('This course has no groups yet. Add a group first.');
      return;
    }
    const targetModule = mods.find((m) => m.id === moduleId) ?? mods[0];
    this.expand(targetModule.id);
    this.editingLesson.set(null);
    this.showPreview.set(false);
    this.lessonForm.reset({
      module_id: targetModule.id,
      title: '',
      slug: '',
      lesson_type: 'reading',
      content_md: '',
      video_url: '',
      duration_minutes: 5,
      order_index: targetModule.lessons.length + 1,
    });
    this.panelOpen.set(true);
  }

  openEdit(lesson: LessonInTree, moduleId: number): void {
    this.showPreview.set(false);
    this.panelOpen.set(true);
    this.loadingContent.set(true);
    this.editingLesson.set({ ...(lesson as unknown as Lesson), module_id: moduleId });
    // Fetch full lesson to get content_md / video_url (not present in the course tree).
    this.catalogService.getLesson(lesson.id).subscribe({
      next: (full) => {
        this.editingLesson.set(full);
        this.lessonForm.reset({
          module_id: full.module_id,
          title: full.title,
          slug: full.slug,
          lesson_type: full.lesson_type,
          content_md: full.content_md ?? '',
          video_url: full.video_url ?? '',
          duration_minutes: full.duration_minutes,
          order_index: full.order_index,
        });
        this.loadingContent.set(false);
      },
      error: () => {
        this.loadingContent.set(false);
        this.toast.error('Failed to load lesson content.');
        this.closePanel();
      },
    });
  }

  closePanel(): void {
    this.panelOpen.set(false);
    this.editingLesson.set(null);
    this.showPreview.set(false);
    this.lessonForm.reset();
  }

  onTitleChange(title: string): void {
    if (!this.editingLesson()) {
      const slug = title
        .toLowerCase()
        .replace(/[^a-z0-9\s-]/g, '')
        .replace(/\s+/g, '-')
        .replace(/-+/g, '-')
        .slice(0, 80);
      this.lessonForm.patchValue({ slug });
    }
  }

  togglePreview(): void {
    this.showPreview.update((v) => !v);
  }

  save(): void {
    if (this.lessonForm.invalid) return;
    const v = this.lessonForm.value;
    this.saveLoading.set(true);
    const editing = this.editingLesson();

    if (editing) {
      const payload = {
        title: v.title,
        slug: v.slug,
        lesson_type: v.lesson_type,
        content_md: v.content_md,
        video_url: v.video_url || null,
        duration_minutes: v.duration_minutes,
        order_index: v.order_index,
      };
      this.adminService.updateLesson(editing.id, payload).subscribe({
        next: () => {
          this.saveLoading.set(false);
          this.toast.success('Lesson updated.');
          this.closePanel();
          this.reloadTree();
        },
        error: () => {
          this.saveLoading.set(false);
          this.toast.error('Failed to update lesson.');
        },
      });
    } else {
      const payload = {
        module_id: v.module_id,
        title: v.title,
        slug: v.slug,
        lesson_type: v.lesson_type,
        content_md: v.content_md,
        video_url: v.video_url || null,
        duration_minutes: v.duration_minutes,
        order_index: v.order_index,
      };
      this.adminService.createLesson(payload).subscribe({
        next: () => {
          this.saveLoading.set(false);
          this.toast.success('Lesson created.');
          this.closePanel();
          this.reloadTree();
        },
        error: () => {
          this.saveLoading.set(false);
          this.toast.error('Failed to create lesson. Is the slug unique within the module?');
        },
      });
    }
  }

  // ── Delete ────────────────────────────────────────────────
  confirmDelete(id: number): void {
    this.deletingId.set(id);
  }

  cancelDelete(): void {
    this.deletingId.set(null);
  }

  executeDelete(id: number): void {
    this.deleteLoading.set(true);
    this.adminService.deleteLesson(id).subscribe({
      next: () => {
        this.deletingId.set(null);
        this.deleteLoading.set(false);
        this.toast.success('Lesson deleted.');
        this.reloadTree();
      },
      error: () => {
        this.deleteLoading.set(false);
        this.toast.error('Failed to delete lesson.');
      },
    });
  }

  // ── Helpers ───────────────────────────────────────────────
  lessonTypeBadge(type: LessonType): string {
    switch (type) {
      case 'video': return 'bg-purple-100 text-purple-700 dark:bg-purple-950 dark:text-purple-300';
      case 'exercise': return 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300';
      case 'quiz': return 'bg-cyan-100 text-cyan-700 dark:bg-cyan-950 dark:text-cyan-300';
      default: return 'bg-app-surface-2 text-app-text-2';
    }
  }

  totalLessons(): number {
    return this.modules().reduce((sum, m) => sum + m.lessons.length, 0);
  }
}
