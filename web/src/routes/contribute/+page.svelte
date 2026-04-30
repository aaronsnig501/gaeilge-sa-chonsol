<script lang="ts">
	import { base } from '$app/paths';
	import ExternalLink from '$lib/components/ExternalLink.svelte';
	import ProgressBar from '$lib/components/ProgressBar.svelte';
	import { getGameHref, getNeedsNativeReviewUrl, getRepoUrl, helpWantedGames } from '$lib/data';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const { status } = data;
	const repoUrl = getRepoUrl();
	const nativeReviewUrl = getNeedsNativeReviewUrl();
	const activeGames = $derived(helpWantedGames(status));
</script>

<svelte:head>
	<title>Ranníocaíocht · Gaeilge sa Chonsol</title>
</svelte:head>

<section class="section-wrap pt-20 pb-10">
	<div class="grid gap-8 lg:grid-cols-[minmax(0,1fr)_320px] lg:items-end">
		<div>
			<p class="mono-label mb-4 text-console-green">// Bí páirteach</p>
			<h1 class="font-display text-[clamp(3rem,7vw,5.8rem)] font-black leading-[0.9] text-white">
				Cuidigh linn
				<span class="block text-console-green">cluichí a aistriú</span>
			</h1>
			<p class="mt-6 max-w-3xl text-lg leading-8 text-console-muted">
				Tá an tionscadal seo ann chun Gaeilge a thabhairt isteach i spásanna digiteacha nach bhfuair
				mórán aire riamh. Tá áit anseo d’aistritheoirí, do chainteoirí dúchais, do hackers ROM,
				agus do dhaoine atá ag iarraidh foghlaim tríd an gcomhoibriú.
			</p>
			<div class="mt-8 flex flex-wrap gap-3">
				<ExternalLink className="console-button console-button-primary" href={repoUrl}>
					Fork ar GitHub
				</ExternalLink>
				<ExternalLink className="console-button console-button-ghost" href={nativeReviewUrl}>
					Athbhreithniú dúchais de dhíth
				</ExternalLink>
			</div>
		</div>

		<aside class="panel scanline-border p-6">
			<p class="mono-label text-console-green">cén fáth a bhfuil sé tábhachtach?</p>
			<div class="mt-5 space-y-4 text-sm leading-7 text-console-muted">
				<p>Cuireann aistriúcháin mhaith Gaeilge beatha nua i gcluichí clasaiceacha agus cruthaíonn siad ábhar foghlama agus pobail timpeall na teanga.</p>
				<p>Ní gá duit a bheith i do shaineolaí ar an dá rud. Is minic a thagann an obair is fearr ó chainteoirí agus forbróirí ag obair le chéile.</p>
			</div>
		</aside>
	</div>
</section>

