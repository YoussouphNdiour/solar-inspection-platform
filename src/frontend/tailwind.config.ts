import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        coa: {
          1: '#FCD34D',  // CoA1 — surveillance (jaune)
          2: '#F97316',  // CoA2 — action sous 3 mois (orange)
          3: '#EF4444',  // CoA3 — action urgente (rouge)
        },
        solar: {
          50: '#fefce8',
          500: '#eab308',
          900: '#713f12',
        },
      },
    },
  },
  plugins: [],
} satisfies Config
