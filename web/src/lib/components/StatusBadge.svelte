<script lang="ts">
	import { getStateMeta } from '$lib/data';
	import type { GameState } from '$lib/types';

	interface Props {
		state: GameState;
	}

	let { state }: Props = $props();
	const meta = $derived(getStateMeta(state));
</script>

<span class={`status-chip ${meta.className}`}>{meta.label}</span>
