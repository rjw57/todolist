import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

// https://vitejs.dev/config/
export default defineConfig({
  base: "/",
  server: {
    port: 3000,
    strictPort: true,
  },
  build: {
    outDir: process.env.APP_BUILD ?? "build/",
    manifest: true,
    copyPublicDir: true,
    rollupOptions: {
      input: "/index.html",
    },
    minify: process.env.NODE_ENV === "production" ? "esbuild" : false,
    sourcemap: process.env.NODE_ENV === "production" ? false : "inline",
  },
  plugins: [react()],
});
