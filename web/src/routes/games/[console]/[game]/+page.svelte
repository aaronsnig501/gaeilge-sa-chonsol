<script lang="ts">
	import ProgressBar from '$lib/components/ProgressBar.svelte';
	import StatusBadge from '$lib/components/StatusBadge.svelte';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const { game } = data;
</script>

<svelte:head>
	<title>{game.title} · Gaeilge sa Chonsol</title>
</svelte:head>

<section class="section-wrap py-16">
	<div class="grid gap-10 lg:grid-cols-[minmax(0,1fr)_340px]">
		<div class="space-y-8">
			<div class="space-y-4">
				<div class="flex flex-wrap items-center gap-3">
					<span class="status-chip border-white/8 bg-white/4 text-console-muted">
						{game.console.toUpperCase()} · {game.region}
					</span>
					<StatusBadge state={game.state} />
				</div>
				<h1 class="font-display text-[clamp(2.6rem,6vw,4.8rem)] font-black leading-[0.92] text-white">
					{game.title}
				</h1>
				<p class="font-mono text-[0.72rem] tracking-[0.15em] text-console-muted">{game.subtitle}</p>
			</div>

			<div class="panel p-6 scanline-border">
				<p class="mono-label text-console-green">// Forléargas</p>
				<div class="mt-5">
					<ProgressBar
						accent={game.accent}
						countText={`${game.categories.reduce((sum, item) => sum + item.translated, 0)}/${game.categories.reduce((sum, item) => sum + item.total, 0)}`}
						label="Iomlán aistrithe"
						progress={game.progress}
					/>
				</div>
				<p class="mt-5 text-sm leading-7 text-console-muted">{game.description}</p>
			</div>

			<div class="panel p-6">
				<p class="mono-label text-console-green">// Catagóirí</p>
				<div class="mt-5 space-y-4">
					{#each game.categories as category}
						<ProgressBar
							accent={game.accent}
							countText={`${category.translated}/${category.total}`}
							compact={true}
							label={category.name}
							progress={category.progress}
						/>
					{/each}
				</div>
			</div>
		</div>

		<aside class="space-y-6">
			{#if game.nightly}
				<div class="panel border-l-4 border-l-console-green p-6">
					<p class="mono-label text-console-green">// Paiste nightly</p>
					<h2 class="mt-4 font-mono text-sm tracking-[0.12em] text-white">↓ {game.nightly.label}</h2>
					<p class="mt-3 text-sm leading-7 text-console-muted">{game.nightly.description}</p>
					<a class="console-button console-button-primary mt-5 w-full" href={game.nightly.href}>
						Íoslódáil paiste
					</a>
				</div>
			{/if}

			<div class="panel p-6">
				<p class="mono-label text-console-green">// Nascanna</p>
				<div class="mt-4 grid gap-3">
					{#if game.links.notes}
						<a class="console-button console-button-ghost w-full" href={game.links.notes}>Nótaí</a>
					{/if}
					{#if game.links.repo}
						<a class="console-button console-button-ghost w-full" href={game.links.repo}>GitHub</a>
					{/if}
					{#if game.links.issues}
						<a class="console-button console-button-ghost w-full" href={game.links.issues}>Eisiúintí</a>
					{/if}
				</div>
			</div>

			<div class="panel p-6">
				<p class="mono-label text-console-green">// Nóta</p>
				<p class="mt-4 text-sm leading-7 text-console-muted">
					Tá an leathanach seo ag léamh a stádais ó <code class="font-mono text-console-green">status.json</code>
					ionas gur féidir leis an suíomh a nuashonrú gan athstruchtúrú láimhe.
				</p>
			</div>
		</aside>
	</div>
</section>
