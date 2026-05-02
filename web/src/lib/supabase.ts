import { browser } from '$app/environment';
import { createBrowserClient, createServerClient } from '@supabase/ssr';
import type { Cookies, RequestEvent } from '@sveltejs/kit';
import type { Session, SupabaseClient } from '@supabase/supabase-js';
import { env } from '$env/dynamic/public';
import type { CategoryStatus, GameStatus, StatusBreakdown, StringRecord, StringStatus, SuggestionRecord } from '$lib/types';

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
	ú: 'ua'
};

export interface SupabaseStringRow {
	game_id: string;
	offset: string;
	english: string;
	irish: string | null;
	budget: number;
	verified: boolean;
	compromised: boolean;
	note: string | null;
	updated_at: string;
}

export interface SupabaseVerificationRow {
	game_id: string;
	offset: string;
	github_username: string | null;
	created_at: string;
}

export interface SupabaseSuggestionRow {
	id: string;
	game_id: string;
	offset: string;
	suggested: string;
	note: string | null;
	github_username: string | null;
	upvotes: number;
	status: 'open' | 'accepted' | 'rejected';
	created_at: string;
}

export interface SupabaseSuggestionVoteRow {
	suggestion_id: string;
	user_id: string;
}

let browserClient: SupabaseClient | null = null;

function publicSupabaseUrl(): string {
	return env.PUBLIC_SUPABASE_URL ?? '';
}

function publicSupabaseKey(): string {
	return env.PUBLIC_SUPABASE_PUBLISHABLE_KEY ?? '';
}

export function isSupabaseConfigured(): boolean {
	return Boolean(publicSupabaseUrl() && publicSupabaseKey());
}

export function createSupabaseBrowserClient(): SupabaseClient | null {
	if (!browser || !isSupabaseConfigured()) return null;
	browserClient ??= createBrowserClient(publicSupabaseUrl(), publicSupabaseKey());
	return browserClient;
}

export function createSupabaseServerClient(event: RequestEvent): SupabaseClient | null {
	if (!isSupabaseConfigured()) return null;

	return createServerClient(publicSupabaseUrl(), publicSupabaseKey(), {
		cookies: {
			getAll: () => event.cookies.getAll(),
			setAll: (cookiesToSet) => {
				cookiesToSet.forEach(({ name, value, options }) => {
					event.cookies.set(name, value, { ...options, path: '/' });
				});
			}
		}
	});
}

export function deriveStringStatus(row: Pick<SupabaseStringRow, 'irish' | 'verified' | 'compromised'>): StringStatus {
	if (!(row.irish ?? '').trim()) return 'untranslated';
	if (row.compromised) return 'compromised';
	if (row.verified) return 'verified';
	return 'draft';
}

function emptyStatusBreakdown(): StatusBreakdown {
	return {
		verified: 0,
		draft: 0,
		compromised: 0,
		untranslated: 0
	};
}

function rebuildCategory(
	category: CategoryStatus,
	overlay: Map<string, SupabaseStringRow>,
	verifications: Map<string, SupabaseVerificationRow>,
	suggestions: Map<string, SuggestionRecord[]>,
): CategoryStatus {
	const strings: StringRecord[] = category.strings.map((entry) => {
		const row = overlay.get(entry.offset.toLowerCase());
		const verification = verifications.get(entry.offset.toLowerCase());
		const suggestionList = suggestions.get(entry.offset.toLowerCase()) ?? [];
		if (!row) {
			return verification
				? {
						...entry,
						verifiedBy: verification.github_username ?? undefined,
						verifiedAt: verification.created_at,
						suggestions: suggestionList,
					}
				: {
						...entry,
						suggestions: suggestionList,
					};
		}

		const irish = (row.irish ?? '').trim();
		return {
			...entry,
			english: row.english || entry.english,
			irish,
			budget: row.budget ?? entry.budget,
			used: encodeRomLength(irish),
			verified: row.verified,
			compromised: row.compromised,
			status: deriveStringStatus(row),
			note: (row.note ?? '').trim() || undefined,
			verifiedBy: verification?.github_username ?? undefined,
			verifiedAt: verification?.created_at,
			suggestions: suggestionList,
		};
	});

	const statusBreakdown = emptyStatusBreakdown();
	let translated = 0;
	let verifiedCount = 0;

	for (const entry of strings) {
		if (entry.irish.trim()) translated += 1;
		if (entry.verified && entry.irish.trim()) verifiedCount += 1;
		statusBreakdown[entry.status] += 1;
	}

	return {
		...category,
		translated,
		progress: category.total > 0 ? Math.round((translated / category.total) * 100) : 0,
		verifiedCount,
		statusBreakdown,
		strings
	};
}

