import {
  Component,
  inject,
  signal,
  ChangeDetectionStrategy,
  DestroyRef,
} from '@angular/core';
import { RouterLink, Router } from '@angular/router';
import {
  ReactiveFormsModule,
  FormGroup,
  FormControl,
  Validators,
  AbstractControl,
  ValidationErrors,
} from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { switchMap } from 'rxjs/operators';
import { LucideAngularModule, Code2, Eye, EyeOff, AlertCircle } from 'lucide-angular';
import { AuthService } from '../../../core/services/auth.service';
import { ToastService } from '../../../core/services/toast.service';

function passwordsMatch(group: AbstractControl): ValidationErrors | null {
  const pw  = group.get('password')?.value;
  const pw2 = group.get('confirm_password')?.value;
  return pw && pw2 && pw !== pw2 ? { passwordsMismatch: true } : null;
}

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [RouterLink, ReactiveFormsModule, LucideAngularModule],
  templateUrl: './register.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RegisterComponent {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  private readonly toast = inject(ToastService);
  private readonly destroyRef = inject(DestroyRef);

  readonly Code2 = Code2;
  readonly Eye = Eye;
  readonly EyeOff = EyeOff;
  readonly AlertCircle = AlertCircle;

  readonly loading = signal(false);
  readonly showPassword = signal(false);
  readonly showConfirm = signal(false);
  readonly errorMessage = signal('');

  readonly form = new FormGroup(
    {
      username: new FormControl('', [
        Validators.required,
        Validators.minLength(3),
        Validators.pattern(/^[a-zA-Z0-9_.-]+$/),
      ]),
      email: new FormControl('', [Validators.required, Validators.email]),
      full_name: new FormControl(''),
      password: new FormControl('', [Validators.required, Validators.minLength(8)]),
      confirm_password: new FormControl('', [Validators.required]),
    },
    { validators: passwordsMatch }
  );

  get usernameCtrl()        { return this.form.controls.username; }
  get emailCtrl()           { return this.form.controls.email; }
  get fullNameCtrl()        { return this.form.controls.full_name; }
  get passwordCtrl()        { return this.form.controls.password; }
  get confirmPasswordCtrl() { return this.form.controls.confirm_password; }

  get passwordsMismatch(): boolean {
    return this.form.hasError('passwordsMismatch') &&
      (this.confirmPasswordCtrl.touched || this.confirmPasswordCtrl.dirty);
  }

  togglePassword(): void { this.showPassword.update(v => !v); }
  toggleConfirm(): void  { this.showConfirm.update(v => !v); }

  onSubmit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    if (this.loading()) return;

    this.loading.set(true);
    this.errorMessage.set('');

    const { username, email, full_name, password } = this.form.getRawValue();

    const req = {
      username: username!,
      email: email!,
      password: password!,
      ...(full_name ? { full_name } : {}),
    };

    this.auth.register(req)
      .pipe(
        takeUntilDestroyed(this.destroyRef),
        switchMap(() => this.auth.login({ identifier: email!, password: password! }))
      )
      .subscribe({
        next: () => {
          this.loading.set(false);
          this.toast.success('Account created! Welcome to StudyingApp.');
          this.router.navigate(['/catalog']);
        },
        error: (err) => {
          this.loading.set(false);
          const detail = err?.error?.detail;
          const msg = Array.isArray(detail)
            ? detail.map((d: any) => d.msg).join(', ')
            : detail || err?.message || 'Registration failed. Please try again.';
          this.errorMessage.set(msg);
          this.toast.error(msg);
        },
      });
  }
}
