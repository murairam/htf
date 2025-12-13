/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      boxShadow: {
        '3xl': '0 35px 60px -15px rgba(0, 0, 0, 0.3), 0 10px 20px -5px rgba(0, 0, 0, 0.2)',
        '4xl': '0 40px 80px -20px rgba(0, 0, 0, 0.4), 0 15px 30px -10px rgba(0, 0, 0, 0.3)',
        'inner-lg': 'inset 0 4px 8px 0 rgba(0, 0, 0, 0.1)',
        'glow': '0 0 20px rgba(34, 197, 94, 0.3), 0 0 40px rgba(34, 197, 94, 0.1)',
      },
    },
  },
  plugins: [],
}
