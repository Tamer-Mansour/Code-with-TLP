import {
  Component,
  OnInit,
  inject,
  signal,
  ChangeDetectionStrategy,
} from '@angular/core';
import { NgClass } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { LucideAngularModule } from 'lucide-angular';
import { AdminService } from '../../../core/services/admin.service';
import { CatalogService } from '../../../core/services/catalog.service';
import { ToastService } from '../../../core/services/toast.service';
import { Course, Subject } from '../../../core/models/types';

@Component({
  selector: 'app-admin-courses',
  standalone: true,
  templateUrl: './admin-courses.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [NgClass, FormsModule, ReactiveFormsModule, LucideAngularModule],
})
export class AdminCoursesComponent implements OnInit {
  private readonly adminService = inject(AdminService);
  private readonly catalogService = inject(CatalogService);
  private readonly toast = inject(ToastService);
  private readonly fb = inject(FormBuilder);

  // ── State ─────────────────────────────────────────────────
  courses = signal<Course[]>([]);
  subjects = signal<Subject[]>([]);
  loading = signal(true);
  panelOpen = signal(false);
  editingCourse = signal<Course | null>(null);
  saveLoading = signal(false);
  deletingId = signal<number | null>(null);
  deleteLoading = signal(false);

  courseForm = this.fb.group({
    title: ['', [Validators.required, Validators.minLength(3)]],
    slug: ['', [Validators.required]],
    summary: [''],
    difficulty: ['beginner', Validators.required],
    subject_id: [null as number | null],
    is_published: [false],
  });

  ngOnInit(): void {
    this.loadCourses();
    this.catalogService.getSubjects().subscribe({
      next: (subs) => this.subjects.set(subs),
    });
  }

  private loadCourses(): void {
    this.loading.set(true);
    this.adminService.getCourses().subscribe({
      next: (courses) => {
        this.courses.set(courses);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.toast.error('Failed to load courses.');
      },
    });
  }

  openCreate(): void {
    this.editingCourse.set(null);
    this.courseForm.reset({ difficulty: 'beginner', is_published: false });
    this.panelOpen.set(true);
  }

  openEdit(course: Course): void {
    this.editingCourse.set(course);
    this.courseForm.reset({
      title: course.title,
      slug: course.slug,
      summary: course.summary ?? '',
      difficulty: course.difficulty,
      subject_id: course.subject_id,
      is_published: course.is_published,
    });
    this.panelOpen.set(true);
  }

  closePanel(): void {
    this.panelOpen.set(false);
    this.editingCourse.set(null);
    this.courseForm.reset();
  }

  onTitleChange(title: string): void {
    if (!this.editingCourse()) {
      const slug = title
        .toLowerCase()
        .replace(/[^a-z0-9\s-]/g, '')
        .replace(/\s+/g, '-')
        .replace(/-+/g, '-')
        .slice(0, 80);
      this.courseForm.patchValue({ slug });
    }
  }

  save(): void {
    if (this.courseForm.invalid) return;
    const val = this.courseForm.value;
    this.saveLoading.set(true);
    const editing = this.editingCourse();

    const obs = editing
      ? this.adminService.updateCourse(editing.id, val)
      : this.adminService.createCourse(val);

    obs.subscribe({
      next: (course) => {
        if (editing) {
          this.courses.update((list) => list.map((c) => (c.id === course.id ? course : c)));
          this.toast.success('Course updated.');
        } else {
          this.courses.update((list) => [course, ...list]);
          this.toast.success('Course created.');
        }
        this.saveLoading.set(false);
        this.closePanel();
      },
      error: () => {
        this.saveLoading.set(false);
        this.toast.error('Failed to save course.');
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
    this.adminService.deleteCourse(id).subscribe({
      next: () => {
        this.courses.update((list) => list.filter((c) => c.id !== id));
        this.deletingId.set(null);
        this.deleteLoading.set(false);
        this.toast.success('Course deleted.');
      },
      error: () => {
        this.deleteLoading.set(false);
        this.toast.error('Failed to delete course.');
      },
    });
  }

  getDifficultyBadge(difficulty: string): string {
    if (difficulty === 'beginner') return 'badge-easy';
    if (difficulty === 'intermediate') return 'badge-medium';
    return 'badge-hard';
  }

  getSubjectName(subjectId: number): string {
    return this.subjects().find((s) => s.id === subjectId)?.name ?? '—';
  }
}
