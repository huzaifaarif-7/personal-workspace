import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Forward all /api requests to the FastAPI backend.
      // This makes them same-origin from the browser's perspective so the
      // session cookie is always sent automatically — no credentials:'include' needed.
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
