import type {
	CategoryStatus,
	GeneratedGameRecord,
	GeneratedGameStatus,
	GameState,
	GameStatus,
	SiteStatus
} from '$lib/types';

const GENERATED_GAME_STATES: GeneratedGameStatus[] = ['complete', 'in-progress', 'planned'];

function clampProgress(value: unknown): number {
	if (typeof value !== 'number' || Number.isNaN(value)) return 0;
	return Math.max(0, Math.min(100, Math.round(value)));
}

function asString(value: unknown, fallback = ''): string {
	return typeof value === 'string' ? value : fallback;
}

function asNumber(value: unknown, fallback = 0): number {
	return typeof value === 'number' && Number.isFinite(value) ? value : fallback;
}

function parseGeneratedState(value: unknown): GeneratedGameStatus {
	return GENERATED_GAME_STATES.includes(value as GeneratedGameStatus)
		? (value as GeneratedGameStatus)
		: 'planned';
}

function toUiState(status: GeneratedGameStatus): GameState {
	switch (status) {
		case 'complete':
			return 'complete';
		case 'in-progress':
			return 'progress';
		case 'planned':
		default:
			return 'wanted';
	}
}

function buildStatusLabel(status: GeneratedGameStatus): string {
	switch (status) {
		case 'complete':
			return 'Críochnaithe';
		case 'in-progress':
			return 'I mbun oibre';
		case 'planned':
		default:
			return 'Cabhair ag teastáil';
	}
}

function buildSubtitle(value: GeneratedGameRecord): string {
	const parts = [asString(value.serial), asString(value.region), asString(value.version && `v${value.version}`)].filter(Boolean);
	if (parts.length > 0) return parts.join(' · ');
	return asString(value.console_label).toUpperCase();
}

function parseGame(game: unknown): GameStatus {
	const value = (game && typeof game === 'object' ? game : {}) as Record<string, unknown>;
	const categories = Array.isArray(value.categories) ? value.categories : [];
	const generated = value as unknown as GeneratedGameRecord;
	const generatedState = parseGeneratedState(value.status);
	const translated = asNumber((value.progress as Record<string, unknown> | undefined)?.translated);
	const total = asNumber((value.progress as Record<string, unknown> | undefined)?.total);
	const progress = clampProgress((value.progress as Record<string, unknown> | undefined)?.percent);

	return {
		console: asString(value.console),
		consoleLabel: asString(value.console_label, asString(value.console).toUpperCase()),
		game: asString(value.id),
		title: asString(value.title),
		subtitle: buildSubtitle(generated),
		region: asString(value.region, asString(value.console_label)),
		serial: asString(value.serial) || undefined,
		year: asNumber(value.year) || undefined,
		state: toUiState(generatedState),
		statusLabel: buildStatusLabel(generatedState),
		progress,
		version: asString(value.version) || undefined,
		description:
			asString(value.description) ||
			`${translated}/${total} téacs aistrithe sa tionscadal seo faoi láthair.`,
		accent: asString(value.accent, '#2ecc71'),
		helpWanted: value.help_wanted === true || progress < 50,
		categories: categories.map((entry) => {
			const category = (entry && typeof entry === 'object' ? entry : {}) as Record<string, unknown>;
			return {
				name: asString(category.name),
				translated: asNumber(category.translated),
				total: asNumber(category.total),
				progress: clampProgress(category.percent)
			};
		}),
		nightly: value.patch_available === true
			? {
					label: `${asString(value.id)}_gaeilge_v${asString(value.version, '0.1')}.bps`,
					description: 'Paiste BPS ar fáil don chluiche seo sa stóras nuair a fhoilsítear é.',
					href: '#'
				}
			: undefined,
		links: {
			repo: asString(value.repo_url) || undefined,
			notes: asString(value.notes_path) || undefined,
			issues: asString(value.issues_url)
				? `${asString(value.issues_url)}?q=${encodeURIComponent(`is:issue ${asString(value.id)}`)}`
				: undefined
		}
	};
}

export async function fetchStatus(fetchFn: typeof fetch): Promise<SiteStatus> {
	const response = await fetchFn('/status.json');
	if (!response.ok) {
		throw new Error(`Failed to load status.json (${response.status})`);
	}

	const payload = (await response.json()) as Record<string, unknown>;
	const games = Array.isArray(payload.games) ? payload.games.map(parseGame) : [];
	const completedGames = games.filter((game) => game.state === 'complete').length;
	const activeGames = games.filter((game) => game.state === 'progress').length;
	const translatedStrings = games.reduce(
		(sum, game) => sum + game.categories.reduce((categorySum, category) => categorySum + category.translated, 0),
		0
	);
	const featuredProgress = games.reduce((best, game) => Math.max(best, game.progress), 0);

	return {
		generatedAt: asString(payload.generated),
		summary: {
			completedGames,
			activeGames,
			translatedStrings,
			featuredProgress
		},
		games
	};
}

export function getGameHref(game: Pick<GameStatus, 'console' | 'game'>): string {
	return `/games/${game.console}/${game.game}`;
}

export function getStateMeta(state: GameState): { label: string; className: string } {
	switch (state) {
		case 'complete':
			return { label: 'Críochnaithe', className: 'border-console-blue/30 bg-console-blue/15 text-console-blue' };
		case 'progress':
			return { label: 'I mbun oibre', className: 'border-console-amber/30 bg-console-amber/15 text-console-amber' };
		case 'wanted':
		default:
			return { label: 'Cabhair ag teastáil', className: 'border-console-red/35 bg-console-red/15 text-console-red' };
	}
}

export function topCategories(game: GameStatus, limit = 3): CategoryStatus[] {
	return game.categories.slice(0, limit);
}

export function consoleName(game: Pick<GameStatus, 'console' | 'consoleLabel'>): string {
	return game.consoleLabel || game.console.toUpperCase();
}
