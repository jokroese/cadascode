<svelte:options runes={true} />

<script lang="ts">
	import Viewer from '$lib/components/Viewer.svelte';
</script>

<main class="page-root">
	<section class="viewer-section">
		<Viewer />
	</section>
</main>

<style>
	.page-root {
		min-height: 100vh;
		display: flex;
	}

	.viewer-section {
		flex: 1;
	}
</style>

