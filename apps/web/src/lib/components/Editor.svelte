<svelte:options runes={true} />

<script lang="ts">
	import { onMount } from 'svelte';
	import '$lib/monaco/bootstrap';

	let el: HTMLDivElement;
	let editor: import('monaco-editor').editor.IStandaloneCodeEditor | null = null;

	onMount(() => {
		let disposed = false;

		(async () => {
			const monaco = await import('monaco-editor');
			if (disposed) return;

			editor = monaco.editor.create(el, {
				value: 'import cadquery as cq\\n\\nresult = cq.Workplane(\"XY\").box(10, 10, 10)\\n',
				language: 'python',
				theme: 'vs-dark',
				automaticLayout: true,
				fontSize: 14,
				minimap: { enabled: false }
			});
			// Basic example: prove that TS worker wiring works
			console.log('Monaco editor ready');
		})();

		return () => {
			disposed = true;
			editor?.dispose();
		};
	});
</script>

<div class="editor-root">
	<div bind:this={el} class="editor-container"></div>
</div>

<style>
	.editor-root {
		width: 100%;
		height: 100%;
		display: flex;
	}

	.editor-container {
		flex: 1;
	}
</style>

