import { fileURLToPath, URL } from 'node:url'

import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'
import vueDevTools from 'vite-plugin-vue-devtools'

const PERMISSIONS_POLICY =
  'accelerometer=(), ambient-light-sensor=(), autoplay=(), battery=(), camera=(), cross-origin-isolated=(), display-capture=(), document-domain=(), encrypted-media=(), execution-while-not-rendered=(), execution-while-out-of-viewport=(), fullscreen=(), geolocation=(), gyroscope=(), keyboard-map=(), magnetometer=(), microphone=(), midi=(), navigation-override=(), payment=(), picture-in-picture=(), publickey-credentials-get=(), screen-wake-lock=(), sync-xhr=(), usb=(), web-share=(), xr-spatial-tracking=(), interest-cohort=()'

// NOTE: script-src unsafe-eval should NOT be set in production
// NOTE: some content security policy are set for VueTools plugin
const CONTENT_SECURITY_POLICY =
  "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; font-src https://fonts.gstatic.com 'self'; img-src data: 'self'; connect-src 'self'; frame-ancestors 'self'"

const REFERRER_POLICY = 'same-origin'

const X_CONTENT_TYPE_OPTIONS = 'nosniff'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), tailwindcss(), vueDevTools()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 8080,
    strictPort: true,
    allowedHosts: process.env.VITE_ALLOWED_HOSTS?.split(',') || [],
    headers: {
      // NOTE: this is only for the development environment, production headers
      //       should be set in the production webserver's configuration
      'Permissions-Policy': PERMISSIONS_POLICY,
      'Content-Security-Policy': CONTENT_SECURITY_POLICY,
      'Referrer-Policy': REFERRER_POLICY,
      'X-Content-Type-Options': X_CONTENT_TYPE_OPTIONS,
    },
  },
})
