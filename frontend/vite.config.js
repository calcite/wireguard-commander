import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://host.docker.internal:5000',
        changeOrigin: true,
        // rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/config': {
        target: 'http://host.docker.internal:5000',
        changeOrigin: true,
        // rewrite: (path) => path.replace(/^\/config/, ''),
      },
      '/ws': {
        target: 'http://host.docker.internal:5000',
        changeOrigin: true,
        ws: true,
        // rewrite: (path) => path.replace(/^\/ws/, ''),
      },
    },
  },
  plugins: [
    vue(),
    vueJsx(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
})
