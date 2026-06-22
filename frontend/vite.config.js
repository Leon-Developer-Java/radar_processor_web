import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// 开发服务器 :5173；/api 与 /outputs 代理到 FastAPI（默认 :8000）。
// 后端端口可用 VITE_PROXY_TARGET 覆盖（与后端 BACKEND_PORT 对应）。
const target = process.env.VITE_PROXY_TARGET || "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    host: "127.0.0.1",
    proxy: {
      "/api": { target, changeOrigin: true },
      "/outputs": { target, changeOrigin: true },
    },
  },
});
