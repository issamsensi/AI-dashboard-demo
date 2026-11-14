/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Space Grotesk"', 'ui-sans-serif', 'system-ui'],
        body: ['"Inter Tight"', 'ui-sans-serif', 'system-ui'],
      },
      colors: {
        surface: {
          50: '#f6f5f1',
          100: '#ece8df',
          900: '#131313',
        },
        ink: '#121212',
        accent: {
          500: '#1f7a6b',
          600: '#166357',
          700: '#114e45',
        },
        sand: '#d9c9a8',
      },
      boxShadow: {
        glow: '0 20px 60px rgba(17, 78, 69, 0.18)',
      },
      keyframes: {
        rise: {
          '0%': { opacity: '0', transform: 'translateY(18px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        rise: 'rise 0.6s ease-out both',
      },
    },
  },
  plugins: [],
};
