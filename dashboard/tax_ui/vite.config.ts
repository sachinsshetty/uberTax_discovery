import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'build',
  },
  preview: {
    port: 11080,
    strictPort: true,
  },
  server: {
    host: true,
    strictPort: true,
    hmr: {
      overlay: false
    },
    port: 11080, // This is the port which we will use in docker (overridden by CLI in Dockerfile)
    // add the next lines if you're using windows and hot reload doesn't work
    watch: {
      usePolling: true
    },
    // Add this to allow the custom domain
    allowedHosts: [
      'tax.dwani.ai',
      '.dwani.ai'  // Optional: Wildcard for all *.dwani.ai subdomains
    ]
  }
})