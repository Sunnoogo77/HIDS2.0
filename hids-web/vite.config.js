import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
// export default defineConfig({
//   plugins: [react()],
// })

export default defineConfig({
  plugins: [react()],
  cacheDir: '.vite',      // au lieu de node_modules/.vite
  server: {
    port: 5173,
    strictPort: true,
    // https: true,       // active si tu veux servir le FRONT en HTTPS
  }
})