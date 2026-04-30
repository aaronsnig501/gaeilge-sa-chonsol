import adapter from '@sveltejs/adapter-static';
import { mdsvex } from 'mdsvex';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

const isDev = process.argv.includes('dev');
const basePath = process.env.BASE_PATH ?? '';

const config = {
	extensions: ['.svelte', '.md'],
	preprocess: [vitePreprocess(), mdsvex({ extensions: ['.md'] })],
	kit: {
		adapter: adapter({
			pages: 'build',
			assets: 'build',
			fallback: undefined,
			precompress: true
		}),
		paths: {
			base: isDev ? '' : basePath
		},
		prerender: {
			entries: ['*']
		}
	}
};

export default config;
