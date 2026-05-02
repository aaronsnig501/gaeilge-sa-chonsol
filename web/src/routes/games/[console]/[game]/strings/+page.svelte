<script lang="ts">
	import { base } from '$app/paths';
	import type { PageProps } from './$types';
	import type { StringRecord, StringStatus } from '$lib/types';

	const DEFAULT_REPO_URL = 'https://github.com/aaronsnig501/gaeilge-sa-chonsol';
	const STATUS_OPTIONS: Array<{ value: 'all' | StringStatus; label: string; dotClass: string }> = [
		{ value: 'all', label: 'Gach ceann', dotClass: 'bg-console-green' },
		{ value: 'verified', label: 'Fíoraithe', dotClass: 'bg-console-green shadow-[0_0_8px_rgba(46,204,113,0.45)]' },
		{ value: 'draft', label: 'Dréacht', dotClass: 'bg-console-amber' },
		{ value: 'compromised', label: 'Comhréiteach', dotClass: 'bg-[#e67e22]' },
		{ value: 'untranslated', label: 'Gan aistriú', dotClass: 'border border-white/20 bg-white/12' },
	];

	const FADA_REPLACEMENTS: Record<string, string> = {
		Á: 'Aa',
		É: 'Ea',
		Í: 'Ia',
		Ó: 'Oa',
		Ú: 'Ua',
		á: 'aa',
		é: 'ea',
		í: 'ia',
		ó: 'oa',
		ú: 'ua',
	};

	let { data }: PageProps = $props();
	const game = $derived(data.game);
	const detailHref = $derived(`${base}/games/${game.console}/${game.game}`);
	const summaryText = $derived(
		`${game.categories.reduce((sum, category) => sum + category.translated, 0)} / ${game.categories.reduce((sum, category) => sum + category.total, 0)} aistrithe · ${game.progress}%`,
	);

	let selectedStatus = $state<'all' | StringStatus>('all');
	let searchQuery = $state('');
	let collapsedGroups = $state<Record<string, boolean>>({});
	let selectedEntry = $state<StringRecord | null>(null);
	let suggestedIrish = $state('');
	let suggestionNote = $state('');

	const filteredCategories = $derived.by(() =>
		game.categories
			.map((category) => ({
				...category,
				strings: category.strings.filter((entry) => matchesFilters(entry, selectedStatus, searchQuery)),
			}))
			.filter((category) => category.strings.length > 0),
	);

	const suggestionUsed = $derived(selectedEntry ? encodeLength(suggestedIrish) : 0);
	const suggestionBudgetTone = $derived(selectedEntry ? budgetTone(suggestionUsed, selectedEntry.budget) : 'ok');
	const suggestionBudgetClass = $derived(
		suggestionBudgetTone === 'over'
			? 'text-console-red'
			: suggestionBudgetTone === 'tight'
				? 'text-console-amber'
				: 'text-console-green',
	);

	function matchesFilters(entry: StringRecord, status: 'all' | StringStatus, query: string): boolean {
		if (status === 'verified' && !entry.verified) return false;
		if (status === 'compromised' && !entry.compromised) return false;
		if (status === 'draft' && (!entry.irish || entry.verified || entry.compromised)) return false;
		if (status === 'untranslated' && entry.irish) return false;
		if (!query.trim()) return true;
		const normalized = query.trim().toLowerCase();
		return [entry.offset, entry.english, entry.irish, entry.note ?? ''].some((value) =>
			value.toLowerCase().includes(normalized),
		);
	}

	function toggleCategory(name: string): void {
		collapsedGroups = {
			...collapsedGroups,
			[name]: !collapsedGroups[name],
		};
	}

	function isCollapsed(name: string): boolean {
		return collapsedGroups[name] === true;
	}

	function statusLabel(status: StringStatus): string {
		switch (status) {
			case 'verified':
				return 'Fíoraithe';
			case 'draft':
				return 'Dréacht';
			case 'compromised':
				return 'Comhréiteach';
			case 'untranslated':
			default:
				return 'Gan aistriú';
		}
	}

	function statusDotClass(status: StringStatus): string {
		switch (status) {
			case 'verified':
				return 'bg-console-green shadow-[0_0_8px_rgba(46,204,113,0.45)]';
			case 'draft':
				return 'bg-console-amber';
			case 'compromised':
				return 'bg-[#e67e22]';
			case 'untranslated':
			default:
				return 'border border-white/20 bg-white/12';
		}
	}

	function encodeLength(value: string): number {
		let encoded = value;
		for (const [original, replacement] of Object.entries(FADA_REPLACEMENTS)) {
			encoded = encoded.replaceAll(original, replacement);
		}
		return Array.from(encoded).length;
	}

	function budgetTone(used: number, budget: number): 'ok' | 'tight' | 'over' | 'empty' {
		if (used <= 0) return 'empty';
		if (used > budget) return 'over';
		if (used >= budget - 2) return 'tight';
		return 'ok';
	}

	function budgetClass(entry: StringRecord): string {
		const tone = budgetTone(entry.used, entry.budget);
		switch (tone) {
			case 'over':
				return 'border-console-red/20 bg-console-red/10 text-console-red';
			case 'tight':
				return 'border-console-amber/20 bg-console-amber/10 text-console-amber';
			case 'ok':
				return 'border-console-green/20 bg-console-green/10 text-console-green';
			case 'empty':
			default:
				return 'border-console-border-subtle bg-white/5 text-console-tertiary';
		}
	}

	function budgetText(entry: StringRecord): string {
		return entry.used > 0 ? `${entry.used}/${entry.budget}` : `0/${entry.budget}`;
	}

	function openSuggest(entry: StringRecord): void {
		selectedEntry = entry;
		suggestedIrish = entry.irish;
		suggestionNote = entry.note ?? '';
	}

	function closeSuggest(): void {
		selectedEntry = null;
		suggestedIrish = '';
		suggestionNote = '';
	}

	function issueNewUrl(): string {
		return `${(game.links.repo ?? DEFAULT_REPO_URL).replace(/\/+$/, '')}/issues/new`;
	}

	function openSuggestionIssue(): void {
		if (!selectedEntry) return;
		const title = `[String Suggestion] ${selectedEntry.offset} · ${selectedEntry.english}`;
		const body = [
			'## Moladh Aistriúcháin',
			'',
			`**Cluiche:** ${game.title}`,
			`**Offset:** ${selectedEntry.offset}`,
			`**Béarla:** ${selectedEntry.english}`,
			`**Buiséad:** ${selectedEntry.budget} giotán`,
			`**Aistriúchán reatha:** ${selectedEntry.irish || 'Gan aistriú'}`,
			`**Moladh nua:** ${suggestedIrish || 'Gan líonadh'}`,
			`**Fad ionchódaithe:** ${suggestionUsed}/${selectedEntry.budget}`,
			'',
			suggestionNote ? `**Nótaí:**\n${suggestionNote}` : '',
		]
			.filter(Boolean)
			.join('\n');
		const url = new URL(issueNewUrl());
		url.searchParams.set('title', title);
		url.searchParams.set('body', body);
		url.searchParams.set('labels', 'string-suggestion,needs-native-review');
		window.open(url.toString(), '_blank', 'noopener,noreferrer');
		closeSuggest();
	}

	function openVerifyIssue(entry: StringRecord): void {
		const title = `[Native Review] ${entry.offset} · ${entry.english}`;
		const body = [
			'## Athbhreithniú Dúchasach',
			'',
			`**Cluiche:** ${game.title}`,
			`**Offset:** ${entry.offset}`,
			`**Béarla:** ${entry.english}`,
			`**Aistriúchán reatha:** ${entry.irish || 'Gan aistriú'}`,
			`**Fad ionchódaithe:** ${entry.used}/${entry.budget}`,
			'',
			'Cuir in iúl anseo an bhfuil an leagan Gaeilge nádúrtha agus inghlactha.',
		].join('\n');
		const url = new URL(issueNewUrl());
		url.searchParams.set('title', title);
		url.searchParams.set('body', body);
		url.searchParams.set('labels', 'needs-native-review');
		window.open(url.toString(), '_blank', 'noopener,noreferrer');
	}
