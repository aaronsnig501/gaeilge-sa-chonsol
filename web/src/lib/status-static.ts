import payload from '../../static/status.json';
import type { GeneratedGameRecord, GeneratedSiteStatus } from '$lib/types';

export function getStaticStatus(): GeneratedSiteStatus {
	return payload as GeneratedSiteStatus;
}

export function getStaticGameParams(): Array<{ console: string; game: string }> {
	return getStaticStatus().games.map((game: GeneratedGameRecord) => ({
		console: game.console,
		game: game.id
	}));
}
