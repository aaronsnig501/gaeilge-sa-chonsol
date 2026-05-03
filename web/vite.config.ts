import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, loadEnv } from 'vite';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig(({ mode }) => {
	const env = loadEnv(mode, '..', '');

	return {
		envDir: '..',
		define: {
			__PUBLIC_SUPABASE_URL__: JSON.stringify(env.PUBLIC_SUPABASE_URL ?? ''),
			__PUBLIC_SUPABASE_PUBLISHABLE_KEY__: JSON.stringify(env.PUBLIC_SUPABASE_PUBLISHABLE_KEY ?? ''),
		},
		plugins: [tailwindcss(), sveltekit()]
	};
});
