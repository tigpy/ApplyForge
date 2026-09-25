/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        paper: '#f3efe6',
        ink: '#1c1914',
        muted: '#5f584e',
        hairline: '#e0d6c6',
        card: '#fffdf8',
        pine: '#1e4636',
        moss: '#e5f0e8',
        copper: '#8d3f1e',
        amber: '#fdf6ed',
      },
      fontFamily: {
        serif: ['var(--font-fraunces)', 'Georgia', 'serif'],
        sans: ['var(--font-figtree)', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
