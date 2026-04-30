import { fetchStatus } from '$lib/data';

export async function load({ fetch }) {
	return {
		status: await fetchStatus(fetch)
	};
}
