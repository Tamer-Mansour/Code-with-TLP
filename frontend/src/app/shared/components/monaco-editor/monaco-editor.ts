import {
  Component,
  ElementRef,
  Input,
  Output,
  EventEmitter,
  OnDestroy,
  AfterViewInit,
  ViewChild,
  OnChanges,
  SimpleChanges,
  ChangeDetectionStrategy,
} from '@angular/core';
import loader from '@monaco-editor/loader';

// Point to the exact Monaco version we have installed
loader.config({
  paths: { vs: 'https://cdn.jsdelivr.net/npm/monaco-editor@0.55.1/min/vs' },
});

@Component({
  selector: 'app-monaco-editor',
  standalone: true,
  templateUrl: './monaco-editor.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MonacoEditorComponent implements AfterViewInit, OnChanges, OnDestroy {
  @ViewChild('editorContainer', { static: true }) editorContainer!: ElementRef<HTMLDivElement>;

  @Input() language: string = 'python';
  @Input() value: string = '';
  @Input() theme: string = 'vs-dark';
  @Input() readOnly: boolean = false;

  @Output() valueChange = new EventEmitter<string>();

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private editor: any = null;
  private monacoInstance: any = null;
  private isUpdatingFromParent = false;

  ngAfterViewInit(): void {
    loader.init().then((monaco) => {
      this.monacoInstance = monaco;
      monaco.editor.defineTheme('darcula', {
        base: 'vs-dark',
        inherit: true,
        rules: [
          { token: 'comment',       foreground: '808080', fontStyle: 'italic' },
          { token: 'keyword',       foreground: 'cc7832', fontStyle: 'bold' },
          { token: 'string',        foreground: '6a8759' },
          { token: 'string.escape', foreground: '6a8759' },
          { token: 'number',        foreground: '6897bb' },
          { token: 'type',          foreground: 'ffc66d' },
          { token: 'class',         foreground: 'ffc66d' },
          { token: 'function',      foreground: 'ffc66d' },
          { token: 'annotation',    foreground: 'bbb529' },
          { token: 'operator',      foreground: 'a9b7c6' },
          { token: 'delimiter',     foreground: 'a9b7c6' },
        ],
        colors: {
          'editor.background':                  '#2b2b2b',
          'editor.foreground':                  '#a9b7c6',
          'editor.lineHighlightBackground':     '#323232',
          'editor.selectionBackground':         '#214283',
          'editor.inactiveSelectionBackground': '#214283',
          'editorLineNumber.foreground':        '#606366',
          'editorLineNumber.activeForeground':  '#a4a3a3',
          'editorGutter.background':            '#313335',
          'editorIndentGuide.background1':      '#3d3d3d',
          'editorBracketMatch.background':      '#3a3a3a',
          'editorBracketMatch.border':          '#ffc66d',
          'editorCursor.foreground':            '#ababab',
          'editor.wordHighlightBackground':     '#3a3a3a80',
          'scrollbarSlider.background':         '#4b4b4b40',
          'scrollbarSlider.hoverBackground':    '#6b6b6b60',
          'scrollbarSlider.activeBackground':   '#8b8b8b80',
          'editorSuggestWidget.background':     '#3c3f41',
          'editorSuggestWidget.border':         '#4b4f52',
          'editorSuggestWidget.selectedBackground': '#4b6eaf',
          'editor.findMatchBackground':         '#32593d',
          'editor.findMatchHighlightBackground':'#1f362880',
        }
      });
      this.editor = monaco.editor.create(this.editorContainer.nativeElement, {
        value: this.value,
        language: this.language,
        theme: this.theme,
        fontSize: 14,
        fontFamily: "'JetBrains Mono', monospace",
        fontLigatures: "'liga', 'calt'",
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
        lineNumbers: 'on',
        roundedSelection: true,
        automaticLayout: true,
        tabSize: 4,
        cursorBlinking: 'smooth',
        cursorSmoothCaretAnimation: 'on',
        smoothScrolling: true,
        renderLineHighlight: 'line',
        guides: { indentation: true, bracketPairs: false },
        bracketPairColorization: { enabled: true },
        lineNumbersMinChars: 3,
        glyphMargin: false,
        folding: false,
        wordWrap: 'on',
        padding: { top: 16, bottom: 16 },
        readOnly: this.readOnly,
        contextmenu: true,
        scrollbar: { verticalScrollbarSize: 6, horizontalScrollbarSize: 6 },
        overviewRulerLanes: 0,
        hideCursorInOverviewRuler: true,
        overviewRulerBorder: false,
      });

      this.editor.onDidChangeModelContent(() => {
        if (!this.isUpdatingFromParent) {
          this.valueChange.emit(this.editor.getValue());
        }
      });
    });
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (!this.editor) return;

    if (changes['language'] && !changes['language'].firstChange) {
      const model = this.editor.getModel();
      if (model && this.monacoInstance) {
        this.monacoInstance.editor.setModelLanguage(model, this.language);
      }
    }

    if (changes['value'] && !changes['value'].firstChange) {
      const currentValue = this.editor.getValue();
      if (currentValue !== this.value) {
        this.isUpdatingFromParent = true;
        this.editor.setValue(this.value ?? '');
        this.isUpdatingFromParent = false;
      }
    }

    if (changes['readOnly'] && !changes['readOnly'].firstChange) {
      this.editor.updateOptions({ readOnly: this.readOnly });
    }

    if (changes['theme'] && !changes['theme'].firstChange && this.monacoInstance) {
      this.monacoInstance.editor.setTheme(this.theme);
    }
  }

  ngOnDestroy(): void {
    if (this.editor) {
      this.editor.dispose();
      this.editor = null;
    }
  }
}
