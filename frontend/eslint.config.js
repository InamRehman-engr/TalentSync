import js from "@eslint/js";

export default [
  {
    ignores: ["node_modules/**", "dist/**", "public/**", "**/*.vue"],
  },
  {
    ...js.configs.recommended,
    files: ["**/*.js", "**/*.cjs", "**/*.mjs"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: {
        window: "readonly",
        document: "readonly",
        navigator: "readonly",
        process: "readonly",
        localStorage: "readonly",
        console: "readonly",
      },
    },
    rules: {
      ...js.configs.recommended.rules,
      "no-unused-vars": "warn",
      "no-console": "off",
    },
  },
];
