import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), VitePWA()],
  server: {
    port: 5173,
    host: true
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          ui: ['react-select', 'lucide-react']
        }
      }
    }
  },
  pwa: {
    registerType: 'autoUpdate',
    includeAssets: ['favicon.svg', 'apple-touch-icon.svg', 'icon-192.svg', 'icon-512.svg'],
    manifest: {
      name: 'NutriSync AI - Food Compatibility App',
      short_name: 'NutriSync AI',
      description: 'AI-powered food compatibility and nutritional guidance app',
      theme_color: '#00c6ff',
      icons: [
        {
          src: 'icon-192.svg',
          sizes: '192x192',
          type: 'image/svg+xml'
        },
        {
          src: 'icon-512.svg',
          sizes: '512x512',
          type: 'image/svg+xml'
        }
      ]
    }
  }
})