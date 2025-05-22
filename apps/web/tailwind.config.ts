import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx}",
    "../../packages/ui/src/**/*.{js,ts,jsx,tsx}", // Adjust path as needed
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};

export default config;
