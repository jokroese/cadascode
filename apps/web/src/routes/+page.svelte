<svelte:options runes={true} />

<script lang="ts">
	import Editor from '$lib/components/Editor.svelte';
	import Viewer from '$lib/components/Viewer.svelte';
	import { runCadQuery } from '$lib/api';

	const initialCode = [
		"import cadquery as cq",
		"",
		"def build(params):",
		"    size = float(params.get('size', 10.0))",
		"    return cq.Workplane('XY').box(size, size, size).val()",
		""
	].join('\n');

	let code = $state(initialCode);
	let currentGlbUrl = $state('/models/box.glb');
	let runStatus = $state<'idle' | 'running' | 'error'>('idle');
	let lastError = $state<string | null>(null);

	async function onRun() {
		runStatus = 'running';
		lastError = null;

		try {
			const result = await runCadQuery({ code, params: { size: 10 } });

			if (result.status === 'ok' && result.glb_url) {
				currentGlbUrl = result.glb_url;
				runStatus = 'idle';
				lastError = null;
			} else if (result.error) {
				runStatus = 'error';
				lastError = `${result.error.type}: ${result.error.message}`;
			} else {
				runStatus = 'error';
				lastError = 'Unknown error running CadQuery code.';
			}
		} catch (error) {
			runStatus = 'error';
			lastError = error instanceof Error ? error.message : String(error);
		}
	}
</script>

<main class="page-root">
	<section class="editor-section">
		<header class="toolbar">
			<button class="run-button" onclick={onRun} disabled={runStatus === 'running'}>
				{runStatus === 'running' ? 'Running…' : 'Run'}
			</button>
			{#if lastError}
				<div class="error-pill" aria-live="polite">
					{lastError}
				</div>
			{/if}
		</header>
		<div class="editor-container">
			<Editor
				initialCode={initialCode}
				onChange={(value) => {
					code = value;
				}}
			/>
		</div>
	</section>

	<section class="viewer-section">
		<Viewer glbUrl={currentGlbUrl} />
	</section>
</main>

<style>
	.page-root {
		min-height: 100vh;
		display: flex;
		background-color: #111827;
		color: #e5e7eb;
	}

	.editor-section {
		display: flex;
		flex-direction: column;
		width: 50%;
		min-width: 0;
		border-right: 1px solid #1f2937;
	}

	.toolbar {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.5rem 0.75rem;
		border-bottom: 1px solid #1f2937;
		background-color: #020617;
	}

	.run-button {
		padding: 0.35rem 0.9rem;
		border-radius: 9999px;
		border: none;
		background: linear-gradient(to right, #22c55e, #16a34a);
		color: #0b1120;
		font-size: 0.85rem;
		font-weight: 600;
		cursor: pointer;
		transition: transform 0.08s ease-out, box-shadow 0.08s ease-out, opacity 0.1s ease-out;
		box-shadow: 0 8px 16px rgba(34, 197, 94, 0.25);
	}

	.run-button:hover:enabled {
		transform: translateY(-1px);
		box-shadow: 0 10px 20px rgba(34, 197, 94, 0.35);
	}

	.run-button:disabled {
		opacity: 0.6;
		cursor: default;
		box-shadow: none;
	}

	.error-pill {
		max-width: 60%;
		padding: 0.3rem 0.75rem;
		border-radius: 9999px;
		background-color: rgba(239, 68, 68, 0.12);
		color: #fca5a5;
		font-size: 0.8rem;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.editor-container {
		flex: 1;
		min-height: 0;
	}

	.viewer-section {
		flex: 1;
		min-width: 0;
	}
</style>

