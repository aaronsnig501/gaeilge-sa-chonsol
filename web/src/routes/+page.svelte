<script lang="ts">
	import GameCard from '$lib/components/GameCard.svelte';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const { status } = data;
</script>

<section class="section-wrap pt-20 pb-14">
	<p class="mono-label mb-4 text-console-green">// Tionscadal foinse oscailte</p>
	<div class="grid gap-10 lg:grid-cols-[minmax(0,1fr)_300px] lg:items-end">
		<div>
			<h1 class="font-display text-[clamp(3rem,8vw,6.5rem)] font-black leading-[0.88] tracking-[-0.02em] text-white">
				GAEILGE
				<span class="block text-console-green">SA CHONSOL</span>
			</h1>
			<p class="mt-6 max-w-2xl text-lg leading-8 text-console-muted">
				Aistriúcháin Gaeilge do chluichí clasaiceacha físeáin. Ag normalú na Gaeilge sa spás
				digiteach, ceann ar cheann.
			</p>
			<div class="mt-8 flex flex-wrap gap-4">
				<a class="console-button console-button-primary" href="#games">Faigh an paiste</a>
				<a class="console-button console-button-ghost" href="/guide">Treoir &rarr;</a>
			</div>
		</div>

		<aside class="panel scanline-border p-5">
			<p class="mono-label text-console-green">stádas beo</p>
			<p class="mt-4 font-display text-5xl font-black text-white">{status.summary.featuredProgress}%</p>
			<p class="mt-2 text-sm leading-6 text-console-muted">
				Críochnú reatha an tionscadail is faide chun cinn sa stóras.
			</p>
		</aside>
	</div>
</section>

<section class="relative z-10 border-y border-console-border bg-console-bg-2/95 py-6">
	<div class="section-wrap grid grid-cols-2 gap-6 md:grid-cols-4">
		<div class="text-center">
			<span class="block font-display text-4xl font-black text-console-green">{status.summary.completedGames}</span>
			<span class="mono-label mt-1 block text-console-muted">cluiche críochnaithe</span>
		</div>
		<div class="text-center">
			<span class="block font-display text-4xl font-black text-console-green">{status.summary.activeGames}</span>
			<span class="mono-label mt-1 block text-console-muted">i mbun oibre</span>
		</div>
		<div class="text-center">
			<span class="block font-display text-4xl font-black text-console-green">{status.summary.translatedStrings}</span>
			<span class="mono-label mt-1 block text-console-muted">téacsanna aistrithe</span>
		</div>
		<div class="text-center">
			<span class="block font-display text-4xl font-black text-console-green">{status.summary.featuredProgress}%</span>
			<span class="mono-label mt-1 block text-console-muted">príomh-dul chun cinn</span>
		</div>
	</div>
</section>

<section class="section-wrap py-12">
	<div class="border border-console-red/25 border-l-4 border-l-console-red bg-console-red/8 p-6 md:flex md:items-center md:gap-8">
		<div class="text-3xl leading-none">⚑</div>
		<div class="mt-4 md:mt-0">
			<h2 class="font-display text-2xl font-bold uppercase tracking-[0.05em] text-white">
				Cabhair ag teastáil
			</h2>
			<p class="mt-2 max-w-3xl text-sm leading-7 text-console-muted">
				Tá roinnt cluichí fós le haistriú go hiomlán. Má tá Gaeilge agat nó má tá suim agat i
				gcódú, féach ar na heisiúintí oscailte agus beidh fáilte romhat ranníocaíocht a dhéanamh.
			</p>
		</div>
		<a class="console-button console-button-ghost mt-5 md:mt-0 md:ml-auto" href="https://github.com/aaronsnig501/gaeilge-sa-chonsol/issues">
			Féach ar eisiúintí
		</a>
	</div>
</section>

<section class="section-wrap pb-16" id="games">
	<div class="mb-8 flex flex-wrap items-end justify-between gap-4 border-b border-console-border pb-4">
		<div>
			<p class="mono-label text-console-green">cluichí</p>
			<h2 class="mt-2 font-display text-3xl font-bold uppercase tracking-[0.05em] text-white">
				Cláraithe sa chóras
			</h2>
		</div>
		<span class="font-mono text-[0.72rem] tracking-[0.12em] text-console-muted">
			// {status.games.length} cláraíodh
		</span>
	</div>

	<div class="grid gap-px overflow-hidden border border-console-border bg-console-border md:grid-cols-2">
		{#each status.games as game}
			<GameCard {game} />
		{/each}
	</div>
</section>
