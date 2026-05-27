import {
  Component,
  inject,
  signal,
  computed,
  OnInit,
  ChangeDetectionStrategy,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import {
  LucideAngularModule,
  Key, Plus, Trash2, Eye, EyeOff, Loader2, Bot, ChevronDown, AlertCircle,
} from 'lucide-angular';
import { ChatService, AiProvider, AiKey, AiKeyCreate } from '../../../core/services/chat.service';

@Component({
  selector: 'app-ai-keys',
  standalone: true,
  imports: [FormsModule, LucideAngularModule, RouterLink],
  templateUrl: './ai-keys.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AiKeysComponent implements OnInit {
  private readonly chatSvc = inject(ChatService);

  // Icons
  readonly Key          = Key;
  readonly Plus         = Plus;
  readonly Trash2       = Trash2;
  readonly Eye          = Eye;
  readonly EyeOff       = EyeOff;
  readonly Loader2      = Loader2;
  readonly Bot          = Bot;
  readonly ChevronDown  = ChevronDown;
  readonly AlertCircle  = AlertCircle;

  // Data
  readonly providers    = signal<AiProvider[]>([]);
  readonly keys         = signal<AiKey[]>([]);
  readonly loading      = signal(false);
  readonly submitting   = signal(false);
  readonly deletingId   = signal<string | null>(null);
  readonly errorMsg     = signal<string | null>(null);
  readonly successMsg   = signal<string | null>(null);

  // Form state
  readonly form = signal<AiKeyCreate>({
    provider: '',
    api_key: '',
    base_url: '',
    default_model: '',
    label: '',
  });
  readonly showApiKey   = signal(false);
  readonly showAddForm  = signal(false);

  // Derived: models for selected provider
  readonly selectedProvider = computed<AiProvider | undefined>(() => {
    return this.providers().find(p => p.id === this.form().provider);
  });

  ngOnInit(): void {
    this.loadAll();
  }

  private loadAll(): void {
    this.loading.set(true);
    this.chatSvc.getProviders().subscribe({
      next: ps => {
        this.providers.set(ps);
        this.chatSvc.getKeys().subscribe({
          next: ks => {
            this.keys.set(ks);
            this.loading.set(false);
          },
          error: () => this.loading.set(false),
        });
      },
      error: () => this.loading.set(false),
    });
  }

  onProviderChange(providerId: string): void {
    const provider = this.providers().find(p => p.id === providerId);
    this.form.update(f => ({
      ...f,
      provider: providerId,
      base_url: provider?.base_url ?? '',
      default_model: provider?.models[0] ?? '',
    }));
  }

  patchForm(patch: Partial<AiKeyCreate>): void {
    this.form.update(f => ({ ...f, ...patch }));
  }

  toggleForm(): void {
    this.showAddForm.update(v => !v);
    this.errorMsg.set(null);
    this.successMsg.set(null);
  }

  submit(): void {
    const f = this.form();
    if (!f.provider || !f.api_key.trim()) {
      this.errorMsg.set('Provider and API key are required.');
      return;
    }

    const payload: AiKeyCreate = {
      provider: f.provider,
      api_key: f.api_key.trim(),
    };
    if (f.base_url?.trim()) payload.base_url = f.base_url.trim();
    if (f.default_model?.trim()) payload.default_model = f.default_model.trim();
    if (f.label?.trim()) payload.label = f.label.trim();

    this.submitting.set(true);
    this.errorMsg.set(null);

    this.chatSvc.addKey(payload).subscribe({
      next: key => {
        this.keys.update(ks => [key, ...ks]);
        this.submitting.set(false);
        this.successMsg.set('API key added successfully.');
        this.showAddForm.set(false);
        this.form.set({ provider: '', api_key: '', base_url: '', default_model: '', label: '' });
        setTimeout(() => this.successMsg.set(null), 3000);
      },
      error: (err) => {
        this.submitting.set(false);
        this.errorMsg.set(err?.error?.detail ?? 'Failed to add key. Please try again.');
      },
    });
  }

  deleteKey(id: string): void {
    this.deletingId.set(id);
    this.chatSvc.deleteKey(id).subscribe({
      next: () => {
        this.keys.update(ks => ks.filter(k => k.id !== id));
        this.deletingId.set(null);
      },
      error: () => this.deletingId.set(null),
    });
  }

  getProviderName(providerId: string): string {
    return this.providers().find(p => p.id === providerId)?.name ?? providerId;
  }
}
