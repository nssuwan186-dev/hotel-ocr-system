/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#006D36',
        'primary-light': '#008a46',
        'primary-dark': '#004d26',
        surface: '#e8eef5',
        'surface-dark': '#d1d9e6',
        'surface-light': '#f0f4f8',
        text: '#29343a',
        'text-muted': '#566168',
        'text-light': '#a0aab4',
      },
      fontFamily: {
        sans: ['Manrope', 'sans-serif'],
      },
      boxShadow: {
        'neu': '6px 6px 12px #d1d9e6, -6px -6px 12px #ffffff',
        'neu-sm': '4px 4px 8px #d1d9e6, -4px -4px 8px #ffffff',
        'neu-inset': 'inset 4px 4px 8px #d1d9e6, inset -4px -4px 8px #ffffff',
        'neu-inset-sm': 'inset 3px 3px 6px #d1d9e6, inset -3px -3px 6px #ffffff',
      },
      borderRadius: {
        'neu': '16px',
        'neu-lg': '24px',
      }
    },
  },
  plugins: [],
}