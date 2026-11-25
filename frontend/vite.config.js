import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// PORT and API_TARGET let the test runner start an isolated copy next to your dev servers.
export default defineConfig({
  plugins: [react()],
  server: {
    port: Number(process.env.PORT) || 5173,
    strictPort: true,
    proxy: { "/api": process.env.API_TARGET || "http://127.0.0.1:8000" },
  },
});
