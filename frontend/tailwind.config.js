/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f7ff',
          100: '#e0effe',
          200: '#bae0fd',
          300: '#7cc8fb',
          400: '#38aaf7',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
          accent: '#0071e3', // Apple Blue
          dark: '#0f172a',
        },
        surface: {
          canvas: '#fafafc',
          card: '#ffffff',
          hover: '#f4f4f7',
          border: '#e2e8f0',
          'border-subtle': '#f1f5f9',
          dark: '#0f172a',
          darker: '#090d16',
        }
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', '-apple-system', 'BlinkMacSystemFont', '"SF Pro Display"', '"Segoe UI"', 'Roboto', 'sans-serif'],
        display: ['"Outfit"', '"Plus Jakarta Sans"', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        'soft': '0 2px 15px -3px rgba(0, 0, 0, 0.07), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        'apple': '0 4px 24px 0 rgba(0, 0, 0, 0.06), 0 1px 2px 0 rgba(0, 0, 0, 0.04)',
        'card': '0 1px 3px rgba(0,0,0,0.05), 0 10px 25px -5px rgba(0,0,0,0.04)',
        'float': '0 20px 40px -15px rgba(0, 0, 0, 0.08)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
}
