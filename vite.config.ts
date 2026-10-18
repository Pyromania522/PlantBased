import { defineConfig } from "vite";

export default defineConfig({
  publicDir: "frontend/public",
  build: {
    target: "es2022",
    outDir: "custom_components/plantbased/frontend",
    emptyOutDir: true,
    copyPublicDir: true,
    lib: {
      entry: "frontend/src/index.ts",
      formats: ["es"],
      fileName: () => "plantbased.js",
    },
    sourcemap: false,
    license: { fileName: "THIRD_PARTY_LICENSES.md" },
  },
});
