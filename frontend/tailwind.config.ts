import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#050505",
        panel: "#0b0b0b",
        line: "rgba(255,255,255,0.08)",
        lineStrong: "rgba(255,255,255,0.14)",
        ink: "#f7f7f5",
        muted: "rgba(255,255,255,0.55)",
        mutedStrong: "rgba(255,255,255,0.72)",
        glow: "#72d0ff",
        accent: "#f4f4f1",
      },
      boxShadow: {
        panel: "0 24px 80px rgba(0,0,0,0.35)",
        shell: "0 30px 120px rgba(0,0,0,0.55)",
        inset: "inset 0 1px 0 rgba(255,255,255,0.06)",
      },
      animation: {
        "fade-up": "fadeUp 420ms ease-out",
        float: "float 6s ease-in-out infinite",
      },
      keyframes: {
        fadeUp: {
          "0%": { opacity: "0", transform: "translateY(16px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-8px)" },
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
