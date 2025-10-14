import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'build',
  },
  // Remove or comment out preview/server sections for pure production builds
  // preview: {
  //   port: 11080,
  //   strictPort: true,
  // },
  // server: { ... }  // Entire server block can be removed for prod
})