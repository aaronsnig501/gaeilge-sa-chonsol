<script lang="ts">
	interface Props {
		href: string;
		className?: string;
		label?: string;
	}

	let { href, className = '', label, children }: Props & { children?: () => unknown } = $props();
</script>

<a
	class={`inline-flex items-center gap-2 ${className}`.trim()}
	href={href}
	rel="noreferrer noopener"
	target="_blank"
>
	{#if children}
		{@render children()}
	{:else if label}
		<span>{label}</span>
	{/if}
	<span
		aria-hidden="true"
		class="inline-flex h-4 w-4 items-center justify-center rounded-[2px] border border-current/35 text-[0.72em] leading-none opacity-85"
	>
		↗
	</span>
</a>
