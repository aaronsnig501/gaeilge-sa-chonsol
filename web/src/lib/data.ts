import type { GameState, GameStatus, SiteStatus } from '$lib/types';

const GAME_STATES: GameState[] = ['complete', 'progress', 'wanted'];

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

function parseGame(game: unknown): GameStatus {
	const value = (game && typeof game === 'object' ? game : {}) as Record<string, unknown>;
	const categories = Array.isArray(value.categories) ? value.categories : [];
	const state = GAME_STATES.includes(value.state as GameState) ? (value.state as GameState) : 'wanted';

	return {
		console: asString(value.console),
		game: asString(value.game),
		title: asString(value.title),
		subtitle: asString(value.subtitle),
		region: asString(value.region),
		serial: asString(value.serial) || undefined,
		year: asNumber(value.year) || undefined,
		state,
		progress: clampProgress(value.progress),
		description: asString(value.description),
		accent: asString(value.accent, '#2ecc71'),
		categories: categories.map((entry) => {
			const category = (entry && typeof entry === 'object' ? entry : {}) as Record<string, unknown>;
			return {
				name: asString(category.name),
				translated: asNumber(category.translated),
				total: asNumber(category.total),
				progress: clampProgress(category.progress)
			};
		}),
		nightly:
			value.nightly && typeof value.nightly === 'object'
				? {
						label: asString((value.nightly as Record<string, unknown>).label),
						description: asString((value.nightly as Record<string, unknown>).description),
						href: asString((value.nightly as Record<string, unknown>).href)
					}
				: undefined,
		links:
			value.links && typeof value.links === 'object'
				? {
						patch: asString((value.links as Record<string, unknown>).patch) || undefined,
						repo: asString((value.links as Record<string, unknown>).repo) || undefined,
						notes: asString((value.links as Record<string, unknown>).notes) || undefined,
						issues: asString((value.links as Record<string, unknown>).issues) || undefined
					}
				: {}
	};
}

export async function fetchStatus(fetchFn: typeof fetch): Promise<SiteStatus> {
	const response = await fetchFn('/status.json');
	if (!response.ok) {
		throw new Error(`Failed to load status.json (${response.status})`);
	}

	const payload = (await response.json()) as Record<string, unknown>;
	const games = Array.isArray(payload.games) ? payload.games.map(parseGame) : [];
	const summary = (payload.summary && typeof payload.summary === 'object'
		? payload.summary
		: {}) as Record<string, unknown>;

	return {
		generatedAt: asString(payload.generatedAt),
		summary: {
			completedGames: asNumber(summary.completedGames),
			activeGames: asNumber(summary.activeGames),
			translatedStrings: asNumber(summary.translatedStrings),
			featuredProgress: clampProgress(summary.featuredProgress)
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
