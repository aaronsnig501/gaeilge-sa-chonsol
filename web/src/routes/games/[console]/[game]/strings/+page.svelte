<script lang="ts">
	import { onMount } from 'svelte';
	import { base } from '$app/paths';
	import type { PageProps } from './$types';
	import type { StringRecord, StringStatus, SuggestionRecord } from '$lib/types';
	import {
		createSupabaseBrowserClient,
		isSupabaseBrowserReady,
		mapSuggestionRows,
		mergeSupabaseRows,
		signInWithGitHub,
		type SupabaseSuggestionRow,
		type SupabaseSuggestionVoteRow,
		type SupabaseStringRow,
		type SupabaseVerificationRow,
	} from '$lib/supabase';
	import { get } from 'svelte/store';
	import { supabaseSession } from '$lib/session';

	const PENDING_VERIFY_KEY = 'gsc:pending-verify';
	const PENDING_SUGGEST_KEY = 'gsc:pending-suggest';
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
	let remoteGame = $state<typeof data.game | null>(null);
	const game = $derived(remoteGame ?? data.game);
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
	let verifyMessage = $state<string | null>(null);
	let verifyMessageTone = $state<'success' | 'error'>('success');
	let suggestionMessage = $state<string | null>(null);
	let suggestionMessageTone = $state<'success' | 'error'>('success');
	let verificationBusyOffsets = $state<Record<string, boolean>>({});
	let suggestionBusy = $state(false);
	let suggestionBusyOffsets = $state<Record<string, boolean>>({});
	let contributor = $state(false);

	function setVerifyBusy(offset: string, busy: boolean): void {
		verificationBusyOffsets = {
			...verificationBusyOffsets,
			[offset]: busy,
		};
	}

	function isVerifyBusy(offset: string): boolean {
		return verificationBusyOffsets[offset] === true;
	}

	function setSuggestionBusy(offset: string, busy: boolean): void {
		suggestionBusyOffsets = {
			...suggestionBusyOffsets,
			[offset]: busy,
		};
	}

	function isSuggestionBusy(offset: string): boolean {
		return suggestionBusyOffsets[offset] === true;
	}

	onMount(async () => {
		if (!isSupabaseBrowserReady()) return;

		const client = createSupabaseBrowserClient();
		if (!client) return;

		await refreshContributorState();
		await refreshFromSupabase();
		await processPendingVerify();
		await processPendingSuggestion();
	});

	async function refreshFromSupabase(): Promise<void> {
		const client = createSupabaseBrowserClient();
		if (!client) return;

		const session = get(supabaseSession);
		const suggestionVotesQuery = session
			? client
					.from('suggestion_votes')
					.select('suggestion_id, user_id')
					.eq('user_id', session.user.id)
			: Promise.resolve({ data: [] as SupabaseSuggestionVoteRow[] | null, error: null });

		const [{ data: rows, error }, { data: verificationRows }, { data: suggestionRows }, voteResult] = await Promise.all([
			client
				.from('strings')
				.select('id, game_id, offset, english, irish, budget, verified, compromised, note, updated_at')
				.eq('game_id', game.game)
				.order('offset', { ascending: true }),
			client
				.from('verifications')
				.select('game_id, offset, github_username, created_at')
				.eq('game_id', game.game)
				.order('created_at', { ascending: false }),
			client
				.from('suggestions')
				.select('id, game_id, offset, suggested, note, github_username, upvotes, status, created_at')
				.eq('game_id', game.game)
				.order('created_at', { ascending: false }),
			suggestionVotesQuery,
		]);

		if (error || !rows) return;
		const latestVerificationByOffset = new Map<string, SupabaseVerificationRow>();
		for (const row of (verificationRows ?? []) as SupabaseVerificationRow[]) {
			const key = row.offset.toLowerCase();
			if (!latestVerificationByOffset.has(key)) {
				latestVerificationByOffset.set(key, row);
			}
		}

		const mappedSuggestions = mapSuggestionRows(
			(suggestionRows ?? []) as SupabaseSuggestionRow[],
			(voteResult.data ?? []) as SupabaseSuggestionVoteRow[],
		);

		remoteGame = mergeSupabaseRows(
			data.game,
			rows as SupabaseStringRow[],
			Array.from(latestVerificationByOffset.values()),
			mappedSuggestions,
		);
	}

	async function refreshContributorState(): Promise<void> {
		const client = createSupabaseBrowserClient();
		const session = get(supabaseSession);
		if (!client || !session) {
			contributor = false;
			return;
		}

		const { data, error } = await client
			.from('contributors')
			.select('user_id')
			.eq('user_id', session.user.id)
			.maybeSingle();

		if (error) {
			contributor = false;
			verifyMessageTone = 'error';
			verifyMessage = `Theip ar sheiceáil ranníocóra: ${error.message}`;
			return;
		}

		contributor = Boolean(data);
	}

	function pendingVerifyPayload(entry: StringRecord): string {
		return JSON.stringify({
			gameId: game.game,
			offset: entry.offset,
		});
	}

	function findEntryByOffset(offset: string): StringRecord | undefined {
		for (const category of game.categories) {
			const entry = category.strings.find((current) => current.offset === offset);
			if (entry) return entry;
		}
		return undefined;
	}

	async function startVerify(entry: StringRecord): Promise<void> {
		verifyMessage = null;
		if (!isSupabaseBrowserReady()) {
			verifyMessageTone = 'error';
			verifyMessage = 'Níl an ghné seo ar fáil faoi láthair.';
			return;
		}
		const session = get(supabaseSession);
		if (!session) {
			sessionStorage.setItem(PENDING_VERIFY_KEY, pendingVerifyPayload(entry));
			await signInWithGitHub(window.location.href);
			return;
		}

		await completeVerify(entry.offset);
	}

	async function processPendingVerify(): Promise<void> {
		const session = get(supabaseSession);
		if (!session) return;

		const raw = sessionStorage.getItem(PENDING_VERIFY_KEY);
		if (!raw) return;

		try {
			const pending = JSON.parse(raw) as { gameId?: string; offset?: string };
			if (pending.gameId !== game.game || !pending.offset) return;
			sessionStorage.removeItem(PENDING_VERIFY_KEY);
			await completeVerify(pending.offset);
		} catch {
			sessionStorage.removeItem(PENDING_VERIFY_KEY);
		}
	}

	function pendingSuggestionPayload(entry: StringRecord): string {
		return JSON.stringify({
			gameId: game.game,
			offset: entry.offset,
			suggested: suggestedIrish,
			note: suggestionNote,
		});
	}

	async function processPendingSuggestion(): Promise<void> {
		const session = get(supabaseSession);
		if (!session) return;

		const raw = sessionStorage.getItem(PENDING_SUGGEST_KEY);
		if (!raw) return;

		try {
			const pending = JSON.parse(raw) as {
				gameId?: string;
				offset?: string;
				suggested?: string;
				note?: string;
			};
			if (pending.gameId !== game.game || !pending.offset || !pending.suggested) return;
			sessionStorage.removeItem(PENDING_SUGGEST_KEY);
			await submitSuggestion(pending.offset, pending.suggested, pending.note ?? '');
		} catch {
			sessionStorage.removeItem(PENDING_SUGGEST_KEY);
		}
	}

	function applyOptimisticVerify(offset: string, sessionUsername?: string): typeof data.game {
		return {
			...game,
			categories: game.categories.map((category) => ({
				...category,
				verifiedCount: category.strings.some((entry) => entry.offset === offset && entry.irish && !entry.verified)
					? category.verifiedCount + 1
					: category.verifiedCount,
				statusBreakdown: {
					...category.statusBreakdown,
					verified:
						category.statusBreakdown.verified +
						(category.strings.some((entry) => entry.offset === offset && entry.irish && !entry.verified) ? 1 : 0),
					draft:
						category.statusBreakdown.draft -
						(category.strings.some((entry) => entry.offset === offset && entry.irish && !entry.verified && !entry.compromised) ? 1 : 0),
				},
				strings: category.strings.map((entry) =>
					entry.offset === offset
						? {
								...entry,
								verified: true,
								status: entry.compromised ? 'compromised' : 'verified',
								verifiedBy: sessionUsername ?? entry.verifiedBy,
								verifiedAt: new Date().toISOString(),
							}
						: entry,
				),
			})),
			statusBreakdown: {
				...game.statusBreakdown,
				verified: game.statusBreakdown.verified + 1,
				draft:
					game.statusBreakdown.draft -
					(game.categories.some((category) =>
						category.strings.some((entry) => entry.offset === offset && entry.irish && !entry.verified && !entry.compromised),
					)
						? 1
						: 0),
			},
		};
	}

	async function completeVerify(offset: string): Promise<void> {
		const client = createSupabaseBrowserClient();
		const session = get(supabaseSession);
		if (!client || !session) return;
		setVerifyBusy(offset, true);
		verifyMessage = null;
		const targetEntry = findEntryByOffset(offset);
		if (!targetEntry?.rowId) {
			verifyMessageTone = 'error';
			verifyMessage = 'Níor aimsíodh an ró Supabase don téacs seo.';
			setVerifyBusy(offset, false);
			return;
		}

		const previousGame = remoteGame ?? data.game;
		const sessionUsername =
			(session.user.user_metadata?.user_name as string | undefined) ??
			(session.user.user_metadata?.preferred_username as string | undefined) ??
			(session.user.email ?? undefined);

		const { data: contributorRow, error: contributorError } = await client
			.from('contributors')
			.select('user_id')
			.eq('user_id', session.user.id)
			.maybeSingle();

		if (contributorError) {
			verifyMessageTone = 'error';
			verifyMessage = `Theip ar sheiceáil ranníocóra: ${contributorError.message}`;
			setVerifyBusy(offset, false);
			return;
		}

		if (!contributorRow) {
			verifyMessageTone = 'error';
			verifyMessage = 'Ní ranníocóir thú go fóill.';
			setVerifyBusy(offset, false);
			return;
		}

		remoteGame = applyOptimisticVerify(offset, sessionUsername);

		const { error: updateError } = await client
			.from('strings')
			.update({ verified: true, updated_at: new Date().toISOString() })
			.eq('id', targetEntry.rowId);

		if (updateError) {
			remoteGame = previousGame;
			verifyMessageTone = 'error';
			verifyMessage = 'Theip ar an bhfíorú. Bain triail eile as.';
			setVerifyBusy(offset, false);
			return;
		}

		const { error: insertError } = await client.from('verifications').insert({
			game_id: game.game,
			offset,
			user_id: session.user.id,
			github_username: sessionUsername ?? null,
		});

		if (insertError) {
			remoteGame = previousGame;
			verifyMessageTone = 'error';
			verifyMessage = 'Níorbh fhéidir logáil an fhíoraithe a dhéanamh.';
			setVerifyBusy(offset, false);
			return;
		}

		await refreshFromSupabase();
		verifyMessageTone = 'success';
		verifyMessage = 'Fíoraíodh an téacs seo sa chluiche.';
		await refreshContributorState();
		setVerifyBusy(offset, false);
	}

	async function submitSuggestion(offset: string, suggested: string, note: string): Promise<void> {
		const client = createSupabaseBrowserClient();
		const session = get(supabaseSession);
		if (!client || !session) return;
		suggestionBusy = true;
		suggestionMessage = null;

		const sessionUsername =
			(session.user.user_metadata?.user_name as string | undefined) ??
			(session.user.user_metadata?.preferred_username as string | undefined) ??
			(session.user.email ?? undefined);

		const { error } = await client.from('suggestions').insert({
			game_id: game.game,
			offset,
			suggested,
			note: note || null,
			user_id: session.user.id,
			github_username: sessionUsername ?? null,
		});

		if (error) {
			suggestionBusy = false;
			suggestionMessage = 'Theip ar sheoladh an mholta. Bain triail eile as.';
			return;
		}

		await refreshFromSupabase();
		suggestionBusy = false;
		suggestionMessage = 'Seoladh an moladh nua.';
		closeSuggest();
	}

	async function submitSuggestionFromPanel(): Promise<void> {
		if (!selectedEntry) return;
		suggestionMessage = null;
		if (!isSupabaseBrowserReady()) {
			suggestionMessageTone = 'error';
			suggestionMessage = 'Níl an ghné seo ar fáil faoi láthair.';
			return;
		}
		const session = get(supabaseSession);
		if (!session) {
			sessionStorage.setItem(PENDING_SUGGEST_KEY, pendingSuggestionPayload(selectedEntry));
			await signInWithGitHub(window.location.href);
			return;
		}

		await submitSuggestion(selectedEntry.offset, suggestedIrish, suggestionNote);
	}

	async function upvoteSuggestion(suggestion: SuggestionRecord): Promise<void> {
		if (suggestion.userHasUpvoted) return;
		const client = createSupabaseBrowserClient();
		const session = get(supabaseSession);
		if (!client) {
			suggestionMessageTone = 'error';
			suggestionMessage = 'Níl vótáil beo cumasaithe ar an suíomh seo fós.';
			return;
		}
		if (!session) {
			await signInWithGitHub(window.location.href);
			return;
		}

		setSuggestionBusy(suggestion.id, true);
		suggestionMessage = null;
		const { error } = await client.from('suggestion_votes').insert({
			suggestion_id: suggestion.id,
			user_id: session.user.id,
		});

		if (error) {
			suggestionMessageTone = 'error';
			suggestionMessage = 'Níor éirigh leis an vóta. B’fhéidir go ndearna tú vóta cheana féin.';
			setSuggestionBusy(suggestion.id, false);
			return;
		}

		await refreshFromSupabase();
		setSuggestionBusy(suggestion.id, false);
	}

	async function acceptSuggestion(entry: StringRecord, suggestion: SuggestionRecord): Promise<void> {
		const client = createSupabaseBrowserClient();
		const session = get(supabaseSession);
		if (!client) {
			suggestionMessageTone = 'error';
			suggestionMessage = 'Níl glacadh le moltaí beo cumasaithe ar an suíomh seo fós.';
			return;
		}
		if (!session) return;
		if (!contributor) {
			suggestionMessage = 'Ní ranníocóir thú go fóill.';
			return;
		}

		setSuggestionBusy(suggestion.id, true);
		suggestionMessage = null;

		const previousGame = remoteGame ?? data.game;
		remoteGame = {
			...game,
			categories: game.categories.map((category) => ({
				...category,
				strings: category.strings.map((current) =>
					current.offset === entry.offset
						? {
								...current,
								irish: suggestion.suggested,
								used: encodeLength(suggestion.suggested),
								note: suggestion.note,
								verified: false,
								verifiedBy: undefined,
								verifiedAt: undefined,
								status: current.compromised ? 'compromised' : 'draft',
								suggestions: (current.suggestions ?? []).map((item) => ({
									...item,
									status: item.id === suggestion.id ? 'accepted' : item.status,
								})),
							}
						: current,
				),
			})),
		};

		const { error: updateStringError } = await client
			.from('strings')
			.update({
				irish: suggestion.suggested,
				note: suggestion.note ?? null,
				verified: false,
				updated_at: new Date().toISOString(),
			})
			.eq('game_id', game.game)
			.eq('offset', entry.offset);

		if (updateStringError) {
			remoteGame = previousGame;
			suggestionMessage = 'Níorbh fhéidir an moladh a ghlacadh.';
			setSuggestionBusy(suggestion.id, false);
			return;
		}

		const { error: updateSuggestionError } = await client
			.from('suggestions')
			.update({ status: 'accepted' })
			.eq('id', suggestion.id);

		if (updateSuggestionError) {
			remoteGame = previousGame;
			suggestionMessage = 'Theip ar nuashonrú stádais an mholta.';
			setSuggestionBusy(suggestion.id, false);
			return;
		}

		await refreshFromSupabase();
		suggestionMessage = 'Glacadh leis an moladh.';
		setSuggestionBusy(suggestion.id, false);
	}

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

	function displayDotClass(entry: StringRecord): string {
		if (entry.verified) {
			return 'bg-console-green shadow-[0_0_8px_rgba(46,204,113,0.45)]';
		}
		if (entry.compromised) {
			return 'bg-[#e67e22]';
		}
		return statusDotClass(entry.status);
	}

	function displayDotLabel(entry: StringRecord): string {
		if (entry.verified && entry.compromised) {
			return 'Fíoraithe sa chluiche · Comhréiteach';
		}
		if (entry.verified) {
			return 'Fíoraithe sa chluiche';
		}
		if (entry.compromised) {
			return 'Comhréiteach';
		}
		return statusLabel(entry.status);
	}

	function verificationBadgeClass(entry: StringRecord): string {
		if (entry.verified) {
			return 'border-console-green/30 bg-console-green-glow text-console-green';
		}
		return 'border-console-border-moderate bg-console-border-subtle text-console-tertiary';
	}

	function verificationBadgeLabel(entry: StringRecord): string {
		return entry.verified ? 'Fíoraithe sa chluiche' : 'Gan fíorú';
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

	function verificationTooltip(entry: StringRecord): string {
		if (!entry.verified) return 'Gan fíorú sa chluiche fós';
		const who = entry.verifiedBy ? ` ag ${entry.verifiedBy}` : '';
		const when = entry.verifiedAt ? ` · ${new Date(entry.verifiedAt).toLocaleString()}` : '';
		return `Fíoraithe sa chluiche${who}${when}`;
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

	{#if verifyMessage}
		<div class={`mb-6 rounded-sm px-4 py-3 text-sm text-console-text ${verifyMessageTone === 'error' ? 'border border-console-red/30 bg-console-red/10' : 'border border-console-green/30 bg-console-green-glow'}`}>
			{verifyMessage}
		</div>
	{/if}

	{#if suggestionMessage}
		<div class={`mb-6 rounded-sm px-4 py-3 text-sm text-console-text ${suggestionMessageTone === 'error' ? 'border border-console-red/30 bg-console-red/10' : 'border border-console-amber/30 bg-console-amber/10'}`}>
			{suggestionMessage}
		</div>
	{/if}

	<div class="mb-8 flex flex-wrap gap-4 font-mono text-[0.58rem] uppercase tracking-[0.1em] text-console-tertiary">
		<span class="inline-flex items-center gap-2">
			<span class="inline-flex rounded-sm border border-console-green/30 bg-console-green-glow px-2 py-0.5 text-console-green">
				✓ Fíoraithe sa chluiche
			</span>
		</span>
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
											<div class="relative inline-flex">
												<span
													class={`mt-1 inline-block h-2 w-2 rounded-full ${displayDotClass(entry)}`}
													title={displayDotLabel(entry)}
												></span>
												{#if entry.verified}
													<div class="pointer-events-none absolute left-4 top-0 z-10 hidden min-w-52 rounded-sm border border-console-green/30 bg-console-bg-3 px-3 py-2 text-[0.62rem] leading-5 text-console-text shadow-lg group-hover:block">
														{verificationTooltip(entry)}
													</div>
												{/if}
											</div>
										</td>
										<td class="w-[28%] px-2 py-3 align-top font-mono text-[0.72rem] text-console-muted">
											{entry.english}
										</td>
										<td class="w-[28%] px-2 py-3 align-top font-mono text-[0.72rem] text-console-irish">
											{#if entry.irish}
												<div>{entry.irish}</div>
												<div class="mt-2 flex flex-wrap gap-2">
													<span
														class={`inline-flex rounded-sm border px-2 py-0.5 font-mono text-[0.52rem] uppercase tracking-[0.08em] ${verificationBadgeClass(entry)}`}
														title={verificationTooltip(entry)}
													>
														{verificationBadgeLabel(entry)}
													</span>
													{#if entry.compromised}
														<span class="inline-flex rounded-sm border border-console-amber/30 bg-console-amber/10 px-2 py-0.5 font-mono text-[0.52rem] uppercase tracking-[0.08em] text-console-amber">
															Comhréiteach
														</span>
													{/if}
												</div>
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
												{#if entry.irish}
													<button
														class="rounded-sm border border-console-green/30 px-2 py-1 font-mono text-[0.56rem] uppercase tracking-[0.06em] text-console-green hover:border-console-green hover:bg-console-green-glow disabled:cursor-not-allowed disabled:opacity-60"
														disabled={isVerifyBusy(entry.offset)}
														onclick={() => startVerify(entry)}
														type="button"
													>
														{isVerifyBusy(entry.offset) ? '…' : entry.verified ? '↺ Athfhíoraigh' : '✓ Fíoraigh'}
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
									{#if entry.suggestions && entry.suggestions.length > 0}
										<tr>
											<td colspan="6" class="px-2 pb-4 pl-28">
												<div class="space-y-3">
													{#each entry.suggestions as suggestion (suggestion.id)}
														<div class="rounded-sm border border-console-border bg-console-bg-3/70 px-4 py-3">
															<div class="flex flex-wrap items-start gap-3">
																<div class="flex-1">
																	<div class="flex flex-wrap items-center gap-2">
																		<span class="font-mono text-[0.72rem] text-console-irish">{suggestion.suggested}</span>
																		<span class={`rounded-sm border px-2 py-0.5 font-mono text-[0.52rem] uppercase tracking-[0.08em] ${suggestion.status === 'accepted' ? 'border-console-green/30 bg-console-green/10 text-console-green' : suggestion.status === 'rejected' ? 'border-console-red/30 bg-console-red/10 text-console-red' : 'border-console-border-moderate bg-console-border-subtle text-console-muted'}`}>
																			{suggestion.status}
																		</span>
																	</div>
																	<p class="mt-2 font-mono text-[0.58rem] uppercase tracking-[0.08em] text-console-tertiary">
																		{suggestion.githubUsername ?? 'gan ainm'} · {new Date(suggestion.createdAt).toLocaleString()}
																	</p>
																	{#if suggestion.note}
																		<p class="mt-2 text-sm leading-6 text-console-muted">{suggestion.note}</p>
																	{/if}
																</div>
																<div class="flex items-center gap-2">
																	<button
																		class="rounded-sm border border-console-border-moderate bg-console-border-subtle px-2 py-1 font-mono text-[0.56rem] uppercase tracking-[0.06em] text-console-muted hover:border-console-green hover:bg-console-green-glow hover:text-console-green disabled:cursor-not-allowed disabled:opacity-60"
																		disabled={suggestion.userHasUpvoted || isSuggestionBusy(suggestion.id)}
																		onclick={() => upvoteSuggestion(suggestion)}
																		type="button"
																	>
																		{suggestion.userHasUpvoted ? '✓ Vótáilte' : isSuggestionBusy(suggestion.id) ? '…' : `▲ ${suggestion.upvotes}`}
																	</button>
																	{#if contributor && suggestion.status === 'open'}
																		<button
																			class="rounded-sm border border-console-green/30 px-2 py-1 font-mono text-[0.56rem] uppercase tracking-[0.06em] text-console-green hover:border-console-green hover:bg-console-green-glow disabled:cursor-not-allowed disabled:opacity-60"
																			disabled={isSuggestionBusy(suggestion.id)}
																			onclick={() => acceptSuggestion(entry, suggestion)}
																			type="button"
																		>
																			{isSuggestionBusy(suggestion.id) ? '…' : 'Glac leis'}
																		</button>
																	{/if}
																</div>
															</div>
														</div>
													{/each}
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
					<button
						class="console-button console-button-primary disabled:cursor-not-allowed disabled:opacity-60"
						disabled={suggestionBusy || !suggestedIrish.trim()}
						onclick={submitSuggestionFromPanel}
						type="button"
					>
						{suggestionBusy ? 'Ag seoladh…' : 'Seol moladh'}
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
						Stórálfar an moladh seo i Supabase. Má tá logáil isteach de dhíth, fillfidh tú ar ais anseo i ndiaidh GitHub OAuth.
					</p>
				</div>
			</div>
		</div>
	{/if}
</div>