</script>

<svelte:head>
	<title>{game.title} · Tábla téacsanna · Gaeilge sa Chonsol</title>
</svelte:head>

<section class="section-wrap py-10">
	<div class="mb-8 flex flex-wrap items-center gap-4">
		<a
			class="inline-flex items-center gap-2 rounded-sm border border-console-border-moderate bg-console-border-subtle px-3 py-2 font-mono text-[0.68rem] uppercase tracking-[0.12em] text-console-muted hover:border-console-green hover:bg-console-green-glow hover:text-console-green"
			href={detailHref}
		>
			<span aria-hidden="true">←</span>
			<span>Ar ais</span>
		</a>
		<div>
			<h1 class="font-display text-[clamp(2rem,5vw,3.3rem)] font-black leading-none text-white">
				{game.title}
			</h1>
			<p class="mt-2 font-mono text-[0.68rem] uppercase tracking-[0.14em] text-console-tertiary">
				{game.consoleLabel} · {game.region} · {game.serial}
			</p>
		</div>
		<p class="ml-auto font-mono text-[0.68rem] uppercase tracking-[0.14em] text-console-tertiary">
			{summaryText}
		</p>
	</div>

	<div class="mb-8">
		<div class="h-1.5 overflow-hidden bg-white/6">
			<div
				class="h-full bg-console-green transition-[width] duration-700 ease-out"
				style={`width:${game.progress}%;box-shadow:0 0 20px ${game.accent}55`}
			></div>
		</div>
	</div>

	<div class="mb-6 flex flex-wrap items-center gap-3 border-b border-console-border pb-4">
		{#each STATUS_OPTIONS as option}
			<button
				class={`inline-flex cursor-pointer items-center gap-2 rounded-sm border px-3 py-2 font-mono text-[0.62rem] uppercase tracking-[0.12em] transition-colors ${selectedStatus === option.value ? 'border-console-green bg-console-green-glow text-console-green' : 'border-console-border-moderate bg-console-border-subtle text-console-muted hover:border-console-green hover:bg-console-green-glow hover:text-console-green'}`}
				onclick={() => (selectedStatus = option.value)}
				type="button"
			>
				<span class={`h-2 w-2 rounded-full ${option.dotClass}`}></span>
				<span>{option.label}</span>
			</button>
		{/each}

		<input
			bind:value={searchQuery}
			class="ml-auto w-full rounded-sm border border-console-border bg-console-bg-2 px-3 py-2 font-mono text-[0.68rem] uppercase tracking-[0.08em] text-console-text outline-none transition-colors placeholder:text-console-muted focus:border-console-green sm:w-64"
			placeholder="Cuardaigh téacs..."
			type="search"
		/>
	</div>

	<div class="mb-8 flex flex-wrap gap-4 font-mono text-[0.58rem] uppercase tracking-[0.1em] text-console-tertiary">
		<span class="inline-flex items-center gap-2">
			<span class="h-2 w-2 rounded-full bg-console-green shadow-[0_0_8px_rgba(46,204,113,0.45)]"></span>
			Fíoraithe
		</span>
		<span class="inline-flex items-center gap-2">
			<span class="h-2 w-2 rounded-full bg-console-amber"></span>
			Dréacht
		</span>
		<span class="inline-flex items-center gap-2">
			<span class="h-2 w-2 rounded-full bg-[#e67e22]"></span>
			Comhréiteach
		</span>
		<span class="inline-flex items-center gap-2">
			<span class="h-2 w-2 rounded-full border border-white/20 bg-white/12"></span>
			Gan aistriú
		</span>
	</div>

	<div class="space-y-8">
		{#each filteredCategories as category (category.name)}
			<section>
				<button
					class="flex w-full cursor-pointer items-center gap-3 border-b border-console-border pb-3 text-left font-mono text-[0.68rem] uppercase tracking-[0.2em] text-console-green hover:text-white"
					onclick={() => toggleCategory(category.name)}
					type="button"
				>
					<span class={`text-[0.7rem] transition-transform ${isCollapsed(category.name) ? '-rotate-90' : ''}`}>▼</span>
					<span>{category.name}</span>
					<span class="ml-auto text-[0.6rem] tracking-[0.12em] text-console-tertiary">
						{category.verifiedCount}/{category.total} fíoraithe
					</span>
				</button>

				{#if !isCollapsed(category.name)}
					<div class="overflow-x-auto">
						<table class="mt-2 w-full min-w-[900px] border-collapse">
							<tbody>
								{#each category.strings as entry (entry.offset)}
									<tr class={`group border-b border-white/4 transition-colors hover:bg-white/[0.02] ${entry.compromised && entry.note ? 'border-l-2 border-l-console-amber' : ''}`}>
										<td class="w-20 px-2 py-3 align-top font-mono text-[0.62rem] text-console-address">
											{entry.offset}
										</td>
										<td class="w-8 px-2 py-3 align-top">
											<span
												class={`mt-1 inline-block h-2 w-2 rounded-full ${statusDotClass(entry.status)}`}
												title={statusLabel(entry.status)}
											></span>
										</td>
										<td class="w-[28%] px-2 py-3 align-top font-mono text-[0.72rem] text-console-muted">
											{entry.english}
										</td>
										<td class="w-[28%] px-2 py-3 align-top font-mono text-[0.72rem] text-console-irish">
											{#if entry.irish}
												{entry.irish}
											{:else}
												<span class="font-body text-[0.76rem] italic text-console-tertiary">gan aistriú</span>
											{/if}
										</td>
										<td class="w-24 px-2 py-3 align-top text-center">
											<span class={`inline-flex rounded-sm border px-2 py-1 font-mono text-[0.58rem] ${budgetClass(entry)}`}>
												{budgetText(entry)}
											</span>
										</td>
										<td class="w-32 px-2 py-3 align-top">
											<div class="flex justify-end gap-2 opacity-0 transition-opacity group-hover:opacity-100">
												{#if entry.irish && !entry.verified}
													<button
														class="rounded-sm border border-console-green/30 px-2 py-1 font-mono text-[0.56rem] uppercase tracking-[0.06em] text-console-green hover:border-console-green hover:bg-console-green-glow"
														onclick={() => openVerifyIssue(entry)}
														type="button"
													>
														✓ Fíoraigh
													</button>
												{/if}
												<button
													class="rounded-sm border border-console-amber/30 px-2 py-1 font-mono text-[0.56rem] uppercase tracking-[0.06em] text-console-amber hover:border-console-amber hover:bg-console-amber/10"
													onclick={() => openSuggest(entry)}
													type="button"
												>
													✎ Mol
												</button>
											</div>
										</td>
									</tr>
									{#if entry.compromised && entry.note}
										<tr>
											<td colspan="6" class="px-2 pb-4 pl-28">
												<div class="flex gap-3 rounded-sm border border-console-amber/20 bg-console-amber/6 px-4 py-3 text-sm leading-6 text-console-muted">
													<span class="text-console-amber">⚠</span>
													<div>
														<p>{entry.note}</p>
														<p class="mt-1 font-mono text-[0.58rem] uppercase tracking-[0.12em] text-console-tertiary">
															Comhréiteach de bharr teorainn bhuiséid · moltaí eile fáilte
														</p>
													</div>
												</div>
											</td>
										</tr>
									{/if}
								{/each}
							</tbody>
						</table>
					</div>
				{/if}
			</section>
		{/each}
	</div>

	{#if filteredCategories.length === 0}
		<div class="panel p-6 text-center font-mono text-[0.68rem] uppercase tracking-[0.12em] text-console-tertiary">
			Níor aimsíodh téacsanna a mheaitseálann na scagairí seo.
		</div>
	{/if}
</section>

<div
	class={`fixed inset-x-0 bottom-0 z-[300] border-t border-console-green bg-console-bg-2 px-4 py-6 transition-transform duration-300 sm:px-8 ${selectedEntry ? 'translate-y-0' : 'translate-y-full'}`}
>
	{#if selectedEntry}
		<div class="mx-auto max-w-6xl">
			<div class="mb-4 flex flex-wrap items-start gap-4">
				<div>
					<h2 class="font-display text-2xl font-bold uppercase tracking-[0.04em] text-white">
						Mol aistriúchán
					</h2>
					<p class="mt-2 font-mono text-[0.68rem] uppercase tracking-[0.12em] text-console-tertiary">
						{selectedEntry.offset} · {selectedEntry.english} · buiséad: {selectedEntry.budget} giotán
					</p>
				</div>
				<button
					class="ml-auto rounded-sm border border-console-border-moderate bg-console-border-subtle px-3 py-2 font-mono text-[0.62rem] uppercase tracking-[0.12em] text-console-muted hover:border-console-green hover:bg-console-green-glow hover:text-console-green"
					onclick={closeSuggest}
					type="button"
				>
					✕ Dún
				</button>
			</div>

				<div class="grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_auto]">
					<div class="space-y-2">
						<label class="mono-label text-console-muted" for="suggest-english">Bunleagan</label>
						<input
							id="suggest-english"
							class="w-full rounded-sm border border-console-border bg-console-bg-3 px-3 py-3 font-mono text-sm text-console-text outline-none"
							readonly
							value={selectedEntry.english}
						/>
					</div>
					<div class="space-y-2">
						<label class="mono-label text-console-muted" for="suggest-irish">Do mholadh</label>
						<input
							bind:value={suggestedIrish}
							id="suggest-irish"
							class="w-full rounded-sm border border-console-border bg-console-bg-3 px-3 py-3 font-mono text-sm text-console-text outline-none focus:border-console-green"
							placeholder="..."
							type="text"
						/>
					<p class={`font-mono text-[0.68rem] uppercase tracking-[0.1em] ${suggestionBudgetClass}`}>
						{suggestionUsed} / {selectedEntry.budget} giotán
					</p>
				</div>
				<div class="flex items-end">
					<button class="console-button console-button-primary" onclick={openSuggestionIssue} type="button">
						Oscail eisiúint
					</button>
					</div>
					<div class="lg:col-span-3 space-y-2">
						<label class="mono-label text-console-muted" for="suggest-note">Nót roghnach</label>
						<textarea
							bind:value={suggestionNote}
							id="suggest-note"
							class="min-h-[88px] w-full rounded-sm border border-console-border bg-console-bg-3 px-3 py-3 text-sm text-console-text outline-none focus:border-console-amber"
							placeholder="m.sh. teorainn giotán, rogha eile, nó ceist d'athbhreithneoir dúchais..."
						></textarea>
					<p class="font-mono text-[0.58rem] uppercase tracking-[0.08em] text-console-tertiary">
						Osclófar eisiúint GitHub réamhlíonta le lipéid `string-suggestion` agus `needs-native-review`.
					</p>
				</div>
			</div>
		</div>
	{/if}
</div>
