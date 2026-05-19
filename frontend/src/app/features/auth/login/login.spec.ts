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
import { LoginComponent } from './login';
import { AuthService } from '../../../core/services/auth.service';
import { ToastService } from '../../../core/services/toast.service';

describe('LoginComponent', () => {
  let fixture: ComponentFixture<LoginComponent>;
  let component: LoginComponent;
  let mockAuth: {
    currentUser: ReturnType<typeof signal>;
    isAuthenticated: ReturnType<typeof computed>;
    isAdmin: ReturnType<typeof computed>;
    login: ReturnType<typeof vi.fn>;
    logout: ReturnType<typeof vi.fn>;
  };
  let mockToast: {
    success: ReturnType<typeof vi.fn>;
    error: ReturnType<typeof vi.fn>;
    toasts: ReturnType<typeof signal>;
  };

  beforeEach(async () => {
    const currentUser = signal(null);
    mockAuth = {
      currentUser,
      isAuthenticated: computed(() => !!currentUser()),
      isAdmin: computed(() => false),
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
        LoginComponent,
        ReactiveFormsModule,
        LucideAngularModule.pick({ Code2, Eye, EyeOff, AlertCircle }),
      ],
      providers: [
        provideRouter(testRoutes),
        { provide: AuthService, useValue: mockAuth },
        { provide: ToastService, useValue: mockToast },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(LoginComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize loading as false', () => {
    expect(component.loading()).toBe(false);
  });

  it('should initialize showPassword as false', () => {
    expect(component.showPassword()).toBe(false);
  });

  it('should initialize errorMessage as empty string', () => {
    expect(component.errorMessage()).toBe('');
  });

  it('should have identifier and password form controls', () => {
    expect(component.identifierCtrl).toBeTruthy();
    expect(component.passwordCtrl).toBeTruthy();
  });

  it('should mark form controls as invalid when empty', () => {
    expect(component.form.invalid).toBe(true);
    // Controls have the error immediately even before touching
    expect(component.identifierCtrl.hasError('required')).toBe(true);
    expect(component.passwordCtrl.hasError('required')).toBe(true);
  });

  it('should be valid when identifier and password are filled', () => {
    component.form.setValue({ identifier: 'testuser', password: 'secret123' });
    expect(component.form.valid).toBe(true);
  });

  it('should toggle showPassword on togglePassword()', () => {
    expect(component.showPassword()).toBe(false);
    component.togglePassword();
    expect(component.showPassword()).toBe(true);
    component.togglePassword();
    expect(component.showPassword()).toBe(false);
  });

  it('should not call auth.login when form is invalid on submit', () => {
    component.form.setValue({ identifier: '', password: '' });
    component.onSubmit();
    expect(mockAuth.login).not.toHaveBeenCalled();
  });

  it('should mark all controls as touched on invalid submit', () => {
    component.form.setValue({ identifier: '', password: '' });
    component.onSubmit();
    expect(component.identifierCtrl.touched).toBe(true);
    expect(component.passwordCtrl.touched).toBe(true);
  });

  it('should call auth.login with correct credentials on valid submit', () => {
    component.form.setValue({ identifier: 'user@test.com', password: 'password1' });
    component.onSubmit();
    expect(mockAuth.login).toHaveBeenCalledWith({
      identifier: 'user@test.com',
      password: 'password1',
    });
  });

  it('should set loading to true during submit and false on success', () => {
    component.form.setValue({ identifier: 'user@test.com', password: 'password1' });
    mockAuth.login.mockReturnValue(of({}));
    component.onSubmit();
    // After observable completes synchronously, loading should be false
    expect(component.loading()).toBe(false);
  });

  it('should set errorMessage on login failure', () => {
    const errorResponse = { error: { detail: 'Invalid credentials.' } };
    mockAuth.login.mockReturnValue(throwError(() => errorResponse));
    component.form.setValue({ identifier: 'bad@user.com', password: 'wrongpass' });
    component.onSubmit();
    expect(component.errorMessage()).toBe('Invalid credentials.');
  });

  it('should call toast.error on login failure', () => {
    const errorResponse = { error: { detail: 'Invalid credentials.' } };
    mockAuth.login.mockReturnValue(throwError(() => errorResponse));
    component.form.setValue({ identifier: 'bad@user.com', password: 'wrongpass' });
    component.onSubmit();
    expect(mockToast.error).toHaveBeenCalled();
  });

  it('should not re-submit when loading is true', () => {
    component.loading.set(true);
    component.form.setValue({ identifier: 'user@test.com', password: 'password1' });
    component.onSubmit();
    expect(mockAuth.login).not.toHaveBeenCalled();
  });
});
