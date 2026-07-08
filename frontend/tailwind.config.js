/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        green: {
          900: '#0f3d20',
          700: '#1e5631',
          500: '#2e7d32',
          300: '#4caf50',
          100: '#a5d6a7',
          50: '#e8f5e9',
        },
        gold: {
          DEFAULT: '#c8a84e',
          light: '#f5e7c8',
        },
        cream: '#f7f5e7',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
