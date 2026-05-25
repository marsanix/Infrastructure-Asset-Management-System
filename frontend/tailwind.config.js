/** @type {import('tailwindcss').Config} */
import animate from 'tailwindcss-animate'
import { setupInspiraUI } from '@inspira-ui/plugins'

export default {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{vue,ts,tsx}',
  ],
  theme: {
    extend: {
      // ── IBM Carbon Color Tokens ──────────────────────────
      colors: {
        primary:      'var(--color-primary)',
        'on-primary': 'var(--color-on-primary)',
        'blue-60':    'var(--color-blue-60)',
        'blue-80':    'var(--color-blue-80)',
        'blue-hover': 'var(--color-blue-hover)',

        ink:          'var(--color-ink)',
        'ink-muted':  'var(--color-ink-muted)',
        'ink-subtle': 'var(--color-ink-subtle)',

        canvas:       'var(--color-canvas)',
        'surface-1':  'var(--color-surface-1)',
        'surface-2':  'var(--color-surface-2)',

        hairline:         'var(--color-hairline)',
        'hairline-strong':'var(--color-hairline-strong)',

        'inverse-canvas':    'var(--color-inverse-canvas)',
        'inverse-surface-1': 'var(--color-inverse-surface-1)',
        'inverse-ink':       'var(--color-inverse-ink)',
        'inverse-ink-muted': 'var(--color-inverse-ink-muted)',

        success: 'var(--color-success)',
        warning: 'var(--color-warning)',
        error:   'var(--color-error)',
        info:    'var(--color-info)',

        // ── Inspira UI color tokens (HSL) ─────────────────
        background:  'hsl(var(--background))',
        foreground:  'hsl(var(--foreground))',
        border:      'hsl(var(--border))',
        input:       'hsl(var(--input))',
        ring:        'hsl(var(--ring))',
        muted: {
          DEFAULT:    'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT:    'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
      },

      // ── IBM Plex Sans ────────────────────────────────────
      fontFamily: {
        sans: ['IBM Plex Sans', 'Helvetica Neue', 'Arial', 'sans-serif'],
      },

      // ── Carbon 4px spacing grid ──────────────────────────
      spacing: {
        'xxs': '4px',
        'xs':  '8px',
        'sm':  '12px',
        'md':  '16px',
        'lg':  '24px',
        'xl':  '32px',
        'xxl': '48px',
        'section': '96px',
      },

      // ── Carbon flat-square border radius ─────────────────
      borderRadius: {
        'none': '0px',
        'xs':   '2px',
        'sm':   '4px',
        'md':   '6px',
        'lg':   '8px',
        'pill': '9999px',
      },

      // ── Font sizes (Carbon type scale) ───────────────────
      fontSize: {
        'caption':    ['12px', { lineHeight: '1.33', letterSpacing: '0.32px' }],
        'body-sm':    ['14px', { lineHeight: '1.29', letterSpacing: '0.16px' }],
        'body':       ['16px', { lineHeight: '1.50', letterSpacing: '0.16px' }],
        'body-lg':    ['18px', { lineHeight: '1.50', letterSpacing: '0' }],
        'subhead':    ['20px', { lineHeight: '1.40', letterSpacing: '0' }],
        'card-title': ['24px', { lineHeight: '1.33', letterSpacing: '0' }],
        'headline':   ['32px', { lineHeight: '1.25', letterSpacing: '0' }],
        'display-md': ['42px', { lineHeight: '1.20', letterSpacing: '0' }],
        'display-lg': ['60px', { lineHeight: '1.17', letterSpacing: '-0.4px' }],
        'display-xl': ['76px', { lineHeight: '1.17', letterSpacing: '-0.5px' }],
      },

      // ── Carbon breakpoints ───────────────────────────────
      screens: {
        'mobile':       '480px',
        'tablet':       '672px',
        'desktop':      '1056px',
        'desktop-xl':   '1312px',
        'max':          '1584px',
      },

      maxWidth: {
        'carbon': '1584px',
      },

      // ── Inspira UI animations ─────────────────────────────
      keyframes: {
        'aurora': {
          from: { backgroundPosition: '50% 50%, 50% 50%' },
          to:   { backgroundPosition: '350% 50%, 350% 50%' },
        },
        'shimmer': {
          from: { backgroundPosition: '0 0' },
          to:   { backgroundPosition: '-200% 0' },
        },
        'meteor': {
          '0%': { transform: 'rotate(215deg) translateX(0)', opacity: '1' },
          '70%': { opacity: '1' },
          '100%': { transform: 'rotate(215deg) translateX(-500px)', opacity: '0' },
        },
        'spotlight': {
          '0%': { opacity: '0', transform: 'translate(-72%, -62%) scale(0.5)' },
          '100%': { opacity: '1', transform: 'translate(-50%,-40%) scale(1)' },
        },
        'border-beam': {
          '100%': { 'offset-distance': '100%' },
        },
        'marquee': {
          from: { transform: 'translateX(0)' },
          to:   { transform: 'translateX(calc(-100% - var(--gap)))' },
        },
        'marquee-vertical': {
          from: { transform: 'translateY(0)' },
          to:   { transform: 'translateY(calc(-100% - var(--gap)))' },
        },
        'fade-in': {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'ripple': {
          '0%, 100%': { transform: 'translate(-50%, -50%) scale(1)' },
          '50%': { transform: 'translate(-50%, -50%) scale(0.9)' },
        },
      },
      animation: {
        'aurora':           'aurora 60s linear infinite',
        'shimmer':          'shimmer 2s linear infinite',
        'meteor':           'meteor 5s linear infinite',
        'spotlight':        'spotlight 2s ease .75s 1 forwards',
        'border-beam':      'border-beam calc(var(--duration)*1s) infinite linear',
        'marquee':          'marquee var(--duration) infinite linear',
        'marquee-vertical': 'marquee-vertical var(--duration) linear infinite',
        'fade-in':          'fade-in 0.5s ease-out forwards',
        'ripple':           'ripple var(--duration,2s) ease calc(var(--i, 0)*.2s) infinite',
      },
    },
  },
  plugins: [animate, setupInspiraUI],
}
