/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1a73e8', // Google Blue
        secondary: '#5f6368', // Google Gray
        dark: '#202124', // Google Dark Gray
        light: '#f1f3f4', // Google Light Gray
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
