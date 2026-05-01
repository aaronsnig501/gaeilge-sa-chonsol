<script lang="ts">
	import { base } from '$app/paths';
	import ExternalLink from '$lib/components/ExternalLink.svelte';
	import GameCard from '$lib/components/GameCard.svelte';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const status = $derived(data.status);
	const helpWantedThreshold = 50;

	type ConsoleFilter = 'all' | string;
	type StatusFilter = 'all' | 'complete' | 'progress' | 'wanted' | 'help-wanted';
	type SortMode = 'progress-desc' | 'progress-asc' | 'alphabetical';

	const consoleOptions = $derived([
		'all',
		...new Set(status.games.map((game) => game.console))
	]);

	let selectedConsole = $state<ConsoleFilter>('all');
	let selectedStatus = $state<StatusFilter>('all');
	let sortMode = $state<SortMode>('progress-desc');

	const helpWantedGames = $derived(
		status.games.filter((game) => game.helpWanted || game.progress < helpWantedThreshold)
	);

	const filteredGames = $derived.by(() => {
		const filtered = status.games.filter((game) => {
			if (selectedConsole !== 'all' && game.console !== selectedConsole) return false;
			if (selectedStatus === 'complete' && game.state !== 'complete') return false;
			if (selectedStatus === 'progress' && game.state !== 'progress') return false;
			if (selectedStatus === 'wanted' && game.state !== 'wanted') return false;
			if (selectedStatus === 'help-wanted' && !(game.helpWanted || game.progress < helpWantedThreshold)) {
				return false;
			}
			return true;
		});

		return filtered.sort((left, right) => {
			if (sortMode === 'alphabetical') return left.title.localeCompare(right.title);
			if (sortMode === 'progress-asc') return left.progress - right.progress || left.title.localeCompare(right.title);
			return right.progress - left.progress || left.title.localeCompare(right.title);
		});
	});
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
				<a class="console-button console-button-ghost" href={`${base}/guide`}>Treoir &rarr;</a>
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
			<span class="mono-label mt-1 block text-console-tertiary">cluiche críochnaithe</span>
		</div>
		<div class="text-center">
			<span class="block font-display text-4xl font-black text-console-green">{status.summary.activeGames}</span>
			<span class="mono-label mt-1 block text-console-tertiary">i mbun oibre</span>
		</div>
		<div class="text-center">
			<span class="block font-display text-4xl font-black text-console-green">{status.summary.translatedStrings}</span>
			<span class="mono-label mt-1 block text-console-tertiary">téacsanna aistrithe</span>
		</div>
		<div class="text-center">
			<span class="block font-display text-4xl font-black text-console-green">{status.summary.featuredProgress}%</span>
			<span class="mono-label mt-1 block text-console-tertiary">príomh-dul chun cinn</span>
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
			{#if helpWantedGames.length > 0}
				<p class="mt-3 font-mono text-[0.68rem] uppercase tracking-[0.12em] text-console-red">
					{helpWantedGames.length} cluiche faoi bhun {helpWantedThreshold}% faoi láthair
				</p>
			{/if}
		</div>
		<ExternalLink
			className="console-button console-button-ghost mt-5 md:mt-0 md:ml-auto"
			href="https://github.com/aaronsnig501/gaeilge-sa-chonsol/issues"
		>
			Féach ar eisiúintí
		</ExternalLink>
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
		<span class="font-mono text-[0.72rem] tracking-[0.12em] text-console-tertiary">
			// {filteredGames.length}/{status.games.length} le feiceáil
		</span>
	</div>

	<div class="mb-6 grid gap-4 rounded-sm border border-console-border bg-console-bg-2/85 p-4 md:grid-cols-[minmax(0,1fr)_220px]">
		<div class="space-y-3">
			<p class="mono-label text-console-green">scagairí</p>
			<div class="flex flex-wrap gap-2">
				{#each consoleOptions as option}
					<button
						class={`status-chip cursor-pointer ${selectedConsole === option ? 'border-console-green bg-console-green-glow text-console-green' : 'border-console-border-moderate bg-console-border-subtle text-console-muted hover:border-console-green hover:bg-console-green-glow hover:text-console-green'}`}
						onclick={() => (selectedConsole = option)}
						type="button"
					>
						{option === 'all' ? 'gach consól' : option.toUpperCase()}
					</button>
				{/each}
			</div>
			<div class="flex flex-wrap gap-2">
				{#each [
					['all', 'gach stádas'],
					['progress', 'i mbun oibre'],
					['help-wanted', 'cabhair ag teastáil'],
					['complete', 'críochnaithe']
				] as [value, label]}
					<button
						class={`status-chip cursor-pointer ${selectedStatus === value ? 'border-console-green bg-console-green-glow text-console-green' : 'border-console-border-moderate bg-console-border-subtle text-console-muted hover:border-console-green hover:bg-console-green-glow hover:text-console-green'}`}
						onclick={() => (selectedStatus = value as StatusFilter)}
						type="button"
					>
						{label}
					</button>
				{/each}
			</div>
		</div>

		<div class="space-y-3">
			<label class="mono-label block text-console-green" for="sort-mode">sórtáil</label>
			<select
				bind:value={sortMode}
				class="w-full rounded-sm border border-console-border bg-console-bg px-3 py-3 font-mono text-xs uppercase tracking-[0.12em] text-console-text outline-none transition-colors focus:border-console-green"
				id="sort-mode"
			>
				<option value="progress-desc">dul chun cinn: ard go híseal</option>
				<option value="progress-asc">dul chun cinn: íseal go hard</option>
				<option value="alphabetical">aibítre</option>
			</select>
		</div>
	</div>

	<div class="grid gap-px overflow-hidden border border-console-border bg-console-border md:grid-cols-2">
		{#each filteredGames as game}
			<GameCard {game} />
		{/each}
	</div>

	{#if filteredGames.length === 0}
		<div class="border border-console-border border-t-0 bg-console-bg-2/75 px-6 py-8 text-center font-mono text-[0.72rem] uppercase tracking-[0.12em] text-console-tertiary">
			Níl cluichí ar bith ag meaitseáil na scagairí seo.
		</div>
	{/if}
</section>
