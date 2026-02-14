<svelte:options runes={true} />

<script lang="ts">
	import { onMount } from 'svelte';

	const defaultSnippet = [
		"import cadquery as cq",
		"",
		"def build(params):",
		"    size = float(params.get('size', 10.0))",
		"    return cq.Workplane('XY').box(size, size, size).val()",
		""
	].join('\n');

	const props = $props<{
		initialCode?: string;
		onChange?: (value: string) => void;
	}>();

	let el: HTMLDivElement;
	let editor: import('monaco-editor').editor.IStandaloneCodeEditor | null = null;

	onMount(() => {
		let disposed = false;

		(async () => {
			// Monaco worker wiring must only run in the browser.
			await import('$lib/monaco/bootstrap');

			const monaco = await import('monaco-editor');
			const { formatCode } = await import('$lib/api');
			if (disposed) return;

			editor = monaco.editor.create(el, {
				value: props.initialCode ?? defaultSnippet,
				language: 'python',
				theme: 'vs-dark',
				automaticLayout: true,
				fontSize: 14,
				minimap: { enabled: false }
			});

			editor.onDidChangeModelContent(() => {
				if (!editor) return;
				const value = editor.getValue();
				props.onChange?.(value);
			});

			// Wire Monaco's format action (Shift+Alt+F / Shift+Option+F) to call our /api/format endpoint
			editor.addCommand(
				monaco.KeyMod.Shift | monaco.KeyMod.Alt | monaco.KeyCode.KeyF,
				async () => {
					if (!editor) return;
					const currentValue = editor.getValue();
					try {
						const formatted = await formatCode(currentValue);
						editor.setValue(formatted);
						props.onChange?.(formatted);
					} catch (error) {
						// eslint-disable-next-line no-console
						console.error('Format failed:', error);
					}
				}
			);
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

