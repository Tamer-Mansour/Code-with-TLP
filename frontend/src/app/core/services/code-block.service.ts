import { Injectable } from '@angular/core';
import type { CodeArtifact, MessagePart } from '../models/chat-ui.model';

/**
 * Splits assistant markdown into ordered text + fenced-code parts.
 *
 * The parser is **streaming-aware**: a trailing code fence with no closing
 * fence yet (because tokens are still arriving) is returned as an incomplete
 * artifact (`complete: false`) so the side panel can render it live, exactly
 * like Claude lifting code into an artifact while it types.
 */
@Injectable({ providedIn: 'root' })
export class CodeBlockService {
  /** Fenced blocks at/above this line count auto-open the side panel. */
  readonly AUTO_OPEN_MIN_LINES = 3;

  private static readonly OPEN_FENCE = /^(\s{0,3})(`{3,}|~{3,})[ \t]*([\w+#.\-]*)[ \t]*$/;
  private static readonly CLOSE_FENCE = /^(\s{0,3})(`{3,}|~{3,})[ \t]*$/;

  /** Parse markdown into ordered parts. Every fenced block becomes a code part. */
  segment(markdown: string): MessagePart[] {
    if (!markdown) return [];

    const lines = markdown.split('\n');
    const parts: MessagePart[] = [];
    let textBuf: string[] = [];
    let ordinal = 0;
    let i = 0;

    const flushText = () => {
      if (textBuf.length === 0) return;
      const md = textBuf.join('\n');
      if (md.trim().length > 0) parts.push({ kind: 'text', markdown: md });
      textBuf = [];
    };

    while (i < lines.length) {
      const open = lines[i].match(CodeBlockService.OPEN_FENCE);
      if (!open) {
        textBuf.push(lines[i]);
        i++;
        continue;
      }

      const fenceTicks = open[2];
      const language = (open[3] || '').toLowerCase();
      const codeLines: string[] = [];
      let j = i + 1;
      let closed = false;

      for (; j < lines.length; j++) {
        const close = lines[j].match(CodeBlockService.CLOSE_FENCE);
        if (close && close[2][0] === fenceTicks[0] && close[2].length >= fenceTicks.length) {
          closed = true;
          break;
        }
        codeLines.push(lines[j]);
      }

      const code = codeLines.join('\n').replace(/\s+$/, '');
      const lineCount = code.length === 0 ? 0 : code.split('\n').length;

      // A bare opening fence with nothing after it yet — keep buffering as text
      // until real content arrives, so we don't flash an empty panel.
      if (!closed && lineCount === 0) {
        textBuf.push(lines[i]);
        i++;
        continue;
      }

      flushText();
      parts.push({
        kind: 'code',
        artifact: {
          id: `cb-${ordinal}`,
          language: language || 'text',
          title: this.titleFor(language),
          code,
          complete: closed,
          lineCount,
        },
      });
      ordinal++;
      i = closed ? j + 1 : lines.length;
    }

    flushText();
    return parts;
  }

  /** All code artifacts in a message, in order. */
  extractArtifacts(markdown: string): CodeArtifact[] {
    return this.segment(markdown)
      .filter((p): p is { kind: 'code'; artifact: CodeArtifact } => p.kind === 'code')
      .map(p => p.artifact);
  }

  /** Whether a message contains at least one fenced code block. */
  hasCode(markdown: string): boolean {
    return this.segment(markdown).some(p => p.kind === 'code');
  }

  /** Map a Monaco/markdown fence language to a friendly display label. */
  titleFor(language: string): string {
    const map: Record<string, string> = {
      ts: 'TypeScript', typescript: 'TypeScript',
      js: 'JavaScript', javascript: 'JavaScript', jsx: 'JavaScript', tsx: 'TypeScript',
      py: 'Python', python: 'Python',
      java: 'Java', cs: 'C#', csharp: 'C#',
      c: 'C', cpp: 'C++', 'c++': 'C++', h: 'C', hpp: 'C++',
      go: 'Go', rs: 'Rust', rust: 'Rust', rb: 'Ruby', ruby: 'Ruby',
      php: 'PHP', swift: 'Swift', kt: 'Kotlin', kotlin: 'Kotlin',
      sql: 'SQL', sh: 'Shell', bash: 'Shell', shell: 'Shell', zsh: 'Shell',
      html: 'HTML', css: 'CSS', scss: 'SCSS', sass: 'Sass', less: 'Less',
      json: 'JSON', yaml: 'YAML', yml: 'YAML', toml: 'TOML', xml: 'XML',
      md: 'Markdown', markdown: 'Markdown', dockerfile: 'Dockerfile',
      text: 'Code', '': 'Code',
    };
    return map[language] ?? (language ? language.toUpperCase() : 'Code');
  }

  /**
   * Normalise a fence language to a Monaco language id.
   * Monaco doesn't know aliases like `py`/`ts`/`c++`.
   */
  toMonacoLanguage(language: string): string {
    const map: Record<string, string> = {
      py: 'python', ts: 'typescript', js: 'javascript', jsx: 'javascript',
      tsx: 'typescript', rb: 'ruby', rs: 'rust', sh: 'shell', bash: 'shell',
      zsh: 'shell', yml: 'yaml', 'c++': 'cpp', h: 'c', hpp: 'cpp', cs: 'csharp',
      md: 'markdown', text: 'plaintext', '': 'plaintext',
    };
    return map[language] ?? language;
  }
}
