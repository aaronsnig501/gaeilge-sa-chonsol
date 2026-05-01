export type GameState = 'complete' | 'progress' | 'wanted';
export type GeneratedGameStatus = 'complete' | 'in-progress' | 'planned';

export interface CategoryStatus {
	name: string;
	translated: number;
	total: number;
	progress: number;
}

export interface GeneratedProgress {
	total: number;
	translated: number;
	percent: number;
}

export interface GeneratedCategoryStatus {
	name: string;
	total: number;
	translated: number;
	percent: number;
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
