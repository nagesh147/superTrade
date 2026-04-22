/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        surface: { 0: '#050609', 1: '#0a0c12', 2: '#0e1118', 3: '#131720', 4: '#181e2a' },
        accent:  { cyan: '#00d4ff', green: '#00ff88', amber: '#ffb800', red: '#ff3d5a', purple: '#7c3aed' },
        border:  { dim: '#1a2035', base: '#212b42', bright: '#2d3a57' },
        text:    { muted: '#4a5568', dim: '#6b7a99', base: '#9aa5c0', bright: '#c5cee0', vivid: '#e8edf7' }
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', '"Fira Code"', 'monospace'],
        display: ['"Syne"', 'sans-serif'],
        body: ['"DM Sans"', 'sans-serif'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4,0,0.6,1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'slide-up': 'slideUp 0.3s ease-out',
        'fade-in': 'fadeIn 0.4s ease-out',
        'blink': 'blink 1s step-end infinite',
      },
      keyframes: {
        glow: { from: { 'box-shadow': '0 0 5px #00d4ff40' }, to: { 'box-shadow': '0 0 20px #00d4ff80, 0 0 40px #00d4ff20' } },
        slideUp: { from: { transform: 'translateY(10px)', opacity: '0' }, to: { transform: 'translateY(0)', opacity: '1' } },
        fadeIn: { from: { opacity: '0' }, to: { opacity: '1' } },
        blink: { '0%,100%': { opacity: '1' }, '50%': { opacity: '0' } },
      },
      backgroundImage: {
        'grid-pattern': 'linear-gradient(rgba(0,212,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0,212,255,0.03) 1px, transparent 1px)',
        'radial-glow': 'radial-gradient(ellipse at center, rgba(0,212,255,0.08) 0%, transparent 70%)',
      },
      backgroundSize: { 'grid': '40px 40px' },
    }
  },
  plugins: [],
}
