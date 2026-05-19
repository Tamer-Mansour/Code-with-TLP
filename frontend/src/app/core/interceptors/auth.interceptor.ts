import { HttpInterceptorFn, HttpRequest, HttpHandlerFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { throwError, catchError, switchMap } from 'rxjs';
import { AuthService } from '../services/auth.service';

const SKIP_URLS = ['/auth/login', '/auth/register', '/auth/refresh'];

function shouldSkip(url: string): boolean {
  return SKIP_URLS.some((path) => url.includes(path));
}

function addAuthHeader(req: HttpRequest<unknown>, token: string): HttpRequest<unknown> {
  return req.clone({
    setHeaders: { Authorization: `Bearer ${token}` },
  });
}

export const authInterceptor: HttpInterceptorFn = (
  req: HttpRequest<unknown>,
  next: HttpHandlerFn
) => {
  const auth = inject(AuthService);

  if (shouldSkip(req.url)) {
    return next(req);
  }

  const token = auth.getAccessToken();
  const authReq = token ? addAuthHeader(req, token) : req;

  return next(authReq).pipe(
    catchError((error: unknown) => {
      if (error instanceof HttpErrorResponse && error.status === 401) {
        return auth.refreshToken().pipe(
          switchMap((tokens) => {
            const retryReq = addAuthHeader(req, tokens.access_token);
            return next(retryReq);
          }),
          catchError((refreshError: unknown) => {
            auth.logout();
            return throwError(() => refreshError);
          })
        );
      }
      return throwError(() => error);
    })
  );
};
