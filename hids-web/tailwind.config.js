/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html','./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#0f172a',            // slate-900+
        panel: '#0f1b2f',         // gray-900
        panel2: '#12213a',
        text: '#e5e7eb',          // gray-200
        muted: '#9ca3af',         // gray-400
        accent: '#60a5fa',        // blue-400
        success: '#34d399',       // emerald-400
        warn: '#f59e0b',          // amber-500
        danger: '#f87171',        // red-400
      },
      boxShadow: {
        soft: '0 10px 30px rgba(0,0,0,.25)'
      },
      borderRadius: {
        xl2: '1rem'
      }
    }
  },
  plugins: [],
}
