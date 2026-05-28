import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { adminGuard } from './core/guards/admin.guard';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./features/landing/landing.component').then((m) => m.LandingComponent),
  },
  {
    path: 'login',
    loadComponent: () =>
      import('./features/auth/login/login').then((m) => m.LoginComponent),
  },
  {
    path: 'register',
    loadComponent: () =>
      import('./features/auth/register/register').then((m) => m.RegisterComponent),
  },
  {
    path: 'catalog',
    loadComponent: () =>
      import('./features/catalog/home/home').then((m) => m.HomeComponent),
  },
  {
    path: 'catalog/subjects/:slug',
    loadComponent: () =>
      import('./features/catalog/subject-detail/subject-detail').then(
        (m) => m.SubjectDetailComponent
      ),
  },
  {
    path: 'catalog/courses/:slug',
    loadComponent: () =>
      import('./features/catalog/course-detail/course-detail').then(
        (m) => m.CourseDetailComponent
      ),
  },
  {
    path: 'catalog/lessons/:id',
    loadComponent: () =>
      import('./features/catalog/lesson-reader/lesson-reader').then(
        (m) => m.LessonReaderComponent
      ),
  },
  {
    path: 'exercises',
    loadComponent: () =>
      import('./features/catalog/exercise-list/exercise-list').then(
        (m) => m.ExerciseListComponent
      ),
  },
  {
    path: 'exercises/:slug',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./features/exercises/exercise-page/exercise-page.component').then(
        (m) => m.ExercisePageComponent
      ),
  },
  {
    path: 'dashboard',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./features/dashboard/dashboard.component').then((m) => m.DashboardComponent),
  },
  {
    path: 'profile',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./features/profile/profile.component').then((m) => m.ProfileComponent),
  },
  {
    path: 'admin',
    canActivate: [authGuard, adminGuard],
    loadComponent: () =>
      import('./features/admin/admin-layout/admin-layout.component').then(
        (m) => m.AdminLayoutComponent
      ),
    children: [
      {
        path: '',
        redirectTo: 'stats',
        pathMatch: 'full',
      },
      {
        path: 'stats',
        loadComponent: () =>
          import('./features/admin/admin-stats/admin-stats.component').then(
            (m) => m.AdminStatsComponent
          ),
      },
      {
        path: 'users',
        loadComponent: () =>
          import('./features/admin/admin-users/admin-users.component').then(
            (m) => m.AdminUsersComponent
          ),
      },
      {
        path: 'courses',
        loadComponent: () =>
          import('./features/admin/admin-courses/admin-courses.component').then(
            (m) => m.AdminCoursesComponent
          ),
      },
      {
        path: 'lessons',
        loadComponent: () =>
          import('./features/admin/admin-lessons/admin-lessons.component').then(
            (m) => m.AdminLessonsComponent
          ),
      },
      {
        path: 'exercises',
        loadComponent: () =>
          import('./features/admin/admin-exercises/admin-exercises.component').then(
            (m) => m.AdminExercisesComponent
          ),
      },
      {
        path: 'submissions',
        loadComponent: () =>
          import('./features/admin/admin-submissions/admin-submissions.component').then(
            (m) => m.AdminSubmissionsComponent
          ),
      },
    ],
  },
  {
    path: 'visualize',
    loadComponent: () =>
      import('./features/visualizers/catalog/catalog.component').then(
        m => m.VizCatalogComponent
      ),
  },
  {
    path: 'visualize/:slug',
    loadComponent: () =>
      import('./features/visualizers/viz-page/viz-page.component').then(
        m => m.VizPageComponent
      ),
  },
  {
    path: 'chat',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./features/chat/chat-page/chat-page.component').then(
        m => m.ChatPageComponent
      ),
  },
  {
    path: 'settings/ai-keys',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./features/chat/ai-keys/ai-keys.component').then(
        m => m.AiKeysComponent
      ),
  },
  {
    path: 'interview',
    loadComponent: () =>
      import('./features/interview/interview-list/interview-list.component').then(
        (m) => m.InterviewListComponent
      ),
  },
  {
    path: 'interview/:slug',
    loadComponent: () =>
      import('./features/interview/interview-category/interview-category.component').then(
        (m) => m.InterviewCategoryComponent
      ),
  },
  {
    path: '**',
    redirectTo: '/catalog',
  },
];