<section class="section-wrap pb-10">
	<div class="mb-6 flex items-end justify-between gap-4 border-b border-console-border pb-4">
		<div>
			<p class="mono-label text-console-green">cluichí gníomhacha</p>
			<h2 class="mt-2 font-display text-3xl font-bold uppercase tracking-[0.05em] text-white">
				Cabhair ag teastáil anois
			</h2>
		</div>
		<span class="font-mono text-[0.72rem] tracking-[0.12em] text-console-muted">
			// {activeGames.length} gníomhach
		</span>
	</div>

	<div class="grid gap-4">
		{#each activeGames as game}
			<div class="panel p-5">
				<div class="flex flex-col gap-5 md:flex-row md:items-start md:justify-between">
					<div class="min-w-0">
						<div class="flex flex-wrap items-center gap-3">
							<span class="status-chip border-white/8 bg-white/4 text-console-muted">
								{game.consoleLabel} · {game.region}
							</span>
							<span class="status-chip border-console-red/35 bg-console-red/12 text-console-red">
								Cabhair ag teastáil
							</span>
						</div>
						<h3 class="mt-4 font-display text-2xl font-bold text-white">{game.title}</h3>
						<p class="mt-2 max-w-3xl text-sm leading-7 text-console-muted">{game.description}</p>
					</div>

					<div class="w-full md:max-w-[320px]">
						<ProgressBar
							accent={game.accent}
							countText={`${game.categories.reduce((sum, item) => sum + item.translated, 0)}/${game.categories.reduce((sum, item) => sum + item.total, 0)}`}
							label="Dul chun cinn"
							progress={game.progress}
						/>
					</div>
				</div>

				<div class="mt-5 flex flex-wrap gap-3 border-t border-console-border pt-4">
					<a class="console-button console-button-ghost" href={getGameHref(game)}>Leathanach an chluiche</a>
					{#if game.links.notes}
						<a class="console-button console-button-ghost" href={game.links.notes}>Nótaí teicniúla</a>
					{/if}
					{#if game.links.issues}
						<ExternalLink className="console-button console-button-ghost" href={game.links.issues}>
							Eisiúintí an chluiche
						</ExternalLink>
					{/if}
				</div>
			</div>
		{/each}
	</div>
</section>

<section class="section-wrap pb-10">
	<div class="grid gap-6 lg:grid-cols-2">
		<div class="panel p-6">
			<p class="mono-label text-console-green">// Conas tosú</p>
			<ol class="mt-5 space-y-5 text-sm leading-7 text-console-muted">
				<li>
					<strong class="text-console-text">1. Fork an repo.</strong>
					Cruthaigh do chóip féin ar GitHub ionas gur féidir leat obair a dhéanamh ar do luas féin.
				</li>
				<li>
					<strong class="text-console-text">2. Suiteáil spleáchais.</strong>
					Úsáid an sreabhadh áitiúil céanna leis an tionscadal:
					<code class="mt-2 block rounded-sm border border-console-border bg-console-bg px-3 py-2 font-mono text-console-green">uv venv && source .venv/bin/activate && uv pip install -e .</code>
				</li>
				<li>
					<strong class="text-console-text">3. Cláraigh an ROM.</strong>
					<code class="mt-2 block rounded-sm border border-console-border bg-console-bg px-3 py-2 font-mono text-console-green">gsc init --console ps1 --game spyro1 --rom ~/roms/spyro.bin</code>
				</li>
				<li>
					<strong class="text-console-text">4. Cuir an CSV in eagar.</strong>
					Oibrigh sna colúin `english` agus `irish`, agus tabhair aird ar na buiséid bhearta.
				</li>
				<li>
					<strong class="text-console-text">5. Bailíochtaigh agus seol PR.</strong>
					Rith `gsc validate`, ansin oscail pull request le nótaí soiléire faoin méid a d’athraigh tú.
				</li>
			</ol>
		</div>

		<div class="panel p-6">
			<p class="mono-label text-console-green">// Cé dó atá sé seo?</p>
			<div class="mt-5 space-y-5 text-sm leading-7 text-console-muted">
				<div>
					<h3 class="font-display text-xl font-bold text-white">Cainteoirí Gaeilge nach forbróirí iad</h3>
					<p class="mt-2">Is féidir leat cabhrú le haistriúcháin, le ton, le cruinneas teanga, agus le hathbhreithniú dúchais fiú mura dteastaíonn uait cód a scríobh.</p>
				</div>
				<div>
					<h3 class="font-display text-xl font-bold text-white">Forbróirí nach cainteoirí líofa iad</h3>
					<p class="mt-2">Is féidir leat uirlisí, tástálacha, tógálacha paiste, agus taighde ar fhormáidí comhaid a fheabhsú gan an t-aistriúchán féin a scríobh.</p>
				</div>
				<div>
					<h3 class="font-display text-xl font-bold text-white">An dá ghrúpa le chéile</h3>
					<p class="mt-2">Sin an tsamhail is fearr: duine amháin ag tuiscint an chóid agus duine eile ag cinntiú go bhfuil an Ghaeilge nádúrtha agus láidir.</p>
				</div>
			</div>
		</div>
	</div>
</section>

<section class="section-wrap pb-16">
	<div class="grid gap-6 lg:grid-cols-[minmax(0,1fr)_340px]">
		<div class="panel p-6">
			<p class="mono-label text-console-green">// Tuilleadh acmhainní</p>
			<div class="mt-5 grid gap-4 sm:grid-cols-2">
				<a class="rounded-sm border border-console-border bg-console-bg/55 p-4 hover:border-console-green" href={`${base}/guide`}>
					<p class="font-display text-xl font-bold text-white">Treoir an tsuímh</p>
					<p class="mt-2 text-sm leading-7 text-console-muted">Forléargas ar struchtúr an tsuímh agus ar an mbealach a úsáidtear `status.json` agus mdsvex.</p>
				</a>
				{#if activeGames[0]?.links.notes}
					<a class="rounded-sm border border-console-border bg-console-bg/55 p-4 hover:border-console-green" href={activeGames[0].links.notes}>
						<p class="font-display text-xl font-bold text-white">Nótaí cluiche</p>
						<p class="mt-2 text-sm leading-7 text-console-muted">Nótaí teicniúla, offsetanna, srianta, agus aistear na haistriúcháin do chluiche ar leith.</p>
					</a>
				{/if}
			</div>
		</div>

		<div class="panel p-6">
			<p class="mono-label text-console-green">// Pobal & teagmháil</p>
			<div class="mt-5 space-y-4 text-sm leading-7 text-console-muted">
				<p>Faoi láthair, is é GitHub príomh-áit an chomhordaithe. Is iad eisiúintí agus pull requests an bealach is soiléire chun obair a roinnt agus ceisteanna a ardú.</p>
				<ExternalLink className="console-button console-button-ghost w-full" href={repoUrl}>
					Príomhrepo ar GitHub
				</ExternalLink>
				<ExternalLink className="console-button console-button-ghost w-full" href={nativeReviewUrl}>
					Eisiúintí le hathbhreithniú dúchais
				</ExternalLink>
			</div>
		</div>
	</div>
</section>
