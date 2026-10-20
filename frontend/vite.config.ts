import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode, command }) => {
  const env = loadEnv(mode, ".", "");
  // Browser sessions use host-only, Secure, SameSite=Lax cookies. A production
  // build must call the frontend's /api route rather than a separate Render site.
  // Synthetic builds retain their explicitly isolated transport configuration.
  const apiBase = (env.VITE_API_URL || "/api").replace(/\/$/, "");
  if (command === "build" && mode === "production" && apiBase !== "/api") {
    throw new Error("PriceYard production builds require VITE_API_URL=/api and the reviewed same-origin API route.");
  }
  const target = env.VITE_DEV_API_TARGET || "http://127.0.0.1:8000";

  return {
    plugins: [react()],
    server: {
      host: "127.0.0.1",
      port: 5173,
      proxy: {
        "/api": {
          target,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ""),
        },
      },
    },
  };
});
