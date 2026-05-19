import { TestBed, ComponentFixture } from '@angular/core/testing';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { signal, computed } from '@angular/core';
import { provideRouter, Routes } from '@angular/router';
import { Component } from '@angular/core';

@Component({ template: '', standalone: true })
class StubComponent {}

const testRoutes: Routes = [
  { path: 'catalog', component: StubComponent },
  { path: 'login', component: StubComponent },
  { path: '**', component: StubComponent },
];
import { of, throwError } from 'rxjs';
import { ReactiveFormsModule } from '@angular/forms';
import {
  LucideAngularModule,
  Code2, Eye, EyeOff, AlertCircle,
} from 'lucide-angular';
import { RegisterComponent } from './register';
import { AuthService } from '../../../core/services/auth.service';
import { ToastService } from '../../../core/services/toast.service';

describe('RegisterComponent', () => {
  let fixture: ComponentFixture<RegisterComponent>;
  let component: RegisterComponent;
  let mockAuth: {
    currentUser: ReturnType<typeof signal>;
    isAuthenticated: ReturnType<typeof computed>;
    isAdmin: ReturnType<typeof computed>;
    register: ReturnType<typeof vi.fn>;
    login: ReturnType<typeof vi.fn>;
    logout: ReturnType<typeof vi.fn>;
  };
  let mockToast: {
    success: ReturnType<typeof vi.fn>;
    error: ReturnType<typeof vi.fn>;
    toasts: ReturnType<typeof signal>;
  };

  const validFormValue = {
    username: 'newuser',
    email: 'new@example.com',
    full_name: 'New User',
    password: 'password123',
    confirm_password: 'password123',
  };

  beforeEach(async () => {
    const currentUser = signal(null);
    mockAuth = {
      currentUser,
      isAuthenticated: computed(() => !!currentUser()),
      isAdmin: computed(() => false),
      register: vi.fn().mockReturnValue(of({})),
      login: vi.fn().mockReturnValue(of({})),
      logout: vi.fn(),
    };

    mockToast = {
      success: vi.fn(),
      error: vi.fn(),
      toasts: signal([]),
    };

    await TestBed.configureTestingModule({
      imports: [
        RegisterComponent,
        ReactiveFormsModule,
        LucideAngularModule.pick({ Code2, Eye, EyeOff, AlertCircle }),
      ],
      providers: [
        provideRouter(testRoutes),
        { provide: AuthService, useValue: mockAuth },
        { provide: ToastService, useValue: mockToast },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(RegisterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize loading as false', () => {
    expect(component.loading()).toBe(false);
  });

  it('should initialize showPassword and showConfirm as false', () => {
    expect(component.showPassword()).toBe(false);
    expect(component.showConfirm()).toBe(false);
  });

  it('should initialize errorMessage as empty string', () => {
    expect(component.errorMessage()).toBe('');
  });

  it('should have all required form controls', () => {
    expect(component.usernameCtrl).toBeTruthy();
    expect(component.emailCtrl).toBeTruthy();
    expect(component.fullNameCtrl).toBeTruthy();
    expect(component.passwordCtrl).toBeTruthy();
    expect(component.confirmPasswordCtrl).toBeTruthy();
  });

  it('should be invalid when form is empty', () => {
    expect(component.form.invalid).toBe(true);
  });

  it('should be valid with all required fields filled and matching passwords', () => {
    component.form.setValue(validFormValue);
    expect(component.form.valid).toBe(true);
  });

  it('should be invalid when passwords do not match', () => {
    component.form.setValue({ ...validFormValue, confirm_password: 'differentpass' });
    expect(component.form.hasError('passwordsMismatch')).toBe(true);
  });

  it('should be invalid when username is too short', () => {
    component.form.setValue({ ...validFormValue, username: 'ab' });
    expect(component.usernameCtrl.hasError('minlength')).toBe(true);
  });

  it('should be invalid when username has invalid characters', () => {
    component.form.setValue({ ...validFormValue, username: 'bad user!' });
    expect(component.usernameCtrl.hasError('pattern')).toBe(true);
  });

  it('should be invalid with an invalid email', () => {
    component.form.setValue({ ...validFormValue, email: 'not-an-email' });
    expect(component.emailCtrl.hasError('email')).toBe(true);
  });

  it('should be invalid when password is shorter than 8 characters', () => {
    component.form.setValue({ ...validFormValue, password: 'short', confirm_password: 'short' });
    expect(component.passwordCtrl.hasError('minlength')).toBe(true);
  });

  it('should toggle showPassword on togglePassword()', () => {
    component.togglePassword();
    expect(component.showPassword()).toBe(true);
    component.togglePassword();
    expect(component.showPassword()).toBe(false);
  });

  it('should toggle showConfirm on toggleConfirm()', () => {
    component.toggleConfirm();
    expect(component.showConfirm()).toBe(true);
    component.toggleConfirm();
    expect(component.showConfirm()).toBe(false);
  });

  it('should mark all controls touched on invalid submit', () => {
    component.onSubmit();
    expect(component.usernameCtrl.touched).toBe(true);
    expect(component.emailCtrl.touched).toBe(true);
    expect(component.passwordCtrl.touched).toBe(true);
    expect(component.confirmPasswordCtrl.touched).toBe(true);
  });

  it('should not call auth.register on invalid form submit', () => {
    component.onSubmit();
    expect(mockAuth.register).not.toHaveBeenCalled();
  });

  it('should call auth.register with correct data on valid submit', () => {
    component.form.setValue(validFormValue);
    component.onSubmit();
    expect(mockAuth.register).toHaveBeenCalledWith({
      username: 'newuser',
      email: 'new@example.com',
      password: 'password123',
      full_name: 'New User',
    });
  });

  it('should call auth.login after successful registration', () => {
    component.form.setValue(validFormValue);
    component.onSubmit();
    expect(mockAuth.login).toHaveBeenCalledWith({
      identifier: 'new@example.com',
      password: 'password123',
    });
  });

  it('should set errorMessage on registration failure', () => {
    const errorResponse = { error: { detail: 'Username already taken.' } };
    mockAuth.register.mockReturnValue(throwError(() => errorResponse));
    component.form.setValue(validFormValue);
    component.onSubmit();
    expect(component.errorMessage()).toBe('Username already taken.');
  });

  it('should handle array detail error messages', () => {
    const errorResponse = { error: { detail: [{ msg: 'Field error 1' }, { msg: 'Field error 2' }] } };
    mockAuth.register.mockReturnValue(throwError(() => errorResponse));
    component.form.setValue(validFormValue);
    component.onSubmit();
    expect(component.errorMessage()).toBe('Field error 1, Field error 2');
  });

  it('should call toast.error on registration failure', () => {
    mockAuth.register.mockReturnValue(throwError(() => ({ error: { detail: 'Error' } })));
    component.form.setValue(validFormValue);
    component.onSubmit();
    expect(mockToast.error).toHaveBeenCalled();
  });

  it('should not submit when loading is true', () => {
    component.loading.set(true);
    component.form.setValue(validFormValue);
    component.onSubmit();
    expect(mockAuth.register).not.toHaveBeenCalled();
  });

  it('passwordsMismatch getter returns false when passwords match and not touched', () => {
    component.form.setValue(validFormValue);
    expect(component.passwordsMismatch).toBe(false);
  });

  it('passwordsMismatch getter returns true when passwords differ and confirm is touched', () => {
    component.form.setValue({ ...validFormValue, confirm_password: 'different' });
    component.confirmPasswordCtrl.markAsTouched();
    expect(component.passwordsMismatch).toBe(true);
  });
});
