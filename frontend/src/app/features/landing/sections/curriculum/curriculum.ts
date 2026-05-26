import { Component, ChangeDetectionStrategy } from '@angular/core';
import { LucideAngularModule, Lightbulb, Cpu, Code, Terminal, Globe, Database, Server, Sigma, GitBranch, Brain } from 'lucide-angular';
import { RevealDirective } from '../../shared/reveal.directive';

interface SubjectCard { name: string; tagline: string; color: string; icon: any; }

@Component({
  selector: 'app-landing-curriculum',
  standalone: true,
  imports: [LucideAngularModule, RevealDirective],
  templateUrl: './curriculum.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LandingCurriculumComponent {
  readonly subjects: SubjectCard[] = [
    { name: 'Foundations', tagline: 'How computing works', color: '#8b5cf6', icon: Lightbulb },
    { name: 'Algorithms', tagline: 'Data structures & algorithms', color: '#3b82f6', icon: Cpu },
    { name: 'Programming', tagline: 'Paradigms & clean code', color: '#06b6d4', icon: Code },
    { name: 'Languages', tagline: 'Python & more', color: '#6366f1', icon: Terminal },
    { name: 'Web Development', tagline: 'Modern frontend', color: '#10b981', icon: Globe },
    { name: 'Databases', tagline: 'SQL & data modeling', color: '#f59e0b', icon: Database },
    { name: 'Systems', tagline: 'OS, architecture, networks', color: '#ef4444', icon: Server },
    { name: 'Theory', tagline: 'Computation & complexity', color: '#ec4899', icon: Sigma },
    { name: 'Software Engineering', tagline: 'Build & ship software', color: '#14b8a6', icon: GitBranch },
    { name: 'Artificial Intelligence', tagline: 'ML, search & LLMs', color: '#f97316', icon: Brain },
  ];

  readonly courses = [
    'Introduction to Computer Science', 'Discrete Mathematics', 'Data Structures',
    'Object-Oriented Programming', 'Computer Architecture', 'Operating Systems',
    'Computer Networks', 'Theory of Computation', 'Software Engineering',
    'Intro to AI & Machine Learning', 'SQL Fundamentals', 'Modern Frontend with Angular',
    'Python Programming', 'Introduction to Algorithms',
  ];
}
