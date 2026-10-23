export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        nexus: {
          dark: "#0b0f19",
          card: "rgba(17, 24, 39, 0.7)",
          indigo: "#6366f1",
          purple: "#a855f7"
        }
      }
    },
  },
  plugins: [],
}
