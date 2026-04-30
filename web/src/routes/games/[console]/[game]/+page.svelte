<script lang="ts">
	import { base } from '$app/paths';
	import ExternalLink from '$lib/components/ExternalLink.svelte';
	import ProgressBar from '$lib/components/ProgressBar.svelte';
	import StatusBadge from '$lib/components/StatusBadge.svelte';
	import { consoleName } from '$lib/data';
	import { getNotesComponent } from '$lib/game-notes';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const { game } = data;
	const notesComponent = $derived(getNotesComponent(game.console, game.game));
	const totalTranslated = $derived(game.categories.reduce((sum, item) => sum + item.translated, 0));
	const totalStrings = $derived(game.categories.reduce((sum, item) => sum + item.total, 0));
	const consoleLabel = $derived(consoleName(game));
	const coverArtPath = $derived(`${base}/covers/${game.game}.png`);
</script>

<svelte:head>
	<title>{game.title} · Gaeilge sa Chonsol</title>
</svelte:head>

<section class="section-wrap py-16">
	<div class="mb-10 grid gap-6 lg:grid-cols-[220px_minmax(0,1fr)] lg:items-center">
		<div class="panel relative aspect-[3/4] overflow-hidden p-3">
			<div
				class="absolute inset-0 opacity-20"
				style={`background:radial-gradient(circle at top, ${game.accent} 0%, transparent 58%)`}
			></div>
			<div class="relative h-full overflow-hidden rounded-sm border border-console-border/70 bg-console-bg/55">
				<img
					alt={`Cover art for ${game.title}`}
					class="h-full w-full object-cover object-center"
					src={coverArtPath}
				/>
				<div class="absolute inset-x-0 bottom-0 bg-gradient-to-t from-console-bg via-console-bg/70 to-transparent p-4">
					<p class="mono-label text-console-green">cover art</p>
					<p class="mt-2 font-display text-2xl font-black leading-none text-white">{game.title}</p>
					<p class="mt-1 font-mono text-[0.68rem] uppercase tracking-[0.12em] text-console-muted">
						{consoleLabel}
					</p>
				</div>
			</div>
		</div>

		<div class="space-y-5">
			<div class="flex flex-wrap items-center gap-3">
				<span class="status-chip border-white/8 bg-white/4 text-console-muted">
					{consoleLabel} · {game.region}
				</span>
				<StatusBadge state={game.state} />
				{#if game.helpWanted}
					<span class="status-chip border-console-red/35 bg-console-red/12 text-console-red">
						Cabhair ag teastáil
					</span>
				{/if}
			</div>
			<h1 class="font-display text-[clamp(2.8rem,6vw,5.4rem)] font-black leading-[0.92] text-white">
				{game.title}
			</h1>
			<p class="font-mono text-[0.72rem] tracking-[0.15em] text-console-muted">{game.subtitle}</p>
			<p class="max-w-3xl text-sm leading-8 text-console-muted">{game.description}</p>
			<div class="flex flex-wrap gap-3">
				{#if game.nightly}
					<a class="console-button console-button-primary" href={game.nightly.href}>Íoslódáil paiste</a>
				{/if}
				{#if game.links.issues}
					<ExternalLink className="console-button console-button-ghost" href={game.links.issues}>
						Eisiúintí GitHub
					</ExternalLink>
				{/if}
			</div>
		</div>
	</div>

	<div class="grid gap-10 lg:grid-cols-[minmax(0,1fr)_340px]">
		<div class="space-y-8">
			<div class="panel p-6 scanline-border">
				<p class="mono-label text-console-green">// Forléargas</p>
				<div class="mt-5">
					<ProgressBar
						accent={game.accent}
						countText={`${totalTranslated}/${totalStrings}`}
						label="Iomlán aistrithe"
						progress={game.progress}
					/>
				</div>
				<div class="mt-5 grid gap-4 sm:grid-cols-3">
					<div class="rounded-sm border border-console-border bg-console-bg/60 p-4">
						<p class="mono-label text-console-muted">stádas</p>
						<p class="mt-2 font-display text-2xl font-bold text-white">{game.statusLabel}</p>
					</div>
					<div class="rounded-sm border border-console-border bg-console-bg/60 p-4">
						<p class="mono-label text-console-muted">aistrithe</p>
						<p class="mt-2 font-display text-2xl font-bold text-white">{totalTranslated}</p>
					</div>
					<div class="rounded-sm border border-console-border bg-console-bg/60 p-4">
						<p class="mono-label text-console-muted">sprioc</p>
						<p class="mt-2 font-display text-2xl font-bold text-white">{totalStrings}</p>
					</div>
				</div>
			</div>

			<div class="panel p-6">
				<p class="mono-label text-console-green">// Miondealú catagóirí</p>
				<div class="mt-5 overflow-hidden rounded-sm border border-console-border">
					<table class="w-full border-collapse">
						<thead class="bg-console-bg/70">
							<tr class="text-left">
								<th class="px-4 py-3 font-mono text-[0.62rem] uppercase tracking-[0.14em] text-console-muted">Catagóir</th>
								<th class="px-4 py-3 font-mono text-[0.62rem] uppercase tracking-[0.14em] text-console-muted">Aistrithe</th>
								<th class="px-4 py-3 font-mono text-[0.62rem] uppercase tracking-[0.14em] text-console-muted">Dul chun cinn</th>
							</tr>
						</thead>
						<tbody>
							{#each game.categories as category}
								<tr class="border-t border-console-border/70 align-top">
									<td class="px-4 py-4">
										<p class="text-sm text-console-text">{category.name}</p>
									</td>
									<td class="px-4 py-4 font-mono text-[0.72rem] uppercase tracking-[0.1em] text-console-muted">
										{category.translated}/{category.total}
									</td>
									<td class="px-4 py-4">
										<div class="flex items-center gap-3">
											<div class="h-1.5 flex-1 bg-white/6">
												<div
													class="h-full"
													style={`width:${category.progress}%;background:${game.accent};box-shadow:0 0 18px ${game.accent}33`}
												></div>
											</div>
											<span class="font-mono text-[0.72rem] uppercase tracking-[0.1em] text-console-muted">
												{category.progress}%
											</span>
										</div>
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			</div>

			{#if notesComponent}
				<div class="panel p-6">
					<p class="mono-label text-console-green">// Nótaí aistriúcháin</p>
					<div class="prose-console mt-6 max-w-none">
						<svelte:component this={notesComponent} />
					</div>
				</div>
			{/if}

			<div class="panel p-6">
				<p class="mono-label text-console-green">// Conas ranníocaíocht a dhéanamh</p>
				<div class="mt-5 space-y-4 text-sm leading-7 text-console-muted">
					<p>
						Baineann ranníocaíocht leis an tionscadal seo le taighde, le haistriúchán, agus le
						tástáil paistí. Tá obair nua níos éasca nuair atá stádas agus catagóirí an chluiche
						soiléir.
					</p>
					<ul class="list-disc space-y-2 pl-5">
						<li>Déan athbhreithniú ar na catagóirí is laige agus ar na buiséid bhearta.</li>
						<li>Úsáid an sreabhadh `gsc extract`, `gsc validate`, agus `gsc patch` go háitiúil.</li>
						<li>Oscail eisiúint GitHub má aimsíonn tú teorainn theicniúil nó téacs amhrasach.</li>
					</ul>
				</div>
			</div>
		</div>

		<aside class="space-y-6">
			{#if game.nightly}
				<div class="panel border-l-4 border-l-console-green p-6">
					<p class="mono-label text-console-green">// Paiste</p>
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
						<ExternalLink className="console-button console-button-ghost w-full" href={game.links.repo}>
							GitHub
						</ExternalLink>
					{/if}
					{#if game.links.issues}
						<ExternalLink className="console-button console-button-ghost w-full" href={game.links.issues}>
							Eisiúintí an chluiche
						</ExternalLink>
					{/if}
				</div>
			</div>

			<div class="panel p-6">
				<p class="mono-label text-console-green">// Stádas reatha</p>
				<div class="mt-4 space-y-3 text-sm leading-7 text-console-muted">
					<p>Tá an leathanach seo ag léamh a stádais ó <code class="font-mono text-console-green">status.json</code>.</p>
					<p>Nuair a athraíonn an CSV aistriúcháin, is féidir an suíomh a athghiniúint gan eagarthóireacht láimhe ar leathanaigh sonraí.</p>
				</div>
			</div>

			<div class="panel p-6">
				<p class="mono-label text-console-green">// Cuidiú úsáideach</p>
				<div class="mt-4 space-y-3 text-sm leading-7 text-console-muted">
					<p>Má tá an cluiche seo fós faoi bhun a sprice, is iad téacsanna gearra UI agus dialóg neamhchríochnaithe na háiteanna is fearr le tosú.</p>
					{#if game.helpWanted}
						<p class="rounded-sm border border-console-red/35 bg-console-red/10 px-4 py-3 text-console-red">
							Tá an cluiche seo lipéadaithe mar obair a bhfuil cabhair de dhíth uirthi faoi láthair.
						</p>
					{/if}
				</div>
			</div>
		</aside>
	</div>
</section>
