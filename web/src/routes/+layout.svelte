<script lang="ts">
	import { base } from '$app/paths';
	import '../app.css';
	import ExternalLink from '$lib/components/ExternalLink.svelte';

	let { children } = $props();
</script>

<svelte:head>
	<title>Gaeilge sa Chonsol</title>
	<meta
		name="description"
		content="Aistriúcháin Gaeilge do chluichí clasaiceacha físeáin agus stádas beo tionscadail."
	/>
</svelte:head>

<div class="relative min-h-screen bg-console-bg text-console-text">
	<header class="sticky top-0 z-50 border-b border-console-border bg-console-bg/92 backdrop-blur-xl">
		<div class="section-wrap flex h-14 items-center gap-6">
			<a class="flex items-center gap-3 text-console-green" href={base || '/'}>
				<img alt="Gaeilge sa Chonsol" class="h-7 w-7" src={`${base}/logo.svg`} />
				<span class="font-mono text-[0.82rem] tracking-[0.18em]">GAEILGE SA CHONSOL</span>
			</a>
			<nav class="ml-auto hidden items-center gap-6 sm:flex">
				<a class="font-mono text-[0.72rem] tracking-[0.12em] text-console-muted hover:text-console-green" href={base || '/'}>
					CLUICHÍ
				</a>
				<a class="font-mono text-[0.72rem] tracking-[0.12em] text-console-muted hover:text-console-green" href={`${base}/guide`}>
					TREORACHA
				</a>
				<a class="font-mono text-[0.72rem] tracking-[0.12em] text-console-muted hover:text-console-green" href={`${base}/contribute`}>
					RANNÍOCAÍOCHT
				</a>
				<ExternalLink
					className="font-mono text-[0.72rem] tracking-[0.12em] text-console-muted hover:text-console-green"
					href="https://github.com/aaronsnig501/gaeilge-sa-chonsol"
				>
					GITHUB
				</ExternalLink>
			</nav>
			<span class="status-chip border-console-green/30 bg-console-green-glow text-console-green">v0.1</span>
		</div>
	</header>

	<main class="relative z-10">
		{@render children()}
	</main>

	<footer class="border-t border-console-border bg-console-bg-2/95 py-8">
		<div class="section-wrap text-center">
			<p class="font-mono text-xs tracking-[0.24em] text-console-green">GAEILGE SA CHONSOL</p>
			<p class="mt-2 font-mono text-[0.68rem] tracking-[0.12em] text-console-muted">
				Foinse oscailte ·
				<ExternalLink
					className="text-console-green hover:text-white"
					href="https://github.com/aaronsnig501/gaeilge-sa-chonsol"
				>
					GitHub
				</ExternalLink>
				· Déanta le cúram don Ghaeilge
			</p>
		</div>
	</footer>
</div>
