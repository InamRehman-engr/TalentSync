import colors from "tailwindcss/colors";

// ═══════════════════════════════════════════════════════════
// ✦  APP COLOR SCHEME — change any color to retheme the app
// ═══════════════════════════════════════════════════════════
const PRIMARY_COLOR = colors.lime;     // Brand / accent  — matches logo lime-green (#CBE06E)
const NEUTRAL_COLOR = colors.neutral;  // Text / surfaces  — matches logo near-black (#0D0D0D)
const SUCCESS_COLOR = colors.emerald;  // Success states   — try: green, teal, lime
const WARNING_COLOR = colors.amber;    // Warning states   — try: yellow, orange
const DANGER_COLOR  = colors.red;      // Error / danger   — try: rose, pink

// ═══════════════════════════════════════════════════════════
// ✦  SECTION COLORS — hero, footer & CTA band theming
// ═══════════════════════════════════════════════════════════
const HERO_BG       = NEUTRAL_COLOR[950];   // Dark hero sections
const FOOTER_BG     = NEUTRAL_COLOR[950];   // Footer background
const HERO_GLOW     = PRIMARY_COLOR[900];   // Hero radial-gradient glow
const CTA_START     = PRIMARY_COLOR[600];   // CTA gradient start
const CTA_MID       = PRIMARY_COLOR[700];   // CTA gradient middle
const CTA_END       = colors.green[700];    // CTA gradient end — complements lime brand

/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: PRIMARY_COLOR,
        neutral: NEUTRAL_COLOR,
        success: SUCCESS_COLOR,
        warning: WARNING_COLOR,
        danger:  DANGER_COLOR,
        'hero':      HERO_BG,
        'footer':    FOOTER_BG,
        'hero-glow': HERO_GLOW,
        'cta-start': CTA_START,
        'cta-mid':   CTA_MID,
        'cta-end':   CTA_END,
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
