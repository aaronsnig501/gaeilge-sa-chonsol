import { error } from '@sveltejs/kit';
import { fetchStatus } from '$lib/data';
import { getStaticGameParams } from '$lib/status-static';

export function entries() {
	return getStaticGameParams();
}

export async function load({ fetch, params }) {
	const status = await fetchStatus(fetch);
	const game = status.games.find((entry) => entry.console === params.console && entry.game === params.game);

	if (!game) {
		throw error(404, 'Game not found');
	}

	return {
		game
	};
}
