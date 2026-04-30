export type GameState = 'complete' | 'progress' | 'wanted';

export interface CategoryStatus {
	name: string;
	translated: number;
	total: number;
	progress: number;
}

export interface GameLinks {
	patch?: string;
	repo?: string;
	notes?: string;
	issues?: string;
}

export interface GameStatus {
	console: string;
	game: string;
	title: string;
	subtitle: string;
	region: string;
	serial?: string;
	year?: number;
	state: GameState;
	progress: number;
	description: string;
	accent: string;
	categories: CategoryStatus[];
	nightly?: {
		label: string;
		description: string;
		href: string;
	};
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
