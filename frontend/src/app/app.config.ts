import { ApplicationConfig, provideAppInitializer, inject } from '@angular/core';
import { provideRouter, withComponentInputBinding } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideMarkdown } from 'ngx-markdown';
import {
  LUCIDE_ICONS, LucideIconProvider,
  Activity, AlertTriangle, ArrowLeft, ArrowRight, Award, BarChart2,
  BookOpen, Calendar, CheckCircle, CheckCircle2, ChevronDown, ChevronUp,
  Clock, Code2, Cpu, Filter, Flame, FlaskConical, Frown,
  GraduationCap, Image, Inbox, Library, Loader2, Lock, LogOut,
  Pencil, Percent, Play, Plus, RefreshCw, Search, Send,
  Shield, SquareCode, Star, Target, Terminal, Trash2, TrendingUp,
  Trophy, User, Users, X, XCircle, Zap,
} from 'lucide-angular';
import { routes } from './app.routes';
import { authInterceptor } from './core/interceptors/auth.interceptor';
import { AuthService } from './core/services/auth.service';
import { ThemeService } from './core/services/theme.service';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes, withComponentInputBinding()),
    provideHttpClient(withInterceptors([authInterceptor])),
    provideMarkdown(),
    {
      provide: LUCIDE_ICONS,
      useValue: new LucideIconProvider({
        Activity, AlertTriangle, ArrowLeft, ArrowRight, Award, BarChart2,
        BookOpen, Calendar, CheckCircle, CheckCircle2, ChevronDown, ChevronUp,
        Clock, Code2, Cpu, Filter, Flame, FlaskConical, Frown,
        GraduationCap, Image, Inbox, Library, Loader2, Lock, LogOut,
        Pencil, Percent, Play, Plus, RefreshCw, Search, Send,
        Shield, SquareCode, Star, Target, Terminal, Trash2, TrendingUp,
        Trophy, User, Users, X, XCircle, Zap,
      }),
      multi: true,
    },
    provideAppInitializer(() => {
      inject(ThemeService).initialize();
      return inject(AuthService).initialize();
    }),
  ],
};
