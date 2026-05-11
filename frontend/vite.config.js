import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// В Docker задаём VITE_BACKEND_URL=http://backend:8000 через docker-compose.
// Для локального запуска (npm run dev) по умолчанию остаётся 127.0.0.1:8000.
const backendUrl = process.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: '0.0.0.0',
    proxy: {
      '/api':    { target: backendUrl, changeOrigin: true },
      '/health': { target: backendUrl, changeOrigin: true }
    }
  }
})
