<script lang="ts">
	interface Props {
		label: string;
		progress: number;
		accent?: string;
		compact?: boolean;
		countText?: string;
	}

	let {
		label,
		progress,
		accent = '#2ecc71',
		compact = false,
		countText
	}: Props = $props();
</script>

<div class={compact ? 'space-y-1' : 'space-y-2'}>
	<div class="flex items-center justify-between gap-3">
		<span class="mono-label text-console-tertiary">{label}</span>
		<div class="flex items-center gap-2">
			{#if countText}
				<span class="font-mono text-[0.65rem] tracking-[0.08em] text-console-muted">{countText}</span>
			{/if}
			<span class="font-display text-base font-bold" style={`color:${accent}`}>{progress}%</span>
		</div>
	</div>
	<div class={compact ? 'h-1.5' : 'h-2'} style="background:rgba(255,255,255,0.06)">
		<div
			class="h-full transition-[width] duration-700 ease-out"
			style={`width:${progress}%;background:${accent};box-shadow:0 0 18px ${accent}33`}
		></div>
	</div>
</div>