export function mergeSupabaseRows(
	game: GameStatus,
	rows: SupabaseStringRow[],
	verificationRows: SupabaseVerificationRow[] = [],
	suggestionRows: SuggestionRecord[] = [],
): GameStatus {
	const overlay = new Map(rows.map((row) => [row.offset.toLowerCase(), row]));
	const verifications = new Map(
		verificationRows.map((row) => [row.offset.toLowerCase(), row]),
	);
	const suggestions = suggestionRows.reduce((acc, row) => {
		const key = row.offset.toLowerCase();
		const existing = acc.get(key) ?? [];
		existing.push(row);
		acc.set(key, existing);
		return acc;
	}, new Map<string, SuggestionRecord[]>());
	for (const values of suggestions.values()) {
		values.sort((a, b) => {
			if (b.upvotes !== a.upvotes) return b.upvotes - a.upvotes;
			return Date.parse(b.createdAt) - Date.parse(a.createdAt);
		});
	}

	const categories = game.categories.map((category) => rebuildCategory(category, overlay, verifications, suggestions));
	const total = categories.reduce((sum, category) => sum + category.total, 0);
	const translated = categories.reduce((sum, category) => sum + category.translated, 0);
	const statusBreakdown = categories.reduce(
		(acc, category) => {
			acc.verified += category.statusBreakdown.verified;
			acc.draft += category.statusBreakdown.draft;
			acc.compromised += category.statusBreakdown.compromised;
			acc.untranslated += category.statusBreakdown.untranslated;
			return acc;
		},
		emptyStatusBreakdown(),
	);

	return {
		...game,
		progress: total > 0 ? Math.round((translated / total) * 100) : 0,
		helpWanted: translated < total,
		statusBreakdown,
		categories
	};
}

function encodeRomLength(value: string): number {
	if (!value.trim()) return 0;
	let encoded = value;
	for (const [original, replacement] of Object.entries(FADA_REPLACEMENTS)) {
		encoded = encoded.replaceAll(original, replacement);
	}
	return Array.from(encoded).length;
}

export async function getInitialSession(cookies: Cookies): Promise<Session | null> {
	if (!isSupabaseConfigured()) return null;

	const client = createServerClient(publicSupabaseUrl(), publicSupabaseKey(), {
		cookies: {
			getAll: () => cookies.getAll(),
			setAll: () => {}
		}
	});

	const { data } = await client.auth.getSession();
	return data.session;
}

export function isSupabaseBrowserReady(): boolean {
	return browser && isSupabaseConfigured();
}

export async function signInWithGitHub(redirectTo: string): Promise<void> {
	const client = createSupabaseBrowserClient();
	if (!client) return;

	await client.auth.signInWithOAuth({
		provider: 'github',
		options: {
			redirectTo,
		},
	});
}

export function mapSuggestionRows(
	rows: SupabaseSuggestionRow[],
	votes: SupabaseSuggestionVoteRow[] = [],
): SuggestionRecord[] {
	const voteSet = new Set(votes.map((vote) => vote.suggestion_id));
	return rows.map((row) => ({
		id: row.id,
		gameId: row.game_id,
		offset: row.offset,
		suggested: row.suggested,
		note: (row.note ?? '').trim() || undefined,
		githubUsername: row.github_username ?? undefined,
		upvotes: row.upvotes,
		status: row.status,
		createdAt: row.created_at,
		userHasUpvoted: voteSet.has(row.id),
	}));
}
