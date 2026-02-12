import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		proxy: {
			// Browser calls /api/* on this server; in Docker proxy to api container, else localhost
			'/api': {
				target: process.env.API_PROXY_TARGET ?? 'http://localhost:8000',
				changeOrigin: true
			}
		}
	}
});
