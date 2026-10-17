import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  server: {
    host: "0.0.0.0",
    port: 5173,
  },
  build: {
    chunkSizeWarningLimit: 900,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes("node_modules")) return undefined;

          if (id.includes("vuetify")) return "vuetify";
          if (id.includes("vue-router")) return "router";
          if (id.includes("pinia")) return "pinia";
          if (id.includes("@mdi") || id.includes("@iconify")) return "icons";

          return "vendor";
        },
      },
    },
  },
});
