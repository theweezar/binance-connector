import { defineConfig } from "eslint/config";
import { includeIgnoreFile } from "@eslint/compat";
import { fileURLToPath } from "node:url";

const rules = {
  "indent": ["error", 2, { "SwitchCase": 1 }],
  "semi": ["error", "always"],
  "quotes": ["error", "double"]
};

const gitignorePath = fileURLToPath(new URL(".gitignore", import.meta.url));

export default defineConfig([
  {
    files: ["**/*.js"],
    ignores: [
      "/web/dist/resources/*",
      "/ignore/*"
    ],
    rules: rules
  },
  includeIgnoreFile(gitignorePath, "Imported .gitignore patterns")
]);
