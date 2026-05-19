import {
  Component,
  OnInit,
  OnDestroy,
  inject,
  signal,
  computed,
  ChangeDetectionStrategy,
} from '@angular/core';
import { NgClass, SlicePipe } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { LucideAngularModule } from 'lucide-angular';
import { Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged, takeUntil } from 'rxjs/operators';
import { AdminService } from '../../../core/services/admin.service';
import { ToastService } from '../../../core/services/toast.service';
import { User, UserRole } from '../../../core/models/types';

@Component({
  selector: 'app-admin-users',
  standalone: true,
  templateUrl: './admin-users.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [NgClass, SlicePipe, FormsModule, ReactiveFormsModule, LucideAngularModule],
})
export class AdminUsersComponent implements OnInit, OnDestroy {
  private readonly adminService = inject(AdminService);
  private readonly toast = inject(ToastService);
  private readonly fb = inject(FormBuilder);
  private readonly destroy$ = new Subject<void>();

  // ── State ─────────────────────────────────────────────────
  users = signal<User[]>([]);
  loading = signal(true);
  searchQuery = signal('');
  roleFilter = signal<string>('');

  // Edit modal
  editingUser = signal<User | null>(null);
  editLoading = signal(false);
  editForm = this.fb.group({
    role: ['student' as UserRole, Validators.required],
    is_active: [true],
    password: [''],
  });

  // Delete confirm
  deletingUserId = signal<number | null>(null);
  deleteLoading = signal(false);

  // Search debounce subject
  private searchSubject = new Subject<string>();

  // ── Computed ──────────────────────────────────────────────
  filteredUsers = computed(() => {
    const q = this.searchQuery().toLowerCase();
    const role = this.roleFilter();
    return this.users().filter((u) => {
      const matchQ = !q || u.username.toLowerCase().includes(q) || u.email.toLowerCase().includes(q);
      const matchRole = !role || u.role === role;
      return matchQ && matchRole;
    });
  });

  ngOnInit(): void {
    this.loadUsers();

    // Debounced search (client-side filter in this case, but could trigger API)
    this.searchSubject.pipe(
      debounceTime(300),
      distinctUntilChanged(),
      takeUntil(this.destroy$)
    ).subscribe((q) => this.searchQuery.set(q));
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private loadUsers(): void {
    this.loading.set(true);
    this.adminService.getUsers().subscribe({
      next: (users) => {
        this.users.set(users);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.toast.error('Failed to load users.');
      },
    });
  }

  onSearch(query: string): void {
    this.searchSubject.next(query);
  }

  setRoleFilter(role: string): void {
    this.roleFilter.set(role);
  }

  openEdit(user: User): void {
    this.editingUser.set(user);
    this.editForm.reset({
      role: user.role,
      is_active: user.is_active,
      password: '',
    });
  }

  closeEdit(): void {
    this.editingUser.set(null);
    this.editForm.reset();
  }

  saveEdit(): void {
    const user = this.editingUser();
    if (!user || this.editForm.invalid) return;
    const val = this.editForm.value;
    const payload: Record<string, unknown> = {
      role: val.role,
      is_active: val.is_active,
    };
    if (val.password) payload['password'] = val.password;

    this.editLoading.set(true);
    this.adminService.updateUser(user.id, payload).subscribe({
      next: (updated) => {
        this.users.update((list) => list.map((u) => (u.id === updated.id ? updated : u)));
        this.editLoading.set(false);
        this.closeEdit();
        this.toast.success('User updated successfully.');
      },
      error: () => {
        this.editLoading.set(false);
        this.toast.error('Failed to update user.');
      },
    });
  }

  confirmDelete(userId: number): void {
    this.deletingUserId.set(userId);
  }

  cancelDelete(): void {
    this.deletingUserId.set(null);
  }

  executeDelete(userId: number): void {
    this.deleteLoading.set(true);
    this.adminService.deleteUser(userId).subscribe({
      next: () => {
        this.users.update((list) => list.filter((u) => u.id !== userId));
        this.deletingUserId.set(null);
        this.deleteLoading.set(false);
        this.toast.success('User deleted successfully.');
      },
      error: () => {
        this.deleteLoading.set(false);
        this.toast.error('Failed to delete user.');
      },
    });
  }

  getUserInitials(user: User): string {
    const name = user.full_name ?? user.username ?? '';
    return name.split(' ').map((w) => w[0]).join('').toUpperCase().slice(0, 2);
  }

  getRoleBadgeClass(role: UserRole): string {
    return role === 'admin'
      ? 'px-2 py-0.5 rounded-full text-xs font-medium bg-purple-900/60 text-purple-300 border border-purple-700/50'
      : 'px-2 py-0.5 rounded-full text-xs font-medium bg-blue-900/60 text-blue-300 border border-blue-700/50';
  }
}
