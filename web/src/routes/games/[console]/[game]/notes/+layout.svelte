<script lang="ts">
	let { children } = $props();
</script>

<section class="section-wrap py-16">
	<div class="mb-8">
		<a
			class="inline-flex items-center gap-2 font-mono text-[0.72rem] uppercase tracking-[0.14em] text-console-green hover:text-white"
			href="../"
		>
			<span aria-hidden="true">←</span>
			<span>Ar ais chuig leathanach an chluiche</span>
		</a>
	</div>

	<div class="panel p-6 sm:p-8">
		<p class="mono-label text-console-green">// Nótaí teicniúla</p>
		<div class="prose-console mt-6 max-w-none">
			{@render children()}
		</div>
	</div>
</section>
