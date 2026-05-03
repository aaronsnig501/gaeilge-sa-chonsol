export type GameState = 'complete' | 'progress' | 'wanted';
export type GeneratedGameStatus = 'complete' | 'in-progress' | 'planned';
export type StringStatus = 'verified' | 'draft' | 'compromised' | 'untranslated';

export type StatusBreakdown = Record<StringStatus, number>;

export interface GeneratedStringRecord {
	offset: string;
	budget: number;
	used: number;
	english: string;
	irish: string;
	status: StringStatus;
	verified?: boolean;
	compromised?: boolean;
	note?: string;
}

export interface CategoryStatus {
	name: string;
	translated: number;
	total: number;
	progress: number;
	verifiedCount: number;
	statusBreakdown: StatusBreakdown;
	strings: StringRecord[];
}

export interface GeneratedProgress {
	total: number;
	translated: number;
	percent: number;
	status_breakdown?: Partial<StatusBreakdown>;
}

export interface GeneratedCategoryStatus {
	name: string;
	total: number;
	translated: number;
	percent: number;
	status_breakdown?: Partial<StatusBreakdown>;
	flags?: Partial<Record<'verified' | 'compromised', number>>;
	verified?: number;
	strings?: GeneratedStringRecord[];
}

export interface GeneratedGameRecord {
	id: string;
	title: string;
	console: string;
	console_label: string;
	status: GeneratedGameStatus;
	version: string;
	repo_path: string;
	patch_available: boolean;
	help_wanted: boolean;
	progress: GeneratedProgress;
	status_breakdown?: Partial<StatusBreakdown>;
	flags?: Partial<Record<'verified' | 'compromised', number>>;
	categories: GeneratedCategoryStatus[];
	region?: string;
	serial?: string;
	description?: string;
	accent?: string;
	repo_url?: string;
	issues_url?: string;
	notes_path?: string;
}

export interface GeneratedSiteStatus {
	generated: string;
	games: GeneratedGameRecord[];
}

export interface GameLinks {
	patch?: string;
	repo?: string;
	notes?: string;
	issues?: string;
	strings?: string;
}

export interface StringRecord {
	rowId?: string;
	offset: string;
	budget: number;
	used: number;
	english: string;
	irish: string;
	status: StringStatus;
	verified: boolean;
	compromised: boolean;
	note?: string;
	verifiedBy?: string;
	verifiedAt?: string;
	suggestions?: SuggestionRecord[];
}

export interface SuggestionRecord {
	id: string;
	gameId: string;
	offset: string;
	suggested: string;
	note?: string;
	githubUsername?: string;
	upvotes: number;
	status: 'open' | 'accepted' | 'rejected';
	createdAt: string;
	userHasUpvoted?: boolean;
}

export interface GameStatus {
	console: string;
	consoleLabel: string;
	game: string;
	title: string;
	subtitle: string;
	region: string;
	serial?: string;
	year?: number;
	state: GameState;
	statusLabel: string;
	progress: number;
	version?: string;
	description: string;
	accent: string;
	helpWanted: boolean;
	statusBreakdown: StatusBreakdown;
	categories: CategoryStatus[];
	links: GameLinks;
}

export interface SiteSummary {
	completedGames: number;
	activeGames: number;
	translatedStrings: number;
	featuredProgress: number;
}

export interface SiteStatus {
	generatedAt: string;
	summary: SiteSummary;
	games: GameStatus[];
}
