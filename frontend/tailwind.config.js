/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // App Backgrounds
        app: 'var(--bg-app)',
        surface: 'var(--bg-surface)',
        'surface-2': 'var(--bg-surface-2)',
        elevated: 'var(--bg-elevated)',

        // Primary Accent
        primary: {
          DEFAULT: 'var(--primary)',
          600: 'var(--primary-600)',
        },

        // Secondary Accent
        accent: {
          DEFAULT: 'var(--accent)',
          600: 'var(--accent-600)',
        },

        // Status Colors
        success: 'var(--success)',
        warning: 'var(--warning)',
        danger: 'var(--danger)',
        info: 'var(--info)',

        // Text
        'text-primary': 'var(--text-primary)',
        'text-secondary': 'var(--text-secondary)',
        'text-muted': 'var(--text-muted)',

        // Interfaces
        border: 'var(--border)',
        divider: 'var(--divider-strong)',
        backdrop: 'var(--backdrop)',
        input: 'var(--input-bg)',
        'input-border': 'var(--input-border)',
        placeholder: 'var(--placeholder)',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
