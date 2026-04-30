<script lang="ts">
	import ProgressBar from '$lib/components/ProgressBar.svelte';
	import StatusBadge from '$lib/components/StatusBadge.svelte';
	import { consoleName, getGameHref, topCategories } from '$lib/data';
	import type { GameStatus } from '$lib/types';

	interface Props {
		game: GameStatus;
	}

	let { game }: Props = $props();
	const href = $derived(getGameHref(game));
	const categories = $derived(topCategories(game));
	const consoleLabel = $derived(consoleName(game));
</script>

<article
	class="group relative flex h-full flex-col gap-5 overflow-hidden bg-console-bg-2 p-6 transition-all duration-200 hover:bg-console-bg-3"
	style={`--card-accent:${game.accent}`}
>
	<div class="absolute inset-y-0 left-0 w-[3px] origin-bottom scale-y-0 bg-[var(--card-accent)] transition-transform duration-200 group-hover:scale-y-100"></div>

	<div class="flex items-start justify-between gap-4">
		<span class="status-chip border-white/8 bg-white/4 text-console-muted">
			{consoleLabel} · {game.region}
		</span>
		<StatusBadge state={game.state} />
	</div>

	<div class="space-y-1">
		<h3 class="font-display text-[1.5rem] font-bold leading-none tracking-[0.03em] text-white">
			<a class="hover:text-[var(--card-accent)]" href={href}>{game.title}</a>
		</h3>
		<p class="font-mono text-[0.68rem] tracking-[0.14em] text-console-muted">
			{game.subtitle}
		</p>
	</div>

	{#if game.helpWanted}
		<div class="inline-flex w-fit items-center gap-2 rounded-sm border border-console-red/35 bg-console-red/12 px-3 py-1.5 font-mono text-[0.62rem] uppercase tracking-[0.12em] text-console-red">
			<span>⚑</span>
			<span>Cabhair ag teastáil</span>
		</div>
	{/if}

	<ProgressBar label="Iomlán aistrithe" progress={game.progress} accent={game.accent} />

	<div class="space-y-2">
		{#each categories as category}
			<div class="grid grid-cols-[minmax(0,1fr)_70px_42px] items-center gap-3">
				<span class="truncate font-mono text-[0.62rem] tracking-[0.08em] text-console-muted">
					{category.name}
				</span>
				<div class="h-[3px] bg-white/5">
					<div class="h-full" style={`width:${category.progress}%;background:${game.accent};opacity:.6`}></div>
				</div>
				<span class="text-right font-mono text-[0.62rem] tracking-[0.08em] text-console-muted">
					{category.progress}%
				</span>
			</div>
		{/each}
	</div>

	<div class="mt-auto flex flex-wrap gap-2 border-t border-console-border pt-4">
		{#if game.nightly}
			<a
				class="flex-1 rounded-sm border border-console-green/30 bg-console-green/10 px-3 py-2 text-center font-mono text-[0.65rem] uppercase tracking-[0.12em] text-console-green hover:border-console-green hover:bg-console-green/18"
				href={game.nightly.href}
			>
				↓ Nightly
			</a>
		{/if}
		<a
			class="flex-1 rounded-sm border border-console-border px-3 py-2 text-center font-mono text-[0.65rem] uppercase tracking-[0.12em] text-console-muted group-hover:border-console-green group-hover:text-console-green"
			href={href}
		>
			Mionsonraí
		</a>
	</div>
</article>
