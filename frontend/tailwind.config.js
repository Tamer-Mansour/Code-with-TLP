/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{html,ts}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // App surfaces — CSS variable-driven so light/dark switching works
        'app-bg':         'rgb(var(--color-app-bg) / <alpha-value>)',
        'app-surface':    'rgb(var(--color-app-surface) / <alpha-value>)',
        'app-surface-2':  'rgb(var(--color-app-surface-2) / <alpha-value>)',
        'app-border':     'rgb(var(--color-app-border) / <alpha-value>)',
        'app-border-2':   'rgb(var(--color-app-border-2) / <alpha-value>)',
        'app-text':       'rgb(var(--color-app-text) / <alpha-value>)',
        'app-text-2':     'rgb(var(--color-app-text-2) / <alpha-value>)',
        'app-text-muted': 'rgb(var(--color-app-text-muted) / <alpha-value>)',
        // Brand (driven by --color-brand-rgb, default blue)
        'brand':          'rgb(var(--color-brand-rgb, 59 130 246) / <alpha-value>)',
        'brand-dark':     'rgb(var(--color-brand-dark-rgb, 37 99 235) / <alpha-value>)',
        'brand-light':    'rgb(var(--color-brand-light-rgb, 96 165 250) / <alpha-value>)',
        // Difficulty labels (kept for utility — used by badge classes via dark:)
        'easy':           '#16a34a', // green-600  — works on both light + dark bg
        'medium':         '#d97706', // amber-600
        'hard':           '#dc2626', // red-600
        // Submission status labels
        'status-accepted': '#16a34a',
        'status-wrong':    '#dc2626',
        'status-tle':      '#d97706',
        'status-mle':      '#ea580c',
        'status-re':       '#9333ea',
        'status-error':    '#6b7280',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
        inter: ['Inter', 'system-ui', 'sans-serif'],
        roboto: ['Roboto', 'system-ui', 'sans-serif'],
        outfit: ['Outfit', 'system-ui', 'sans-serif'],
        'jetbrains-mono': ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
        'fira-code': ['Fira Code', 'Consolas', 'monospace'],
        poppins: ['Poppins', 'system-ui', 'sans-serif'],
        nunito: ['Nunito', 'system-ui', 'sans-serif'],
        'open-sans': ['Open Sans', 'system-ui', 'sans-serif'],
        lato: ['Lato', 'system-ui', 'sans-serif'],
        montserrat: ['Montserrat', 'system-ui', 'sans-serif'],
        raleway: ['Raleway', 'system-ui', 'sans-serif'],
        ubuntu: ['Ubuntu', 'system-ui', 'sans-serif'],
        'source-sans-3': ['Source Sans 3', 'system-ui', 'sans-serif'],
        'dm-sans': ['DM Sans', 'system-ui', 'sans-serif'],
        'space-grotesk': ['Space Grotesk', 'system-ui', 'sans-serif'],
        tajawal: ['Tajawal', 'system-ui', 'sans-serif'],
        cairo: ['Cairo', 'system-ui', 'sans-serif'],
        amiri: ['Amiri', 'system-ui', 'serif'],
        'noto-naskh-arabic': ['Noto Naskh Arabic', 'system-ui', 'serif'],
        'el-messiri': ['El Messiri', 'system-ui', 'sans-serif'],
        changa: ['Changa', 'system-ui', 'sans-serif'],
        'readex-pro': ['Readex Pro', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        'xs':   ['0.75rem',  { lineHeight: '1rem' }],
        'sm':   ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem',     { lineHeight: '1.5rem' }],
        'lg':   ['1.125rem', { lineHeight: '1.75rem' }],
        'xl':   ['1.25rem',  { lineHeight: '1.75rem' }],
        '2xl':  ['1.5rem',   { lineHeight: '2rem' }],
        '3xl':  ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl':  ['2.25rem',  { lineHeight: '2.5rem' }],
      },
      spacing: {
        'navbar':  '3.5rem',
        'sidebar': '15rem',
      },
      borderRadius: {
        'sm': '0.375rem',
        DEFAULT: '0.5rem',
        'lg': '0.75rem',
        'xl': '1rem',
      },
      boxShadow: {
        'card':    '0 1px 3px rgba(0,0,0,0.10), 0 1px 2px rgba(0,0,0,0.06)',
        'popover': '0 8px 32px rgba(0,0,0,0.14)',
        'brand':   '0 0 0 3px rgba(59,130,246,0.35)',
      },
      animation: {
        'fade-in':    'fadeIn 0.2s ease-out',
        'slide-up':   'slideUp 0.25s ease-out',
        'slide-down': 'slideDown 0.25s ease-out',
        'spin-slow':  'spin 1.5s linear infinite',
        'pulse-soft': 'pulse 2s cubic-bezier(0.4,0,0.6,1) infinite',
      },
      keyframes: {
        fadeIn:    { from: { opacity: '0' }, to: { opacity: '1' } },
        slideUp:   { from: { opacity: '0', transform: 'translateY(8px)'  }, to: { opacity: '1', transform: 'translateY(0)' } },
        slideDown: { from: { opacity: '0', transform: 'translateY(-8px)' }, to: { opacity: '1', transform: 'translateY(0)' } },
      },
      transitionDuration: {
        DEFAULT: '150ms',
        '200': '200ms',
        '300': '300ms',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms')({ strategy: 'class' }),
    require('@tailwindcss/typography'),
  ],
};
