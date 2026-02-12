<svelte:options runes={true} />

<script lang="ts">
	import { onMount } from 'svelte';
	import Editor from '$lib/components/Editor.svelte';

	onMount(async () => {
		// This route is our early smoke test for Monaco wiring.
		// We don't introspect the editor instance here, but we can
		// at least log a marker when the component is mounted.
		console.log('monaco-smoke route mounted');
	});
</script>

<main class="page-root">
	<section class="editor-section">
		<Editor />
	</section>
</main>

<style>
	.page-root {
		min-height: 100vh;
		display: flex;
	}

	.editor-section {
		flex: 1;
	}
</style>

