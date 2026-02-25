import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        "do-blue": "#0069ff",
        "do-dark": "#0d1117",
        "p1-red": "#ff4444",
        "p2-orange": "#ff8c00",
        "p3-yellow": "#ffd700",
      },
    },
  },
  plugins: [],
};
export default config;
