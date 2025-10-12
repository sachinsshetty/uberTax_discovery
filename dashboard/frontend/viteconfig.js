import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,  // Listen on all interfaces (0.0.0.0) for Docker/Cloudflare access
    allowedHosts: ['new-tax.dwani.ai', '.dwani.ai', 'tax.dwani.ai'],  // Allow the specific domain and subdomains
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})